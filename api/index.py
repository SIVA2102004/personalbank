import sys
import os

# Add backend directory to Python sys.path so backend imports work seamlessly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app