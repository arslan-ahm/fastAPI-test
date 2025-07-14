"""
Vercel handler for FastAPI Recipe API
"""
import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import the FastAPI app
from main import app

# Export the app for Vercel
# Vercel looks for 'app' variable in the handler file
# No need for explicit handler function with modern Vercel Python runtime
