"""
Advanced Email Tool - Main Entry Point
======================================
Desktop application for bulk personalized email sending.
Matches client-specific attachments using identifier patterns.

Author: Sidhant
Version: 1.4.0
"""

import sys
import os

# Ensure the application directory is in path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


def main():
    """Main application entry point."""
    # Import PyQt5 first to set up the application
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt
    
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application instance
    app = QApplication(sys.argv)
    
    try:
        # Initialize configuration and directories
        import config
        config.ensure_directories()
        
        # Set up logging
        from utils import setup_logger
        logger = setup_logger()
        logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
        
        # Initialize theme manager
        from utils.theme_manager import ThemeManager, set_theme_manager
        theme_manager = ThemeManager(app)
        set_theme_manager(theme_manager)
        theme_manager.initialize()
        
        # Check for required dependencies
        if not _check_dependencies():
            QMessageBox.critical(
                None,
                "Missing Dependencies",
                "Required dependencies are not installed.\n\n"
                "Please run: pip install -r requirements.txt"
            )
            return 1
        
        # Check for Outlook availability (Windows only)
        if sys.platform == 'win32':
            outlook_status = _check_outlook()
            if outlook_status == "new_outlook":
                QMessageBox.warning(
                    None,
                    "New Outlook Detected",
                    "⚠️ New Outlook detected!\n\n"
                    "This app requires Outlook Classic, which supports automation.\n"
                    "New Outlook is a web-based app and cannot be automated.\n\n"
                    "To switch back to Classic Outlook:\n"
                    "1. Open Outlook\n"
                    "2. Go to Settings (gear icon)\n"
                    "3. Toggle OFF 'New Outlook'\n\n"
                    "The app will run, but email sending will not work until you switch."
                )
            elif outlook_status == "not_found":
                QMessageBox.warning(
                    None,
                    "Outlook Not Available",
                    "Microsoft Outlook is not installed or not accessible.\n\n"
                    "The application will run, but email sending will not work."
                )
        
        # Import and create main window
        from ui.main_window import MainWindow
        
        window = MainWindow()
        window.show()
        
        logger.info("Application startup complete")
        
        return app.exec_()
        
    except Exception as e:
        # Log and show error
        error_msg = f"Application failed to start: {e}"
        print(error_msg)
        
        try:
            from utils import get_logger
            get_logger().critical(error_msg, exc_info=True)
        except:
            pass
        
        QMessageBox.critical(
            None,
            "Startup Error",
            f"The application failed to start.\n\n{error_msg}"
        )
        return 1


def _check_dependencies() -> bool:
    """
    Check if required dependencies are installed.
    
    Returns:
        True if all dependencies are available
    """
    required = [
        ('PyQt5', 'PyQt5.QtWidgets'),
        ('openpyxl', 'openpyxl'),
    ]
    
    # pywin32 only required on Windows
    if sys.platform == 'win32':
        required.append(('pywin32', 'win32com.client'))
    
    for name, module in required:
        try:
            __import__(module)
        except ImportError:
            print(f"Missing dependency: {name}")
            return False
    
    return True


def _check_outlook() -> str:
    """
    Check if Outlook is available and which version.
    
    Returns:
        "ok" - Outlook Classic available
        "new_outlook" - New Outlook detected (not supported)
        "not_found" - Outlook not installed
    """
    if sys.platform != 'win32':
        return "not_found"
    
    # First check if New Outlook process is running
    try:
        import subprocess
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq olk.exe'],
            capture_output=True, text=True, timeout=5
        )
        if 'olk.exe' in result.stdout:
            return "new_outlook"
    except Exception:
        pass
    
    # Try to connect to Outlook Classic
    try:
        import win32com.client
        outlook = win32com.client.Dispatch("Outlook.Application")
        _ = outlook.GetNamespace("MAPI")
        return "ok"
    except Exception:
        # Check if New Outlook is installed but not running
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Office\16.0\Outlook\Preferences"
            )
            value, _ = winreg.QueryValueEx(key, "UseNewOutlook")
            winreg.CloseKey(key)
            if value == 1:
                return "new_outlook"
        except Exception:
            pass
        
        return "not_found"


if __name__ == "__main__":
    sys.exit(main())
