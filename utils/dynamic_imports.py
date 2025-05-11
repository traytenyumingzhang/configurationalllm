#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dynamic Imports Utility
Explicitly imports modules that might be loaded dynamically to ensure py2app includes them
"""

import importlib
import sys
import logging

logger = logging.getLogger(__name__)

# Registry of modules that might be imported dynamically
DYNAMIC_MODULES = [
    # Standard library modules often imported dynamically
    'json',
    'os',
    'sys',
    'pathlib',
    'shutil',
    'datetime',
    'logging',
    'importlib',
    'importlib.resources',
    
    # PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    
    # Project modules
    'core.llm_processor',
    'gui.main_window',
    'gui.pages',
    'utils.config_manager',
    
    # Third-party dependencies
    'anthropic',
    'openai',
    'PyPDF2',
    'pandas',
    'numpy',
]

# Modules to try importing but ignore if not available
OPTIONAL_MODULES = [
    'requests',
    'certifi',
    'urllib3',
    'chardet',
    'idna',
    'ssl',
]

def import_module(module_name):
    """
    Import a module by name and return the module object
    Logs an error if import fails but doesn't raise an exception
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        logger.warning(f"Could not import module {module_name}: {e}")
        return None

def ensure_imports():
    """
    Ensure all dynamic modules are imported and registered.
    This function should be called during application initialization
    to make sure py2app includes all necessary modules in the bundle.
    """
    imported_modules = {}
    
    # Import all required modules
    for module_name in DYNAMIC_MODULES:
        module = import_module(module_name)
        if module:
            imported_modules[module_name] = module
            logger.debug(f"Successfully imported {module_name}")
    
    # Try importing optional modules
    for module_name in OPTIONAL_MODULES:
        try:
            module = importlib.import_module(module_name)
            imported_modules[module_name] = module
            logger.debug(f"Successfully imported optional module {module_name}")
        except ImportError:
            # Ignore import errors for optional modules
            pass
    
    return imported_modules

def print_import_info():
    """Print information about imported modules for debugging"""
    print("=== Dynamic Import Information ===")
    print(f"Python version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print("\nImported Modules:")
    
    imported = ensure_imports()
    for name, module in imported.items():
        path = getattr(module, '__file__', 'Unknown location')
        print(f" - {name}: {path}")
    
    print("\nSearch Path:")
    for path in sys.path:
        print(f" - {path}")
    
    print("=================================")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Print debug information if executed directly
    print_import_info()
