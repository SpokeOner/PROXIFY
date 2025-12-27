# GitHub Upload Instructions

## Step 1: Initialize Git Repository

Open PowerShell in the PROXIFY folder and run:

```powershell
git init
```

## Step 2: Add All Files

```powershell
git add .
```

## Step 3: Create Initial Commit

```powershell
git commit -m "Initial commit: PROXIFY proxy checker tool"
```

## Step 4: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `PROXIFY` (or any name you prefer)
3. Description: "Professional proxy checker, scraper, and connection tester"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 5: Connect Local Repository to GitHub

After creating the repo, GitHub will show you commands. Use these (replace `YOUR_USERNAME` with your GitHub username):

```powershell
git remote add origin https://github.com/YOUR_USERNAME/PROXIFY.git
git branch -M main
git push -u origin main
```

## Alternative: If you already have a repository

If the repository already exists on GitHub, just run:

```powershell
git remote add origin https://github.com/SpokeOner/PROXIFY.git
git branch -M main
git push -u origin main
```

## Quick All-in-One Commands

If you want to do it all at once:

```powershell
git init
git add .
git commit -m "Initial commit: PROXIFY proxy checker tool"
git remote add origin https://github.com/SpokeOner/PROXIFY.git
git branch -M main
git push -u origin main
```

**Note:** You may be prompted for your GitHub username and password/token. If you have 2FA enabled, you'll need to use a Personal Access Token instead of your password.

