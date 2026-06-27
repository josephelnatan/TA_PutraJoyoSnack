import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('TIDB_USER')}:"
        f"{os.getenv('TIDB_PASSWORD')}@"
        f"{os.getenv('TIDB_HOST')}:"
        f"{os.getenv('TIDB_PORT')}/"
        f"{os.getenv('TIDB_DATABASE')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False