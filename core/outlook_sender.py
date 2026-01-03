"""
Advanced Email Tool - Outlook Sender
====================================
Handles sending emails through Microsoft Outlook using COM automation.
Supports multiple accounts, offline detection, and preview display.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from utils import get_logger
from core.email_builder import Email

import config


@dataclass
class OutlookAccount:
    """Represents an Outlook email account."""
    name: str
    email: str
    account_type: str
    index: int  # 1-based index for COM


class OutlookSender:
    """
    Sends emails through Microsoft Outlook.
    
    Uses COM automation to interact with Outlook.
    Supports account selection, offline detection, and send/display modes.
    """
    
    def __init__(self):
        """Initialize the Outlook sender."""
        self.logger = get_logger()
        self.outlook = None
        self.namespace = None
        self.accounts: List[OutlookAccount] = []
        self.selected_account: Optional[OutlookAccount] = None
        self._initialized = False
    
    def initialize(self) -> Tuple[bool, str]:
        """
        Initialize connection to Outlook.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            import win32com.client
            
            self.logger.info("Initializing Outlook connection...")
            
            # Use EnsureDispatch for more stable COM connection
            # This generates Python wrappers for better reliability
            try:
                self.outlook = win32com.client.gencache.EnsureDispatch("Outlook.Application")
            except Exception:
                # Fallback to regular Dispatch if gencache fails
                self.outlook = win32com.client.Dispatch("Outlook.Application")
            
            self.namespace = self.outlook.GetNamespace("MAPI")
            
            # Load accounts
            self._load_accounts()
            
            self._initialized = True
            self.logger.info(f"Outlook initialized with {len(self.accounts)} account(s)")
            
            return True, ""
            
        except Exception as e:
            error_msg = str(e)
            if "not registered" in error_msg.lower():
                return False, "Microsoft Outlook is not installed"
            elif "cannot start" in error_msg.lower():
                return False, "Cannot start Outlook. Please ensure Outlook is properly configured."
            else:
                self.logger.error(f"Outlook initialization failed: {e}", exc_info=True)
                return False, f"Failed to connect to Outlook: {e}"
    
    def _get_fresh_outlook(self):
        """
        Get a fresh Outlook Application object.
        
        This helps avoid stale COM connection issues.
        """
        import win32com.client
        try:
            # Try EnsureDispatch first
            return win32com.client.gencache.EnsureDispatch("Outlook.Application")
        except Exception:
            # Fallback to Dispatch
            return win32com.client.Dispatch("Outlook.Application")
    
    def _load_accounts(self) -> None:
        """Load available email accounts from Outlook."""
        self.accounts = []
        
        try:
            accounts = self.namespace.Accounts
            for i in range(1, accounts.Count + 1):
                account = accounts.Item(i)
                self.accounts.append(OutlookAccount(
                    name=account.DisplayName,
                    email=account.SmtpAddress,
                    account_type=account.AccountType,
                    index=i
                ))
            
            # Set default to first account if available
            if self.accounts:
                self.selected_account = self.accounts[0]
                
        except Exception as e:
            self.logger.error(f"Error loading accounts: {e}")
    
    def get_accounts(self) -> List[OutlookAccount]:
        """
        Get list of available Outlook accounts.
        
        Returns:
            List of OutlookAccount objects
        """
        return self.accounts.copy()
    
    def select_account(self, email: str) -> bool:
        """
        Select an account by email address.
        
        Args:
            email: Email address of the account to select
            
        Returns:
            True if account found and selected
        """
        for account in self.accounts:
            if account.email.lower() == email.lower():
                self.selected_account = account
                self.logger.info(f"Selected account: {email}")
                return True
        
        self.logger.warning(f"Account not found: {email}")
        return False
    
    def select_account_by_index(self, index: int) -> bool:
        """
        Select an account by list index.

        Args:
            index: 0-based index in accounts list

        Returns:
            True if valid index
        """
        if 0 <= index < len(self.accounts):
            self.selected_account = self.accounts[index]
            self.logger.info(f"Selected account: {self.selected_account.email}")
            return True
        return False

    def get_selected_account(self) -> Optional[OutlookAccount]:
        """
        Get the currently selected account.

        Returns:
            The selected OutlookAccount, or None if no account selected
        """
        return self.selected_account
    
    def is_online(self) -> Tuple[bool, str]:
        """
        Check if Outlook is online (connected).
        
        Returns:
            Tuple of (is_online, status_message)
        """
        if not self._initialized:
            return False, "Outlook not initialized"
        
        try:
            # Check offline status
            if self.namespace.Offline:
                return False, "Outlook is in offline mode"
            return True, "Outlook is online"
            
        except Exception as e:
            self.logger.error(f"Error checking online status: {e}")
            return False, f"Error checking status: {e}"
    
    def send_email(
        self, 
        email: Email,
        display_only: bool = False
    ) -> Tuple[bool, str]:
        """
        Send or display an email.
        
        Args:
            email: Email object to send
            display_only: If True, display in Outlook instead of sending
            
        Returns:
            Tuple of (success, message)
        """
        if not self._initialized:
            return False, "Outlook not initialized"
        
        if not email.to:
            return False, "No recipients specified"
        
        try:
            # Get fresh Outlook connection to avoid stale COM issues
            outlook = self._get_fresh_outlook()
            namespace = outlook.GetNamespace("MAPI")
            
            # Create mail item
            mail = outlook.CreateItem(0)  # 0 = olMailItem
            
            # Set sender account if specified
            if self.selected_account:
                try:
                    accounts = namespace.Accounts
                    mail._oleobj_.Invoke(
                        *(64209, 0, 8, 0, 
                          accounts.Item(self.selected_account.index))
                    )
                except Exception as e:
                    self.logger.warning(f"Could not set sender account: {e}")
            
            # Set recipients
            mail.To = "; ".join(email.to)
            
            if email.cc:
                mail.CC = "; ".join(email.cc)
            
            if email.bcc:
                mail.BCC = "; ".join(email.bcc)
            
            # Set subject
            mail.Subject = email.subject
            
            # Handle embedded images (convert base64 to CID attachments)
            body_html = email.body_html
            if email.embedded_images:
                body_html = self._process_embedded_images(mail, email.embedded_images, body_html)
            
            # Set body
            mail.HTMLBody = body_html
            
            # Add regular attachments
            for attachment_path in email.attachments:
                try:
                    mail.Attachments.Add(attachment_path)
                except Exception as e:
                    self.logger.warning(f"Could not attach file: {attachment_path} - {e}")
            
            # Send or display
            if display_only:
                mail.Display()
                return True, "Email displayed in Outlook"
            else:
                mail.Send()
                return True, "Email sent successfully"
                
        except Exception as e:
            self.logger.error(f"Error sending email: {e}", exc_info=True)
            return False, f"Error: {e}"
    
    def _process_embedded_images(
        self, 
        mail, 
        images: List[Dict[str, Any]], 
        body_html: str
    ) -> str:
        """
        Process embedded images - save to temp files and add as CID attachments.
        
        Args:
            mail: Outlook mail item
            images: List of image dicts with 'data', 'mime_type', 'cid', 'original_tag'
            body_html: HTML body with base64 images
            
        Returns:
            HTML body with CID references
        """
        import tempfile
        import base64
        import os
        
        # PR_ATTACH_CONTENT_ID property tag
        PR_ATTACH_CONTENT_ID = "http://schemas.microsoft.com/mapi/proptag/0x3712001F"
        
        for img in images:
            try:
                # Determine file extension
                mime_type = img.get('mime_type', 'image/png')
                ext_map = {
                    'image/png': '.png',
                    'image/jpeg': '.jpg',
                    'image/gif': '.gif',
                    'image/bmp': '.bmp',
                }
                ext = ext_map.get(mime_type, '.png')
                
                # Save base64 data to temp file
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                    temp_path = f.name
                    image_data = base64.b64decode(img['data'])
                    f.write(image_data)
                
                # Add as attachment
                attachment = mail.Attachments.Add(temp_path)
                
                # Set Content-ID for inline display
                cid = img['cid']
                attachment.PropertyAccessor.SetProperty(PR_ATTACH_CONTENT_ID, cid)
                
                # Replace original tag with CID reference in HTML
                original_tag = img.get('original_tag', '')
                if original_tag:
                    cid_tag = f'<img src="cid:{cid}" />'
                    body_html = body_html.replace(original_tag, cid_tag)
                
                # Clean up temp file (Outlook has already read it)
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as e:
                self.logger.warning(f"Could not embed image: {e}")
        
        return body_html
    
    def send_emails_batch(
        self,
        emails: List[Email],
        display_only: bool = False,
        interval: float = None,
        progress_callback=None,
        cancel_check=None
    ) -> Dict[str, Any]:
        """
        Send multiple emails with progress tracking.
        
        Args:
            emails: List of Email objects
            display_only: If True, display instead of send
            interval: Seconds between emails (default from config)
            progress_callback: Function(current, total, email, status, message)
            cancel_check: Function returning True if cancelled
            
        Returns:
            Dictionary with results summary
        """
        if interval is None:
            interval = config.SEND_INTERVAL
        
        results = {
            'total': len(emails),
            'sent': 0,
            'failed': 0,
            'cancelled': False,
            'details': []
        }
        
        for idx, email in enumerate(emails):
            # Check for cancellation
            if cancel_check and cancel_check():
                results['cancelled'] = True
                self.logger.info("Batch send cancelled by user")
                break
            
            # Send email
            success, message = self.send_email(email, display_only)
            
            detail = {
                'index': idx,
                'to': email.to,
                'subject': email.subject,
                'success': success,
                'message': message
            }
            results['details'].append(detail)
            
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            # Progress callback
            if progress_callback:
                progress_callback(idx + 1, len(emails), email, success, message)
            
            # Delay between emails (except for last one)
            if idx < len(emails) - 1:
                time.sleep(interval)
        
        self.logger.info(
            f"Batch complete: {results['sent']} sent, "
            f"{results['failed']} failed, "
            f"cancelled={results['cancelled']}"
        )
        
        return results
    
    def create_preview_html(self, email: Email) -> str:
        """
        Create HTML preview of an email.
        
        Args:
            email: Email object
            
        Returns:
            HTML string for preview display
        """
        from utils.html_converter import escape_html
        
        # Build attachment list
        attachment_list = ""
        for path in email.attachments:
            import os
            filename = os.path.basename(path)
            attachment_list += f"<li>{escape_html(filename)}</li>"
        
        if not attachment_list:
            attachment_list = "<li><em>No attachments</em></li>"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .email-container {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            background: #f0f0f0;
            padding: 15px;
            border-bottom: 1px solid #ddd;
        }}
        .header-row {{
            margin: 5px 0;
        }}
        .header-label {{
            font-weight: bold;
            display: inline-block;
            width: 80px;
        }}
        .body {{
            padding: 20px;
        }}
        .attachments {{
            background: #f9f9f9;
            padding: 15px;
            border-top: 1px solid #ddd;
        }}
        .attachments h4 {{
            margin-top: 0;
        }}
        .attachments ul {{
            margin: 0;
            padding-left: 20px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-row">
                <span class="header-label">To:</span>
                {escape_html("; ".join(email.to))}
            </div>
            {"<div class='header-row'><span class='header-label'>CC:</span>" + escape_html("; ".join(email.cc)) + "</div>" if email.cc else ""}
            {"<div class='header-row'><span class='header-label'>BCC:</span>" + escape_html("; ".join(email.bcc)) + "</div>" if email.bcc else ""}
            <div class="header-row">
                <span class="header-label">Subject:</span>
                {escape_html(email.subject)}
            </div>
        </div>
        <div class="body">
            {email.body_html}
        </div>
        <div class="attachments">
            <h4>Attachments ({len(email.attachments)})</h4>
            <ul>{attachment_list}</ul>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def close(self) -> None:
        """Release Outlook COM objects."""
        self.outlook = None
        self.namespace = None
        self.accounts = []
        self.selected_account = None
        self._initialized = False
        self.logger.info("Outlook connection closed")
