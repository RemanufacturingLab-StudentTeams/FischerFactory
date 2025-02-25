"""Hey, modularity! This module is here so that import configurations and resources are accessible anywhere in the program, and to fix circular dependencies that happened when this was in `app/app.py`. 
"""

mode = None
"""Specifies what mode the program is running in. Either 'dev', 'prod', or 'test'. Set in `app/app.py`."""

# Exports
__all__ =["mode"]