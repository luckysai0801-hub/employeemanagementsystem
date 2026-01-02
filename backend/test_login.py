#!/usr/bin/env python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def main():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'employee_management')
    
    print(f"Connecting to: {mongo_url}")
    print(f"Database: {db_name}")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Check connection
        await client.admin.command('ismaster')
        print("✓ MongoDB connection successful")
        
        # Check if user exists
        user = await db.users.find_one({"username": "phanendra"})
        if user:
            print(f"✓ User 'phanendra' found in database")
            print(f"  - User ID: {user.get('id')}")
            print(f"  - Role: {user.get('role')}")
            print(f"  - Status: {user.get('status')}")
            print(f"  - Password hash exists: {'password' in user}")
            
            # Test password verification
            password_hash = user.get('password')
            test_password = "123456"
            
            if password_hash:
                try:
                    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8'))
                    print(f"  - Password '123456' verification: {'✓ PASS' if is_valid else '✗ FAIL'}")
                except Exception as e:
                    print(f"  - Password verification error: {e}")
            else:
                print("  - ERROR: No password hash found!")
        else:
            print("✗ User 'phanendra' NOT found - need to create it")
            # Create the user
            new_password = "123456"
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user_doc = {
                "id": "admin-001",
                "username": "phanendra",
                "password": password_hash,
                "role": "Admin",
                "status": "active",
                "last_login": None,
                "failed_attempts": 0
            }
            
            result = await db.users.insert_one(user_doc)
            print(f"✓ User created with ID: {result.inserted_id}")
            
            # Verify password works
            is_valid = bcrypt.checkpw(new_password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"  - Password verification: {'✓ PASS' if is_valid else '✗ FAIL'}")
        
        print("\n✓ Login system ready!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
