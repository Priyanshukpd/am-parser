#!/usr/bin/env python3
"""
AM App Demo - Showcase unified parsing capabilities
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from am_app import AMApp, parse_file

def demo():
    print("🚀 AM App Demo - Unified Mutual Fund Parser")
    print("=" * 50)
    
    sample_file = "data/samples/mutualfund_sample.csv"
    
    # Check if sample file exists
    if not Path(sample_file).exists():
        print(f"❌ Sample file not found: {sample_file}")
        return
    
    print(f"📁 Using sample file: {sample_file}")
    
    # Demo 1: Simple parsing
    print("\n1️⃣  Simple Manual Parsing:")
    print("-" * 30)
    result = parse_file(sample_file, method="manual")
    print(f"✅ Found {len(result['holdings'])} holdings")
    print(f"💰 Total value: ${result['totals']['mkt_value']:,.2f}")
    
    # Demo 2: With preview
    print("\n2️⃣  Manual Parsing with Preview:")
    print("-" * 35)
    result_preview = parse_file(sample_file, method="manual", show_preview=True)
    if "debug" in result_preview:
        print(f"🔍 Detected columns: {', '.join(result_preview['debug']['columns'])}")
    
    # Demo 3: Analysis
    print("\n3️⃣  File Analysis:")
    print("-" * 20)
    from am_services import load_tabular
    df = load_tabular(sample_file)
    print(f"📊 File contains {len(df)} rows and {len(df.columns)} columns")
    print(f"🏷️  Columns: {list(df.columns)}")
    
    # Demo 4: Programmatic usage with app instance
    print("\n4️⃣  Using AMApp Class:")
    print("-" * 25)
    app = AMApp()
    
    # Save to file
    output_file = "demo_result.json"
    result_saved = app.parse_file(
        sample_file, 
        method="manual", 
        output_file=output_file
    )
    print(f"📄 Result saved to {output_file}")
    
    print("\n✨ Demo complete! Try these commands:")
    print("   python -m am_app --help")
    print("   python -m am_app analyze --input data/samples/mutualfund_sample.csv")
    print("   python -m am_app parse --input data/samples/mutualfund_sample.csv --method manual --show-preview")

if __name__ == "__main__":
    demo()
