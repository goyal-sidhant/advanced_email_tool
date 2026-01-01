"""
Advanced Email Tool - Email Builder
===================================
Constructs email objects ready for sending via Outlook.
Combines template, data, and attachments into complete emails.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from utils import get_logger
from core.template_engine import TemplateEngine


@dataclass
class Email:
    """
    Represents a complete email ready for sending.
    
    Attributes:
        to: List of recipient email addresses
        cc: List of CC email addresses
        bcc: List of BCC email addresses
        subject: Email subject line
        body_html: HTML formatted body
        body_text: Plain text body (fallback)
        attachments: List of file paths to attach
        row_data: Original data row (for reference)
        row_index: Index in original data (for tracking)
    """
    to: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    subject: str = ""
    body_html: str = ""
    body_text: str = ""
    attachments: List[str] = field(default_factory=list)
    row_data: Dict[str, Any] = field(default_factory=dict)
    row_index: int = -1
    
    def get_total_recipients(self) -> int:
        """Get total number of recipients (TO + CC + BCC)."""
        return len(self.to) + len(self.cc) + len(self.bcc)
    
    def get_attachment_count(self) -> int:
        """Get number of attachments."""
        return len(self.attachments)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'to': self.to,
            'cc': self.cc,
            'bcc': self.bcc,
            'subject': self.subject,
            'body_html': self.body_html,
            'attachments': self.attachments,
            'row_index': self.row_index,
        }


class EmailBuilder:
    """
    Builds Email objects from templates and data.
    
    Combines:
    - Subject template
    - Body template
    - Row data from Excel
    - Static attachments
    - Variable attachments (matched by identifier)
    """
    
    def __init__(self):
        """Initialize the email builder."""
        self.logger = get_logger()
        self.template_engine = TemplateEngine()
        
        # Configuration
        self.subject_template: str = ""
        self.body_template: str = ""
        self.email_column: str = ""
        self.cc_column: Optional[str] = None
        self.bcc_column: Optional[str] = None
        self.identifier_column: Optional[str] = None
        self.universal_bcc: Optional[str] = None
        
        # Attachments
        self.static_attachments: List[str] = []
        self.attachment_matcher = None  # Will be set externally
    
    def set_templates(self, subject: str, body: str) -> None:
        """
        Set email templates.
        
        Args:
            subject: Subject line template with {variables}
            body: Body HTML template with {variables}
        """
        self.subject_template = subject
        self.body_template = body
        self.logger.debug("Templates set")
    
    def set_column_mapping(
        self,
        email_column: str,
        cc_column: Optional[str] = None,
        bcc_column: Optional[str] = None,
        identifier_column: Optional[str] = None
    ) -> None:
        """
        Set column mapping for email fields.
        
        Args:
            email_column: Column name containing recipient emails
            cc_column: Column name for CC (optional)
            bcc_column: Column name for BCC (optional)
            identifier_column: Column name for file matching identifier
        """
        self.email_column = email_column
        self.cc_column = cc_column
        self.bcc_column = bcc_column
        self.identifier_column = identifier_column
    
    def set_universal_bcc(self, bcc_address: Optional[str]) -> None:
        """
        Set a BCC address to add to all emails.
        
        Args:
            bcc_address: Email address to BCC on all emails
        """
        self.universal_bcc = bcc_address
    
    def set_static_attachments(self, file_paths: List[str]) -> None:
        """
        Set static attachments (sent to all recipients).
        
        Args:
            file_paths: List of file paths
        """
        self.static_attachments = file_paths.copy()
    
    def set_attachment_matcher(self, matcher) -> None:
        """
        Set the attachment matcher for variable attachments.
        
        Args:
            matcher: AttachmentMatcher instance
        """
        self.attachment_matcher = matcher
    
    def build_email(
        self, 
        row_data: Dict[str, Any],
        row_index: int = -1
    ) -> Email:
        """
        Build a complete email from row data.
        
        Args:
            row_data: Dictionary of column values for this recipient
            row_index: Index of row in original data
            
        Returns:
            Complete Email object
        """
        email = Email()
        email.row_data = row_data
        email.row_index = row_index
        
        # Process recipients (TO)
        email_value = str(row_data.get(self.email_column, ""))
        email.to = self._parse_email_list(email_value)
        
        # Process CC
        if self.cc_column and self.cc_column in row_data:
            cc_value = str(row_data.get(self.cc_column, ""))
            email.cc = self._parse_email_list(cc_value)
        
        # Process BCC
        bcc_list = []
        if self.bcc_column and self.bcc_column in row_data:
            bcc_value = str(row_data.get(self.bcc_column, ""))
            bcc_list = self._parse_email_list(bcc_value)
        
        # Add universal BCC
        if self.universal_bcc:
            if self.universal_bcc not in bcc_list:
                bcc_list.append(self.universal_bcc)
        
        email.bcc = bcc_list
        
        # Substitute templates
        email.subject = self.template_engine.substitute(
            self.subject_template, row_data
        )
        email.body_html = self.template_engine.substitute(
            self.body_template, row_data
        )
        
        # Generate plain text version
        from utils.html_converter import html_to_plain_text
        email.body_text = html_to_plain_text(email.body_html)
        
        # Gather attachments
        attachments = []
        
        # Add static attachments
        attachments.extend(self.static_attachments)
        
        # Add variable attachments (matched by identifier)
        if self.attachment_matcher and self.identifier_column:
            identifier = str(row_data.get(self.identifier_column, "")).strip()
            if identifier:
                matches = self.attachment_matcher.match_identifier(identifier)
                for full_path, filename, size in matches:
                    attachments.append(full_path)
        
        email.attachments = attachments
        
        return email
    
    def build_emails(
        self, 
        data_rows: List[Dict[str, Any]]
    ) -> List[Email]:
        """
        Build emails for multiple data rows.
        
        Args:
            data_rows: List of row dictionaries
            
        Returns:
            List of Email objects
        """
        emails = []
        for idx, row_data in enumerate(data_rows):
            email = self.build_email(row_data, idx)
            emails.append(email)
        return emails
    
    def _parse_email_list(self, email_string: str) -> List[str]:
        """
        Parse email string into list of addresses.
        
        Handles semicolon-separated multiple emails.
        
        Args:
            email_string: String containing one or more emails
            
        Returns:
            List of email addresses
        """
        if not email_string:
            return []
        
        # Split by semicolon and clean up
        emails = [e.strip() for e in email_string.split(';') if e.strip()]
        return emails
    
    def validate_build_config(
        self, 
        available_columns: List[str]
    ) -> List[str]:
        """
        Validate that builder configuration is complete and valid.
        
        Args:
            available_columns: List of available column names
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check email column
        if not self.email_column:
            errors.append("Email column not specified")
        elif self.email_column not in available_columns:
            errors.append(f"Email column '{self.email_column}' not found in data")
        
        # Check templates
        if not self.subject_template:
            errors.append("Subject template is empty")
        if not self.body_template:
            errors.append("Body template is empty")
        
        # Validate template variables
        all_template = self.subject_template + " " + self.body_template
        is_valid, used_vars, missing_vars = self.template_engine.validate_variables(
            all_template, available_columns
        )
        if not is_valid:
            errors.append(f"Template uses undefined variables: {', '.join(missing_vars)}")
        
        # Check CC column if specified
        if self.cc_column and self.cc_column not in available_columns:
            errors.append(f"CC column '{self.cc_column}' not found in data")
        
        # Check BCC column if specified
        if self.bcc_column and self.bcc_column not in available_columns:
            errors.append(f"BCC column '{self.bcc_column}' not found in data")
        
        # Check identifier column if specified
        if self.identifier_column and self.identifier_column not in available_columns:
            errors.append(f"Identifier column '{self.identifier_column}' not found in data")
        
        return errors
    
    def get_preview_data(
        self, 
        row_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate preview data for an email without building full object.
        
        Args:
            row_data: Row data dictionary
            
        Returns:
            Dictionary with preview information
        """
        # Get recipients
        email_value = str(row_data.get(self.email_column, ""))
        to_list = self._parse_email_list(email_value)
        
        # Substitute templates
        subject = self.template_engine.substitute(self.subject_template, row_data)
        body = self.template_engine.substitute(self.body_template, row_data)
        
        # Get attachment info
        attachment_info = []
        
        # Static
        for path in self.static_attachments:
            from utils import get_file_size_formatted
            attachment_info.append({
                'type': 'static',
                'path': path,
                'filename': os.path.basename(path) if path else "",
                'size': get_file_size_formatted(path),
            })
        
        # Variable
        if self.attachment_matcher and self.identifier_column:
            identifier = str(row_data.get(self.identifier_column, "")).strip()
            if identifier:
                matches = self.attachment_matcher.match_identifier(identifier)
                for full_path, filename, size in matches:
                    from utils import format_bytes
                    attachment_info.append({
                        'type': 'variable',
                        'path': full_path,
                        'filename': filename,
                        'size': format_bytes(size),
                    })
        
        return {
            'to': to_list,
            'subject': subject,
            'body_html': body,
            'attachments': attachment_info,
            'attachment_count': len(attachment_info),
        }
