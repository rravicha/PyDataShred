from models import *
# from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()
# engine = create_engine("sqlite:///database.db")
class Register(Domain):
    @classmethod
    def metadata(cls, metadata_json):
        client_dict = json.loads(json_data)
        return Client(**client_dict)
