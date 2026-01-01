"""
Advanced Email Tool - Template Engine
=====================================
Handles email template variable substitution.
Replaces {variable} placeholders with actual data.
"""

import re
from typing import Dict, Any, List, Tuple, Optional

from utils import get_logger


class TemplateEngine:
    """
    Handles template variable substitution.
    
    Takes a template with {variable} placeholders and replaces
    them with actual values from row data.
    """
    
    def __init__(self):
        """Initialize the template engine."""
        self.logger = get_logger()
        self.variable_pattern = re.compile(r'\{([^}]+)\}')
    
    def substitute(
        self, 
        template: str, 
        data: Dict[str, Any],
        missing_placeholder: str = "{MISSING}"
    ) -> str:
        """
        Substitute variables in template with values from data.
        
        Args:
            template: Template string with {variable} placeholders
            data: Dictionary mapping variable names to values
            missing_placeholder: Text to use for missing variables
            
        Returns:
            Template with variables replaced by values
        """
        if not template:
            return ""
        
        def replace_var(match):
            var_name = match.group(1)
            if var_name in data:
                value = data[var_name]
                # Convert None to empty string
                if value is None:
                    return ""
                return str(value)
            else:
                self.logger.warning(f"Variable '{var_name}' not found in data")
                return missing_placeholder
        
        return self.variable_pattern.sub(replace_var, template)
    
    def substitute_safe(
        self, 
        template: str, 
        data: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """
        Substitute variables and report any missing variables.
        
        Args:
            template: Template string with {variable} placeholders
            data: Dictionary mapping variable names to values
            
        Returns:
            Tuple of (substituted_text, list_of_missing_variables)
        """
        if not template:
            return "", []
        
        missing_vars = []
        
        def replace_var(match):
            var_name = match.group(1)
            if var_name in data:
                value = data[var_name]
                if value is None:
                    return ""
                return str(value)
            else:
                missing_vars.append(var_name)
                return f"{{{var_name}}}"  # Keep original placeholder
        
        result = self.variable_pattern.sub(replace_var, template)
        return result, missing_vars
    
    def extract_variables(self, template: str) -> List[str]:
        """
        Extract all variable names from a template.
        
        Args:
            template: Template string
            
        Returns:
            List of unique variable names (in order of appearance)
        """
        if not template:
            return []
        
        variables = self.variable_pattern.findall(template)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for var in variables:
            if var not in seen:
                seen.add(var)
                unique.append(var)
        
        return unique
    
    def validate_variables(
        self, 
        template: str, 
        available_columns: List[str]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate that all template variables exist in available columns.
        
        Args:
            template: Template string
            available_columns: List of available column names
            
        Returns:
            Tuple of (all_valid, used_variables, missing_variables)
        """
        variables = self.extract_variables(template)
        available_set = set(available_columns)
        
        missing = [var for var in variables if var not in available_set]
        
        return len(missing) == 0, variables, missing
    
    def preview_substitution(
        self, 
        template: str, 
        data: Dict[str, Any],
        highlight: bool = True
    ) -> str:
        """
        Generate a preview of substitution, optionally highlighting replaced parts.
        
        Args:
            template: Template string
            data: Data dictionary
            highlight: If True, wrap substituted values in markers
            
        Returns:
            Preview string with substitutions
        """
        if not template:
            return ""
        
        if not highlight:
            return self.substitute(template, data)
        
        def replace_var_highlighted(match):
            var_name = match.group(1)
            if var_name in data:
                value = data[var_name]
                if value is None:
                    value = ""
                # Use HTML-style highlighting for preview
                return f'<span style="background-color: #ffff00;">{value}</span>'
            else:
                return f'<span style="background-color: #ff0000; color: white;">{{{var_name}}}</span>'
        
        return self.variable_pattern.sub(replace_var_highlighted, template)
    
    def create_sample_data(self, template: str) -> Dict[str, str]:
        """
        Create sample data for template preview.
        
        Args:
            template: Template string
            
        Returns:
            Dictionary with sample values for each variable
        """
        variables = self.extract_variables(template)
        
        sample_values = {
            'Name': 'John Smith',
            'Email': 'john@example.com',
            'Company': 'ABC Corporation',
            'Subject': 'Important Notice',
            'Month': 'January 2025',
            'Year': '2024-25',
            'Amount': '₹10,000',
            'Date': '01-Jan-2025',
            'Identifier': 'ABC123',
        }
        
        result = {}
        for var in variables:
            if var in sample_values:
                result[var] = sample_values[var]
            else:
                result[var] = f'[{var}]'
        
        return result
    
    def get_variable_usage_report(
        self, 
        subject: str, 
        body: str, 
        available_columns: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a report on variable usage in subject and body.
        
        Args:
            subject: Email subject template
            body: Email body template
            available_columns: Available column names
            
        Returns:
            Dictionary with usage statistics and issues
        """
        subject_vars = self.extract_variables(subject)
        body_vars = self.extract_variables(body)
        all_vars = list(set(subject_vars + body_vars))
        
        available_set = set(available_columns)
        
        used_columns = [v for v in all_vars if v in available_set]
        unused_columns = [c for c in available_columns if c not in all_vars]
        missing_vars = [v for v in all_vars if v not in available_set]
        
        return {
            'subject_variables': subject_vars,
            'body_variables': body_vars,
            'all_variables': all_vars,
            'used_columns': used_columns,
            'unused_columns': unused_columns,
            'missing_variables': missing_vars,
            'is_valid': len(missing_vars) == 0,
        }


# Convenience function for simple substitution
def substitute_template(template: str, data: Dict[str, Any]) -> str:
    """
    Simple template substitution function.
    
    Args:
        template: Template with {variable} placeholders
        data: Data dictionary
        
    Returns:
        Substituted string
    """
    engine = TemplateEngine()
    return engine.substitute(template, data)
