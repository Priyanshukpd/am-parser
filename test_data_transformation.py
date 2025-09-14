#!/usr/bin/env python3
"""
Quick test of the fixed data transformation
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from am_services.file_processing_service import FileProcessingService
from am_persistence.file_upload_repository import FileUploadRepository
from am_persistence import create_mutual_fund_service
from am_common.upload_models import FileUpload, FileType, ProcessingStatus


async def test_data_transformation():
    """Test the data transformation fix"""
    print("🧪 Testing Data Transformation Fix")
    print("=" * 50)
    
    try:
        # Initialize services
        service = create_mutual_fund_service(
            mongo_uri="mongodb://admin:password123@localhost:27017",
            db_name="mutual_funds"
        )
        
        repo = FileUploadRepository(service.database)
        processing_service = FileProcessingService(repo, service)
        
        print("✅ Services initialized")
        
        # Create a mock parser result in Portfolio format
        mock_parser_result = {
            "fund": {
                "name": "Test Mutual Fund",
                "report_date": "2025-03-31",
                "currency": "INR"
            },
            "holdings": [
                {
                    "name": "Test Company 1",
                    "isin": "INE123A01000",
                    "weight": 5.25,
                    "mkt_value": 100000
                },
                {
                    "name": "Test Company 2", 
                    "isin": "INE456B01000",
                    "weight": 3.75,
                    "mkt_value": 75000
                }
            ],
            "totals": {
                "mkt_value": 175000,
                "weight": 9.0
            },
            "meta": {}
        }
        
        # Create a mock sheet file
        mock_sheet_file = type('MockFile', (), {
            'sheet_name': 'YO01',
            'original_filename': 'test-portfolio_YO01.xlsx'
        })()
        
        print("📊 Testing transformation with mock data...")
        
        # Test the transformation
        transformed = processing_service._transform_to_mutual_fund_portfolio(
            mock_parser_result, 
            mock_sheet_file
        )
        
        print("✅ Transformation successful!")
        print(f"📋 Transformed data:")
        print(f"   Mutual Fund Name: {transformed['mutual_fund_name']}")
        print(f"   Portfolio Date: {transformed['portfolio_date']}")
        print(f"   Total Holdings: {transformed['total_holdings']}")
        print(f"   Portfolio Holdings Count: {len(transformed['portfolio_holdings'])}")
        
        if transformed['portfolio_holdings']:
            print(f"   Sample Holding:")
            holding = transformed['portfolio_holdings'][0]
            print(f"     Name: {holding['name_of_instrument']}")
            print(f"     ISIN: {holding['isin_code']}")
            print(f"     Weight: {holding['percentage_to_nav']}")
        
        # Test creating MutualFundPortfolio object
        from am_common.mutual_fund_models import MutualFundPortfolio
        portfolio = MutualFundPortfolio(**transformed)
        print("✅ MutualFundPortfolio object created successfully!")
        
        print(f"\n🎉 Data transformation test passed!")
        print(f"   ✅ Parser result → API format transformation working")
        print(f"   ✅ Pydantic validation passing")
        print(f"   ✅ Ready for complete workflow testing")
        
        await service.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_data_transformation())