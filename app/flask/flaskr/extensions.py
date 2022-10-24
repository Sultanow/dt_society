from flask_pymongo import PyMongo
from flask_caching import Cache

mongo = PyMongo()
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
