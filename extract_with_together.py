#!/usr/bin/env python3
"""
Standalone Together AI Excel Extractor
Extract mutual fund portfolio data from Excel files using Together AI
"""

import pandas as pd
import json
import re
from pathlib import Path
from typing import Optional
from together import Together

# -------------------------------
# 1. Configuration
# -------------------------------
EXCEL_FILE = "data/samples/c45b0-copy-of-motilal-hy-portfolio-march-2025.xlsx"
SHEET_NAME = "YO17"  # Change this to any sheet: YO01, YO02, YO58, etc.
TOGETHER_API_KEY = "bff39f38ee07df9a08ff8d2e7279b9d7223ab3f283a30bc39590d36f77dbd2fd"

# Initialize Together client
client = Together(api_key=TOGETHER_API_KEY)

# -------------------------------
# 2. Read & Clean One Sheet
# -------------------------------
def read_sheet_as_text(file_path: str, sheet_name: str) -> Optional[str]:
    """Read Excel sheet and convert to clean text format"""
    try:
        print(f"📄 Reading sheet '{sheet_name}' from {file_path}...")
        
        # Read Excel with header detection
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

        # Drop completely empty rows/columns
        df.dropna(how='all', axis=1, inplace=True)
        df.dropna(how='all', inplace=True)
        
        print(f"📊 Sheet dimensions: {df.shape[0]} rows x {df.shape[1]} columns")

        # Convert to clean markdown-style table
        return df.to_markdown(index=False) if hasattr(df, 'to_markdown') else str(df)
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")
        return None

# -------------------------------
# 3. Extract JSON from LLM Response
# -------------------------------
def extract_json_from_response(text: str) -> Optional[str]:
    """
    Extract JSON content from LLM response that might contain extra text
    Handles cases where LLM doesn't return pure JSON
    """
    # Remove any code block markers
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = text.strip()
    
    # Find JSON object boundaries
    brace_count = 0
    start_idx = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx != -1:
                # Found complete JSON object
                candidate = text[start_idx:i+1]
                try:
                    # Test if it's valid JSON
                    json.loads(candidate)
                    print(f"✅ Found valid JSON object ({len(candidate)} characters)")
                    return candidate
                except json.JSONDecodeError:
                    print(f"⚠️  Invalid JSON found, continuing search...")
                    continue
    
    # If we can't find a complete JSON, try other patterns
    patterns = [
        r'\{.*\}',  # Simple JSON object
        r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
        r'```\s*(\{.*?\})\s*```',  # JSON in generic code blocks
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            json_str = matches[0] if isinstance(matches[0], str) else matches[0]
            try:
                # Test if it's valid JSON
                json.loads(json_str)
                print(f"✅ Pattern match found valid JSON ({len(json_str)} characters)")
                return json_str
            except json.JSONDecodeError:
                continue
    
    print(f"❌ No valid JSON found, returning raw text for debugging")
    return text

# -------------------------------
# 4. Prompt LLM via Together to Extract JSON
# -------------------------------
def extract_json_from_table(table_text: str, sheet_name: str) -> str:
    """Extract portfolio JSON from table text using Together AI"""
    prompt = f"""
You are a financial data parser. Extract **ALL** stock holdings from the table below.

Rules:
- Return ONLY a JSON object with:
  - mutual_fund_name: string
  - portfolio_date: "March 2025"
  - total_holdings: number
  - portfolio_holdings: list of all stocks with:
      - name_of_instrument (string)
      - isin_code (string)
      - percentage_to_nav (string with % sign)
- DO NOT summarize, skip, or truncate.
- Extract **every single stock** in the table.
- If quantity or value has commas (e.g., 457,329), convert to number: 457329.
- Make sure you list all stocks in portfolio_holdings array
- total_holdings should match the count of items in portfolio_holdings array

Here is the equity portfolio from sheet {sheet_name}:
{table_text}

Return the JSON object only.
"""

    print(f"📝 Prompt length: {len(prompt)} characters")
    
    try:
        response = client.chat.completions.create(
            # model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            # model="deepseek-ai/DeepSeek-V3.1",
            model="openai/gpt-oss-20b",
            # model="deepseek-ai/DeepSeek-R1-0528-tput",
            # model="google/gemma-3n-E4B-it",
            messages=[
                {"role": "system", "content": "You are a precise financial data extractor. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50000
        )

        raw_output = response.choices[0].message.content.strip()
        print(f"📄 Response length: {len(raw_output)} characters")
        
        return raw_output

    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        raise

# -------------------------------
# 5. Main Execution
# -------------------------------
def main():
    """Main execution function"""
    print(f"🚀 Starting Together AI extraction from {EXCEL_FILE}")
    print(f"📋 Target sheet: {SHEET_NAME}")
    print("=" * 60)
    
    # Step 1: Read Excel sheet
    table_text = read_sheet_as_text(EXCEL_FILE, SHEET_NAME)
    if not table_text:
        print("❌ Failed to read or parse the sheet.")
        return

    # Step 2: Extract JSON via LLM
    print("\n🧠 Sending to LLM for JSON extraction...")
    try:
        raw_output = extract_json_from_table(table_text, SHEET_NAME)
        
        # Step 3: Clean and parse JSON
        print("\n🔧 Processing LLM response...")
        clean_json = extract_json_from_response(raw_output)
        
        try:
            parsed_json = json.loads(clean_json)
            print("✅ Successfully extracted and parsed JSON!")
            
            # Display summary
            print(f"\n📊 Extraction Summary:")
            print(f"   Fund: {parsed_json.get('mutual_fund_name', 'Unknown')}")
            print(f"   Date: {parsed_json.get('portfolio_date', 'Unknown')}")
            print(f"   Holdings: {parsed_json.get('total_holdings', 0)}")
            print(f"   Actual holdings count: {len(parsed_json.get('portfolio_holdings', []))}")
            
            # Save to file
            output_file = f"{SHEET_NAME}_extracted.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved to {output_file}")
            
            # Pretty print first few holdings
            print(f"\n🔍 Sample holdings:")
            for i, holding in enumerate(parsed_json.get('portfolio_holdings', [])[:5], 1):
                print(f"   {i}. {holding.get('name_of_instrument', 'Unknown')} ({holding.get('percentage_to_nav', 'N/A')})")
            
            if len(parsed_json.get('portfolio_holdings', [])) > 5:
                print(f"   ... and {len(parsed_json.get('portfolio_holdings', [])) - 5} more")
            
        except json.JSONDecodeError as e:
            print(f"⚠️  LLM did not return valid JSON. Error: {e}")
            print("📝 Saving raw output for debugging...")
            
            # Save raw output for debugging
            debug_file = f"{SHEET_NAME}_raw_output.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(raw_output)
            print(f"🐛 Raw output saved to {debug_file}")
            
            # Save cleaned attempt too
            clean_file = f"{SHEET_NAME}_cleaned_attempt.txt"
            with open(clean_file, 'w', encoding='utf-8') as f:
                f.write(clean_json)
            print(f"🧹 Cleaned attempt saved to {clean_file}")
            
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")

if __name__ == "__main__":
    main()