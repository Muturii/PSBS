from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo

class User:
    @staticmethod
    def create(full_name, email, password, role='citizen'):
        password_hash = generate_password_hash(password)
        user_doc = {
            "full_name": full_name,
            "email": email.lower().strip(),
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.now()
        }
        return mongo.db.users.insert_one(user_doc)

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({"email": email.lower().strip()})

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)


class ServiceRequest:
    @staticmethod
    def create(user_id, category, location, description, image_filename=None):
        request_doc = {
            "user_id": ObjectId(user_id),
            "category": category,
            "location": location,
            "description": description,
            "image_filename": image_filename,
            "status": "Pending",
            "admin_comment": "",
            "activity_log": [
                {
                    "status": "Pending",
                    "comment": "Request submitted by citizen",
                    "timestamp": datetime.now().strftime("%b %d, %Y - %I:%M %p")
                }
            ],
            "created_at": datetime.now()
        }
        return mongo.db.requests.insert_one(request_doc)

    @staticmethod
    def get_all():
        return list(mongo.db.requests.find().sort("_id", -1))

    @staticmethod
    def get_by_user(user_id):
        return list(mongo.db.requests.find({"user_id": ObjectId(user_id)}).sort("_id", -1))

    @staticmethod
    def update_status(request_id, status, comment=""):
        log_entry = {
            "status": status,
            "comment": comment,
            "timestamp": datetime.now().strftime("%b %d, %Y - %I:%M %p")
        }
        
        mongo.db.requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": status,
                    "admin_comment": comment,
                    "updated_at": datetime.now()
                },
                "$push": {
                    "activity_log": log_entry
                }
            }
        )

    @staticmethod
    def add_rating(request_id, rating, rating_comment=""):
        mongo.db.requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "rating": int(rating),
                    "rating_comment": rating_comment,
                    "rated_at": datetime.now().strftime("%b %d, %Y - %I:%M %p")
                }
            }
        )

    @staticmethod
    def get_analytics():
        total = mongo.db.requests.count_documents({})
        pending = mongo.db.requests.count_documents({"status": "Pending"})
        in_progress = mongo.db.requests.count_documents({"status": "In Progress"})
        resolved = mongo.db.requests.count_documents({"status": "Resolved"})
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved
        }