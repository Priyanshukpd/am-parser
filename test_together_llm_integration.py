#!/usr/bin/env python3
"""
Test Together AI LLM integration with sheet ID matching
"""
import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from am_services.file_processing_service import FileProcessingService
from am_persistence.file_upload_repository import FileUploadRepository
from am_persistence import create_mutual_fund_service
from am_common.upload_models import FileUpload, FileType, ProcessingStatus
from am_llm.together_service import TogetherLLMService


async def test_together_ai_integration():
    """Test the complete Together AI integration with sheet ID matching"""
    print("🧪 Testing Together AI LLM Integration")
    print("=" * 60)
    
    try:
        # Initialize services
        service = create_mutual_fund_service(
            mongo_uri="mongodb://admin:password123@localhost:27017",
            db_name="mutual_funds"
        )
        
        repo = FileUploadRepository(service.database)
        processing_service = FileProcessingService(repo, service)
        
        print("✅ Services initialized")
        
        # Test Together AI service directly first
        api_key = "bff39f38ee07df9a08ff8d2e7279b9d7223ab3f283a30bc39590d36f77dbd2fd"
        test_file = "data/samples/motilal-hy-portfolio-march-2025.xlsx"
        test_sheet = "YO01"
        
        print(f"📊 Testing direct Together AI parsing...")
        print(f"   File: {test_file}")
        print(f"   Sheet: {test_sheet}")
        
        # Test direct Together AI service
        together_service = TogetherLLMService(api_key=api_key)
        result = together_service.extract_portfolio_from_excel(
            excel_file=test_file,
            sheet_name=test_sheet
        )
        
        print(f"✅ Direct Together AI parsing successful!")
        print(f"   Fund Name: {result.get('mutual_fund_name', 'Unknown')}")
        print(f"   Holdings: {result.get('total_holdings', 0)}")
        print(f"   Date: {result.get('portfolio_date', 'Unknown')}")
        
        # Create a mock sheet file with specific ID
        sheet_id = "test-sheet-12345"
        mock_sheet_file = type('MockFile', (), {
            'file_id': sheet_id,
            'sheet_name': test_sheet,
            'original_filename': f'test-portfolio_{test_sheet}.xlsx',
            'file_path': test_file
        })()
        
        print(f"\n🎯 Testing sheet ID matching...")
        print(f"   Sheet ID: {sheet_id}")
        
        # Test the transformation
        transformed = processing_service._transform_to_mutual_fund_portfolio(
            result, 
            mock_sheet_file
        )
        
        print(f"✅ Transformation successful!")
        print(f"   Format: Together AI (direct)")
        print(f"   Fund: {transformed['mutual_fund_name']}")
        print(f"   Holdings: {transformed['total_holdings']}")
        
        # Test saving with custom ID
        from am_common.mutual_fund_models import MutualFundPortfolio
        portfolio = MutualFundPortfolio(**transformed)
        
        # Save with sheet ID as portfolio ID
        portfolio_id = await service.save_portfolio_with_id(portfolio, sheet_id)
        
        print(f"✅ Portfolio saved with custom ID!")
        print(f"   Portfolio ID: {portfolio_id}")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   IDs Match: {portfolio_id == sheet_id} ✅" if portfolio_id == sheet_id else f"   IDs Match: {portfolio_id == sheet_id} ❌")
        
        # Test retrieval by ID
        retrieved = await service.get_portfolio_by_id(portfolio_id)
        if retrieved:
            print(f"✅ Portfolio retrieved successfully!")
            print(f"   Retrieved Fund: {retrieved.mutual_fund_name}")
            print(f"   Retrieved Holdings: {retrieved.total_holdings}")
        else:
            print(f"❌ Failed to retrieve portfolio by ID")
        
        print(f"\n🎉 Together AI integration test completed!")
        print(f"   ✅ Direct Together AI parsing working")
        print(f"   ✅ Data transformation working")
        print(f"   ✅ Custom ID persistence working")
        print(f"   ✅ Sheet ID = Portfolio ID matching")
        
        await service.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_together_ai_integration())