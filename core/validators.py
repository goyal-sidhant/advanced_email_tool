"""
Advanced Email Tool - Validators
================================
Validation utilities for emails, templates, and attachments.
"""

import re
from typing import Tuple, List, Optional, Set
from pathlib import Path

import config
from utils import get_file_size


def validate_email_address(email: str) -> Tuple[bool, str]:
    """
    Validate a single email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        error_message is empty if valid
    """
    if not email:
        return False, "Email address is empty"
    
    email = email.strip()
    
    # Basic format check using regex
    # This pattern handles most common email formats
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        # Check for common issues
        if '@' not in email:
            return False, "Missing @ symbol"
        if email.count('@') > 1:
            return False, "Multiple @ symbols"
        if '.' not in email.split('@')[1]:
            return False, "Invalid domain (missing dot)"
        return False, "Invalid email format"
    
    return True, ""


def is_valid_email(email: str) -> bool:
    """
    Simple check if an email address is valid.
    
    Args:
        email: Email address to check
        
    Returns:
        True if valid, False otherwise
    """
    is_valid, _ = validate_email_address(email)
    return is_valid


def validate_email_list(email_string: str, separator: str = ';') -> Tuple[bool, List[str], List[str]]:
    """
    Validate a string containing one or more email addresses.
    
    Args:
        email_string: String with email(s), possibly separated by separator
        separator: Character separating multiple emails (default: ';')
        
    Returns:
        Tuple of (all_valid, valid_emails, error_messages)
    """
    if not email_string:
        return False, [], ["No email addresses provided"]
    
    # Split by separator and clean up
    emails = [e.strip() for e in email_string.split(separator) if e.strip()]
    
    if not emails:
        return False, [], ["No valid email addresses after parsing"]
    
    valid_emails = []
    errors = []
    
    for email in emails:
        is_valid, error = validate_email_address(email)
        if is_valid:
            valid_emails.append(email)
        else:
            errors.append(f"{email}: {error}")
    
    all_valid = len(errors) == 0
    return all_valid, valid_emails, errors


def suggest_email_correction(email: str) -> Optional[str]:
    """
    Suggest correction for common email typos.
    
    Args:
        email: Email address to check
        
    Returns:
        Suggested correction, or None if no suggestion
    """
    if not email or '@' not in email:
        return None
    
    local_part, domain = email.rsplit('@', 1)
    domain_lower = domain.lower()
    
    # Check against known typos
    if domain_lower in config.EMAIL_TYPO_SUGGESTIONS:
        corrected_domain = config.EMAIL_TYPO_SUGGESTIONS[domain_lower]
        return f"{local_part}@{corrected_domain}"
    
    return None


def validate_template_variables(
    template: str, 
    available_columns: List[str]
) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that all variables in a template exist in available columns.
    
    Args:
        template: Template string containing {variable} placeholders
        available_columns: List of column names from Excel
        
    Returns:
        Tuple of (all_valid, used_variables, missing_variables)
    """
    if not template:
        return True, [], []
    
    # Find all {variable} patterns
    pattern = r'\{([^}]+)\}'
    variables = re.findall(pattern, template)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variables = []
    for var in variables:
        if var not in seen:
            seen.add(var)
            unique_variables.append(var)
    
    # Check against available columns
    available_set = set(available_columns)
    missing = [var for var in unique_variables if var not in available_set]
    
    all_valid = len(missing) == 0
    return all_valid, unique_variables, missing


def extract_template_variables(template: str) -> List[str]:
    """
    Extract all variable names from a template.
    
    Args:
        template: Template string with {variable} placeholders
        
    Returns:
        List of unique variable names
    """
    if not template:
        return []
    
    pattern = r'\{([^}]+)\}'
    variables = re.findall(pattern, template)
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for var in variables:
        if var not in seen:
            seen.add(var)
            unique.append(var)
    
    return unique


def check_attachment_size(
    file_paths: List[str], 
    max_size_bytes: int = None
) -> Tuple[bool, int, str]:
    """
    Check total size of attachments against limit.
    
    Args:
        file_paths: List of file paths to check
        max_size_bytes: Maximum allowed total size (default from config)
        
    Returns:
        Tuple of (within_limit, total_size_bytes, formatted_size_string)
    """
    if max_size_bytes is None:
        max_size_bytes = config.MAX_ATTACHMENT_SIZE_BYTES
    
    total_size = 0
    for path in file_paths:
        total_size += get_file_size(path)
    
    within_limit = total_size <= max_size_bytes
    
    # Format size string
    if total_size < 1024:
        formatted = f"{total_size} B"
    elif total_size < 1024 * 1024:
        formatted = f"{total_size / 1024:.1f} KB"
    else:
        formatted = f"{total_size / (1024 * 1024):.1f} MB"
    
    return within_limit, total_size, formatted


def validate_identifier(identifier: str) -> Tuple[bool, str]:
    """
    Validate an identifier string.
    
    Args:
        identifier: Identifier to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not identifier:
        return False, "Identifier is empty"
    
    identifier = str(identifier).strip()
    
    if not identifier:
        return False, "Identifier is empty after trimming"
    
    # Check for problematic characters that might cause file matching issues
    problematic = ['/', '\\', '\n', '\r', '\t']
    for char in problematic:
        if char in identifier:
            return False, f"Identifier contains invalid character: {repr(char)}"
    
    return True, ""


def check_duplicate_identifiers(
    identifiers: List[str]
) -> Tuple[bool, List[Tuple[str, List[int]]]]:
    """
    Check for duplicate identifiers in a list.
    
    Args:
        identifiers: List of identifier strings
        
    Returns:
        Tuple of (has_duplicates, list of (identifier, [row_indices]))
    """
    # Track where each identifier appears
    occurrences = {}
    for idx, identifier in enumerate(identifiers):
        id_str = str(identifier).strip() if identifier else ""
        if id_str:
            if id_str not in occurrences:
                occurrences[id_str] = []
            occurrences[id_str].append(idx)
    
    # Find duplicates
    duplicates = [(id_str, indices) for id_str, indices in occurrences.items() 
                  if len(indices) > 1]
    
    has_duplicates = len(duplicates) > 0
    return has_duplicates, duplicates


def validate_excel_columns(
    columns: List[str],
    required_columns: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validate that required columns exist in Excel.
    
    Args:
        columns: List of column names from Excel
        required_columns: List of required column names
        
    Returns:
        Tuple of (all_present, missing_columns)
    """
    column_set = set(columns)
    missing = [col for col in required_columns if col not in column_set]
    
    return len(missing) == 0, missing


def validate_file_path(path: str) -> Tuple[bool, str]:
    """
    Validate a file path exists and is accessible.
    
    Args:
        path: File path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path is empty"
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        return False, "File does not exist"
    
    if not path_obj.is_file():
        return False, "Path is not a file"
    
    # Try to read the file
    try:
        with open(path, 'rb') as f:
            f.read(1)
        return True, ""
    except PermissionError:
        return False, "Permission denied"
    except Exception as e:
        return False, f"Cannot access file: {e}"


def validate_directory_path(path: str) -> Tuple[bool, str]:
    """
    Validate a directory path exists and is accessible.
    
    Args:
        path: Directory path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path is empty"
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        return False, "Directory does not exist"
    
    if not path_obj.is_dir():
        return False, "Path is not a directory"
    
    # Try to list the directory
    try:
        list(path_obj.iterdir())
        return True, ""
    except PermissionError:
        return False, "Permission denied"
    except Exception as e:
        return False, f"Cannot access directory: {e}"
