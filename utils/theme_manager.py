"""
Advanced Email Tool - Theme Manager
===================================
Handles theme switching between light and dark modes.
Supports system theme detection on Windows.
"""

import os
import json
from typing import Optional
from pathlib import Path

import config


class ThemeManager:
    """
    Manages application themes (light/dark mode).
    
    Features:
    - Load/save theme preference
    - Detect Windows system theme
    - Apply stylesheets
    """
    
    def __init__(self, app):
        """
        Initialize the theme manager.
        
        Args:
            app: QApplication instance
        """
        self.app = app
        self.app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self._current_theme = config.THEME_LIGHT
        
        # Stylesheet paths
        self._light_stylesheet_path = self.app_dir / "resources" / "style.qss"
        self._dark_stylesheet_path = self.app_dir / "resources" / "style_dark.qss"
    
    def load_preference(self) -> str:
        """
        Load saved theme preference.
        
        Returns:
            Theme name (light/dark/system)
        """
        try:
            if config.PREFERENCES_FILE.exists():
                with open(config.PREFERENCES_FILE, 'r') as f:
                    prefs = json.load(f)
                    return prefs.get('theme', config.DEFAULT_THEME)
        except Exception:
            pass
        return config.DEFAULT_THEME
    
    def save_preference(self, theme: str) -> None:
        """
        Save theme preference.
        
        Args:
            theme: Theme name to save
        """
        try:
            prefs = {}
            if config.PREFERENCES_FILE.exists():
                with open(config.PREFERENCES_FILE, 'r') as f:
                    prefs = json.load(f)
            
            prefs['theme'] = theme
            
            with open(config.PREFERENCES_FILE, 'w') as f:
                json.dump(prefs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save theme preference: {e}")
    
    def detect_system_theme(self) -> str:
        """
        Detect Windows system theme (dark or light).
        
        Returns:
            'dark' or 'light'
        """
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            # AppsUseLightTheme: 0 = dark, 1 = light
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return config.THEME_LIGHT if value == 1 else config.THEME_DARK
        except Exception:
            # Default to light if can't detect
            return config.THEME_LIGHT
    
    def get_effective_theme(self, theme: str) -> str:
        """
        Get the actual theme to apply (resolves 'system' to light/dark).
        
        Args:
            theme: Requested theme (light/dark/system)
            
        Returns:
            'light' or 'dark'
        """
        if theme == config.THEME_SYSTEM:
            return self.detect_system_theme()
        return theme
    
    def apply_theme(self, theme: str) -> None:
        """
        Apply a theme to the application.
        
        Args:
            theme: Theme name (light/dark/system)
        """
        effective_theme = self.get_effective_theme(theme)
        self._current_theme = effective_theme
        
        # Select stylesheet path
        if effective_theme == config.THEME_DARK:
            stylesheet_path = self._dark_stylesheet_path
        else:
            stylesheet_path = self._light_stylesheet_path
        
        # Load and apply stylesheet
        if stylesheet_path.exists():
            try:
                with open(stylesheet_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                self.app.setStyleSheet(stylesheet)
            except Exception as e:
                print(f"Warning: Could not load stylesheet: {e}")
        else:
            print(f"Warning: Stylesheet not found: {stylesheet_path}")
    
    def initialize(self) -> str:
        """
        Initialize theme from saved preference.
        
        Returns:
            Applied theme name
        """
        theme = self.load_preference()
        self.apply_theme(theme)
        return theme
    
    def set_theme(self, theme: str, save: bool = True) -> None:
        """
        Set and apply a new theme.
        
        Args:
            theme: Theme name (light/dark/system)
            save: Whether to save preference
        """
        self.apply_theme(theme)
        if save:
            self.save_preference(theme)
    
    def get_current_theme(self) -> str:
        """
        Get the current effective theme.
        
        Returns:
            'light' or 'dark'
        """
        return self._current_theme
    
    def is_dark_mode(self) -> bool:
        """
        Check if current theme is dark.
        
        Returns:
            True if dark mode
        """
        return self._current_theme == config.THEME_DARK


# Global theme manager instance (set in main.py)
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> Optional[ThemeManager]:
    """Get the global theme manager instance."""
    return _theme_manager


def set_theme_manager(manager: ThemeManager) -> None:
    """Set the global theme manager instance."""
    global _theme_manager
    _theme_manager = manager
