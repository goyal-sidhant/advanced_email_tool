"""
Advanced Email Tool - Template Storage
======================================
Handles saving and loading email templates.
Templates are stored as JSON files in the templates directory.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from utils import get_logger

import config


class TemplateStorage:
    """
    Manages email template persistence.
    
    Each template is stored as a separate JSON file containing:
    - Subject line template
    - Body HTML template
    - Metadata (created date, last modified)
    """
    
    def __init__(self):
        """Initialize template storage."""
        self.logger = get_logger()
        self.templates_dir = config.TEMPLATES_DIR
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure templates directory exists."""
        config.ensure_directories()
    
    def _get_template_path(self, name: str) -> Path:
        """
        Get the file path for a template name.
        
        Args:
            name: Template name
            
        Returns:
            Path object for the template file
        """
        # Sanitize name for filesystem
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
        safe_name = safe_name.strip()[:50]  # Limit length
        return self.templates_dir / f"{safe_name}.json"
    
    def save_template(
        self,
        name: str,
        subject: str,
        body: str,
        description: str = ""
    ) -> Tuple[bool, str]:
        """
        Save an email template.
        
        Args:
            name: Template name
            subject: Subject line template
            body: Body HTML template
            description: Optional description
            
        Returns:
            Tuple of (success, message)
        """
        if not name:
            return False, "Template name is required"
        
        if not subject and not body:
            return False, "Template must have subject or body"
        
        try:
            template_path = self._get_template_path(name)
            
            # Check if updating existing
            is_update = template_path.exists()
            existing_created = None
            if is_update:
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                        existing_created = existing.get('created_at')
                except Exception:
                    pass
            
            template_data = {
                'name': name,
                'subject': subject,
                'body': body,
                'description': description,
                'created_at': existing_created or datetime.now().isoformat(),
                'modified_at': datetime.now().isoformat(),
                'version': config.APP_VERSION,
            }
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            action = "updated" if is_update else "saved"
            self.logger.info(f"Template {action}: {name}")
            return True, f"Template {action} successfully"
            
        except Exception as e:
            self.logger.error(f"Error saving template: {e}", exc_info=True)
            return False, f"Error saving template: {e}"
    
    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load an email template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template dictionary or None if not found
        """
        try:
            template_path = self._get_template_path(name)
            
            if not template_path.exists():
                self.logger.warning(f"Template not found: {name}")
                return None
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            self.logger.debug(f"Template loaded: {name}")
            return template
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid template file format: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading template: {e}", exc_info=True)
            return None
    
    def delete_template(self, name: str) -> Tuple[bool, str]:
        """
        Delete a template.
        
        Args:
            name: Template name
            
        Returns:
            Tuple of (success, message)
        """
        try:
            template_path = self._get_template_path(name)
            
            if not template_path.exists():
                return False, "Template not found"
            
            os.remove(template_path)
            self.logger.info(f"Template deleted: {name}")
            return True, "Template deleted"
            
        except Exception as e:
            self.logger.error(f"Error deleting template: {e}")
            return False, f"Error deleting template: {e}"
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all saved templates.
        
        Returns:
            List of template info dictionaries
        """
        templates = []
        
        try:
            for file_path in self.templates_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                    
                    templates.append({
                        'name': template.get('name', file_path.stem),
                        'description': template.get('description', ''),
                        'modified_at': template.get('modified_at', ''),
                        'has_subject': bool(template.get('subject')),
                        'has_body': bool(template.get('body')),
                    })
                except Exception as e:
                    self.logger.warning(f"Error reading template file {file_path}: {e}")
                    continue
            
            # Sort by modified date (newest first)
            templates.sort(key=lambda x: x.get('modified_at', ''), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listing templates: {e}")
        
        return templates
    
    def get_template_names(self) -> List[str]:
        """
        Get list of template names.
        
        Returns:
            List of template name strings
        """
        return [t['name'] for t in self.list_templates()]
    
    def template_exists(self, name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            name: Template name
            
        Returns:
            True if template exists
        """
        return self._get_template_path(name).exists()
    
    def rename_template(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """
        Rename a template.
        
        Args:
            old_name: Current template name
            new_name: New template name
            
        Returns:
            Tuple of (success, message)
        """
        if not new_name:
            return False, "New name is required"
        
        if self.template_exists(new_name):
            return False, "A template with that name already exists"
        
        try:
            # Load existing
            template = self.load_template(old_name)
            if not template:
                return False, "Template not found"
            
            # Save with new name
            template['name'] = new_name
            success, msg = self.save_template(
                new_name,
                template.get('subject', ''),
                template.get('body', ''),
                template.get('description', '')
            )
            
            if not success:
                return False, msg
            
            # Delete old
            self.delete_template(old_name)
            
            return True, "Template renamed"
            
        except Exception as e:
            self.logger.error(f"Error renaming template: {e}")
            return False, f"Error renaming template: {e}"
    
    def duplicate_template(self, name: str, new_name: str) -> Tuple[bool, str]:
        """
        Create a copy of a template.
        
        Args:
            name: Template to copy
            new_name: Name for the copy
            
        Returns:
            Tuple of (success, message)
        """
        if not new_name:
            return False, "New name is required"
        
        if self.template_exists(new_name):
            return False, "A template with that name already exists"
        
        try:
            template = self.load_template(name)
            if not template:
                return False, "Template not found"
            
            return self.save_template(
                new_name,
                template.get('subject', ''),
                template.get('body', ''),
                f"Copy of {name}"
            )
            
        except Exception as e:
            self.logger.error(f"Error duplicating template: {e}")
            return False, f"Error: {e}"
    
    def export_template(self, name: str, export_path: str) -> Tuple[bool, str]:
        """
        Export a template to a specific file.
        
        Args:
            name: Template name
            export_path: Path to export to
            
        Returns:
            Tuple of (success, message)
        """
        try:
            template = self.load_template(name)
            if not template:
                return False, "Template not found"
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            return True, f"Template exported to {export_path}"
            
        except Exception as e:
            self.logger.error(f"Error exporting template: {e}")
            return False, f"Error: {e}"
    
    def import_template(self, import_path: str, name: str = None) -> Tuple[bool, str]:
        """
        Import a template from a file.
        
        Args:
            import_path: Path to import from
            name: Optional override name (uses file's name if not provided)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            template_name = name or template.get('name', 'Imported Template')
            
            return self.save_template(
                template_name,
                template.get('subject', ''),
                template.get('body', ''),
                template.get('description', '')
            )
            
        except Exception as e:
            self.logger.error(f"Error importing template: {e}")
            return False, f"Error: {e}"
