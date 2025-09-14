#!/usr/bin/env python3
"""
Check current portfolios in database
"""
import requests

def check_portfolios():
    try:
        response = requests.get('http://127.0.0.1:8000/portfolios/')
        portfolios = response.json()
        
        print(f"Found {len(portfolios)} portfolios:")
        print("=" * 50)
        
        for i, p in enumerate(portfolios):
            if i >= len(portfolios) - 4:  # Show last 4
                print(f"Fund: {p.get('mutual_fund_name', 'Unknown')}")
                print(f"Date: {p.get('portfolio_date', 'Unknown')}")
                print(f"Holdings: {p.get('total_holdings', 0)}")
                print(f"ID: {p.get('_id', 'Unknown')}")
                print("-" * 30)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_portfolios()