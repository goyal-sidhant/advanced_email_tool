"""
Advanced Email Tool - Main Entry Point
======================================
Desktop application for bulk personalized email sending.
Matches client-specific attachments using identifier patterns.

Author: Sidhant
Version: 1.0.0
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
            if not _check_outlook():
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


def _check_outlook() -> bool:
    """
    Check if Outlook is available.
    
    Returns:
        True if Outlook can be accessed
    """
    if sys.platform != 'win32':
        return False
    
    try:
        import win32com.client
        outlook = win32com.client.Dispatch("Outlook.Application")
        _ = outlook.GetNamespace("MAPI")
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
