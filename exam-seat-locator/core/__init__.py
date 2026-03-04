"""
core/__init__.py
Instantiates the AppCache singleton and loads it immediately.
Import `cache` anywhere in the app to get the pre-loaded, ready cache.
"""

from .cache import AppCache

# Single shared instance — built once when the package is first imported
cache = AppCache()
cache.load()
