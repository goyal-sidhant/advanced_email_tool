"""
Advanced Email Tool - Recipient Lists Storage
=============================================
Handles saving and loading recipient selection lists.
Allows users to save groups like "GST Clients", "Mumbai Clients", etc.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from utils import get_logger

import config


class RecipientListStorage:
    """
    Manages recipient list persistence.
    
    Each list is stored as a JSON file containing:
    - List name
    - Selected row indices
    - Metadata
    """
    
    def __init__(self):
        """Initialize recipient list storage."""
        self.logger = get_logger()
        self.lists_dir = config.RECIPIENT_LISTS_DIR
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure lists directory exists."""
        config.ensure_directories()
    
    def _get_list_path(self, name: str) -> Path:
        """
        Get the file path for a list name.
        
        Args:
            name: List name
            
        Returns:
            Path object for the list file
        """
        # Sanitize name for filesystem
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
        safe_name = safe_name.strip()[:50]
        return self.lists_dir / f"{safe_name}.json"
    
    def save_list(
        self,
        name: str,
        selected_indices: List[int],
        description: str = "",
        source_file: str = "",
        recipient_emails: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Save a recipient list.

        Args:
            name: List name
            selected_indices: List of selected row indices (0-based)
            description: Optional description
            source_file: Optional path to source Excel file
            recipient_emails: Email per selected row — lets the list follow
                the same clients even after rows move in the Excel file

        Returns:
            Tuple of (success, message)
        """
        if not name:
            return False, "List name is required"
        
        if not selected_indices:
            return False, "No recipients selected"
        
        try:
            list_path = self._get_list_path(name)
            
            # Check if updating existing
            is_update = list_path.exists()
            existing_created = None
            if is_update:
                try:
                    with open(list_path, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                        existing_created = existing.get('created_at')
                except Exception:
                    pass
            
            list_data = {
                'name': name,
                'selected_indices': sorted(selected_indices),
                'count': len(selected_indices),
                'description': description,
                'source_file': source_file,
                'created_at': existing_created or datetime.now().isoformat(),
                'modified_at': datetime.now().isoformat(),
            }
            if recipient_emails:
                list_data['recipient_emails'] = list(recipient_emails)
            
            with open(list_path, 'w', encoding='utf-8') as f:
                json.dump(list_data, f, indent=2)
            
            action = "updated" if is_update else "saved"
            self.logger.info(f"Recipient list {action}: {name} ({len(selected_indices)} recipients)")
            return True, f"List {action} with {len(selected_indices)} recipients"
            
        except Exception as e:
            self.logger.error(f"Error saving list: {e}", exc_info=True)
            return False, f"Error saving list: {e}"
    
    def load_list(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a recipient list by name.
        
        Args:
            name: List name
            
        Returns:
            List dictionary or None if not found
        """
        try:
            list_path = self._get_list_path(name)
            
            if not list_path.exists():
                self.logger.warning(f"List not found: {name}")
                return None
            
            with open(list_path, 'r', encoding='utf-8') as f:
                list_data = json.load(f)
            
            self.logger.debug(f"List loaded: {name}")
            return list_data
            
        except Exception as e:
            self.logger.error(f"Error loading list: {e}", exc_info=True)
            return None
    
    @staticmethod
    def resolve_selection(
        list_data: Dict[str, Any],
        current_emails: List[str]
    ) -> Tuple[List[int], List[str]]:
        """
        Match a saved list against the currently loaded rows.

        Matches by email (case-insensitive) when the list stores emails,
        so the selection follows the same clients even after rows are
        inserted, deleted, or re-sorted in Excel. Older lists without
        emails fall back to their raw indices, range-checked.

        Args:
            list_data: Saved list dictionary (from load_list)
            current_emails: Email value of each currently loaded row, in order

        Returns:
            Tuple of (row indices to select, saved emails not found)
        """
        saved_emails = list_data.get('recipient_emails')

        if not saved_emails:
            max_idx = len(current_emails) - 1
            saved_indices = list_data.get('selected_indices', [])
            return [i for i in saved_indices if 0 <= i <= max_idx], []

        email_rows: Dict[str, List[int]] = {}
        for idx, email in enumerate(current_emails):
            key = str(email or '').strip().lower()
            if key:
                email_rows.setdefault(key, []).append(idx)

        indices: List[int] = []
        missing: List[str] = []
        for email in saved_emails:
            key = str(email or '').strip().lower()
            rows = email_rows.get(key)
            if rows:
                indices.extend(rows)
            else:
                missing.append(email)

        return sorted(set(indices)), missing

    def get_selected_indices(self, name: str) -> Optional[List[int]]:
        """
        Get just the selected indices from a list.
        
        Args:
            name: List name
            
        Returns:
            List of indices or None if not found
        """
        list_data = self.load_list(name)
        if list_data:
            return list_data.get('selected_indices', [])
        return None
    
    def delete_list(self, name: str) -> Tuple[bool, str]:
        """
        Delete a recipient list.
        
        Args:
            name: List name
            
        Returns:
            Tuple of (success, message)
        """
        try:
            list_path = self._get_list_path(name)
            
            if not list_path.exists():
                return False, "List not found"
            
            os.remove(list_path)
            self.logger.info(f"List deleted: {name}")
            return True, "List deleted"
            
        except Exception as e:
            self.logger.error(f"Error deleting list: {e}")
            return False, f"Error deleting list: {e}"
    
    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all saved recipient lists.
        
        Returns:
            List of list info dictionaries
        """
        lists = []
        
        try:
            for file_path in self.lists_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        list_data = json.load(f)
                    
                    lists.append({
                        'name': list_data.get('name', file_path.stem),
                        'count': list_data.get('count', 0),
                        'description': list_data.get('description', ''),
                        'modified_at': list_data.get('modified_at', ''),
                        'source_file': list_data.get('source_file', ''),
                    })
                except Exception as e:
                    self.logger.warning(f"Error reading list file {file_path}: {e}")
                    continue
            
            # Sort by modified date (newest first)
            lists.sort(key=lambda x: x.get('modified_at', ''), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listing recipient lists: {e}")
        
        return lists
    
    def get_list_names(self) -> List[str]:
        """
        Get names of all saved lists.
        
        Returns:
            List of list name strings
        """
        return [lst['name'] for lst in self.list_all()]
    
    def list_exists(self, name: str) -> bool:
        """
        Check if a list exists.
        
        Args:
            name: List name
            
        Returns:
            True if list exists
        """
        return self._get_list_path(name).exists()
    
    def rename_list(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """
        Rename a recipient list.
        
        Args:
            old_name: Current list name
            new_name: New list name
            
        Returns:
            Tuple of (success, message)
        """
        if not new_name:
            return False, "New name is required"
        
        if self.list_exists(new_name):
            return False, "A list with that name already exists"
        
        try:
            list_data = self.load_list(old_name)
            if not list_data:
                return False, "List not found"
            
            # Save with new name
            success, msg = self.save_list(
                new_name,
                list_data.get('selected_indices', []),
                list_data.get('description', ''),
                list_data.get('source_file', '')
            )
            
            if not success:
                return False, msg
            
            # Delete old
            self.delete_list(old_name)
            
            return True, "List renamed"
            
        except Exception as e:
            self.logger.error(f"Error renaming list: {e}")
            return False, f"Error: {e}"
    
    def merge_lists(
        self,
        list_names: List[str],
        new_name: str,
        union: bool = True
    ) -> Tuple[bool, str]:
        """
        Merge multiple lists into one.
        
        Args:
            list_names: Names of lists to merge
            new_name: Name for merged list
            union: If True, union of all; if False, intersection
            
        Returns:
            Tuple of (success, message)
        """
        if len(list_names) < 2:
            return False, "Need at least 2 lists to merge"
        
        if not new_name:
            return False, "New list name is required"
        
        try:
            all_indices = []
            for name in list_names:
                indices = self.get_selected_indices(name)
                if indices is None:
                    return False, f"List not found: {name}"
                all_indices.append(set(indices))
            
            if union:
                merged = set.union(*all_indices)
            else:
                merged = set.intersection(*all_indices)
            
            return self.save_list(
                new_name,
                list(merged),
                f"Merged from: {', '.join(list_names)}"
            )
            
        except Exception as e:
            self.logger.error(f"Error merging lists: {e}")
            return False, f"Error: {e}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored lists.
        
        Returns:
            Dictionary with statistics
        """
        lists = self.list_all()
        
        if not lists:
            return {
                'total_lists': 0,
                'total_recipients': 0,
                'average_size': 0,
            }
        
        total_recipients = sum(lst.get('count', 0) for lst in lists)
        
        return {
            'total_lists': len(lists),
            'total_recipients': total_recipients,
            'average_size': total_recipients / len(lists) if lists else 0,
            'largest_list': max(lists, key=lambda x: x.get('count', 0))['name'] if lists else None,
            'smallest_list': min(lists, key=lambda x: x.get('count', 0))['name'] if lists else None,
        }
