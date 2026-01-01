"""
Advanced Email Tool - HTML Converter
====================================
Utilities for converting between rich text and HTML formats.
Used for email composition and template storage.
"""

import re
from typing import Optional


def plain_text_to_html(text: str) -> str:
    """
    Convert plain text to basic HTML.
    
    - Escapes HTML special characters
    - Converts newlines to <br> tags
    - Wraps in paragraph tags
    
    Args:
        text: Plain text string
        
    Returns:
        HTML formatted string
    """
    if not text:
        return "<p></p>"
    
    # Escape HTML special characters
    text = escape_html(text)
    
    # Convert newlines to <br>
    text = text.replace('\n', '<br>\n')
    
    # Wrap in paragraph
    return f"<p>{text}</p>"


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for HTML
    """
    if not text:
        return ""
    
    replacements = [
        ('&', '&amp;'),   # Must be first
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
    
    return text


def unescape_html(text: str) -> str:
    """
    Unescape HTML entities back to characters.
    
    Args:
        text: HTML text with entities
        
    Returns:
        Text with entities converted to characters
    """
    if not text:
        return ""
    
    replacements = [
        ('&lt;', '<'),
        ('&gt;', '>'),
        ('&quot;', '"'),
        ('&#39;', "'"),
        ('&amp;', '&'),   # Must be last
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
    
    return text


def html_to_plain_text(html: str) -> str:
    """
    Convert HTML to plain text.
    
    - Removes HTML tags
    - Converts <br> and </p> to newlines
    - Unescapes HTML entities
    
    Args:
        html: HTML string
        
    Returns:
        Plain text string
    """
    if not html:
        return ""
    
    text = html
    
    # Convert line break tags to newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
    # Convert paragraph ends to double newlines
    text = re.sub(r'</p>\s*<p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    
    # Convert list items to newlines with bullets
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Unescape HTML entities
    text = unescape_html(text)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def wrap_in_html_document(body_html: str, title: str = "Email") -> str:
    """
    Wrap HTML body content in a complete HTML document.
    
    Args:
        body_html: HTML content for the body
        title: Document title
        
    Returns:
        Complete HTML document string
    """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{escape_html(title)}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333333;
            margin: 20px;
        }}
        table {{
            border-collapse: collapse;
            margin: 10px 0;
        }}
        td, th {{
            border: 1px solid #cccccc;
            padding: 8px;
        }}
        th {{
            background-color: #f0f0f0;
        }}
    </style>
</head>
<body>
{body_html}
</body>
</html>"""


def extract_body_from_html(html_document: str) -> str:
    """
    Extract body content from a complete HTML document.
    
    Args:
        html_document: Complete HTML document
        
    Returns:
        Content between <body> tags, or original if no body tags
    """
    if not html_document:
        return ""
    
    # Try to extract body content
    match = re.search(r'<body[^>]*>(.*?)</body>', html_document, 
                      flags=re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return html_document


def sanitize_html_for_email(html: str) -> str:
    """
    Sanitize HTML for safe email content.
    
    - Removes script tags
    - Removes event handlers
    - Removes external resources (optional)
    
    Args:
        html: HTML content
        
    Returns:
        Sanitized HTML safe for email
    """
    if not html:
        return ""
    
    sanitized = html
    
    # Remove script tags and content
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, 
                       flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style tags (keep inline styles)
    sanitized = re.sub(r'<style[^>]*>.*?</style>', '', sanitized,
                       flags=re.DOTALL | re.IGNORECASE)
    
    # Remove event handlers (onclick, onload, etc.)
    sanitized = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized,
                       flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    sanitized = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 
                       'href="#"', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def convert_newlines_to_br(text: str) -> str:
    """
    Convert newline characters to HTML <br> tags.
    
    Args:
        text: Text with newlines
        
    Returns:
        Text with <br> tags
    """
    if not text:
        return ""
    return text.replace('\r\n', '<br>').replace('\n', '<br>').replace('\r', '<br>')


def normalize_html_whitespace(html: str) -> str:
    """
    Normalize whitespace in HTML content.
    
    Args:
        html: HTML content
        
    Returns:
        HTML with normalized whitespace
    """
    if not html:
        return ""
    
    # Replace multiple spaces with single space (outside of <pre> tags)
    # This is a simple implementation - doesn't handle <pre> tags
    html = re.sub(r' {2,}', ' ', html)
    
    # Remove spaces around tags
    html = re.sub(r'>\s+<', '><', html)
    
    return html.strip()
