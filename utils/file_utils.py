"""
Advanced Email Tool - File Utilities
====================================
Utilities for file operations, path handling, and network drive checks.
Handles Windows-specific path issues like 260 character limit.
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional, Generator
import time

import config


def write_json_atomic(path, data, **json_kwargs) -> None:
    """
    Write JSON to a file atomically (temp file + os.replace).

    A crash or power loss mid-write can never leave a truncated file —
    the old content survives until the new one is complete.
    """
    import json

    path = str(path)
    tmp_path = path + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, **json_kwargs)
    os.replace(tmp_path, path)


def ensure_extended_path(path: str) -> str:
    """
    Convert a path to extended-length path format for Windows.
    
    This allows paths longer than 260 characters on Windows 10+.
    
    Args:
        path: Original file path
        
    Returns:
        Extended path (prefixed with \\\\?\\ if needed)
    """
    if not path:
        return path
    
    # Convert to absolute path
    abs_path = os.path.abspath(path)
    
    # If already extended or not Windows-style path, return as-is
    if abs_path.startswith("\\\\?\\"):
        return abs_path
    
    # Add extended path prefix for long paths
    if len(abs_path) > 240:  # Leave some margin
        if abs_path.startswith("\\\\"):
            # UNC path (network): \\server\share -> \\?\UNC\server\share
            return "\\\\?\\UNC\\" + abs_path[2:]
        else:
            # Local path: C:\folder -> \\?\C:\folder
            return "\\\\?\\" + abs_path
    
    return abs_path


def is_valid_path(path: str) -> bool:
    """
    Check if a path string is valid (not empty, no invalid characters).
    
    Args:
        path: Path string to validate
        
    Returns:
        True if path is valid, False otherwise
    """
    if not path or not path.strip():
        return False
    
    # Check for invalid characters (Windows)
    invalid_chars = '<>"|?*'
    for char in invalid_chars:
        if char in path:
            return False
    
    return True


def check_path_accessible(path: str) -> Tuple[bool, str]:
    """
    Check if a file or directory path is accessible.
    
    Args:
        path: Path to check
        
    Returns:
        Tuple of (is_accessible, error_message)
        error_message is empty string if accessible
    """
    if not path:
        return False, "Path is empty"
    
    try:
        extended_path = ensure_extended_path(path)
        
        if os.path.isfile(extended_path):
            # Check if file can be opened
            with open(extended_path, 'rb') as f:
                f.read(1)  # Try reading 1 byte
            return True, ""
        
        elif os.path.isdir(extended_path):
            # Check if directory can be listed
            os.listdir(extended_path)
            return True, ""
        
        else:
            return False, "Path does not exist"
            
    except PermissionError:
        return False, "Permission denied"
    except FileNotFoundError:
        return False, "Path not found"
    except OSError as e:
        return False, f"OS error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def check_network_drive(path: str, timeout: int = None) -> Tuple[bool, str]:
    """
    Check if a network drive/path is accessible.
    
    Args:
        path: Network path to check (e.g., \\\\server\\share)
        timeout: Timeout in seconds (default from config)
        
    Returns:
        Tuple of (is_accessible, error_message)
    """
    if timeout is None:
        timeout = config.NETWORK_CHECK_TIMEOUT
    
    if not path:
        return False, "Path is empty"
    
    # Quick check - is this a network path?
    is_network = path.startswith("\\\\") or path.startswith("//")
    
    if not is_network:
        # Not a network path, use regular check
        return check_path_accessible(path)
    
    try:
        extended_path = ensure_extended_path(path)
        
        # Try to list directory with implicit timeout
        # (Python doesn't have built-in timeout for file ops,
        # but network timeout is usually handled by OS)
        start_time = time.time()
        
        if os.path.isdir(extended_path):
            os.listdir(extended_path)
            return True, ""
        elif os.path.isfile(extended_path):
            return True, ""
        else:
            return False, "Network path not found or not accessible"
            
    except PermissionError:
        return False, "Permission denied on network path"
    except FileNotFoundError:
        return False, "Network path not found"
    except OSError as e:
        if "network" in str(e).lower():
            return False, "Network unavailable"
        return False, f"Network error: {e}"
    except Exception as e:
        return False, f"Error accessing network path: {e}"


def get_file_size(path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: Path to file
        
    Returns:
        File size in bytes, or 0 if error
    """
    try:
        extended_path = ensure_extended_path(path)
        return os.path.getsize(extended_path)
    except Exception:
        return 0


