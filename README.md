# Shopify Data Pipeline 

## Overview
_FYI: Read the NB at the end of the page to know why you see the .env file_

This repository contains a Python-based data pipeline for processing daily Shopify configurations. The pipeline is designed to:

1. **Extract**: Download a CSV file from an S3 bucket.
2. **Transform**: Filter and transform the data.
3. **Load**: Load the processed data into a PostgreSQL database.

The pipeline is built using Docker, Docker Compose, and Apache Airflow for orchestration.

## Requirements

- **Python**: Required for implementation.
- **Airflow**: Used for task orchestration.
- **Docker**: For containerization.
- **Docker Compose**: For managing multi-container Docker applications.
- **PostgreSQL**: Target database for loading data.

## Pipeline Description

### Extract
- **Source**: S3 bucket `alg-data-public`.
- **File Naming**: `[YYYY-MM-DD].csv` (Replace `[YYYY-MM-DD]` with the appropriate date).
- **Date Range**: Process files from `2019-04-01` to `2019-04-07`.
### Transform
- **Filter**: Remove rows with empty `application_id`.
- **Transform**: Add a column `has_specific_prefix`:
- `true` if `index_prefix` differs from `shopify_`.
- `false` otherwise.
### Load
- **Destination**: PostgreSQL instance.
- **Action**: Load valid rows into the PostgreSQL database.


This pipeline is heavily dependent on Airflow running in a docker container.
## What Can You Do with Airflow?
Airflow is an orchestration tool that triggers tasks on a schedule or when certain events occur. Here are some common use cases:

- **Replace Cron Jobs:** Airflow provides a visual interface to monitor job execution and alerts for job failures.
- **Extract Data:** Use Airflow to extract data from databases, check data quality, and store results in data warehouses.
- **Transform Data:** Interface with services like EMR for data processing and write results to data warehouses.
- **Train Machine Learning Models:** Extract, process, and train models, then write results to a database for consumption by other applications.
- **Crawl Data from the Internet:** Periodically gather data from websites and store it in your database.

*The possibilities are almost endless.*

## Key Concepts

- **DAGs:** Directed Acyclic Graphs represent the workflow in Airflow, where tasks are nodes and dependencies are edges.
- **Operators:** Define the actions within tasks, e.g., `PythonOperator` for Python scripts, `BashOperator` for shell commands.
- **Sensors:** Wait for specific events to occur, such as the arrival of a file or an API response.
- **Tasks:** Instances of operators that execute within a DAG according to defined dependencies.


## Executing this pipeline
### Prerequisites
Ensure you have Docker and Docker Compose installed on your machine.

**Clone the repository**

From a command line terminal, copy and paste the command below

    git clone  [https://github.com/vadramson/Shopify_pipeline.git

This will download the latest version of this repository, you should now see a folder **shopify_pipeline**. Go into the folder by executing the command below

    cd shopify_pipeline
Once inside the shopify_pipeline folder, you should have a folder tree like so.

    ├── README.md
    ├── airflow-docker
    │   ├── Dockerfile
    │   ├── dags
    │   │   ├── pandas_app_dag.py
    │   │   ├── streamlit_dag.py
    │   │   └── test_dags.py
    │   ├── init-db.sh
    │   ├── init.sql
    │   ├── plugins
    │   └── servers.json
    ├── directory_structure.txt
    ├── docker-compose.yml
    ├── pandas-app
    │   ├── Dockerfile
    │   ├── main.py
    │   ├── pytest.ini
    │   ├── requirements.txt
    │   ├── src
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── data_processing.py
    │   │   └── database_operations.py
    │   ├── streamlit_analytics.py
    │   └── tests
    │       ├── test_config.py
    │       ├── test_data_processing.py
    │       └── test_database_operations.py
    └── pyspark
        └── main.py

Make sure you are at the root and initialise the Airflow instance with the airflow service using the command. 

	docker-compose up airflow-init
This pulls all the images and create all the services listed in the docker-compose file, it will take a few minutes the first time. This initialising all the containers, creates a database shopify_db, and creates three schemas(***raw, staging, analytics***) within the database. 

![Initialise Airflow screen](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2021.52.52.png)

After initializing the Airflow instance, you can now run all the services listed in the docker-compose file using the command. 

	docker-compose up

![running_airflow](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2021.53.43.png)

![Connected](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2021.54.03.png)

This starts all the services

#### To check which services are running, enter the command 
	docker ps
 
Once all services are healthy, you can now open your browser and go to

	http://localhost:8080/home

The following page should be display 


![airflowLogin](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2021.57.44.png)


Enter the username and password as specified in the docker-compose file and login, default is **username**: *airflow*, **password**: *airflow*


The following screen should be displayed

![Connected](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2021.58.34.png)

What you see are the existing Dags.

The setup also includes a PostgreSQL database and a pgAdmin container which you can access by going to this url

http://localhost:5050/browser/

You should see this displayed

![pgadminlogin](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2022.02.15.png)

You will be required to enter a password to connect to pgAdmin and to the Postgres Group server fist enter default is **pgAdmin Password**: *admin*,  then **server group password**: *airflow*

You should now have access to the databases, explore the contents of the shopify_database.


*You can now proceed in running a dag*

Head back to the airflow tab on your browser and click on the dag,  Run_Shopify_Complete_ELT_Pandas, and then on graph, you should see the dag display as in the image below. There are 3 dags, the first one runs all the tests, the second one runs the pipeline and the third one runs a Streamlit file that connects to the database and display an analytics dashboard of the data ingested data.

![complete](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2022.15.23.png)

Click the run button and if all the tests cases succeed, then the pipeline will be run and eventually the streamlit file. You can access the streamlit file by going to this link.

http://localhost:8501/

You should see this display, if there are no conflicting ports.

![streamlit_dashboard](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2022.33.44.png)

You can head back to the pgAdmin tab to see the data in the **shopify_configs** table.

![data_in_table](https://github.com/vadramson/Shopify_pipeline/blob/main/img/Screenshot%202024-09-11%20at%2022.26.31.png)

**NB:** 

> For testing purposes only the .env files have been reintroduce for
> simplicity testing only.
