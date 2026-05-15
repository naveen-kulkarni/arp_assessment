#!/usr/bin/env python
"""Quick test for manager portfolio access."""
import urllib.request
import json

BASE_URL = "http://localhost:8000"

# Login
login_data = json.dumps({"username": "manager@local"}).encode('utf-8')
login_req = urllib.request.Request(
    f"{BASE_URL}/api/auth/login",
    data=login_data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(login_req, timeout=5) as response:
        login_result = json.loads(response.read().decode('utf-8'))
        token = login_result.get("access_token")
        print(f"✓ Manager login successful")
        print(f"  Token: {token[:20]}...")
    
    # Test portfolio
    portfolio_req = urllib.request.Request(
        f"{BASE_URL}/api/data/portfolio",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    with urllib.request.urlopen(portfolio_req, timeout=5) as response:
        portfolio_data = json.loads(response.read().decode('utf-8'))
        print(f"\n✓ Portfolio fetch successful")
        print(f"  Portfolio Value: ${portfolio_data.get('total_portfolio_value', 0):,.2f}")
        print(f"  Holdings: {portfolio_data.get('holdings_count', 0)}")
        print(f"  Allocation: {portfolio_data.get('allocation_percentage', {})}")

except urllib.error.HTTPError as e:
    error = json.loads(e.read().decode('utf-8'))
    print(f"✗ Error: {e.code}")
    print(f"  {error}")
except Exception as e:
    print(f"✗ Error: {e}")
