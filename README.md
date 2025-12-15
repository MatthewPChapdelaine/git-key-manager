# Git Key Manager - Installation & Usage Guide

## Quick Start

### Prerequisites
- Debian-based Linux (Ubuntu, Linux Mint, Debian, etc.)
- Python 3.6+
- PyQt5
- OpenSSH client

### Build and Install

1. **Save the files:**
   - Save `git-key-manager.py` (the main Python application)
   - Save `build-deb.sh` (the build script)

2. **Make the build script executable:**
   ```bash
   chmod +x build-deb.sh
   ```

3. **Run the build script:**
   ```bash
   ./build-deb.sh
   ```

4. **Install the package:**
   ```bash
   sudo dpkg -i git-key-manager_1.0.0_all.deb
   ```

5. **If you get dependency errors, fix them with:**
   ```bash
   sudo apt-get install -f
   ```

6. **Launch the application:**
   ```bash
   git-key-manager
   ```
   Or find it in your applications menu.

## How to Use

### First Time Setup

1. **Start the application** - A system tray icon will appear (red circle initially)

2. **Add your SSH keys:**
   - Click the tray icon (or right-click)
   - Select "Manage Keys"
   - Click "Add Key"
   - Enter a name (e.g., "Work" or "Personal")
   - Browse to your SSH private key (usually `~/.ssh/id_rsa` or `~/.ssh/id_ed25519`)
   - Click OK

3. **Load a key:**
   - Right-click the tray icon
   - Hover over "Load Key"
   - Click on the key you want to use
   - The icon will turn **GREEN** ✓

### Understanding the Indicator

- 🔴 **RED**: No keys loaded - You'll need credentials for Git operations
- 🟢 **GREEN**: Key(s) loaded - Git operations work without credentials!

### Daily Usage

**To push/pull to GitHub without credentials:**
1. Load your key (icon turns green)
2. Use Git normally: `git push`, `git pull`, etc.
3. No username/password needed!

**To switch between keys** (work vs personal):
1. Right-click tray icon
2. Load Key → Select the key you want
3. The new key is now active

**To test your connection:**
1. Right-click tray icon
2. Click "Test GitHub Connection"
3. You'll see your GitHub username if successful

**To unload all keys** (for security):
1. Right-click tray icon
2. Click "Unload All Keys"
3. Icon turns red

## Setting Up GitHub SSH (If You Haven't Already)

### Generate an SSH key (if you don't have one):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### Add the public key to GitHub:
```bash
cat ~/.ssh/id_ed25519.pub
```
Copy the output and:
1. Go to GitHub.com → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste your public key
4. Save

### Convert HTTPS repos to SSH:
If your repos use HTTPS URLs, convert them:
```bash
cd your-repo
git remote set-url origin git@github.com:username/repo.git
```

Or for new clones, use SSH URLs:
```bash
git clone git@github.com:username/repo.git
```

## Auto-Start at Login

### GNOME (Ubuntu, Fedora, etc.):
1. Open "Startup Applications"
2. Click "Add"
3. Name: Git Key Manager
4. Command: `/usr/bin/git-key-manager`
5. Click "Add"

### KDE (Kubuntu, etc.):
1. System Settings → Startup and Shutdown → Autostart
2. Click "Add Application"
3. Select Git Key Manager

### XFCE:
1. Settings → Session and Startup → Application Autostart
2. Click "Add"
3. Name: Git Key Manager
4. Command: `/usr/bin/git-key-manager`

## Troubleshooting

### "Permission denied (publickey)" error
- Make sure the indicator is **GREEN**
- Test connection: Right-click → "Test GitHub Connection"
- Verify your public key is added to GitHub

### Icon not appearing in system tray
- Some desktop environments hide tray icons by default
- GNOME: Install "AppIndicator Support" extension
- KDE: Check System Tray Settings

### ssh-agent not running
The app will try to start it automatically, but if issues persist:
```bash
eval "$(ssh-agent -s)"
```

### Key won't load
- Check the key file exists: `ls -la ~/.ssh/`
- Verify permissions: `chmod 600 ~/.ssh/id_ed25519`
- Try loading manually: `ssh-add ~/.ssh/id_ed25519`

### Green light but still asking for credentials
Your repo might be using HTTPS instead of SSH:
```bash
cd your-repo
git remote -v
```
If you see `https://github.com`, convert it:
```bash
git remote set-url origin git@github.com:username/repo.git
```

## Uninstalling

```bash
sudo dpkg -r git-key-manager
```

## Security Notes

- Keys are loaded into `ssh-agent` in memory only
- Keys are not stored or transmitted by this application
- Use "Unload All Keys" when stepping away from your computer
- Consider using password-protected SSH keys for extra security

## Advanced Usage

### Multiple Keys for Different Repos
You can have work and personal keys and switch between them:
1. Add both keys to the manager
2. Load "Work" key when working on work projects
3. Load "Personal" key for personal projects
4. Git will automatically use the loaded key

### Using with Password-Protected Keys
If your key has a passphrase:
1. When you load the key, you'll be prompted for the passphrase
2. After entering it once, the key stays loaded (green indicator)
3. No need to re-enter for each Git operation

### Checking Loaded Keys
Right-click icon → The status shows how many keys are currently loaded

## Support

If you encounter issues:
1. Check the terminal output: Run `git-key-manager` from terminal to see error messages
2. Verify SSH setup: `ssh -T git@github.com`
3. Check ssh-agent: `ssh-add -l`

## What This Solves

**Before Git Key Manager:**
- Manual ssh-agent management
- Typing credentials repeatedly
- Keys not persisting between sessions
- Uncertainty about authentication status

**After Git Key Manager:**
- One-click key loading
- Visual confirmation (green = good to go!)
- Keys stay loaded until you unload them
- Seamless Git operations without credential prompts
