#!/bin/bash
# Git Key Manager - Debian Package Builder
# Run this script to create the .deb package

set -e

PACKAGE_NAME="git-key-manager"
VERSION="1.0.0"
ARCH="all"
BUILD_DIR="build/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "Building Git Key Manager v${VERSION}..."

# Clean previous build
rm -rf build
mkdir -p "$BUILD_DIR"

# Create directory structure
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/64x64/apps"
mkdir -p "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME"

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3, python3-pyqt5, openssh-client
Maintainer: Your Name <your.email@example.com>
Description: Git SSH Key Manager with Visual Indicator
 Git Key Manager provides easy SSH key management for GitHub
 and other Git services with a visual indicator showing when
 keys are loaded. Features include:
 .
  - System tray integration
  - Visual key status indicator (green = loaded, red = not loaded)
  - Support for multiple SSH keys
  - One-click key loading
  - GitHub connection testing
  - Auto-start support
EOF

# Create postinst script
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Ensure ssh-agent is available
if ! command -v ssh-agent &> /dev/null; then
    echo "Warning: ssh-agent not found. Please install openssh-client."
fi

# Set permissions
chmod +x /usr/bin/git-key-manager

echo ""
echo "Git Key Manager installed successfully!"
echo "Run 'git-key-manager' to start, or find it in your applications menu."
echo ""
echo "To start automatically at login, enable it in your desktop environment's"
echo "startup applications settings."
echo ""

exit 0
EOF

chmod 755 "$BUILD_DIR/DEBIAN/postinst"

# Create prerm script
cat > "$BUILD_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Kill any running instances
pkill -f git-key-manager || true

exit 0
EOF

chmod 755 "$BUILD_DIR/DEBIAN/prerm"

# Copy main application
cp git-key-manager.py "$BUILD_DIR/usr/bin/git-key-manager"
chmod 755 "$BUILD_DIR/usr/bin/git-key-manager"

# Create desktop entry
cat > "$BUILD_DIR/usr/share/applications/$PACKAGE_NAME.desktop" << EOF
[Desktop Entry]
Name=Git Key Manager
Comment=Manage SSH keys for Git with visual indicator
Exec=/usr/bin/git-key-manager
Icon=git-key-manager
Terminal=false
Type=Application
Categories=Development;Utility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

# Create a simple icon (you should replace this with a proper icon)
cat > "$BUILD_DIR/usr/share/icons/hicolor/64x64/apps/$PACKAGE_NAME.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="28" fill="#2ecc71"/>
  <path d="M 20 32 L 28 40 L 44 24" stroke="white" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
EOF

# Create copyright file
cat > "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: git-key-manager
Source: https://github.com/yourusername/git-key-manager

Files: *
Copyright: 2024 Your Name
License: MIT
EOF

# Create changelog
cat > "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/changelog.gz" << EOF
git-key-manager (1.0.0) unstable; urgency=low

  * Initial release
  * System tray integration
  * Multiple key support
  * Visual status indicator
  * GitHub connection testing

 -- Your Name <your.email@example.com>  $(date -R)
EOF

gzip -9 "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/changelog.gz"

# Create README
cat > "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/README" << 'EOF'
Git Key Manager
===============

A system tray application for managing SSH keys for Git operations.

Features:
- Visual indicator (green = keys loaded, red = no keys)
- Easy key loading with one click
- Support for multiple SSH keys
- GitHub connection testing
- System tray integration

Usage:
1. Click the system tray icon to open the manager
2. Add your SSH keys (usually in ~/.ssh/)
3. Click on a key name to load it
4. Green indicator = ready to push/pull without credentials
5. Red indicator = no key loaded

The application will ensure ssh-agent is running and manage your keys
automatically. As long as the indicator is green, you won't need to
enter credentials for Git operations.

Support:
For issues or questions, visit: https://github.com/yourusername/git-key-manager
EOF

# Build the package
echo "Building .deb package..."
dpkg-deb --build "$BUILD_DIR"

# Move to current directory
mv "$BUILD_DIR.deb" "./${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

echo ""
echo "================================================"
echo "Package built successfully!"
echo "================================================"
echo ""
echo "Install with:"
echo "  sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "Or double-click the .deb file in your file manager."
echo ""
echo "After installation, run: git-key-manager"
echo ""
