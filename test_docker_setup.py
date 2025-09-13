#!/usr/bin/env python3
"""
Test Docker MongoDB Setup
Verifies that MongoDB is running and the service can connect
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to find external modules
sys.path.insert(0, str(Path(__file__).parent))

from am_persistence import create_mutual_fund_service


async def test_mongodb_connection():
    """Test MongoDB connection with different configurations"""
    
    print("🧪 Testing MongoDB Connection")
    print("=" * 35)
    
    # Test configurations
    test_configs = [
        {
            "name": "Default (localhost:27017)",
            "uri": "mongodb://localhost:27017",
            "db": "mutual_funds"
        },
        {
            "name": "With Docker credentials",
            "uri": "mongodb://admin:password123@localhost:27017",
            "db": "mutual_funds"
        }
    ]
    
    for config in test_configs:
        print(f"\n🔍 Testing: {config['name']}")
        print(f"   URI: {config['uri']}")
        
        try:
            service = create_mutual_fund_service(
                mongo_uri=config['uri'],
                db_name=config['db']
            )
            
            # Test connection by getting collection
            collection = service._get_collection()
            print(f"   ✅ Connection successful!")
            
            # Test basic operations
            portfolios = await service.list_portfolios(limit=1)
            print(f"   📊 Found {len(portfolios)} existing portfolio(s)")
            
            await service.close()
            print(f"   🔐 Connection closed")
            break
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    else:
        print("\n❌ All connection attempts failed!")
        print("💡 Make sure Docker is running: docker-compose up -d")
        return False
    
    print("\n✅ MongoDB connection test successful!")
    return True


def check_docker_status():
    """Check if Docker Compose services are running"""
    import subprocess
    
    print("🐳 Checking Docker Compose Status")
    print("=" * 35)
    
    try:
        result = subprocess.run(
            ["docker-compose", "ps"], 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            print("\n📋 Service Status:")
            print(result.stdout)
            
            # Check if MongoDB container is running
            if "am_parser_mongodb" in result.stdout and "Up" in result.stdout:
                print("✅ MongoDB container is running")
                return True
            else:
                print("❌ MongoDB container is not running")
                print("💡 Start with: docker-compose up -d")
                return False
        else:
            print("❌ Docker Compose not available or not in correct directory")
            return False
            
    except FileNotFoundError:
        print("❌ Docker Compose not found")
        print("💡 Install Docker Desktop: https://www.docker.com/products/docker-desktop")
        return False


async def main():
    """Main test function"""
    print("🚀 AM Parser - MongoDB Docker Test")
    print("=" * 40)
    
    # Check Docker status first
    docker_ok = check_docker_status()
    
    if not docker_ok:
        print("\n🛠️  To start MongoDB:")
        print("   docker-compose up -d")
        print("\n🌐 Web interface will be at:")
        print("   http://localhost:8081 (webadmin / webpass123)")
        return
    
    # Test MongoDB connection
    connection_ok = await test_mongodb_connection()
    
    if connection_ok:
        print("\n🎉 Setup Complete!")
        print("💡 Try saving a portfolio:")
        print("   python -m am_app save-portfolio --input data/mfextractedholdings/motilaloswalmf.json")
        print("\n🌐 View data in web interface:")
        print("   http://localhost:8081")


if __name__ == "__main__":
    asyncio.run(main())
