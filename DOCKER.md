# AM Parser - Docker Setup

## MongoDB with Docker Compose

This project includes a complete MongoDB setup using Docker Compose for easy development.

### Quick Start

```bash
# Start MongoDB and web interface
docker-compose up -d

# Check services status
docker-compose ps

# Test with sample data
python -m am_app save-portfolio --input data/mfextractedholdings/motilaloswalmf.json

# View data in web interface
# Open: http://localhost:8081 (webadmin / webpass123)
```

### Services Included

| Service | Port | Purpose | Credentials |
|---------|------|---------|-------------|
| MongoDB | 27017 | Database | admin / password123 |
| Mongo Express | 8081 | Web UI | webadmin / webpass123 |

### Connection Details

**Python Application**:
```python
# Default (works out of the box)
service = create_mutual_fund_service()

# With authentication
service = create_mutual_fund_service(
    mongo_uri="mongodb://admin:password123@localhost:27017"
)
```

**CLI Usage**:
```bash
# Default connection
python -m am_app save-portfolio --input portfolio.json

# Custom connection
python -m am_app save-portfolio --input portfolio.json --mongo-uri mongodb://admin:password123@localhost:27017
```

### Data Persistence

- MongoDB data is persisted in Docker volumes
- Survives container restarts
- To reset: `docker-compose down -v` (⚠️ deletes all data)

### Development Workflow

1. **Start Services**: `docker-compose up -d`
2. **Load Data**: `python -m am_app save-portfolio --input data/mfextractedholdings/motilaloswalmf.json`
3. **View Data**: http://localhost:8081
4. **Query Data**: Use the AM Parser service methods
5. **Stop Services**: `docker-compose down`

See `mongo-init/README.md` for detailed configuration and troubleshooting.
