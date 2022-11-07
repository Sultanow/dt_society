from flask_pymongo import PyMongo
from flask_caching import Cache
from flask_cors import CORS
from flask_session import Session

mongo = PyMongo()
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cors = CORS(resources={r"/*": {"origins": "http://localhost:4200"}})
session = Session()
