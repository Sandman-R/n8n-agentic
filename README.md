# N8N Agentic - Retail Data Analysis & Forecasting Platform

A comprehensive retail data analysis and forecasting platform built with n8n, Python API, and machine learning, fully containerized with Docker deployment.

## 📋 Project Overview

This project integrates the following core functionalities:

- **Data Processing**: Cleaning and preprocessing of retail transaction data
- **Product Clustering**: Machine learning-based product clustering analysis
- **Sales Forecasting**: Time-series predictions based on historical data
- **API Service**: Flask REST API for data queries and model predictions
- **Workflow Automation**: Automated data processing pipelines via n8n
- **Data Persistence**: PostgreSQL database support

## 🚀 Quick Start

### System Requirements

- Docker & Docker Compose
- Python 3.8+
- PostgreSQL 15 (automatically deployed via Docker)

### Installation and Running

1. **Clone the repository**
```bash
git clone <repository>
cd n8n-agentic
```

2. **Start Docker containers**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database service
- n8n workflow automation platform
- Python API service

3. **Verify service status**
```bash
# Check all containers status
docker-compose ps

# View logs in real-time
docker-compose logs -f
```

## 📁 Project Structure

```
n8n-agentic/
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # n8n image build file
├── load_retail.py              # Retail data loading script
├── 
├── python-api/                 # Flask REST API
│   ├── app.py                  # API application entry point
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # API image build
│   └── __pycache__/            # Python cache
│
├── clustering data/            # Clustering-related data
│   ├── product_features_clustered.csv
│   ├── product_features_full.csv
│   └── product_features_scaled.csv
│
├── online retail/              # Raw retail data
│   ├── all_products_cleaned.csv
│   └── total_retail_cleaned.csv
│
├── outputs/                    # Model outputs and reports
│   └── final_report_20260325/
│       ├── model_artifacts/
│       └── test_report_3period/
│
├── testFiles/                  # Test and prediction scripts
│   ├── predict_product_sales.py
│   ├── predict_retail.py
│   ├── analyze_retail.py
│   └── test.py
│
└── *.csv / *.json              # Data and configuration files
```

## 🔧 Configuration Guide

### Docker Compose Configuration

Main service configuration in `docker-compose.yml`:

- **PostgreSQL**: Retail data storage
  - Port: 5432
  - Default database: retail
  - User: postgres / Password: postgres

- **n8n**: Workflow automation platform
  - Port: 5678
  - Database: PostgreSQL
  - Automation script storage: `/files` (mapped to `testFiles/` directory)

- **Python API**: Flask REST service
  - Calls model prediction scripts
  - Supports health checks and business request handling

### Python Dependencies

Main installed packages:
- **flask**: REST API framework
- **pandas**: Data processing
- **numpy**: Numerical computation
- **scikit-learn**: Machine learning algorithms
- **sqlalchemy**: Database ORM
- **psycopg2-binary**: PostgreSQL driver

## 📊 Core Features

### Data Processing

**load_retail.py** - Load retail data into database:
- Read Excel transaction data
- Standardize column names
- Data cleaning (handle missing values)
- Generate derived features (e.g., revenue)
- Store in PostgreSQL

### Prediction Models

**testFiles/predict_product_sales.py** - Product sales forecasting:
- Sales prediction based on product features
- Support for parallel predictions across multiple clusters
- Return results in JSON format

### API Endpoints

Main endpoints provided by Flask API:

```
GET /health              # Health check
POST /predict            # Product sales prediction
GET /clusters            # Get cluster information
GET /products/<id>       # Get product details
```

## 🏃 Basic Commands

### Starting/Stopping Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View real-time logs
docker-compose logs -f

# Start specific service only
docker-compose up -d postgres
docker-compose up -d n8n
```

### Accessing Services

- **n8n Dashboard**: http://localhost:5678
- **PostgreSQL**: localhost:5432
- **Python API**: http://localhost:5000 (if configured)

### Database Operations

```bash
# Enter PostgreSQL container
docker exec -it n8n-postgres psql -U postgres -d retail

# Query data
SELECT * FROM transactions LIMIT 10;
SELECT * FROM products LIMIT 10;
```

## 📈 Data Pipeline

```
Raw Data (Excel) 
    ↓
load_retail.py (Data Cleaning)
    ↓
PostgreSQL (Data Storage)
    ↓
Python Scripts (Feature Engineering & Clustering)
    ↓
CSV Output (Features & Models)
    ↓
REST API (Model Serving)
    ↓
n8n Workflows (Automated Invocation)
```

## 🎯 Prediction & Analysis Features

### Generated Artifacts

- **model_artifacts**: Optimal model parameters
- **cluster_comparison.csv**: Cluster comparative analysis
- **per_cluster_period_mape_*.csv**: Prediction accuracy metrics per cluster

### Model Evaluation

The project includes three-period model evaluation reports:
- MAPE (Mean Absolute Percentage Error)
- Cluster performance comparison
- Overall accuracy summary

## 🔐 Security Recommendations

> **Important**: The following configuration is for development use only

- Change default PostgreSQL password (for production)
- Disable n8n basic authentication (currently disabled)
- Add authentication mechanisms to API
- Use environment variables for sensitive information



## 🚢 Production Deployment

### Docker Image Building

```bash
# Build custom n8n image (with Python)
docker build -t n8n-with-python:latest .

# Build Python API image
docker build -t retail-api:latest ./python-api
```

### Environment Variable Configuration

Create `.env` file (for production):
```env
POSTGRES_USER=retail_user
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=retail_production
N8N_SECURE_COOKIE=true
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<strong_password>
```

## 📞 Support

If you have questions, please check:
- Build configuration in Dockerfile
- Service configuration in docker-compose.yml
- Test script examples in testFiles/

## 📄 License

[Add your license information here]

---

**Last Updated**: March 28, 2026  
**Project Version**: 1.0  
**Python Version**: 3.8+  
**Docker Version**: 20.10+
