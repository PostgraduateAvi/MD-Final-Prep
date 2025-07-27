#!/usr/bin/env python3
"""
MD Final Prep - Automation Test Suite
====================================

Quick test suite to verify all automation components are working correctly.
"""

import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_automation_components():
    """Test all automation components"""
    
    tests = [
        {
            "name": "Quick Setup Check",
            "command": [sys.executable, "quick_setup.py", "--check"],
            "timeout": 60
        },
        {
            "name": "Main Agent Status",
            "command": [sys.executable, "md_final_prep_agent.py", "--mode", "status"],
            "timeout": 30
        },
        {
            "name": "Configuration Loading", 
            "command": [sys.executable, "-c", "import json; print('Config:', json.load(open('md_prep_config.json')))"],
            "timeout": 10
        }
    ]
    
    print("🧪 Testing MD Final Prep Automation Components")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n🔍 {test['name']}")
        try:
            result = subprocess.run(
                test["command"],
                capture_output=True,
                text=True,
                timeout=test["timeout"]
            )
            
            if result.returncode == 0:
                print(f"  ✅ PASSED")
                passed += 1
            else:
                print(f"  ❌ FAILED - Return code: {result.returncode}")
                print(f"     Error: {result.stderr[:100]}...")
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ TIMEOUT")
        except Exception as e:
            print(f"  💥 ERROR: {e}")
    
    # File existence tests
    print(f"\n📁 Testing Output Files")
    output_files = [
        "tokenized_content.json",
        "token_summary.csv",
        "token_summary.txt",
        "md_prep_config.json"
    ]
    
    file_tests_passed = 0
    for filename in output_files:
        if Path(filename).exists():
            print(f"  ✅ {filename}")
            file_tests_passed += 1
        else:
            print(f"  ❌ {filename} (missing)")
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"TEST SUMMARY")
    print(f"Component tests: {passed}/{total}")
    print(f"File tests: {file_tests_passed}/{len(output_files)}")
    
    if passed == total and file_tests_passed >= 3:
        print(f"🎉 ALL TESTS PASSED - Automation system ready!")
        return True
    else:
        print(f"⚠️  SOME TESTS FAILED - Check setup")
        return False

if __name__ == "__main__":
    success = test_automation_components()
    sys.exit(0 if success else 1)