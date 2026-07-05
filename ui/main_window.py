"""
Advanced Email Tool - Main Window
=================================
Main application window coordinating all tabs.
"""

from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QStatusBar, QMenuBar, QMenu, QAction, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCloseEvent, QKeySequence

from ui.tab_excel import TabExcel
from ui.tab_compose import TabCompose
from ui.tab_attachments import TabAttachments
from ui.tab_recipients import TabRecipients
from ui.tab_preview import TabPreview
from ui.tab_send import TabSend
from ui.components.dialogs import show_question, show_info, show_warning, show_error, show_file_dialog, show_save_dialog

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
        self._setup_shortcuts()
        self._connect_signals()
        self._setup_auto_save()

    def start_background_init(self) -> None:
        """
        Kick off deferred startup work — called by main.py right after
        show(), so the window paints before any slow work begins.
        """
        QTimer.singleShot(0, self.tab_send.start_outlook_init)
        QTimer.singleShot(0, self._check_restore_session)
    
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

        # Profile menu
        profile_menu = menubar.addMenu("&Profile")

        save_profile_action = QAction("💾 &Save Profile...", self)
        save_profile_action.setShortcut("Ctrl+Shift+S")
        save_profile_action.setToolTip("Save all settings to a shareable profile file")
        save_profile_action.triggered.connect(self._save_profile)
        profile_menu.addAction(save_profile_action)

        load_profile_action = QAction("📂 &Load Profile...", self)
        load_profile_action.setShortcut("Ctrl+Shift+O")
        load_profile_action.setToolTip("Load settings from a profile file")
        load_profile_action.triggered.connect(self._load_profile)
        profile_menu.addAction(load_profile_action)

        profile_menu.addSeparator()

        profile_info_action = QAction("ℹ️ Profile &Info", self)
        profile_info_action.triggered.connect(self._show_profile_info)
        profile_menu.addAction(profile_info_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Theme submenu
        theme_menu = view_menu.addMenu("🎨 Theme")
        
        self.theme_system_action = QAction("System (Auto)", self)
        self.theme_system_action.setCheckable(True)
        self.theme_system_action.triggered.connect(lambda: self._set_theme("system"))
        theme_menu.addAction(self.theme_system_action)
        
        self.theme_light_action = QAction("☀️ Light", self)
        self.theme_light_action.setCheckable(True)
        self.theme_light_action.triggered.connect(lambda: self._set_theme("light"))
        theme_menu.addAction(self.theme_light_action)
        
        self.theme_dark_action = QAction("🌙 Dark", self)
        self.theme_dark_action.setCheckable(True)
        self.theme_dark_action.triggered.connect(lambda: self._set_theme("dark"))
        theme_menu.addAction(self.theme_dark_action)
        
        # Set initial check state
        self._update_theme_menu_state()
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _set_theme(self, theme: str) -> None:
        """
        Set the application theme.
        
        Args:
            theme: Theme name (light/dark/system)
        """
        from utils.theme_manager import get_theme_manager
        
        theme_manager = get_theme_manager()
        if theme_manager:
            theme_manager.set_theme(theme)
            self._update_theme_menu_state()
            self.logger.info(f"Theme changed to: {theme}")
    
    def _update_theme_menu_state(self) -> None:
        """Update theme menu checkmarks based on current preference."""
        from utils.theme_manager import get_theme_manager
        
        theme_manager = get_theme_manager()
        if theme_manager:
            current = theme_manager.load_preference()
            self.theme_system_action.setChecked(current == "system")
            self.theme_light_action.setChecked(current == "light")
            self.theme_dark_action.setChecked(current == "dark")
    
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
    
    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Tab navigation: Ctrl+1 to Ctrl+6
        for i in range(6):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.tab_widget.setCurrentIndex(idx))
        
        # Next tab: Ctrl+Tab
        next_tab = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab.activated.connect(self._next_tab)
        
        # Previous tab: Ctrl+Shift+Tab
        prev_tab = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab.activated.connect(self._prev_tab)
        
        # Navigation in Preview tab: Left/Right arrows when in preview
        left_arrow = QShortcut(QKeySequence(Qt.Key_Left), self)
        left_arrow.activated.connect(self._preview_prev)
        
        right_arrow = QShortcut(QKeySequence(Qt.Key_Right), self)
        right_arrow.activated.connect(self._preview_next)
    
    def _next_tab(self) -> None:
        """Go to next tab."""
        current = self.tab_widget.currentIndex()
        next_idx = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_idx)
    
    def _prev_tab(self) -> None:
        """Go to previous tab."""
        current = self.tab_widget.currentIndex()
        prev_idx = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_idx)
    
    def _preview_prev(self) -> None:
        """Go to previous recipient in preview (only when Preview tab active)."""
        if self.tab_widget.currentIndex() == 4:  # Preview tab
            self.tab_preview._prev_recipient()
    
    def _preview_next(self) -> None:
        """Go to next recipient in preview (only when Preview tab active)."""
        if self.tab_widget.currentIndex() == 4:  # Preview tab
            self.tab_preview._next_recipient()
    
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

        # Tab navigation signals
        self.tab_excel.navigate_next.connect(self._next_tab)

        self.tab_compose.navigate_previous.connect(self._prev_tab)
        self.tab_compose.navigate_next.connect(self._next_tab)

        self.tab_attachments.navigate_previous.connect(self._prev_tab)
        self.tab_attachments.navigate_next.connect(self._next_tab)

        self.tab_recipients.navigate_previous.connect(self._prev_tab)
        self.tab_recipients.navigate_next.connect(self._next_tab)

        self.tab_preview.navigate_previous.connect(self._prev_tab)
        self.tab_preview.navigate_next.connect(self._next_tab)

        self.tab_send.navigate_previous.connect(self._prev_tab)
    
    def _setup_auto_save(self) -> None:
        """Set up auto-save functionality."""
        self.auto_save_manager.set_state_getter(self._get_session_state)
        # Don't snapshot widget state while a send is mutating it
        self.auto_save_manager.set_pause_check(self.tab_send.is_sending)
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
            identifier_column=mapping.get('identifier'),
            identifier_column2=mapping.get('identifier2'),
            identifier_logic=mapping.get('identifier_logic', 'OR')
        )
        
        # Update attachments tab with identifiers from both columns
        id_col1 = mapping.get('identifier')
        id_col2 = mapping.get('identifier2')
        
        if id_col1 or id_col2:
            data = self.tab_excel.get_data()
            identifiers = []
            for row in data:
                if id_col1:
                    id1 = str(row.get(id_col1, '')).strip()
                    if id1 and id1 not in identifiers:
                        identifiers.append(id1)
                if id_col2:
                    id2 = str(row.get(id_col2, '')).strip()
                    if id2 and id2 not in identifiers:
                        identifiers.append(id2)
            self.tab_attachments.set_identifiers(identifiers)
        
        # Update recipients tab, keeping any curated selection — only the
        # mapping changed, not the rows themselves
        columns = self.tab_excel.get_columns()
        data = self.tab_excel.get_data()
        self.tab_recipients.set_data(
            data, columns,
            mapping.get('to'),
            mapping.get('identifier'),
            preserve_selection=True
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
        # Set embedded images (for inline display)
        self.email_builder.set_embedded_images(
            self.tab_compose.get_embedded_images()
        )
    
    def _on_attachments_changed(self) -> None:
        """Handle attachment configuration changes."""
        self.email_builder.set_static_attachments(
            self.tab_attachments.get_static_attachments()
        )
        self.email_builder.set_attachment_matcher(
            self.tab_attachments.get_attachment_matcher()
        )
        # Apply attachment toggles
        self.email_builder.set_attachment_toggles(
            self.tab_attachments.is_static_enabled(),
            self.tab_attachments.is_dynamic_enabled()
        )
    
    def _on_selection_changed(self, count: int) -> None:
        """Handle recipient selection changes."""
        self.status_bar.showMessage(f"{count} recipients selected")
    
    def _on_tab_changed(self, index: int) -> None:
        """Handle tab changes."""
        # Status bar hints for each tab
        hints = {
            0: "Load Excel file and map columns to email fields",
            1: "Create email subject and body using {Variables}",
            2: "Configure static and dynamic attachments",
            3: "Select which recipients to send emails to",
            4: "Preview how emails will look before sending",
            5: "Send emails via Outlook"
        }
        self.status_bar.showMessage(hints.get(index, "Ready"))

        # Update preview when entering Preview tab
        if index == 4:  # Preview tab
            self._update_preview()

        # Update send tab when entering
        elif index == 5:  # Send tab
            self._update_send_tab()
    
    def _update_preview(self) -> None:
        """Update preview tab with current data."""
        data = self.tab_excel.get_data()
        columns = self.tab_excel.get_columns()
        selected_indices = self.tab_recipients.get_selected_indices()
        mapping = self.tab_excel.get_column_mapping()
        
        self.tab_preview.set_email_builder(self.email_builder)
        self.tab_preview.set_preview_data(
            data,
            selected_indices,
            mapping.get('to', ''),
            columns=columns,
            name_column=None,  # Will auto-detect
            identifier_column=mapping.get('identifier')
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
            'enable_static_attachments': self.tab_attachments.is_static_enabled(),
            'enable_dynamic_attachments': self.tab_attachments.is_dynamic_enabled(),
            'selected_recipients': self.tab_recipients.get_selected_indices(),
            'selected_account': self.tab_send.get_selected_account() or '',
        }
    
    def _restore_session_state(self, state: Dict[str, Any]) -> None:
        """Restore session from saved state."""
        # Restore Excel file; the load runs in a worker thread, so column
        # mapping and recipient selection are applied once the data arrives
        excel_path = state.get('excel_file_path')
        if excel_path:
            started = self.tab_excel.load_file_path(
                excel_path,
                on_loaded=lambda: self._restore_data_dependent_state(state)
            )
            if not started:
                show_warning(
                    self,
                    "Excel File Not Found",
                    f"The Excel file from your last session was not found:\n"
                    f"{excel_path}\n\n"
                    "Click Browse on the Excel tab to reselect it."
                )

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

        # Restore attachment toggles (default to True for backward compatibility)
        self.tab_attachments.set_toggles(
            state.get('enable_static_attachments', True),
            state.get('enable_dynamic_attachments', True)
        )

    def _restore_data_dependent_state(self, state: Dict[str, Any]) -> None:
        """Apply the parts of a session that need Excel data to be loaded."""
        mapping = state.get('column_mapping', {})
        if mapping:
            self.tab_excel.set_column_mapping(mapping)

        selected = state.get('selected_recipients', [])
        if selected:
            self.tab_recipients.set_selected_indices(selected)

        self.status_bar.showMessage("Session restored", 4000)
    
    def _check_restore_session(self) -> None:
        """Check for and offer to restore saved session."""
        if self.session_manager.has_saved_session():
            # Don't offer to restore an empty snapshot (e.g. auto-saved
            # right after a New Session)
            state = self.session_manager.load_session()
            if not SessionManager.has_meaningful_content(state):
                return

            info = self.session_manager.get_session_info()

            # Build detailed info
            excel_file = info.get('excel_file', 'Not set')
            if excel_file and excel_file != 'Not set':
                import os
                excel_file = os.path.basename(excel_file)
            
            template_name = info.get('template_name', 'None')
            recipients = info.get('selected_count', 0)
            saved_at = info.get('saved_at', 'unknown')
            
            # Calculate time ago
            try:
                from datetime import datetime
                saved_time = datetime.fromisoformat(saved_at)
                now = datetime.now()
                diff = now - saved_time
                if diff.days > 0:
                    time_ago = f"{diff.days} day(s) ago"
                elif diff.seconds > 3600:
                    time_ago = f"{diff.seconds // 3600} hour(s) ago"
                else:
                    time_ago = f"{diff.seconds // 60} minute(s) ago"
            except:
                time_ago = saved_at
            
            reply = show_question(
                self,
                "Restore Previous Session?",
                f"Found a saved session:\n\n"
                f"📁 File: {excel_file}\n"
                f"📝 Template: {template_name}\n"
                f"👥 Recipients: {recipients} selected\n"
                f"🕐 Last saved: {time_ago}\n\n"
                "Do you want to restore this session?"
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

            # Fresh builder first, so reset-triggered signals repopulate it
            # with empty state rather than the old one
            self.email_builder = EmailBuilder()

            self.tab_excel.reset()
            self.tab_compose.reset()
            self.tab_attachments.reset()
            self.tab_recipients.clear()

            self.tab_widget.setCurrentIndex(0)
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

    def _get_profile_state(self) -> Dict[str, Any]:
        """
        Get current state as a shareable profile.

        Returns:
            Dictionary with all profile settings
        """
        import os
        from datetime import datetime

        mapping = self.tab_excel.get_column_mapping()
        excel_path = self.tab_excel.get_file_path() or ''

        return {
            '_profile_metadata': {
                'version': config.APP_VERSION,
                'created_at': datetime.now().isoformat(),
                'description': 'Email Tool Profile',
            },
            'excel': {
                'file_path': excel_path,
                'file_name': os.path.basename(excel_path) if excel_path else '',
                'column_mapping': mapping,
            },
            'compose': {
                'subject_template': self.tab_compose.get_subject_template(),
                'body_template': self.tab_compose.get_body_template(),
                'universal_bcc': self.tab_compose.get_universal_bcc() or '',
            },
            'attachments': {
                'static_attachments': self.tab_attachments.get_static_attachments(),
                'attachment_folder': self.tab_attachments.get_attachment_folder() or '',
                'attachment_recursive': self.tab_attachments.is_recursive(),
                'enable_static': self.tab_attachments.is_static_enabled(),
                'enable_dynamic': self.tab_attachments.is_dynamic_enabled(),
            },
            'send': {
                'selected_account': self.tab_send.get_selected_account() or '',
            },
        }

    def _save_profile(self) -> None:
        """Save current settings to a profile file."""
        import json
        import os

        # Get save path
        save_path = show_save_dialog(
            self,
            "Save Profile",
            "JSON Files (*.json);;All Files (*.*)",
            default_name="email_profile.json"
        )

        if not save_path:
            return

        # Ensure .json extension
        if not save_path.lower().endswith('.json'):
            save_path += '.json'

        try:
            profile = self._get_profile_state()

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)

            show_info(
                self,
                "Profile Saved",
                f"Profile saved to:\n{os.path.basename(save_path)}\n\n"
                f"You can share this file with others or use it to quickly "
                f"restore your email settings."
            )
            self.status_bar.showMessage(f"Profile saved: {os.path.basename(save_path)}")
            self.logger.info(f"Profile saved to: {save_path}")

        except Exception as e:
            show_error(self, "Save Error", f"Could not save profile:\n{e}")
            self.logger.error(f"Profile save error: {e}")

    def _load_profile(self) -> None:
        """Load settings from a profile file."""
        import json
        import os

        # Get load path
        load_path = show_file_dialog(
            self,
            "Load Profile",
            "JSON Files (*.json);;All Files (*.*)"
        )

        if not load_path:
            return

        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)

            # Validate it's a profile
            if '_profile_metadata' not in profile and 'excel' not in profile:
                show_error(
                    self,
                    "Invalid Profile",
                    "This file does not appear to be a valid email profile."
                )
                return

            # Confirm loading
            reply = show_question(
                self,
                "Load Profile?",
                f"Load profile from:\n{os.path.basename(load_path)}\n\n"
                f"This will replace your current settings.\n"
                f"Continue?"
            )

            if not reply:
                return

            self._apply_profile(profile)

            show_info(self, "Profile Loaded", "Profile loaded successfully!")
            self.status_bar.showMessage(f"Profile loaded: {os.path.basename(load_path)}")
            self.logger.info(f"Profile loaded from: {load_path}")

        except json.JSONDecodeError as e:
            show_error(self, "Load Error", f"Invalid JSON file:\n{e}")
        except Exception as e:
            show_error(self, "Load Error", f"Could not load profile:\n{e}")
            self.logger.error(f"Profile load error: {e}")

    def _apply_profile(self, profile: Dict[str, Any]) -> None:
        """
        Apply a loaded profile to the application.

        Args:
            profile: Profile dictionary to apply
        """
        import os

        # Restore Excel file if exists
        excel_config = profile.get('excel', {})
        excel_path = excel_config.get('file_path', '')

        if excel_path and os.path.exists(excel_path):
            # The load runs in a worker thread — apply the column mapping
            # once the data is actually available
            mapping = excel_config.get('column_mapping', {})
            self.tab_excel.load_file_path(
                excel_path,
                on_loaded=(
                    (lambda: self.tab_excel.set_column_mapping(mapping))
                    if mapping else None
                )
            )
        elif excel_path:
            show_warning(
                self,
                "Excel File Not Found",
                f"The Excel file in the profile was not found:\n"
                f"{excel_path}\n\n"
                f"Please load the Excel file manually."
            )

        # Restore compose settings
        compose_config = profile.get('compose', {})
        self.tab_compose.set_subject_template(compose_config.get('subject_template', ''))
        self.tab_compose.set_body_template(compose_config.get('body_template', ''))
        self.tab_compose.set_universal_bcc(compose_config.get('universal_bcc', ''))

        # Restore attachments
        attach_config = profile.get('attachments', {})

        static = attach_config.get('static_attachments', [])
        # Filter to only existing files
        existing_static = [f for f in static if os.path.exists(f)]
        if existing_static:
            self.tab_attachments.set_static_attachments(existing_static)
        if len(existing_static) < len(static):
            show_warning(
                self,
                "Some Attachments Missing",
                f"{len(static) - len(existing_static)} static attachment(s) "
                f"were not found and will be skipped."
            )

        folder = attach_config.get('attachment_folder', '')
        if folder and os.path.exists(folder):
            self.tab_attachments.set_folder(
                folder,
                attach_config.get('attachment_recursive', False)
            )
        elif folder:
            show_warning(
                self,
                "Attachment Folder Not Found",
                f"The attachment folder was not found:\n{folder}"
            )

        # Restore attachment toggles (default to True for backward compatibility)
        self.tab_attachments.set_toggles(
            attach_config.get('enable_static', True),
            attach_config.get('enable_dynamic', True)
        )

    def _show_profile_info(self) -> None:
        """Show information about what a profile contains."""
        QMessageBox.information(
            self,
            "About Profiles",
            "<h3>What is a Profile?</h3>"
            "<p>A profile saves your email settings to a file that can be:</p>"
            "<ul>"
            "<li><b>Shared</b> - Send to colleagues to use the same settings</li>"
            "<li><b>Reused</b> - Load for recurring email campaigns</li>"
            "<li><b>Backed up</b> - Keep a copy of your configuration</li>"
            "</ul>"
            "<h4>What's saved in a profile:</h4>"
            "<ul>"
            "<li>Excel file path and column mappings</li>"
            "<li>Email subject and body templates</li>"
            "<li>Static and variable attachment settings</li>"
            "<li>BCC settings</li>"
            "</ul>"
            "<p><i>Note: The actual Excel data and attachments are not stored "
            "in the profile - only the paths and settings.</i></p>"
        )
