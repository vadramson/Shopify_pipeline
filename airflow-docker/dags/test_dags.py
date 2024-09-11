from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta


# Default arguments for the DAG
default_args = {
'owner'                 : 'airflow',
'description'           : 'Use of the DockerOperator',
'depend_on_past'        : False,
'start_date'            : datetime(2024, 9, 11),
'email_on_failure'      : True,
'email_on_retry'        : False,
'retries'               : 1,
'retry_delay'           : timedelta(minutes=5)
}

# Define the DAG
#with DAG('Run_Pandas_Shopify_ELT', default_args=default_args, schedule_interval="5 * * * *", catchup=False) as dag:

with DAG('Run_Shopify_ELT_Pandas_testing', default_args=default_args, schedule_interval=None) as dag:
    # Task to trigger pandas-app using DockerOperator
    run_pandas_app_testing = DockerOperator(
        privileged=True,
        task_id='run_pandas_app_tests',
        image='shopify_pipeline-pandas-app',  # shopify_pipeline-pandas-app:latest This should match your container name or image name
        container_name='vadrama_pandas_tests',  # The container name for the pandas app
        api_version='auto',
        auto_remove=True,  # Automatically remove the container after task completion
        command="pytest /app/tests",  # Modify based on how the pandas-app runs
        docker_url='unix://var/run/docker.sock',  # Docker socket location
        network_mode='shopify_pipeline_airflow-network',  # bridge Ensure it's in the same network
        mount_tmp_dir=False, 
        tmp_dir='/tmp/airflow'
    )

    run_pandas_app_testing

