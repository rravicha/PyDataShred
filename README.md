# PyDataShred 🔄

> A comprehensive wrapper for modern data engineering with focus on data shredding capabilities

## 🌟 Features

### Core Components
- **Python Processing**
  - File Ingestion
  - Database Ingestion (MySQL)
  
- **PySpark Integration**
  - File Ingestion
  - Database Ingestion

- **API Support**
  - ⚡ Batch Processing
  - 🔄 Streaming
  - 📊 MetaData Ingestion Framework (Multi-Cloud Approach) *[Current Sprint]*

- **SCD (Slowly Changing Dimensions)**
  - Spark Implementation
  - Non-Spark Implementation

### Frontend Options
- 📱 StreamLit
- 🌐 FastHTML
- ⚛️ Modern Web Frameworks
  - SvelteKit
  - ReactJS

### Orchestration Solutions
- 🔄 Apache Airflow
- 🌊 Apache Beam
- ⚡ AWS Step Functions

## 🌐 Multi-Cloud Support
- Amazon Web Services (AWS)
- Microsoft Azure
- Google Cloud Platform (GCS)
- Databricks

## 🔌 Integrations
- Sentry.io - Error Tracking
- Splunk (Optional) - Log Management
- Snowflake/SnowPark - [Documentation](https://docs.snowflake.com/en/developer-guide/snowpark/python/testing-python-snowpark)

## ☁️ Supported Cloud Platforms
- Google Cloud
- AWS
- Azure
- Snowflake
- Heroku

## 💻 Development Environment
- Gitpod
- GitHub Codespaces

## 🛠️ Setup Guide

### MySQL Installation in Codespace
```bash
# Update package list and install MySQL
sudo apt-get update
sudo apt-get install -y mysql-server

# Start MySQL service
sudo service mysql start

# Login to MySQL
mysql -u scott -p
```

## 📚 Project Architecture
```
Wrapper
│
├── Handler
│   │
│   └── Delegator
│       ├── Mapper
│       └── Service
│           └── Repository
```

## 📝 Notes
- What is Pydantic? [Add explanation here]
- using typing especially Union[str,List[str]]!!