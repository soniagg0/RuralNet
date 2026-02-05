from pymongo import MongoClient
from datetime import datetime

client= MongoClient("mongodb+srv://paupujolromeu_db_user:vZkdYpzTnNEQV3Rk@cluster0.kogkbc3.mongodb.net/?appName=Cluster0")
db= client.ttn_db #nom de la bd
collection=db.ttn_data # Colssció = tabla sql, guradoa dades que son json


def insert_ttn_payload_bd(payload: dict):

    collection.insert_one(payload)
    
def get_all_payloads():
    return list(collection.find({}, {"_id": 0}))

