'''
# Comprehensive Test Suite for the Lead Sniper System

This test suite includes unit tests, integration tests, and end-to-end pipeline tests.
'''

import sys
sys.path.append("..")

# Unit Tests
from main import add, subtract

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(1, 1) == 0

# Integration Tests
from database import Database

def test_add_and_save():
    db = Database()
    result = add(10, 5)
    db.save("add_result", result)
    assert db.load("add_result") == 15

# End-to-end Pipeline Tests
from pipeline import run_pipeline

def test_run_pipeline():
    result = run_pipeline(10, 5, 3)
    assert result == 12
