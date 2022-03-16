#setting up db using pymongo
import pymongo
from pymongo import MongoClient

dbclient = pymongo.MongoClient("mongodb+srv:// Paste it or By Env")
database = dbclient["Name"]

user_collection = database['users']

async def present_in_userbase(user_id : int):
    found = user_collection.find_one({'_id': user_id})
    if found:
        return True
    else:
        return False

async def add_to_userbase(user_id: int):
    user_collection.insert_one({'_id': user_id})
    return

async def get_users():
    user_docs = user_collection.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids
    
async def del_from_userbase(user_id: int):
    user_collection.delete_one({'_id': user_id})
    return