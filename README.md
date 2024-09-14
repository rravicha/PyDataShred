# PyDataShred
This project emphasis on creating a wrapper for the modern data engineering which involves data shredding at its core

Steps to install mysql in codespace
https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04
install mysql : sudo apt install mysql-server
start mysql :  | codespace wont support systemctl so using service

>>> sudo su
>>> sudo service mysql start
>>> mysql -u scott -p <-login

what is pydantic??


# Project Workflow:
------- ------
Python
    File Ingestion
    Database Ingestion - mysql
Pyspark
    File Ingestion
    Databse Ingestion
API
    Batch
    Streaming
SCD
    Spark / Non Spark
Orchestration:
    Airflow / Apache Beam
    
Multi Cloud Support
    AWS/Azure/GCS - Databricks
Sentry.io Integration

Splunk Integration  -  Optional

Snowflake integration

# Multi Cloud Accounts
Google
AWS
Azure
Google Cloud
Snowflake
Heroku
