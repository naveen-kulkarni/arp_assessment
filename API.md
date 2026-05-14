# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/api/health` and `/api/auth/login`) require JWT authentication:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST `/api/auth/login`
Login user and get JWT token.

**Request:**
```json
{
  "username": "analyst@local"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "username": "analyst@local",
    "role": "analyst",
    "email": "analyst@local"
  }
}
```

**Status:** 200 OK, 404 Not Found

---

#### POST `/api/auth/verify`
Verify JWT token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "valid": true,
  "user": "analyst@local"
}
```

**Status:** 200 OK, 401 Unauthorized

---

### Data Endpoints

#### GET `/api/data/portfolio`
Get portfolio holdings and exposure analysis.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "exposures": [
    {
      "symbol": "AAPL",
      "quantity": 100.5,
      "current_price": 150.25,
      "position_value": 15100.13,
      "exposure_percentage": 25.34,
      "asset_class": "stocks"
    }
  ],
  "overexposed_assets": [
    {
      "symbol": "BTC",
      "exposure_percentage": 35.2
    }
  ]
}
```

**Status:** 200 OK, 401 Unauthorized, 403 Forbidden

---

#### GET `/api/data/trades`
Get recent trades (last 7 days).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "trades": [
    {
      "id": 1,
      "symbol": "AAPL",
      "type": "buy",
      "quantity": 50.0,
      "price": 145.0,
      "total": 7250.0,
      "date": "2024-05-10T10:30:00",
      "status": "completed",
      "risk_score": 42
    }
  ],
  "total_trades": 15
}
```

**Status:** 200 OK, 401 Unauthorized, 403 Forbidden

---

#### GET `/api/data/risk-alerts`
Get active risk alerts.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "alerts": [
    {
      "type": "flagged_trade",
      "symbol": "MSFT",
      "reason": "High volatility",
      "risk_score": 85,
      "severity": "high"
    },
    {
      "type": "overexposure",
      "symbol": "BTC",
      "exposure_percent": 35.5,
      "severity": "medium"
    }
  ],
  "total_alerts": 2,
  "high_severity": 1
}
```

**Status:** 200 OK, 401 Unauthorized, 403 Forbidden

---

### AI Agent

#### POST `/api/agent/query`
Query the AI agent.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "question": "What are our top holdings?"
}
```

**Response:**
```json
{
  "question": "What are our top holdings?",
  "answer": "Based on the data analysis...",
  "summary": "Our top holdings are AAPL (25%) and MSFT (18%)",
  "tools_used": ["get_asset_exposure"],
  "data": {
    "get_asset_exposure": {
      "exposures": [...],
      "overexposed_assets": [...]
    }
  }
}
```

**Status:** 200 OK, 401 Unauthorized, 403 Forbidden

**Access Control:** Different tools available based on user role:
- analyst: portfolio, market data
- risk: full access
- manager: summary only
- intern: summary only

---

### Audit Logs

#### GET `/api/audit/logs`
Get audit trail of AI queries (manager only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "user": "analyst@local",
      "role": "analyst",
      "question": "What are our top holdings?",
      "tools_called": ["get_asset_exposure"],
      "allowed": true,
      "denial_reason": null,
      "timestamp": "2024-05-14T10:30:00"
    },
    {
      "id": 2,
      "user": "intern@local",
      "role": "intern",
      "question": "Get recent trades",
      "tools_called": ["get_recent_trades"],
      "allowed": false,
      "denial_reason": "User does not have access to: get_recent_trades",
      "timestamp": "2024-05-14T10:31:00"
    }
  ]
}
```

**Status:** 200 OK, 401 Unauthorized, 403 Forbidden (non-managers)

---

### Health & Setup

#### GET `/api/health`
Health check.

**Response:**
```json
{
  "status": "healthy"
}
```

**Status:** 200 OK

---

#### POST `/api/setup/init-data`
Initialize mock data.

**Response:**
```json
{
  "message": "Mock data initialized"
}
```

**Status:** 200 OK

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Question required"
}
```

### 401 Unauthorized
```json
{
  "error": "Authorization required"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied"
}
```

### 404 Not Found
```json
{
  "error": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Role-Based Access

### Analyst
- Can access portfolio and market data
- Cannot access trades or risk details
- Cannot view audit logs

### Risk
- Full access to all data
- Can view portfolio, trades, alerts
- Cannot view audit logs

### Manager
- Can only view summaries
- Can view audit logs
- Cannot access detailed trading data

### Intern
- Limited access
- Can only view portfolio summary
- Cannot access any other data

---

## Example Usage

### 1. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst@local"}'
```

### 2. Get Portfolio
```bash
curl -X GET http://localhost:8000/api/data/portfolio \
  -H "Authorization: Bearer <token>"
```

### 3. Query Agent
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are our top holdings?"}'
```

### 4. Get Audit Logs (Manager only)
```bash
curl -X GET http://localhost:8000/api/audit/logs \
  -H "Authorization: Bearer <manager_token>"
```

---

## Rate Limiting

Currently not implemented. To add in production:
- Implement Flask-Limiter
- Set limits per endpoint and role
- Track by username or IP

---

## CORS

CORS is enabled for development. Update for production:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## Future Enhancements

- [ ] Pagination for large datasets
- [ ] Filtering and sorting
- [ ] GraphQL API
- [ ] WebSocket for real-time updates
- [ ] Rate limiting
- [ ] API versioning
- [ ] OpenAPI/Swagger documentation
