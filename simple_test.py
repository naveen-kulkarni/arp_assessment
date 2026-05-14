#!/usr/bin/env python
"""Simple test for portfolio access."""
import urllib.request
import json

def test_endpoint():
    """Test the portfolio endpoint directly."""
    try:
        # Test health endpoint first
        with urllib.request.urlopen("http://localhost:8000/api/health", timeout=5) as response:
            health = json.loads(response.read().decode('utf-8'))
            print("✓ Backend is running")
            print(f"  Health: {health}")
        
        # Test login for manager
        login_data = json.dumps({"username": "manager@local"}).encode('utf-8')
        login_req = urllib.request.Request(
            "http://localhost:8000/api/auth/login",
            data=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(login_req, timeout=5) as response:
            login_result = json.loads(response.read().decode('utf-8'))
            token = login_result.get("access_token")
            print("✓ Manager login successful")
            print(f"  Token: {token[:20]}...")
        
        # Test portfolio endpoint
        portfolio_req = urllib.request.Request(
            "http://localhost:8000/api/data/portfolio",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        try:
            with urllib.request.urlopen(portfolio_req, timeout=5) as response:
                portfolio_data = json.loads(response.read().decode('utf-8'))
                print("✓ Portfolio fetch successful")
                print(f"  Data keys: {list(portfolio_data.keys())}")
                
                if "total_portfolio_value" in portfolio_data:
                    print(f"  Portfolio Value: ${portfolio_data.get('total_portfolio_value', 'N/A'):,.2f}")
        
        except urllib.error.HTTPError as e:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"✗ Portfolio fetch failed: {e.code}")
            print(f"  Error: {error_data}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_endpoint()