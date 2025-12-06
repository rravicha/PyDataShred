# PyDataShred Release Notes

## Version History

### 1.0 - Initial Release
- 🎉 Initial Project Structuring
- 📁 Added necessary files for basic project build
- ⚖️ Added License
- 🔧 Added `helper/data.py` - Methods for file based Ingestion

### 1.0.1 - Metadata & Cloud Integration
#### Cloud Infrastructure
- 🌨️ **Snowpark Table Integration**
  - Delta Live Table with Partition
  - SCD Type 2 Implementation
- 📊 **AWS Integration**
  - CSV file with multi-date support
  - AWS Delta file with partition
  - SCD Type 2 Implementation

#### Development Updates
- 🏗️ Full Fledged Dataclass Usage
  - Enhanced `api/models.py`
  - Multi Cloud Updates
- 🧪 Reformat Pytest Structure
- 🏛️ Documentation
    - 🔄 Core Architecture - Figma
        - System Architecture
    - 📖 How to Use Guide
        - Installation Steps
        - Configuration Settings
        - Basic Usage Examples
    - 📋 Coding Standards
        - Python Style Guide
        - Code Review Process
        - Best Practices

### 1.1 - File Operations
- 📂 File Copy Utility
  - On-premises support
  - Multi-cloud support (AWS/Azure/GCP)

### 1.2 - Database Integration
- 🗄️ Database Ingestion
  - SQL Alchemy Integration
  - Relational Database Support

### 1.3 - Streaming Data
- 🔄 Kafka Ingestion
  - Python implementation
  - PySpark integration

### 1.4 - Snowflake Operations
- ❄️ Snowflake Integration
  - Read operations
  - Write operations
  - SCD Type 2 implementation

### 1.5 - API Integration
- 🌐 API Ingestion Support

### 9.9 - Future Release
- 🎨 PyDataShred Frontend Dashboard
  - FastHTML implementation
  - SvelteKit integration
  - StreamLit support

---
*For more information, please visit our [documentation](https://pydatashred.readthedocs.io/).*