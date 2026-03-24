from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
#this the four step dag
with DAG(
    dag_id='tap2eat_data_pipeline',
    start_date=datetime(2026,3,18),
    schedule_interval=None,# will be manually triggering it
    catchup=False,
) as dag:
    clean_data=BashOperator(
        task_id='clean_extracted_csv',
        bash_command='python /opt/airflow/data/notebook/wrangle.py'
    )
    combine_data=BashOperator(
        task_id='combine_csv',
        bash_command='python /opt/airflow/data/data_processed/csv_combiner.py'
)

    clean_data >> combine_data