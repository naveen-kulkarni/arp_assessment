# Quick Start Guide

Get the ARP Assessment Platform running in minutes.

## Option 1: Docker (Recommended - Easiest)

### Requirements
- Docker and Docker Compose installed

### Steps

1. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

2. **Start services**
   ```bash
   docker compose up
   ```

3. **Initialize data** (in another terminal)
   ```bash
   docker compose exec backend python manage.py seed
   ```

4. **Open in browser**
   - Dashboard: http://localhost:8501
   - API: http://localhost:8000

### Stop Services
```bash
docker compose down
```

---

## Option 2: Local Python (Windows)

### Requirements
- Python 3.9+
- Git

### Steps

1. **Clone & Enter Directory**
   ```bash
   cd arp_assessment
   ```

2. **Run Setup Script**
   ```bash
   run_local.bat
   ```

3. **Open in Browser**
   - Dashboard: http://localhost:8501
   - API: http://localhost:8000

The script will:
- Create virtual environment
- Install dependencies
- Initialize database
- Start backend API
- Start Streamlit dashboard

---

## Option 3: Local Python (Linux/macOS)

### Requirements
- Python 3.9+
- Git
- Bash

### Steps

1. **Clone & Enter Directory**
   ```bash
   cd arp_assessment
   ```

2. **Run Setup Script**
   ```bash
   chmod +x run_local.sh
   ./run_local.sh
   ```

3. **Open in Browser**
   - Dashboard: http://localhost:8501
   - API: http://localhost:8000

---

## Login

1. Open dashboard: http://localhost:8501
2. Select a user role:
   - **analyst@local** - Portfolio & market data
   - **risk@local** - Full access (trades, risk, alerts)
   - **manager@local** - Summary & audit logs
   - **intern@local** - Limited access

3. Click "Login"

---

## Try These Features

### 1. View Portfolio
- Navigate to "Portfolio" tab
- See holdings and allocation
- Check for overexposed assets

### 2. View Recent Trades
- Navigate to "Trades" tab
- See last 7 days of trading
- Risk scores shown (color-coded)

### 3. Monitor Risks
- Navigate to "Alerts" tab
- See active risk alerts
- Review flagged trades

### 4. Chat with AI Agent
- Navigate to "AI Agent" tab
- Try questions like:
  - "What are our top holdings?"
  - "Which assets are overexposed?"
  - "What is our portfolio value?"

### 5. View Audit Logs (Manager Only)
- Login as manager@local
- Navigate to "Audit Logs"
- See all queries and access decisions

---

## API Testing

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst@local"}'
```

### Get Portfolio
```bash
curl -X GET http://localhost:8000/api/data/portfolio \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Query AI Agent
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are our top holdings?"}'
```

---

## Troubleshooting

### Port Already in Use
If port 8000 or 8501 is in use:

**Docker:**
```bash
docker compose down
docker compose up  # Will use different ports if needed
```

**Local:**
Update ports in `.env`:
```bash
API_PORT=8001
STREAMLIT_PORT=8502
```

### Database Error
Delete and recreate:

**Docker:**
```bash
docker compose exec backend rm data/arp_assessment.db
docker compose restart backend
```

**Local:**
```bash
rm arp_assessment.db
python manage.py init
python manage.py seed
```

### Module Not Found
Make sure dependencies are installed:

**Docker:**
```bash
docker compose up --build  # Rebuild image
```

**Local:**
```bash
pip install -r requirements.txt
```

---

## Command Reference

### Local Python

```bash
# Initialize database
python manage.py init

# Generate mock data
python manage.py seed

# Reset database
python manage.py reset

# Run tests
pytest

# Run with coverage
pytest --cov=src

# Validate setup
python validate.py
```

### Docker

```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Initialize data
docker compose exec backend python manage.py seed

# Run tests in container
docker compose exec backend pytest
```

---

## Default Credentials

No passwords needed - just select a user:

| Username | Role | Permissions |
|----------|------|------------|
| analyst@local | Analyst | Portfolio + Market Data |
| risk@local | Risk Officer | Full Access |
| manager@local | Manager | Summary + Audit |
| intern@local | Intern | Limited |

---

## What's Included

✅ **Backend API** - Flask RESTful API
✅ **Dashboard** - Streamlit web UI
✅ **Database** - SQLite with sample data
✅ **AI Agents** - Natural language queries
✅ **RBAC** - 4 roles with different permissions
✅ **Audit Logs** - All interactions logged
✅ **Docker** - Full containerization
✅ **Tests** - Unit & integration tests
✅ **Docs** - Complete documentation

---

## Next Steps

1. Explore the dashboard
2. Try different user roles
3. Query the AI agent
4. Check the API documentation: `API.md`
5. Review the README for architecture details
6. Run tests: `pytest`

---

## Documentation

- **README.md** - Full architecture and documentation
- **API.md** - API endpoint reference
- **Dockerfile** - Container configuration
- **docker-compose.yml** - Multi-service setup
- **validate.py** - Setup validation script

---

## Questions?

Check:
1. README.md - Architecture and detailed info
2. API.md - API endpoints and usage
3. Logs - Look at stdout or `logs/arp_assessment.log`
4. validate.py - Check setup is correct

---

**Enjoy exploring the ARP Assessment Platform! 🚀**
