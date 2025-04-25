import os, sys

# Add the backend directory to the Python path so that app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 