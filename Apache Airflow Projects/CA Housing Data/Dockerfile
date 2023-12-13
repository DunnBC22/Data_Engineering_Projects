FROM apache/airflow:2.7.3
COPY requirements.txt /requirements.txt

RUN pip install --user --upgrade pip
RUN pip install apache-airflow-providers-postgres
RUN pip install 'apache-airflow[pandas]'