from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)

db = client["teen_patti_bot"]

users = db["users"]