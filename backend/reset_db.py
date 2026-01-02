import os
import shutil
import uuid
import bcrypt
import pymongo
import logging
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'ems')

def main():
    logging.basicConfig(level=logging.INFO)
    print(f"Connecting to MongoDB at {MONGO_URL}, database '{DB_NAME}'")
    client = pymongo.MongoClient(MONGO_URL)

    # Drop the whole database
    print(f"Dropping database '{DB_NAME}'...")
    client.drop_database(DB_NAME)
    print("Database dropped.")

    # Clear uploads directory
    uploads_dir = ROOT / 'uploads'
    if uploads_dir.exists():
        print(f"Clearing uploads folder: {uploads_dir}")
        for child in uploads_dir.iterdir():
            try:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
            except Exception as e:
                print(f"Warning: could not remove {child}: {e}")
        print("Uploads cleared.")
    else:
        uploads_dir.mkdir(parents=True, exist_ok=True)
        print("Uploads folder created.")

    # Recreate a default admin user
    db = client[DB_NAME]
    users = db.users

    admin_username = os.environ.get('DEFAULT_ADMIN_USER', 'phanendra')
    admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', '123456')
    admin_role = os.environ.get('DEFAULT_ADMIN_ROLE', 'Admin')

    # Hash password with bcrypt to match server behavior
    hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    admin_doc = {
        'id': str(uuid.uuid4()),
        'username': admin_username,
        'role': admin_role,
        'password': hashed,
        'last_login': None,
        'status': 'active',
        'failed_attempts': 0,
    }

    users.insert_one(admin_doc)
    print(f"Inserted default admin user: {admin_username}")

    print("Reset complete.")


if __name__ == '__main__':
    main()
#!/usr/bin/env python
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt


def main():
    ROOT = Path(__file__).parent
    load_dotenv(ROOT / '.env')

    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'employee_management')

    print(f"Connecting to MongoDB: {mongo_url} (db: {db_name})")
    client = MongoClient(mongo_url)

    # Drop the database
    print(f"Dropping database '{db_name}'...")
    client.drop_database(db_name)
    print("Database dropped.")

    # Clear uploads directory
    uploads_dir = ROOT / 'uploads'
    if uploads_dir.exists() and uploads_dir.is_dir():
        print(f"Clearing uploads in: {uploads_dir}")
        for child in uploads_dir.iterdir():
            try:
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    shutil.rmtree(child)
            except Exception as e:
                print(f"  - Failed to remove {child}: {e}")
        print("Uploads cleared.")
    else:
        print("Uploads directory not found — skipping.")

    # Recreate minimal database and default admin user
    db = client[db_name]
    print("Creating default admin user 'phanendra' with password '123456'...")
    password_plain = "123456"
    hashed = bcrypt.hashpw(password_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    admin_doc = {
        "id": "admin-001",
        "username": "phanendra",
        "password": hashed,
        "role": "Admin",
        "status": "active",
        "last_login": None,
        "failed_attempts": 0
    }

    res = db.users.insert_one(admin_doc)
    print(f"Inserted admin user, mongo id: {res.inserted_id}")

    # Optional: create indexes or seed collections if desired
    print("Reset complete.")


if __name__ == '__main__':
    main()
