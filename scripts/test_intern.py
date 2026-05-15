#!/usr/bin/env python
"""Test intern portfolio access."""
import urllib.request
import json

BASE_URL = "http://localhost:8000"

# Login
login_data = json.dumps({"username": "intern@local"}).encode('utf-8')
login_req = urllib.request.Request(
    f"{BASE_URL}/api/auth/login",
    data=login_data,
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(login_req, timeout=5) as response:
    token = json.loads(response.read().decode()).get('access_token')
    print("✓ Intern login successful")

# Test portfolio
portfolio_req = urllib.request.Request(
    f"{BASE_URL}/api/data/portfolio",
    headers={'Authorization': f'Bearer {token}'}
)

with urllib.request.urlopen(portfolio_req, timeout=5) as response:
    data = json.loads(response.read().decode())
    print(f"✓ Intern portfolio: ${data.get('total_portfolio_value', 0):,.2f}")
