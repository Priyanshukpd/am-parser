"""
FastAPI REST API for Mutual Fund Portfolio Service
Provides HTTP endpoints for saving and retrieving mutual fund portfolio data
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import sys
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager

# Add parent directory to path to find external modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from am_persistence import create_mutual_fund_service, MutualFundService
from am_common.mutual_fund_models import MutualFundPortfolio, PortfolioSummary


# Global service instance
service_instance: Optional[MutualFundService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown"""
    global service_instance
    
    # Startup: Initialize service
    try:
        service_instance = create_mutual_fund_service(
            mongo_uri="mongodb://admin:password123@localhost:27017",
            db_name="mutual_funds"
        )
        print("✅ Connected to MongoDB")
        yield
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise
    finally:
        # Shutdown: Close service
        if service_instance:
            await service_instance.close()
            print("🔐 MongoDB connection closed")


# Create FastAPI app with lifecycle management
app = FastAPI(
    title="Mutual Fund Portfolio API",
    description="REST API for managing mutual fund portfolio data",
    version="1.0.0",
    lifespan=lifespan
)


def get_service() -> MutualFundService:
    """Dependency to get the service instance"""
    if service_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not available"
        )
    return service_instance


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Mutual Fund Portfolio API",
        "version": "1.0.0",
        "endpoints": {
            "save_portfolio": "POST /portfolios",
            "get_portfolio": "GET /portfolios/{portfolio_id}",
            "list_portfolios": "GET /portfolios",
            "search_portfolios": "GET /portfolios/search?fund_name=...",
            "get_holdings_by_isin": "GET /holdings/{isin_code}",
            "get_fund_statistics": "GET /funds/{fund_name}/statistics"
        }
    }


@app.post("/portfolios", response_model=dict, status_code=status.HTTP_201_CREATED)
async def save_portfolio(
    portfolio_data: dict,
    service: MutualFundService = Depends(get_service)
):
    """
    Save a mutual fund portfolio to the database
    
    Args:
        portfolio_data: JSON data containing mutual fund portfolio information
        
    Returns:
        Saved portfolio data with database ID
    """
    try:
        # Validate and create portfolio model
        portfolio = MutualFundPortfolio(**portfolio_data)
        
        # Save to database via service
        portfolio_id = await service.save_portfolio(portfolio)
        
        # Retrieve the saved portfolio to return complete data
        saved_portfolio = await service.get_portfolio_by_id(portfolio_id)
        
        if not saved_portfolio:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve saved portfolio"
            )
        
        return {
            "status": "success",
            "message": "Portfolio saved successfully",
            "data": {
                "id": portfolio_id,
                "mutual_fund_name": saved_portfolio.mutual_fund_name,
                "portfolio_date": saved_portfolio.portfolio_date,
                "total_holdings": saved_portfolio.total_holdings,
                "created_at": saved_portfolio.created_at.isoformat() if saved_portfolio.created_at else None,
                "updated_at": saved_portfolio.updated_at.isoformat() if saved_portfolio.updated_at else None
            },
            "portfolio": saved_portfolio.model_dump()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid portfolio data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save portfolio: {str(e)}"
        )


@app.get("/portfolios/{portfolio_id}", response_model=dict)
async def get_portfolio(
    portfolio_id: str,
    service: MutualFundService = Depends(get_service)
):
    """
    Get a specific portfolio by ID
    
    Args:
        portfolio_id: MongoDB ObjectId of the portfolio
        
    Returns:
        Portfolio data if found
    """
    try:
        portfolio = await service.get_portfolio_by_id(portfolio_id)
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio with ID {portfolio_id} not found"
            )
        
        return {
            "status": "success",
            "data": {
                "id": portfolio_id,
                "mutual_fund_name": portfolio.mutual_fund_name,
                "portfolio_date": portfolio.portfolio_date,
                "total_holdings": portfolio.total_holdings
            },
            "portfolio": portfolio.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve portfolio: {str(e)}"
        )


@app.get("/portfolios", response_model=dict)
async def list_portfolios(
    fund_name: Optional[str] = None,
    limit: int = 50,
    service: MutualFundService = Depends(get_service)
):
    """
    List all portfolios or filter by fund name
    
    Args:
        fund_name: Optional fund name to filter by
        limit: Maximum number of portfolios to return (default: 50)
        
    Returns:
        List of portfolio summaries
    """
    try:
        portfolios = await service.list_portfolios(fund_name=fund_name, limit=limit)
        
        return {
            "status": "success",
            "count": len(portfolios),
            "data": [
                {
                    "fund_name": p.fund_name,
                    "portfolio_date": p.portfolio_date,
                    "total_holdings": p.total_holdings,
                    "total_percentage": p.total_percentage,
                    "top_holdings_count": len(p.top_holdings)
                } for p in portfolios
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list portfolios: {str(e)}"
        )


@app.get("/portfolios/search", response_model=dict)
async def search_portfolios(
    fund_name: str,
    service: MutualFundService = Depends(get_service)
):
    """
    Search portfolios by fund name
    
    Args:
        fund_name: Fund name to search for
        
    Returns:
        List of matching portfolio summaries
    """
    try:
        portfolios = await service.list_portfolios(fund_name=fund_name)
        
        return {
            "status": "success",
            "query": fund_name,
            "count": len(portfolios),
            "data": [
                {
                    "fund_name": p.fund_name,
                    "portfolio_date": p.portfolio_date,
                    "total_holdings": p.total_holdings,
                    "total_percentage": p.total_percentage
                } for p in portfolios
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search portfolios: {str(e)}"
        )


@app.get("/holdings/{isin_code}", response_model=dict)
async def get_holdings_by_isin(
    isin_code: str,
    service: MutualFundService = Depends(get_service)
):
    """
    Get all holdings with specific ISIN code
    
    Args:
        isin_code: ISIN code to search for
        
    Returns:
        List of holdings with the specified ISIN
    """
    try:
        holdings = await service.get_holdings_by_isin(isin_code)
        
        return {
            "status": "success",
            "isin_code": isin_code,
            "count": len(holdings),
            "data": holdings
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get holdings: {str(e)}"
        )


@app.get("/funds/{fund_name}/statistics", response_model=dict)
async def get_fund_statistics(
    fund_name: str,
    service: MutualFundService = Depends(get_service)
):
    """
    Get statistics for a specific fund
    
    Args:
        fund_name: Name of the mutual fund
        
    Returns:
        Fund statistics
    """
    try:
        stats = await service.get_fund_statistics(fund_name)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No statistics found for fund: {fund_name}"
            )
        
        return {
            "status": "success",
            "fund_name": fund_name,
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fund statistics: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if app.debug else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", response_model=dict)
async def health_check(service: MutualFundService = Depends(get_service)):
    """Health check endpoint"""
    try:
        # Test database connection
        collection = service._get_collection()
        count = await collection.count_documents({})
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_portfolios": count
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )