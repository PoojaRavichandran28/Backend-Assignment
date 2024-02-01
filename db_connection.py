import psycopg2
from psycopg2 import sql
from config.db_config import DB_CONFIG


def connect_to_db(db_name=None):
    try:
        connection = psycopg2.connect(
            dbname=db_name or DB_CONFIG['DBNAME'],
            user=DB_CONFIG['USER'],
            password=DB_CONFIG['PASSWORD'],
            host=DB_CONFIG['HOST'],
            port=DB_CONFIG['PORT']
        )
        cursor = connection.cursor()
        return connection, cursor
    except psycopg2.Error as e:
        print(f"Error: {e}")


def close_connection(cursor, connection):
    if cursor:
        cursor.close()
    if connection:
        connection.close()


def create_database_if_not_exists():
    try:
        connection, cursor = connect_to_db(db_name='postgres')
        connection.autocommit = True
        cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), (DB_CONFIG['DBNAME'],))
        exists = cursor.fetchone()

        if exists is None:
            # Database does not exist, create it
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG['DBNAME'])))
        else:
            print(f"The database '{DB_CONFIG['DBNAME']}' already exists.")

    except psycopg2.Error as e:
        print(f"Error: {e}")

    finally:
        close_connection(cursor, connection)


def create_email_data_table():
    try:
        connection, cursor = connect_to_db()
        query = '''CREATE TABLE email_data (
                id SERIAL PRIMARY KEY,
                message_id VARCHAR(255) UNIQUE,
                from_address VARCHAR(255),
                to_address VARCHAR(255),
                subject VARCHAR(255),
                message_content BYTEA NOT NULL,
                date_received TIMESTAMP
                );'''
        cursor.execute(query)
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        connection.commit()
    except psycopg2.Error as e:
        print(f'Error: {e}')
    finally:
        close_connection(cursor, connection)


def insert_email_data(data):
    try:
        connection, cursor = connect_to_db()
        message_id = data['message_id']
        from_address = data['From']
        to_address = data['To']
        date_received = data['Date']
        subject = data['Subject']
        message_content = data['message'].encode('utf-8')
        insert_query = sql.SQL("""
                INSERT INTO email_data (message_id, from_address, to_address, date_received, subject, message_content)
                VALUES (%s, %s, %s, %s, %s, %s)
            """)
        cursor.execute(insert_query, (message_id, from_address, to_address, date_received, subject, psycopg2.Binary(message_content)))
        connection.commit()
    except psycopg2.Error as e:
        print(f'Error: {e}')
    finally:
        close_connection(cursor, connection)
