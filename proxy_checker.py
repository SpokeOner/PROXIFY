# https://github.com/SpokeOner
import requests
import time
import os
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Optional, Dict, List

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

STATS_FILE = "stats.json"
PROXIES_FILE = "proxies.txt"
VALID_FILE = "valid.txt"
INVALID_FILE = "invalid.txt"
SCRAPED_FILE = "scraped.txt"

PROXIFY_ASCII = f"""
{CYAN}
  ____  ____   _____  _____ _______   __
 |  _ \|  _ \ / _ \ \/ /_ _|  ___\ \ / /
 | |_) | |_) | | | \  / | || |_   \ V / 
 |  __/|  _ <| |_| /  \ | ||  _|   | |  
 |_|   |_| \_\\___/_/\_\___|_|     |_|  
                                        
{RESET}"""

MAX_THREADS = 500
DEFAULT_TIMEOUT = 8
IPINFO_TIMEOUT = 5
SCRAPE_TIMEOUT = 10
HTTPBIN_URL = "http://httpbin.org/ip"
IPINFO_URL = "https://ipinfo.io"
SCRAPE_URLS = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000"
]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def menu():
    while True:
        clear_screen()
        print(PROXIFY_ASCII)
        print("1. Basic Proxy Checker")
        print("2. Proxy Scraper")
        print("3. Proxy Connection Tester")
        print("4. Stats")
        print("Press ENTER to exit")
        choice = input("\nSelect an option: ").strip()
        
        if choice == "1":
            proxy_checker()
        elif choice == "2":
            proxy_scraper()
        elif choice == "3":
            proxy_connector()
        elif choice == "4":
            show_stats()
        elif choice == "":
            break
        else:
            print("Invalid option.")
            time.sleep(1)

