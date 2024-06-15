from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Connection:
    def __new__(cls, database):
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI environment variable not set")

            # Debugging output to ensure the URI is correct
            print(f"Connecting to MongoDB with URI: {mongo_uri}")

            # Establish a connection to the MongoDB server with SSL options
            connection = MongoClient(mongo_uri, ssl=True, tlsAllowInvalidCertificates=True)
            print("Connection established successfully")
            return connection[database]
        except Exception as e:
            print(f"Error establishing MongoDB connection: {e}")
            raise

# Example usage
try:
    db = Connection('your_database_name')
    print("Connection established successfully")
except Exception as e:
    print(f"Failed to connect to database: {e}")
