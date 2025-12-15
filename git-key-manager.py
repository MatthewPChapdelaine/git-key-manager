#!/usr/bin/env python3
"""
Git Key Manager - SSH Key Management Tool for GitHub
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction, 
                             QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QMessageBox, QInputDialog,
                             QFileDialog)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

class GitKeyManager(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.config_dir = Path.home() / ".config" / "git-key-manager"
        self.config_file = self.config_dir / "keys.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.keys = self.load_keys()
        self.active_key = None
        
        self.setup_ui()
        self.check_ssh_agent()
        self.update_status()
        
        # Auto-check status every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)
    
    def create_icon(self, color):
        """Create a colored circle icon"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()
        return QIcon(pixmap)
    
    def setup_ui(self):
        """Setup system tray icon and menu"""
        self.setIcon(self.create_icon("#808080"))  # Gray initially
        self.setToolTip("Git Key Manager - No key loaded")
        
        menu = QMenu()
        
        # Key section
        self.key_menu = QMenu("Load Key")
        menu.addMenu(self.key_menu)
        self.rebuild_key_menu()
        
        menu.addSeparator()
        
        # Status action
        self.status_action = QAction("Status: No key loaded", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Management actions
        manage_action = QAction("Manage Keys", menu)
        manage_action.triggered.connect(self.show_key_manager)
        menu.addAction(manage_action)
        
        unload_action = QAction("Unload All Keys", menu)
        unload_action.triggered.connect(self.unload_all_keys)
        menu.addAction(unload_action)
        
        test_action = QAction("Test GitHub Connection", menu)
        test_action.triggered.connect(self.test_github)
        menu.addAction(test_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_activated)
        self.show()
    
    def rebuild_key_menu(self):
        """Rebuild the key selection menu"""
        self.key_menu.clear()
        
        if not self.keys:
            no_keys = QAction("No keys configured", self.key_menu)
            no_keys.setEnabled(False)
            self.key_menu.addAction(no_keys)
        else:
            for name, path in self.keys.items():
                action = QAction(name, self.key_menu)
                action.triggered.connect(lambda checked, n=name, p=path: self.load_key(n, p))
                self.key_menu.addAction(action)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.Trigger:
            self.show_key_manager()
    
    def load_keys(self):
        """Load saved keys from config"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_keys(self):
        """Save keys to config"""
        with open(self.config_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def check_ssh_agent(self):
        """Ensure ssh-agent is running"""
        result = subprocess.run(['ssh-add', '-l'], 
                              capture_output=True, text=True)
        if result.returncode == 2:  # Agent not running
            self.showMessage("Git Key Manager", 
                           "SSH agent not running. Starting it...",
                           QSystemTrayIcon.Information, 3000)
            subprocess.run(['ssh-agent', '-s'], capture_output=True)
    
    def load_key(self, name, path):
        """Load an SSH key"""
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            self.showMessage("Error", f"Key file not found: {path}",
                           QSystemTrayIcon.Critical, 3000)
            return
        
        result = subprocess.run(['ssh-add', path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            self.active_key = name
            self.showMessage("Git Key Manager", 
                           f"Key '{name}' loaded successfully!",
                           QSystemTrayIcon.Information, 3000)
            self.update_status()
        else:
            self.showMessage("Error", 
                           f"Failed to load key: {result.stderr}",
                           QSystemTrayIcon.Critical, 3000)
    
    def unload_all_keys(self):
        """Unload all SSH keys"""
        subprocess.run(['ssh-add', '-D'], capture_output=True)
        self.active_key = None
        self.showMessage("Git Key Manager", 
                       "All keys unloaded",
                       QSystemTrayIcon.Information, 3000)
        self.update_status()
    
    def update_status(self):
        """Update icon and status based on loaded keys"""
        result = subprocess.run(['ssh-add', '-l'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            # Keys are loaded
            self.setIcon(self.create_icon("#00FF00"))  # Green
            key_count = len(result.stdout.strip().split('\n'))
            status = f"✓ {key_count} key(s) loaded"
            self.setToolTip(f"Git Key Manager - {status}")
            self.status_action.setText(f"Status: {status}")
        else:
            # No keys loaded
            self.setIcon(self.create_icon("#FF0000"))  # Red
            self.setToolTip("Git Key Manager - No keys loaded")
            self.status_action.setText("Status: No keys loaded")
            self.active_key = None
    
    def test_github(self):
        """Test GitHub SSH connection"""
        result = subprocess.run(['ssh', '-T', 'git@github.com'],
                              capture_output=True, text=True,
                              timeout=10)
        
        # GitHub returns exit code 1 on successful auth
        if "successfully authenticated" in result.stderr.lower():
            username = result.stderr.split("Hi ")[1].split("!")[0] if "Hi " in result.stderr else "Unknown"
            self.showMessage("GitHub Connection", 
                           f"✓ Connected as: {username}",
                           QSystemTrayIcon.Information, 5000)
        else:
            self.showMessage("GitHub Connection", 
                           f"✗ Connection failed\n{result.stderr[:200]}",
                           QSystemTrayIcon.Warning, 5000)
    
    def show_key_manager(self):
        """Show the key management dialog"""
        dialog = KeyManagerDialog(self)
        dialog.exec_()


class KeyManagerDialog(QDialog):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("Git Key Manager")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("SSH Key Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Status indicator
        self.status_label = QLabel()
        self.update_status_label()
        layout.addWidget(self.status_label)
        
        # Key list
        list_label = QLabel("Configured Keys:")
        layout.addWidget(list_label)
        
        self.key_list = QListWidget()
        self.refresh_key_list()
        layout.addWidget(self.key_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Key")
        add_btn.clicked.connect(self.add_key)
        button_layout.addWidget(add_btn)
        
        load_btn = QPushButton("Load Selected")
        load_btn.clicked.connect(self.load_selected_key)
        button_layout.addWidget(load_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_key)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        unload_btn = QPushButton("Unload All Keys")
        unload_btn.clicked.connect(self.unload_keys)
        action_layout.addWidget(unload_btn)
        
        test_btn = QPushButton("Test GitHub")
        test_btn.clicked.connect(self.manager.test_github)
        action_layout.addWidget(test_btn)
        
        layout.addLayout(action_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def update_status_label(self):
        result = subprocess.run(['ssh-add', '-l'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            key_count = len(result.stdout.strip().split('\n'))
            self.status_label.setText(f"🟢 Status: {key_count} key(s) loaded")
            self.status_label.setStyleSheet("color: green; font-weight: bold; padding: 10px;")
        else:
            self.status_label.setText("🔴 Status: No keys loaded")
            self.status_label.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
    
    def refresh_key_list(self):
        self.key_list.clear()
        for name, path in self.manager.keys.items():
            self.key_list.addItem(f"{name} - {path}")
    
    def add_key(self):
        name, ok = QInputDialog.getText(self, "Add Key", "Enter key name (e.g., 'Work', 'Personal'):")
        if not ok or not name:
            return
        
        path, _ = QFileDialog.getOpenFileName(self, "Select SSH Private Key",
                                              str(Path.home() / ".ssh"),
                                              "All Files (*)")
        if not path:
            return
        
        self.manager.keys[name] = path
        self.manager.save_keys()
        self.manager.rebuild_key_menu()
        self.refresh_key_list()
        
        QMessageBox.information(self, "Success", f"Key '{name}' added successfully!")
    
    def load_selected_key(self):
        current = self.key_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a key to load.")
            return
        
        name = current.text().split(" - ")[0]
        path = self.manager.keys[name]
        self.manager.load_key(name, path)
        self.update_status_label()
    
    def remove_key(self):
        current = self.key_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a key to remove.")
            return
        
        name = current.text().split(" - ")[0]
        reply = QMessageBox.question(self, "Confirm", 
                                    f"Remove key '{name}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            del self.manager.keys[name]
            self.manager.save_keys()
            self.manager.rebuild_key_menu()
            self.refresh_key_list()
    
    def unload_keys(self):
        self.manager.unload_all_keys()
        self.update_status_label()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    manager = GitKeyManager()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
