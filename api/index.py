"""
Vercel deployment handler for FastAPI Recipe API.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export the FastAPI app for Vercel
# Vercel expects the ASGI app to be available at module level
application = app

# Alternative export names for compatibility
handler = app
asgi = app

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
