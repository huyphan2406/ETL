from pathlib import Path
from mysql.connector import Error

def create_mysql_schema(connection, cursor, database):
    schema_path = Path(r"C:/Users/Laptop/PycharmProjects/DE/sql/schema.sql")
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    print(f"CREATED DATABASE {database} IN MYSQL")
    try:
        cursor.execute(f"USE {database}") # use database
        with open(schema_path, "r") as file:
            sql_script = file.read()
            sql_commands = [cmd.strip() for cmd in sql_script.split(";") if cmd.strip()]
            for cmd in sql_commands:
                cursor.execute(cmd)
                print("EXECUTED MYSQL COMMAND")
        connection.commit()
        print("CREATED MYSQL SCHEMA")
    except Error as e:
        connection.rollback()
        raise Exception(f"FAILED TO CREATE MYSQL SCHEMA {e}") from e

def create_mongodb_schema(db):
    if "Users" in db.list_collection_names():
        db.Users.drop()

    db.create_collection(
        "Users",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "login"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "login": {"bsonType": "string"},
                    "gravatar_ID": {"bsonType": "string"},
                    "avatar_url": {"bsonType": "string"},
                    "url": {"bsonType": "string"},
                },
            }
        }
    )
    db.Users12345.create_index("user_id", unique=True)
    print("CREATED MONGODB SCHEMA")

def create_redis_schema(client):
    try:
        client.flushdb() # drop database

        client.set("user:1:login", "GoogleCodeExporter")
        client.set("user:1:gravatar_id", "")
        client.set("user:1:avatar_url", "https://avatars.githubusercontent.com/u/9614759?")
        client.set("user:1:url", "https://api.github.com/users/GoogleCodeExporter")

        client.sadd("user_id", "user:1")

        print("ADD DATA SUCCESSFULLY TO REDIS")

    except Error as e:
        raise Exception(f"FAILED TO ADD DATA TO REDIS {e}") from e

def validate():
    return