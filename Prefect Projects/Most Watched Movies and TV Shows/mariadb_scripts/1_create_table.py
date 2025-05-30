import pymysql

# Database connection parameters
connection = pymysql.connect(
    host='mariadb',
    user='mariadb_user',
    password='mariadb_pass',
    database='most_watched_movies_and_tv_shows_mariadb_db',
    port=3306
)

try:
    with connection.cursor() as cursor:
        with open('/load_data/1_create_table.sql', 'r') as file:
            sql_script = file.read()
            for statement in sql_script.strip().split(';'):
                if statement:
                    cursor.execute(statement)
    connection.commit()
finally:
    connection.close()