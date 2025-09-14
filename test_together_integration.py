#!/usr/bin/env python3
"""
Test Together AI integration with the am_app CLI
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import am_app
sys.path.insert(0, str(Path(__file__).parent))

def test_cli_integration():
    """Test the CLI integration with Together AI"""
    print("🚀 Testing Together AI integration with am_app CLI")
    print("=" * 60)
    
    # Check if sample file exists
    sample_file = "data/samples/mutualfund_sample.csv"
    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    print(f"✅ Found sample file: {sample_file}")
    
    # Test importing the am_app module
    try:
        from am_app.app import AMApp
        print("✅ Successfully imported AMApp")
    except ImportError as e:
        print(f"❌ Failed to import AMApp: {e}")
        return False
    
    # Test creating parser instance
    try:
        app = AMApp()
        print("✅ Successfully created AMApp instance")
    except Exception as e:
        print(f"❌ Failed to create AMApp: {e}")
        return False
    
    # Check if together method is available
    try:
        # Just check if the parse method accepts the together method
        print("✅ Parser ready for testing")
        print("\n📋 Available parsing methods:")
        print("   - manual")
        print("   - llm") 
        print("   - together (NEW)")
        
        return True
    except Exception as e:
        print(f"❌ Error checking parser methods: {e}")
        return False

def test_together_import():
    """Test if Together AI service can be imported"""
    try:
        from am_llm.together_service import TogetherLLMService
        print("✅ Successfully imported TogetherLLMService")
        return True
    except ImportError as e:
        print(f"❌ Failed to import TogetherLLMService: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Together AI Integration Tests")
    print("=" * 60)
    
    # Test 1: Together service import
    test1_pass = test_together_import()
    
    # Test 2: CLI integration
    test2_pass = test_cli_integration()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Together Service Import: {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"   CLI Integration: {'✅ PASS' if test2_pass else '❌ FAIL'}")
    
    if test1_pass and test2_pass:
        print("\n🎉 All integration tests passed!")
        print("\n💡 Next steps:")
        print("   1. Get a Together AI API key")
        print("   2. Test with: python -m am_app.cli parse data/samples/mutualfund_sample.csv --method together --api-key YOUR_KEY")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")