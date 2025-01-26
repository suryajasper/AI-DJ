import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("MONGODB_PASSWORD")
try:
    uri = f"mongodb+srv://georgemathew9203:{password}@djbestie.cfczo.mongodb.net/?retryWrites=true&w=majority&appName=DJBestie"
    client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
    client.admin.command("ping")
    print("Connected successfully")
    client.close()
except Exception as e:
    raise Exception(
        "The following error occurred: ", e)



