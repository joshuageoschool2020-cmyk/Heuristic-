# Tech Context – Technology Stack

## Backend Stack
- **Language**: Python 3.x
- **Web Framework**: FastAPI 0.100+
- **ASGI Server**: Uvicorn
- **Data Processing**: Pandas
- **ML/Stats**: Scikit-learn
- **Serialization**: Pydantic

## Frontend Stack
- **HTML**: Vanilla HTML5 (embedded in `api.py`)
- **CSS**: Tailwind CSS (CDN)
- **JavaScript**: Vanilla ES6+ (no frameworks)
- **API Client**: Fetch API (native browser)

## Deployment Stack
- **Host**: Render.com (Web Service)
- **Container**: Linux container (Python runtime)
- **Port**: 10000 (default, configurable via PORT env var)
- **Git**: GitHub (auto-deploying on push)

## Database/Storage (Future)
- [ ] PostgreSQL for user accounts, API keys, usage analytics
- [ ] Redis for caching analysis results, rate limiting
- [ ] CSV export option (current: memory-based)

## Development Tools
- **Version Control**: Git + GitHub
- **Terminal**: PowerShell (Windows), Bash (Linux/Mac)
- **Testing**: Python unittest / pytest (not yet configured)
- **IDE**: VS Code (with Copilot extensions)

## Dependency Inventory

### Current (in requirements.txt)
```
fastapi
uvicorn
pandas
scikit-learn
```

### Future Candidates
- `pydantic-settings` – Configuration management
- `python-dotenv` – Environment variable loading
- `sqlalchemy` – Database ORM
- `pytest` – Testing framework
- `black` – Code formatting
- `pylint` – Linting
- `redis` – Caching
- `psycopg2` – PostgreSQL driver

## Version Pinning Strategy
- **Current**: No version pins (risky for production)
- **Recommended**: Pin major versions (e.g., `fastapi>=0.100,<1.0`)
- **Strict**: Pin exact versions (e.g., `fastapi==0.104.1`) for Render reproducibility

## Performance Targets
- **Response time**: < 500ms for `/explain`
- **Throughput**: 100+ requests/second
- **Uptime**: 99.9%
- **Confidence accuracy**: > 90% (domain-dependent)

## Security Considerations
- [ ] API rate limiting (future: implement in /explain)
- [ ] Input validation (Pydantic models enforce structure)
- [ ] CORS policy (currently allowing all origins)
- [ ] SQL injection prevention (N/A until database added)
- [ ] Authentication (future: API keys, OAuth)
