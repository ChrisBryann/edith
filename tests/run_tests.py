#!/usr/bin/env python3

if __name__ == "__main__":
    import sys
    import pytest
    print("🚀 Running automated test suite via pytest...")
    # Run all tests in the 'tests/' directory with verbose output
    sys.exit(pytest.main(["-v", "tests/"]))