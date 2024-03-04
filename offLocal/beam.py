import os
from pymongo import MongoClient
from datetime import datetime
from ..misc.config import MONGODB_USERNAME, MONGODB_PASSWORD

# Still need to configure new MongoDB Atlas cluster
MONGODB_CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@silov3-1stcluster.m6deilx.mongodb.net/?retryWrites=true&w=majority&appName=SiloV3-1stCluster"

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.get_database("Database1")
collection = db.get_collection("Collection1")

def beam_to_cloud(folder_path):
    # Iterate over files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Extract metadata
        metadata = {
            "filename": filename,
            "path": file_path,
            "upload_date": datetime.utcnow(),
            # Add more metadata fields as needed
        }
        # Insert metadata into MongoDB
        collection.insert_one(metadata)
        print(f"Beamed {filename} to MongoDB Atlas.")

if __name__ == "__main__":
    # Path to the SH folder
    folder_path = os.path.expanduser("~/Desktop/SiloV3/SH")
    beam_to_cloud(folder_path)
