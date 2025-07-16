"""
Vercel deployment handler for FastAPI Recipe API.
"""

from app import app

# Export the ASGI app for Vercel
application = app
