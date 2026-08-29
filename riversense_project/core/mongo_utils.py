from pymongo import MongoClient

MONGO_URI = "mongodb+srv://admin:admin@cluster0.hthlpbe.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["test"]
collection = db["waters"]


def get_latest_water_data():
    try:
        # safer: sort by _id (always exists)
        doc = collection.find_one(sort=[("_id", -1)])

        if not doc:
            return None

        return {
            "turbidity": doc.get("turbidity_value", 0),
            "status": doc.get("turbidity_status", 0),
            "time": str(doc.get("time", "No time"))
        }

    except Exception as e:
        print("🔥 Mongo Error:", e)
        return None