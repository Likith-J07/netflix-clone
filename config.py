import os

class Config:
    # MySQL Database
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:kanyewestthegoat07%24@localhost/netflix_clone'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret Key
    SECRET_KEY = 'netflix123secret'

    