"""Start the Flask server programmatically."""
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from run_flask import main
main()
