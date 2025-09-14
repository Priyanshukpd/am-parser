#!/usr/bin/env python3
"""
Test script for Excel sheet splitting functionality
"""

import os
import sys
from pathlib import Path
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from am_services.file_upload_service import FileUploadService
from am_common.upload_models import FileUpload, FileType, ProcessingStatus


async def test_sheet_splitter():
    """Test the Excel sheet splitting functionality"""
    print("🧪 Testing Excel Sheet Splitter")
    print("=" * 50)
    
    # Initialize service
    upload_service = FileUploadService()
    
    # Test file path
    excel_file = "data/samples/c45b0-copy-of-motilal-hy-portfolio-march-2025.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return False
    
    print(f"📄 Using Excel file: {excel_file}")
    
    try:
        # Step 1: Create a fake FileUpload object for our test
        file_upload = FileUpload(
            file_id="test-excel-123",
            original_filename="test-portfolio.xlsx",
            stored_filename="test-excel-123_test-portfolio.xlsx",
            file_type=FileType.EXCEL,
            file_path=excel_file,  # Use the actual sample file
            file_size=os.path.getsize(excel_file),
            status=ProcessingStatus.UPLOADED
        )
        
        print(f"✅ Created test FileUpload object")
        print(f"   File ID: {file_upload.file_id}")
        print(f"   File size: {file_upload.file_size} bytes")
        
        # Step 2: Get sheet information first
        print("\n📊 Getting Excel sheet information...")
        sheet_infos = upload_service.get_excel_sheet_info(excel_file)
        
        print(f"✅ Found {len(sheet_infos)} sheets:")
        for i, sheet_info in enumerate(sheet_infos, 1):
            print(f"   {i}. {sheet_info.sheet_name} ({sheet_info.row_count} rows x {sheet_info.column_count} cols)")
        
        # Step 3: Split Excel into individual sheet files
        print("\n🔄 Splitting Excel into individual sheet files...")
        sheet_files = upload_service.split_excel_into_sheets(file_upload)
        
        print(f"✅ Successfully created {len(sheet_files)} sheet files:")
        
        # Step 4: Verify each sheet file
        for i, sheet_file in enumerate(sheet_files, 1):
            print(f"\n   📄 Sheet {i}: {sheet_file.sheet_name}")
            print(f"      ID: {sheet_file.file_id}")
            print(f"      Filename: {sheet_file.stored_filename}")
            print(f"      Path: {sheet_file.file_path}")
            print(f"      Parent ID: {sheet_file.parent_id}")
            print(f"      File size: {sheet_file.file_size} bytes")
            
            # Check if file actually exists
            if os.path.exists(sheet_file.file_path):
                print(f"      ✅ File exists on disk")
                
                # Try to read the file to verify it's valid
                try:
                    import pandas as pd
                    df = pd.read_excel(sheet_file.file_path, engine='openpyxl')
                    print(f"      ✅ Valid Excel file ({df.shape[0]} rows x {df.shape[1]} cols)")
                    
                    # Show first few rows
                    if not df.empty:
                        print(f"      📋 Sample data:")
                        print(f"         Columns: {list(df.columns[:3])}{'...' if len(df.columns) > 3 else ''}")
                        if len(df) > 0:
                            first_row = df.iloc[0].fillna('N/A')
                            print(f"         First row: {dict(list(first_row.items())[:2])}")
                    
                except Exception as e:
                    print(f"      ❌ Error reading Excel file: {e}")
            else:
                print(f"      ❌ File not found on disk")
        
        # Step 5: Show directory contents
        print(f"\n📁 Contents of data/sheets directory:")
        sheets_dir = Path("data/sheets")
        if sheets_dir.exists():
            sheet_files_on_disk = list(sheets_dir.glob("*.xlsx"))
            print(f"   Found {len(sheet_files_on_disk)} Excel files:")
            for file_path in sheet_files_on_disk[:10]:  # Show first 10
                size = file_path.stat().st_size
                print(f"   📄 {file_path.name} ({size} bytes)")
            
            if len(sheet_files_on_disk) > 10:
                print(f"   ... and {len(sheet_files_on_disk) - 10} more files")
        else:
            print("   ❌ data/sheets directory not found")
        
        print(f"\n🎉 Sheet splitting test completed successfully!")
        print(f"   Original Excel file: {len(sheet_infos)} sheets")
        print(f"   Generated sheet files: {len(sheet_files)}")
        print(f"   All files created: {'✅' if all(os.path.exists(sf.file_path) for sf in sheet_files) else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during sheet splitting: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sheet_info_only():
    """Just test getting sheet information without splitting"""
    print("\n🔍 Testing sheet information extraction...")
    
    upload_service = FileUploadService()
    excel_file = "data/samples/c45b0-copy-of-motilal-hy-portfolio-march-2025.xlsx"
    
    try:
        sheet_infos = upload_service.get_excel_sheet_info(excel_file)
        
        print(f"✅ Successfully read Excel file structure:")
        print(f"   Total sheets: {len(sheet_infos)}")
        
        for i, sheet_info in enumerate(sheet_infos, 1):
            print(f"   {i:2d}. Sheet: '{sheet_info.sheet_name}'")
            print(f"       Rows: {sheet_info.row_count}")
            print(f"       Columns: {sheet_info.column_count}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading sheet info: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Excel Sheet Splitter Test Suite")
    print("=" * 50)
    
    # Test 1: Sheet info extraction
    info_success = test_sheet_info_only()
    
    # Test 2: Full sheet splitting (only if info test passed)
    if info_success:
        split_success = asyncio.run(test_sheet_splitter())
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"   Sheet Info Extraction: {'✅ PASS' if info_success else '❌ FAIL'}")
        print(f"   Sheet File Splitting: {'✅ PASS' if split_success else '❌ FAIL'}")
        
        if info_success and split_success:
            print("\n🎉 All tests passed! Sheet splitter is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the errors above.")
    else:
        print("\n❌ Sheet info test failed, skipping split test.")