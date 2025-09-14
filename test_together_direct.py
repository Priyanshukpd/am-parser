#!/usr/bin/env python3
"""
Test Together AI service directly to debug the parsing issue
"""

import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from am_llm.together_service import TogetherLLMService

def test_together_ai():
    """Test Together AI service directly"""
    
    print("🧪 Testing Together AI Service Directly")
    print("=" * 50)
    
    # Initialize service
    api_key = "bff39f38ee07df9a08ff8d2e7279b9d7223ab3f283a30bc39590d36f77dbd2fd"
    service = TogetherLLMService(api_key=api_key)
    
    # Test file
    excel_file = "data/samples/motilal-hy-portfolio-march-2025.xlsx"
    sheet_name = "YO03"  # The problematic sheet
    
    print(f"📁 File: {excel_file}")
    print(f"📋 Sheet: {sheet_name}")
    
    try:
        # Step 1: Read sheet
        print("\n📖 Step 1: Reading Excel sheet...")
        table_text = service.read_sheet_as_text(excel_file, sheet_name)
        
        if table_text:
            print(f"✅ Sheet read successfully")
            print(f"📄 Text length: {len(table_text)} characters")
            print(f"📝 First 500 chars: {table_text[:500]}")
            
            # Step 2: Extract via Together AI
            print("\n🤖 Step 2: Extracting via Together AI...")
            result = service.extract_json_from_table(table_text, sheet_name)
            
            if result:
                print("✅ Together AI extraction successful!")
                print(f"📊 Fund: {result.get('mutual_fund_name', 'Unknown')}")
                print(f"📅 Date: {result.get('portfolio_date', 'Unknown')}")
                print(f"🔢 Holdings: {result.get('total_holdings', 0)}")
                
                # Show first few holdings
                holdings = result.get('portfolio_holdings', [])
                if holdings:
                    print(f"\n📋 Sample holdings:")
                    for i, holding in enumerate(holdings[:3]):
                        print(f"  {i+1}. {holding.get('name_of_instrument', 'Unknown')}: {holding.get('percentage_to_nav', '0%')}")
                    if len(holdings) > 3:
                        print(f"  ... and {len(holdings) - 3} more")
                        
                return result
            else:
                print("❌ Together AI extraction failed")
                return None
                
        else:
            print("❌ Failed to read sheet")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_together_ai()
    
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")