def classify_ip(ip: str) -> str:
    try:
        response = requests.get(f"{IPINFO_URL}/{ip}/json", timeout=IPINFO_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        org = data.get("org", "").lower()
        
        if any(word in org for word in ["mobile", "cellular", "wireless"]):
            return "Mobile"
        elif any(word in org for word in ["datacenter", "hosting", "server", "cloud"]):
            return "Datacenter"
        elif any(word in org for word in ["isp", "internet service provider"]):
            return "Residential"
        else:
            return "Residential"
    except (requests.RequestException, KeyError, ValueError):
        return "Unknown"

def get_ip_info(ip: str) -> Dict:
    try:
        response = requests.get(f"{IPINFO_URL}/{ip}/json", timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return {}

def extract_ip(proxy: str) -> str:
    try:
        if '@' in proxy:
            return proxy.split('@')[1].split(':')[0]
        return proxy.split(':')[0]
    except (IndexError, AttributeError):
        return "0.0.0.0"

def check_proxy(proxy_url: str) -> Tuple[str, bool, Optional[str], Optional[str], Optional[int]]:
    proxies = {
        "http": f"http://{proxy_url}",
        "https": f"http://{proxy_url}",
    }
    
    try:
        start = time.time()
        response = requests.get(HTTPBIN_URL, proxies=proxies, timeout=DEFAULT_TIMEOUT)
        elapsed = int((time.time() - start) * 1000)
        
        if response.status_code == 200:
            ip = extract_ip(proxy_url)
            proxy_type = classify_ip(ip)
            info = get_ip_info(ip)
            country = info.get("country", "Unknown")
            city = info.get("city", "Unknown")
            org = info.get("org", "Unknown")
            hostname = info.get("hostname", "Unknown")
            loc = info.get("loc", "Unknown")
            asn = org.split()[0] if org != "Unknown" else "Unknown"
            
            print(f"{GREEN}[\u2713] {proxy_url} | {proxy_type} | {country} | {city} | "
                  f"ASN: {asn} | ISP: {org} | Hostname: {hostname} | "
                  f"Coordinates: {loc} | {elapsed}ms{RESET}")
            return proxy_url, True, proxy_type, country, elapsed
    except (requests.RequestException, KeyError, ValueError):
        pass
    
    print(f"{RED}[\u00d7] {proxy_url}{RESET}")
    return proxy_url, False, None, None, None

def proxy_checker():
    start_time = time.time()
    clear_screen()
    print(PROXIFY_ASCII)
    
    try:
        with open(PROXIES_FILE, "r", encoding="utf-8") as f:
            proxy_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{RED}Missing '{PROXIES_FILE}'{RESET}")
        input("Press Enter to return to menu...")
        return
    
    if not proxy_list:
        print(f"{RED}No proxies found in '{PROXIES_FILE}'{RESET}")
        input("Press Enter to return to menu...")
        return
    
    while True:
        try:
            threads = int(input(f"Enter thread amount (max {MAX_THREADS}): ").strip())
            if 1 <= threads <= MAX_THREADS:
                break
            print(f"Please enter a number between 1 and {MAX_THREADS}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    print(f"\nChecking {len(proxy_list)} proxies with {threads} threads...\n")
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(check_proxy, proxy_list))
    
    valid = [r for r in results if r[1]]
    invalid = [r for r in results if not r[1]]
    
    counts = {"Residential": 0, "Datacenter": 0, "Mobile": 0, "Unknown": 0}
    for _, _, ptype, _, _ in valid:
        if ptype in counts:
            counts[ptype] += 1
        else:
            counts["Unknown"] += 1
    
    try:
        with open(VALID_FILE, "w", encoding="utf-8") as f:
            for proxy, _, _, _, _ in valid:
                f.write(f"{proxy}\n")
        
        with open(INVALID_FILE, "w", encoding="utf-8") as f:
            for proxy, _, _, _, _ in invalid:
                f.write(f"{proxy}\n")
    except IOError as e:
        print(f"{RED}Error writing results: {e}{RESET}")
    
    elapsed = time.time() - start_time
    update_stats(checked=len(proxy_list), valid=len(valid), runtime=elapsed)
    
    print()
    print(f"{GREEN}Total Valid: {len(valid)}{RESET}")
    print(f"{YELLOW}Residential: {counts['Residential']}{RESET}")
    print(f"{CYAN}Datacenter: {counts['Datacenter']}{RESET}")
    print(f"{YELLOW}Mobile: {counts['Mobile']}{RESET}")
    print(f"{RED}Dead: {len(invalid)}{RESET}")
    print(f"Check time: {elapsed:.2f} seconds\n")
    
    while True:
        user_input = input("Press 1 to see country count summary, or Enter to exit: ").strip()
        if user_input == "1":
            country_counts = {}
            for _, _, _, country, _ in valid:
                if country and country != "Unknown":
                    country_counts[country] = country_counts.get(country, 0) + 1
            
            if country_counts:
                print("\nCountry counts:")
                for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"{country} - {count}")
                print()
            else:
                print("No country data available.\n")
        elif user_input == "":
            break
        else:
            print("Invalid input. Please press 1 or Enter.")
    
    input("Press Enter to return to menu...")

def proxy_scraper():
    clear_screen()
    print(PROXIFY_ASCII)
    
    all_proxies = set()
    for url in SCRAPE_URLS:
        try:
            response = requests.get(url, timeout=SCRAPE_TIMEOUT)
            response.raise_for_status()
            proxies = response.text.strip().splitlines()
            all_proxies.update(proxy.strip() for proxy in proxies if proxy.strip())
        except (requests.RequestException, ValueError):
            continue
    
    if all_proxies:
        try:
            with open(SCRAPED_FILE, "a", encoding="utf-8") as f:
                for proxy in all_proxies:
                    f.write(f"{proxy}\n")
            print(f"{GREEN}Scraped {len(all_proxies)} proxies saved to {SCRAPED_FILE}{RESET}")
            update_stats(scraped=len(all_proxies))
        except IOError as e:
            print(f"{RED}Error saving proxies: {e}{RESET}")
    else:
        print(f"{RED}No proxies scraped.{RESET}")
    
    input("Press Enter to return to menu...")

def proxy_connector():
    clear_screen()
    print(PROXIFY_ASCII)
    
    proxy = input("Enter proxy (user:pass@ip:port or ip:port): ").strip()
    if not proxy:
        print(f"{RED}No proxy provided.{RESET}")
        input("Press Enter to return to menu...")
        return
    
    proto = input("Protocol (http/socks5): ").strip().lower()
    if proto not in ["http", "socks5"]:
        print(f"{RED}Invalid protocol.{RESET}")
        input("Press Enter to return to menu...")
        return
    
    proxies = {
        "http": f"{proto}://{proxy}",
        "https": f"{proto}://{proxy}"
    }
    
    try:
        start = time.time()
        response = requests.get(f"{IPINFO_URL}/json", proxies=proxies, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        elapsed = int((time.time() - start) * 1000)
        data = response.json()
        
        ip = data.get("ip", "Unknown")
        country = data.get("country", "Unknown")
        city = data.get("city", "Unknown")
        isp = data.get("org", "Unknown")
        hostname = data.get("hostname", "Unknown")
        loc = data.get("loc", "Unknown")
        asn = isp.split()[0] if isp != "Unknown" else "Unknown"
        
        print(f"{GREEN}Connected to proxy | {country} | {city} | ASN: {asn} | "
              f"ISP: {isp} | Hostname: {hostname} | Coordinates: {loc} | {elapsed}ms{RESET}")
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"{RED}Connection failed: {e}{RESET}")
    
    input("Press Enter to return to menu...")

def update_stats(checked: int = 0, scraped: int = 0, valid: int = 0, runtime: float = 0):
    stats = {"checked": 0, "scraped": 0, "valid": 0, "runtime": 0}
    
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                stats = json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
    
    stats["checked"] = stats.get("checked", 0) + checked
    stats["scraped"] = stats.get("scraped", 0) + scraped
    stats["valid"] = stats.get("valid", 0) + valid
    stats["runtime"] = stats.get("runtime", 0) + runtime
    
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except IOError:
        pass

def show_stats():
    clear_screen()
    print(PROXIFY_ASCII)
    
    if not os.path.exists(STATS_FILE):
        print("No stats recorded yet.")
        input("Press Enter to return to menu...")
        return
    
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
    except (IOError, json.JSONDecodeError):
        print("Error reading stats file.")
        input("Press Enter to return to menu...")
        return
    
    valid_rate = (stats["valid"] / stats["checked"] * 100) if stats.get("checked") else 0
    runtime = time.strftime("%H:%M:%S", time.gmtime(stats.get("runtime", 0)))
    
    print(f"{CYAN}Total Checked: {stats.get('checked', 0)}")
    print(f"Total Scraped: {stats.get('scraped', 0)}")
    print(f"Total Valid: {stats.get('valid', 0)}")
    print(f"Runtime: {runtime}")
    print(f"Valid Rate: {valid_rate:.2f}%{RESET}")
    
    input("Press Enter to return to menu...")

if __name__ == "__main__":
    menu()
