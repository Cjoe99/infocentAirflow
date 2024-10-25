from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

# 任務1：打印訊息
def task1():
    print("Running Task 1")

# 任務2：打印訊息
def task2():
    print("Running Task 2")

# 定義在失敗時發送 Slack 通知的回調函數
def slack_failure_callback(context):
    slack_msg = f"""
        :red_circle: Task Failed. 
        *Task*: {context.get('task_instance').task_id}  
        *Dag*: {context.get('task_instance').dag_id}  
        *Execution Time*: {context.get('execution_date')}  
        *Log URL*: {context.get('task_instance').log_url}
    """
    failure_notification = SlackWebhookOperator(
        task_id='slack_failure_notification',
        slack_webhook_conn_id='slack_webhook',  # 連接到你在 Airflow Connections 中配置的 Slack Webhook
        message=slack_msg,
        channel='#airflownotice',  # 指定你的 Slack 頻道
        dag=context['dag']
    )
    return failure_notification.execute(context=context)

# 預設參數設置
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=3),  # 修改為3秒延遲
    'on_failure_callback': slack_failure_callback,  # 失敗時發送 Slack 通知
}

# 定義 DAG
with DAG(
    'SlackMsgTest_dag',
    default_args=default_args,
    description='An example DAG with Python operators and Slack notifications',
    schedule_interval="* * * * *",  # 每分鐘執行一次
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example']
) as dag:

    # 定義 Task 1
    task1_obj = PythonOperator(
        task_id='task1',
        python_callable=task1,
    )

    # 定義 Task 2
    task2_obj = PythonOperator(
        task_id='task2',
        python_callable=task2,
    )

    # 成功時發送 Slack 通知
    slack_success_notification = SlackWebhookOperator(
        task_id='slack_success_notification',
        slack_webhook_conn_id='slack_webhook',  # 連接到你在 Airflow Connections 中配置的 Slack Webhook
        message=":white_check_mark: Task 2 completed successfully in Airflow."
    )

    # 設置任務依賴性：task1 完成後執行 task2，task2 完成後發送 Slack 成功通知
    task1_obj >> task2_obj >> slack_success_notification
