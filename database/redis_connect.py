import redis
from redis.exceptions import ConnectionError
from config.database_config import get_database_config
from schema import create_redis_schema

class RedisConnect:
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = int(db)
        self.config = {"host" : host, "port" : port, "username" : user, "password" : password, "db" : db}
        self.client = None

    def connect(self):
        try:
            self.client = redis.Redis (**self.config, decode_responses = True)
            self.client.ping() # test connection
            print("CONNECTED TO REDIS")
            return self.client
        except ConnectionError as e:
             raise Exception(f"FAILED CONNECT TO REDIS: {e}") from e

    def close(self):
        if self.client:
            self.client.close()
            print("REDIS CONNECTION CLOSED")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    config_Redis = get_database_config()
    with RedisConnect(config_Redis["redis"].host, config_Redis["redis"].port, config_Redis["redis"].user, config_Redis["redis"].password, config_Redis["redis"].database) as redis:
        create_redis_schema(redis.connect())

    # validate data

if __name__ == "__main__":
    main()