import mysql.connector
from config.database_config import get_database_config
from database.schema import create_mysql_schema

class MySQLConnect:
    def __init__(self, host, port, user, password, database) :
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.config = {"host" : host, "port" : port, "user" : user, "password" : password, "database" : database}
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config) # connect
            self.cursor = self.connection.cursor() # execute
            print(f"CONNECTED TO MYSQL")
            return self.connection, self.cursor
        except Exception as e:
            raise Exception(f"FAILED CONNECT TO MYSQL: {e}") from e

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print (f"MYSQL CLOSED")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    config_MySQL = get_database_config()

    with MySQLConnect(config_MySQL["mysql"].host, config_MySQL["mysql"].port, config_MySQL["mysql"].user, config_MySQL["mysql"].password, config_MySQL["mysql"].database) as mysql:
        db = mysql
        create_mysql_schema(db.connection, db.cursor, config_MySQL["mysql"].database)

    # validate data

if __name__ == "__main__":
    main()