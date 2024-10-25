from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# 導入你的腳本
import ptt_up_to_kafka

# 定義DAG參數
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

# 建立DAG實例
dag = DAG('complex_dag', default_args=default_args, schedule_interval='@daily')

# 定義任務
task = PythonOperator(
    task_id='run_my_script',
    python_callable=ptt_up_to_kafka.main_function,  # 指定執行腳本的主函數
    dag=dag,
)