def get_file_size_formatted(path: str) -> str:
    """
    Get human-readable file size.
    
    Args:
        path: Path to file
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    size_bytes = get_file_size(path)
    return format_bytes(size_bytes)


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes into human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def scan_directory(
    directory: str,
    recursive: bool = False,
    extensions: List[str] = None
) -> Generator[Tuple[str, str, int], None, None]:
    """
    Scan a directory and yield file information.
    
    Args:
        directory: Directory path to scan
        recursive: Whether to scan subdirectories
        extensions: List of file extensions to include (e.g., ['.pdf', '.xlsx'])
                   If None or empty, includes all files
        
    Yields:
        Tuples of (full_path, filename, size_bytes)
    """
    if not directory:
        return
    
    extended_dir = ensure_extended_path(directory)
    
    # Normalize extensions to lowercase with dot prefix
    if extensions:
        extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                      for ext in extensions]
    
    try:
        if recursive:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(extended_dir):
                for filename in files:
                    if _should_include_file(filename, extensions):
                        full_path = os.path.join(root, filename)
                        try:
                            size = os.path.getsize(full_path)
                            yield (full_path, filename, size)
                        except OSError:
                            # Skip files we can't access
                            continue
        else:
            # Only scan immediate directory
            for entry in os.scandir(extended_dir):
                if entry.is_file():
                    if _should_include_file(entry.name, extensions):
                        try:
                            size = entry.stat().st_size
                            yield (entry.path, entry.name, size)
                        except OSError:
                            continue
                            
    except PermissionError:
        return
    except FileNotFoundError:
        return
    except Exception:
        return


def _should_include_file(filename: str, extensions: Optional[List[str]]) -> bool:
    """
    Check if a file should be included based on extension filter.
    
    Args:
        filename: Name of the file
        extensions: List of allowed extensions (None = all)
        
    Returns:
        True if file should be included
    """
    if not extensions:
        return True
    
    _, ext = os.path.splitext(filename)
    return ext.lower() in extensions


def get_path_length(path: str) -> int:
    """
    Get the length of a path string.
    
    Args:
        path: Path to measure
        
    Returns:
        Character length of the absolute path
    """
    return len(os.path.abspath(path))


def check_path_length(path: str, warn_threshold: int = 240) -> Tuple[bool, str]:
    """
    Check if a path might have length issues.
    
    Args:
        path: Path to check
        warn_threshold: Character count to warn at (default 240)
        
    Returns:
        Tuple of (is_ok, warning_message)
    """
    length = get_path_length(path)
    
    if length > 260:
        return False, f"Path exceeds 260 characters ({length} chars). May cause issues on older systems."
    elif length > warn_threshold:
        return True, f"Path is {length} characters. Close to 260 limit."
    else:
        return True, ""


def list_files_with_identifier(
    directory: str,
    identifier: str,
    recursive: bool = False,
    extensions: List[str] = None
) -> List[Tuple[str, str, int]]:
    """
    Find all files in directory whose names contain the identifier.
    
    Args:
        directory: Directory to search
        identifier: Identifier string to match (exact substring match, case-sensitive)
        recursive: Whether to search subdirectories
        extensions: File extensions to include
        
    Returns:
        List of tuples (full_path, filename, size_bytes) for matching files
    """
    matches = []
    
    for full_path, filename, size in scan_directory(directory, recursive, extensions):
        # Exact substring match in filename (case-sensitive)
        if identifier in filename:
            matches.append((full_path, filename, size))
    
    return matches
