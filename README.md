# PROXIFY

A professional proxy checker, scraper, and connection tester tool with comprehensive proxy analysis capabilities.

## Features

- **Proxy Checker**: Validate proxies from a list with detailed information
- **Multi-Protocol Support**: Automatically detects and tests both HTTP and SOCKS5 proxies
- **Proxy Scraper**: Automatically scrape proxies from public sources
- **Connection Tester**: Test individual proxy connections
- **Statistics**: Track your proxy checking history
- **Proxy Classification**: Automatically classify proxies as Residential, Datacenter, or Mobile
- **Geographic Information**: Get country, city, ISP, ASN, and location data for each proxy
- **Multi-threaded**: Fast concurrent checking with configurable thread count

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SpokeOner/PROXIFY.git
cd PROXIFY
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python proxy_checker.py
```

### Menu Options

1. **Basic Proxy Checker**: Check proxies from `proxies.txt`
   - Place your proxies in `proxies.txt` (one per line)
   - Format: `ip:port` or `user:pass@ip:port`
   - Automatically tests both HTTP and SOCKS5 protocols
   - Results are saved to `valid.txt` and `invalid.txt`
   - Valid proxies show the protocol type (HTTP or SOCKS5) in the output

2. **Proxy Scraper**: Scrape proxies from public sources
   - Automatically fetches proxies from multiple sources
   - Results are appended to `scraped.txt`

3. **Proxy Connection Tester**: Test a single proxy connection
   - Enter proxy details manually
   - Supports HTTP and SOCKS5 protocols
   - Displays detailed connection information

4. **Stats**: View statistics from all checking sessions
   - Total proxies checked
   - Total proxies scraped
   - Total valid proxies found
   - Total runtime
   - Valid rate percentage

## File Format

### Input (`proxies.txt`)
```
192.168.1.1:8080
user:pass@192.168.1.2:3128
10.0.0.1:1080
```

### Output Files
- `valid.txt`: Working proxies
- `invalid.txt`: Non-working proxies
- `scraped.txt`: Proxies from scraping
- `stats.json`: Statistics data

## Configuration

You can modify these constants in `proxy_checker.py`:
- `MAX_THREADS`: Maximum thread count (default: 500)
- `DEFAULT_TIMEOUT`: Request timeout in seconds (default: 8)
- `IPINFO_TIMEOUT`: IP info lookup timeout (default: 5)
- `SCRAPE_TIMEOUT`: Scraping timeout (default: 10)

## Requirements

- Python 3.7+
- requests library
- PySocks library (for SOCKS5 support)

## License

This project is open source and available for use.

## Author

[SpokeOner](https://github.com/SpokeOner)

