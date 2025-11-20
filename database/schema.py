from pathlib import Path
from typing import Any
from mysql.connector import Error


def create_mysql_schema(connection: Any, cursor: Any, database: str):
    schema_path = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    try:
        cursor.execute(f"USE {database}")
        with open(schema_path, "r", encoding="utf-8") as file:
            sql_script = file.read()
            sql_commands = [cmd.strip() for cmd in sql_script.split(";") if cmd.strip()]
            for cmd in sql_commands:
                cursor.execute(cmd)
                print("Executed MySQL command")
        connection.commit()
        print("Created MySQL schema successfully")
    except Error as e:
        connection.rollback()
        print(f"Failed to create MySQL schema: {e}")
        raise


def create_mongodb_schema(db: Any):
    if "Users" in db.list_collection_names():
        db["Users"].drop()

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
    db["Users"].create_index("user_id", unique=True)
    print("Created MongoDB schema for collection: Users")


def validate():
    pass