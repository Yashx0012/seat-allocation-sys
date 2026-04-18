#!/usr/bin/env python
"""
Wrapper script to workaround Flask Python 3.14 compatibility issue
"""

import sys
import pkgutil

# Monkey-patch pkgutil.get_loader for compatibility with Python 3.14
if not hasattr(pkgutil, 'get_loader'):
    from importlib.util import find_spec
    def get_loader(module_name):
        """Compatibility shim for pkgutil.get_loader"""
        spec = find_spec(module_name)
        return spec.loader if spec else None
    pkgutil.get_loader = get_loader

# Now import and run the app
from app import app

if __name__ == '__main__':
    app.run(debug=True, port=5001)
