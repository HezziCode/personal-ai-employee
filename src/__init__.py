"""
AI Employee - Personal AI FTE System
Main package initialization

Lazy imports to avoid dependency issues
"""

__version__ = "0.1.0"
__author__ = "Huzaifa"

__all__ = [
    "OdooClient",
    "TwitterPoster",
    "InstagramPoster",
]

# Lazy imports - only load when needed
def __getattr__(name):
    if name == "OdooClient":
        from src.accounting.odoo_client import OdooClient
        return OdooClient
    elif name == "TwitterPoster":
        from src.social.twitter import TwitterPoster
        return TwitterPoster
    elif name == "InstagramPoster":
        from src.social.instagram import InstagramPoster
        return InstagramPoster
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
