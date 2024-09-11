from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'description': 'Run multiple tasks with DockerOperator',
    'depend_on_past': False,
    'start_date': datetime(2024, 9, 11),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG('Run_Shopify_Complete_ELT_Pandas', default_args=default_args, schedule_interval=None, catchup=False) as dag:

    # Task 1: Run tests
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

    # Task 2: Run main.py
    run_main_app = DockerOperator(
        privileged=True,
        task_id='run_main_app',
        image='shopify_pipeline-pandas-app',  # Use your rebuilt image
        container_name='vadrama_main',  # Unique container name
        api_version='auto',
        auto_remove=True,  
        command="python /app/main.py",  # Specify the command to run main.py
        docker_url='unix://var/run/docker.sock', 
        network_mode='shopify_pipeline_airflow-network',  
        mount_tmp_dir=False, 
        tmp_dir='/tmp/airflow'
    )

    # Task 3: Run streamlit_analytics.py
    run_streamlit_analytics = DockerOperator(
        privileged=True,
        task_id='run_streamlit_analytics',
        image='shopify_pipeline-pandas-app',  # Use the same image
        container_name='vadrama_streamlit_analytics_pandas',  # Unique container name, can be any name
        api_version='auto',
        auto_remove=True,  
        command="streamlit run /app/streamlit_analytics.py",  # Specify the command to run streamlit_analytics.py
        docker_url='unix://var/run/docker.sock', 
        network_mode='shopify_pipeline_airflow-network',  
        mount_tmp_dir=False, 
        tmp_dir='/tmp/airflow'
    )

    # Dependencies between tasks 
    run_pandas_app_testing >> run_main_app >> run_streamlit_analytics
