from fastapi_CRUD import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr
from typing import List
import bcrypt
from bson import ObjectId
import motor.motor_asyncio

app = FastAPI()

# Database connection
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.Sample


class User(BaseModel):
    name: str
    email: EmailStr
    password: str

# Create User


@app.post("/users", response_model=dict)
async def create_user(user: User):
    try:
        # Check if email already exists
        if await db.users.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already exists")

        # Hash password
        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'), bcrypt.gensalt())
        user_data = user.dict()
        user_data["password"] = hashed_password

        # Insert user into database
        db_response = await db.users.insert_one(user_data)
        return {"message": "User Created", "id": str(db_response.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating user")

# Get Users


@app.get("/users", response_model=List[dict])
async def get_some_users():
    try:
        data = await db.users.find().to_list(None)
        for user in data:
            user["_id"] = str(user["_id"])
            # Remove the password field from the response
            if 'password' in user:
                del user['password']
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Cannot read users")

# Update User


@app.patch('/users/{id}', response_model=dict)
async def update_user(id: str, user: User):
    try:
        ObjectId(id)  # Validate ObjectId
        update_data = user.dict(exclude_unset=True)

        db_response = await db.users.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if db_response.modified_count == 1:
            return {"message": "User Updated"}
        else:
            return {"message": "Nothing to update"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to update user")

# Delete User


@app.delete("/users/{id}", response_model=dict)
async def delete_user(id: str):
    try:
        ObjectId(id)  # Validate ObjectId
        db_response = await db.users.delete_one({"_id": ObjectId(id)})
        if db_response.deleted_count == 1:
            return {"message": "User Deleted"}
        else:
            return {"message": "Nothing to delete"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Sorry, cannot delete user")
