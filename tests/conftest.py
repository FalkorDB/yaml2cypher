"""
Pytest configuration file for yaml2cypher tests.

This file can contain shared fixtures and configuration for pytest.
"""

import sys
import os

# Add the parent directory to the Python path
# This ensures that the tests can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
