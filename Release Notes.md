>>> 1.0
    * Initial Project Structuring
    * Added necessary files for basic project build
    * Added License
    * Added helper/data.py | Methods for file based Ingestion
>>> 1.1.1
    * MetaData Ingestion Processing | On Prem | Sqlite / Mysql
        --> Metadata Source will be Sqlite
        --> Data will be from tests_data or On Prem Databases
        --> Sqlite to Delta Partition Files (On Prem) | Scd 1 & Scd 2 | Create Models Accordingly\
        <!-- raw.emp > delta on prem file with partition > shred > sqlite views/current and history e2e automate -->
>>> 1.1.2
    * MetaData Ingestion Processing | Multi Cloud | DBX
        --> Snowpark Table | Delta Live Table with Partition | Scd 2
        --> CSV file with multi date | aws-delta file with partition | Scd 2
    * Full Fledged Dataclass Usage
        --> api/models.py | Multi Cloud Updates
    * Reformat Pytest
>>> 1.2
    * Database Ingestion | SQL Alchemy | Mysql
>>> 2.0
    * PyDataShred | Frontend | FastHtml / SvelteKit
    