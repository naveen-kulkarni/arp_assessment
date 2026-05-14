#!/usr/bin/env python
"""Test manager and intern portfolio access using urllib."""
import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:8000"

def test_role(username):
    """Test portfolio access for a role."""
    print(f"\n{'='*60}")
    print(f"Testing role: {username}")
    print(f"{'='*60}")
    
    try:
        # Login
        login_data = json.dumps({"username": username}).encode('utf-8')
        login_req = urllib.request.Request(
            f"{BASE_URL}/api/auth/login",
            data=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(login_req, timeout=5) as response:
            login_result = json.loads(response.read().decode('utf-8'))
            token = login_result.get("access_token")
            user_role = login_result.get("user", {}).get("role")
            
            print(f"✓ Login successful")
            print(f"  Role: {user_role}")
            print(f"  Token: {token[:20]}...")
        
        # Test portfolio endpoint
        portfolio_req = urllib.request.Request(
            f"{BASE_URL}/api/data/portfolio",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        try:
            with urllib.request.urlopen(portfolio_req, timeout=5) as response:
                portfolio_data = json.loads(response.read().decode('utf-8'))
                print(f"\n✓ Portfolio fetch successful")
                
                # Show summary data
                if "total_portfolio_value" in portfolio_data:
                    print(f"  Portfolio Value: ${portfolio_data.get('total_portfolio_value', 'N/A'):,.2f}")
                    print(f"  Holdings Count: {portfolio_data.get('holdings_count', 'N/A')}")
                    
                    if "allocation_percentage" in portfolio_data:
                        print(f"  Asset Allocation: {portfolio_data.get('allocation_percentage')}")
                
                # Show exposure data if available
                if "exposures" in portfolio_data:
                    exposures = portfolio_data.get("exposures", [])
                    print(f"  Exposures: {len(exposures)} holdings")
                    for exp in exposures[:3]:
                        print(f"    - {exp['symbol']}: {exp['exposure_percentage']:.1f}%")
        
        except urllib.error.HTTPError as e:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"\n✗ Portfolio fetch failed: {e.code}")
            print(f"  Error: {error_data}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Testing ARP Assessment Platform - Portfolio Access by Role")
    print(f"Base URL: {BASE_URL}")
    
    # Test each role
    test_role("analyst@local")
    test_role("risk@local")
    test_role("manager@local")
    test_role("intern@local")
    
    print(f"\n{'='*60}")
    print("Test complete!")
