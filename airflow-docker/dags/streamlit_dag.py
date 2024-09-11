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

with DAG('Run_Shopify_Streamlit_ELT_Pandas', default_args=default_args, schedule_interval=None, catchup=False) as dag:

    # Run streamlit_analytics.py
    run_streamlit_analytics = DockerOperator(
        privileged=True,
        task_id='run_streamlit_analytics',
        image='shopify_pipeline-pandas-app',  # Use the same image
        container_name='vadrama_streamlit_analytics__pandas',  # Unique container name, can be any name
        api_version='auto',
        auto_remove=True,  
        command="streamlit run /app/streamlit_analytics.py --server.port 8590",  # Specify the command to run streamlit_analytics.py
        docker_url='unix://var/run/docker.sock', 
        network_mode='shopify_pipeline_airflow-network',  
        mount_tmp_dir=False, 
        tmp_dir='/tmp/airflow'
    )

    # Dependencies between tasks 
    run_streamlit_analytics
