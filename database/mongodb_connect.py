from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.database_config import get_database_config
from database.schema import create_mongodb_schema

class MongoDBConnect:
    def __init__(self, mongo_uri, db_name):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.mongo_uri)
            self.client.server_info() # test connection
            self.db = self.client[self.db_name]
            print("CONNECTED TO MONGODB")
            return self.db
        except ConnectionFailure as e:
            raise Exception(f"FAILED CONNECT TO MONGODB: {e}") from e

    def close(self):
        if self.client:
            self.client.close()
            print("MONGODB CONNECTION CLOSED")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    config_MongoDB = get_database_config()
    with MongoDBConnect(config_MongoDB["mongodb"].uri, config_MongoDB["mongodb"].db_name) as mongo:
        db = mongo.connect()
        create_mongodb_schema(db)

    #validate data

if __name__ == "__main__":
    main()

