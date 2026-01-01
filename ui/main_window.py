"""
Advanced Email Tool - Main Window
=================================
Main application window coordinating all tabs.
"""

from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QStatusBar, QMenuBar, QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCloseEvent

from ui.tab_excel import TabExcel
from ui.tab_compose import TabCompose
from ui.tab_attachments import TabAttachments
from ui.tab_recipients import TabRecipients
from ui.tab_preview import TabPreview
from ui.tab_send import TabSend
from ui.components.dialogs import show_question, show_info, show_warning

from core.email_builder import EmailBuilder
from data.session_manager import SessionManager, AutoSaveManager
from utils import get_logger

import config


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Coordinates:
    - Tab navigation (Excel → Compose → Attachments → Recipients → Preview → Send)
    - Data flow between tabs
    - Session auto-save and restore
    - Menu bar actions
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.logger = get_logger()
        self.email_builder = EmailBuilder()
        self.session_manager = SessionManager()
        self.auto_save_manager = AutoSaveManager(self.session_manager)
        
        self._setup_window()
        self._setup_menu()
        self._setup_tabs()
        self._setup_status_bar()
        self._connect_signals()
        self._setup_auto_save()
        
        # Check for saved session
        self._check_restore_session()
    
    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.resize(config.WINDOW_DEFAULT_WIDTH, config.WINDOW_DEFAULT_HEIGHT)
    
    def _setup_menu(self) -> None:
        """Set up menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Session", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_session)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save Session", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_tabs(self) -> None:
        """Set up tab widget and all tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.tab_excel = TabExcel()
        self.tab_compose = TabCompose()
        self.tab_attachments = TabAttachments()
        self.tab_recipients = TabRecipients()
        self.tab_preview = TabPreview()
        self.tab_send = TabSend()
        
        # Add tabs with icons/numbers
        self.tab_widget.addTab(self.tab_excel, "1. Excel")
        self.tab_widget.addTab(self.tab_compose, "2. Compose")
        self.tab_widget.addTab(self.tab_attachments, "3. Attachments")
        self.tab_widget.addTab(self.tab_recipients, "4. Recipients")
        self.tab_widget.addTab(self.tab_preview, "5. Preview")
        self.tab_widget.addTab(self.tab_send, "6. Send")
        
        layout.addWidget(self.tab_widget)
    
    def _setup_status_bar(self) -> None:
        """Set up status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self) -> None:
        """Connect signals between tabs."""
        # Excel tab signals
        self.tab_excel.data_loaded.connect(self._on_data_loaded)
        self.tab_excel.mapping_changed.connect(self._on_mapping_changed)
        
        # Compose tab signals
        self.tab_compose.template_changed.connect(self._on_template_changed)
        
        # Attachments tab signals
        self.tab_attachments.attachments_changed.connect(self._on_attachments_changed)
        
        # Recipients tab signals
        self.tab_recipients.selection_changed.connect(self._on_selection_changed)
        
        # Tab change
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _setup_auto_save(self) -> None:
        """Set up auto-save functionality."""
        self.auto_save_manager.set_state_getter(self._get_session_state)
        self.auto_save_manager.start(config.AUTO_SAVE_INTERVAL)
    
    def _on_data_loaded(self, columns: list, data: list) -> None:
        """Handle Excel data loaded."""
        self.logger.info(f"Data loaded: {len(columns)} columns, {len(data)} rows")
        
        # Update compose tab with available columns
        self.tab_compose.set_available_columns(columns)
        
        # Update recipients tab
        mapping = self.tab_excel.get_column_mapping()
        self.tab_recipients.set_data(
            data, columns,
            mapping.get('to'),
            mapping.get('identifier')
        )
        
        # Update status
        self.status_bar.showMessage(f"Loaded {len(data)} rows from Excel")
    
    def _on_mapping_changed(self, mapping: dict) -> None:
        """Handle column mapping changes."""
        # Update email builder
        self.email_builder.set_column_mapping(
            email_column=mapping.get('to', ''),
            cc_column=mapping.get('cc'),
            bcc_column=mapping.get('bcc'),
            identifier_column=mapping.get('identifier')
        )
        
        # Update attachments tab with identifiers
        if mapping.get('identifier'):
            data = self.tab_excel.get_data()
            identifiers = [row.get(mapping['identifier'], '') for row in data]
            self.tab_attachments.set_identifiers(identifiers)
        
        # Update recipients tab
        columns = self.tab_excel.get_columns()
        data = self.tab_excel.get_data()
        self.tab_recipients.set_data(
            data, columns,
            mapping.get('to'),
            mapping.get('identifier')
        )
    
    def _on_template_changed(self) -> None:
        """Handle template changes."""
        self.email_builder.set_templates(
            self.tab_compose.get_subject_template(),
            self.tab_compose.get_body_template()
        )
        self.email_builder.set_universal_bcc(
            self.tab_compose.get_universal_bcc()
        )
    
    def _on_attachments_changed(self) -> None:
        """Handle attachment configuration changes."""
        self.email_builder.set_static_attachments(
            self.tab_attachments.get_static_attachments()
        )
        self.email_builder.set_attachment_matcher(
            self.tab_attachments.get_attachment_matcher()
        )
    
    def _on_selection_changed(self, count: int) -> None:
        """Handle recipient selection changes."""
        self.status_bar.showMessage(f"{count} recipients selected")
    
    def _on_tab_changed(self, index: int) -> None:
        """Handle tab changes."""
        tab_name = self.tab_widget.tabText(index)
        
        # Update preview when entering Preview tab
        if index == 4:  # Preview tab
            self._update_preview()
        
        # Update send tab when entering
        elif index == 5:  # Send tab
            self._update_send_tab()
    
    def _update_preview(self) -> None:
        """Update preview tab with current data."""
        data = self.tab_excel.get_data()
        selected_indices = self.tab_recipients.get_selected_indices()
        mapping = self.tab_excel.get_column_mapping()
        
        self.tab_preview.set_email_builder(self.email_builder)
        self.tab_preview.set_preview_data(
            data,
            selected_indices,
            mapping.get('to', '')
        )
    
    def _update_send_tab(self) -> None:
        """Update send tab with emails to send."""
        data = self.tab_excel.get_data()
        selected_indices = self.tab_recipients.get_selected_indices()
        
        # Build emails
        emails = []
        for idx in selected_indices:
            if idx < len(data):
                email = self.email_builder.build_email(data[idx], idx)
                emails.append(email)
        
        self.tab_send.set_email_builder(self.email_builder)
        self.tab_send.set_emails(emails)
    
    def _get_session_state(self) -> Dict[str, Any]:
        """Get current session state for saving."""
        mapping = self.tab_excel.get_column_mapping()
        
        return {
            'excel_file_path': self.tab_excel.get_file_path() or '',
            'column_mapping': mapping,
            'subject_template': self.tab_compose.get_subject_template(),
            'body_template': self.tab_compose.get_body_template(),
            'universal_bcc': self.tab_compose.get_universal_bcc() or '',
            'static_attachments': self.tab_attachments.get_static_attachments(),
            'attachment_folder': self.tab_attachments.get_attachment_folder() or '',
            'attachment_recursive': self.tab_attachments.is_recursive(),
            'selected_recipients': self.tab_recipients.get_selected_indices(),
            'selected_account': self.tab_send.get_selected_account() or '',
        }
    
    def _restore_session_state(self, state: Dict[str, Any]) -> None:
        """Restore session from saved state."""
        # Restore Excel file
        excel_path = state.get('excel_file_path')
        if excel_path:
            self.tab_excel.load_file_path(excel_path)
        
        # Restore column mapping
        mapping = state.get('column_mapping', {})
        if mapping:
            self.tab_excel.set_column_mapping(mapping)
        
        # Restore compose
        self.tab_compose.set_subject_template(state.get('subject_template', ''))
        self.tab_compose.set_body_template(state.get('body_template', ''))
        self.tab_compose.set_universal_bcc(state.get('universal_bcc', ''))
        
        # Restore attachments
        static = state.get('static_attachments', [])
        if static:
            self.tab_attachments.set_static_attachments(static)
        
        folder = state.get('attachment_folder')
        if folder:
            self.tab_attachments.set_folder(
                folder,
                state.get('attachment_recursive', False)
            )
        
        # Restore recipient selection
        selected = state.get('selected_recipients', [])
        if selected:
            self.tab_recipients.set_selected_indices(selected)
    
    def _check_restore_session(self) -> None:
        """Check for and offer to restore saved session."""
        if self.session_manager.has_saved_session():
            info = self.session_manager.get_session_info()
            
            reply = show_question(
                self,
                "Restore Session?",
                f"Found saved session from {info.get('saved_at', 'unknown')}.\n\n"
                f"Excel: {info.get('excel_file', 'Not set')}\n\n"
                "Do you want to restore it?"
            )
            
            if reply:
                state = self.session_manager.load_session()
                if state:
                    self._restore_session_state(state)
                    self.status_bar.showMessage("Session restored")
                    self.logger.info("Session restored")
    
    def _new_session(self) -> None:
        """Start a new session."""
        reply = show_question(
            self,
            "New Session?",
            "This will clear all current data. Continue?"
        )
        
        if reply:
            self.session_manager.clear_session()
            # Reset all tabs (would need reset methods)
            self.status_bar.showMessage("New session started")
    
    def _save_session(self) -> None:
        """Manually save session."""
        state = self._get_session_state()
        if self.session_manager.save_session(state):
            self.status_bar.showMessage("Session saved")
            show_info(self, "Saved", "Session saved successfully.")
        else:
            show_warning(self, "Warning", "Could not save session.")
    
    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"About {config.APP_NAME}",
            f"<h2>{config.APP_NAME}</h2>"
            f"<p>Version {config.APP_VERSION}</p>"
            f"<p>Bulk personalized email sending tool with "
            f"attachment matching.</p>"
            f"<p>Created by {config.APP_AUTHOR}</p>"
        )
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        # Check if sending
        if self.tab_send.is_sending():
            reply = QMessageBox.question(
                self,
                "Sending in Progress",
                "Emails are still being sent. Are you sure you want to exit?\n\n"
                "Progress will be saved and can be resumed.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                event.ignore()
                return
        
        # Save session
        self.auto_save_manager.save_now()
        self.auto_save_manager.stop()
        
        self.logger.info("Application closing")
        event.accept()
