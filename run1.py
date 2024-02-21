import json
import logging

import bcrypt
import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, Response, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Database connection
try:
    mongo = pymongo.MongoClient(
        host='localhost',
        port=27017,
        # username='root',
        # password='root',
        serverSelectionTimeoutMS=1000
    )
    db = mongo.Sample
    mongo.server_info()
    logging.info("Successfully connected to the database")
except pymongo.errors.ServerSelectionTimeoutError as e:
    logging.error(
        "Couldn't connect to the database. Please check your MongoDB connection settings.", exc_info=True)

# Marshmallow Schemas


class UserSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


user_schema = UserSchema()

# Create User


@app.route("/users", methods=["POST"])
def create_user():
    try:
        user_data = request.get_json()
        errors = user_schema.validate(user_data)
        if errors:
            return jsonify(errors), 400

        # Check if email already exists
        if db.users.find_one({"email": user_data["email"]}):
            return jsonify({"message": "Email already exists"}), 400

        # Hash password
        hashed_password = bcrypt.hashpw(
            user_data["password"].encode('utf-8'), bcrypt.gensalt())
        user_data["password"] = hashed_password

        # Insert user into database
        db_response = db.users.insert_one(user_data)
        return jsonify({"message": "User Created", "id": str(db_response.inserted_id)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        logging.error("Error creating user", exc_info=True)
        return jsonify({"message": "Error creating user"}), 500

# Get Users


@app.route("/users", methods=["GET"])
def get_some_users():
    try:
        data = list(db.users.find())
        for user in data:
            user["_id"] = str(user["_id"])
            # Remove the password field from the response
            if 'password' in user:
                del user['password']
        return Response(
            response=json.dumps(data),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        print(e)
        return Response(
            response=json.dumps({"message": "Cannot read users"}),
            status=500,
            mimetype="application/json"
        )


# Update User


@app.route('/users/<id>', methods=['PATCH'])
def update_user(id):
    try:
        ObjectId(id)  # Validate ObjectId
        user_data = request.get_json()
        update_data = user_schema.load(user_data, partial=True)

        db_response = db.users.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data})
        if db_response.modified_count == 1:
            return jsonify({"message": "User Updated"}), 200
        else:
            return jsonify({"message": "Nothing to update"}), 200
    except InvalidId:
        return jsonify({"message": "Invalid ObjectId format"}), 400
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        logging.error("Error updating user", exc_info=True)
        return jsonify({"message": "Unable to update user"}), 500

# Delete User


@app.route("/users/<id>", methods=['DELETE'])
def delete_user(id):
    try:
        ObjectId(id)  # Validate ObjectId
        db_response = db.users.delete_one({"_id": ObjectId(id)})
        if db_response.deleted_count == 1:
            return jsonify({"message": "User Deleted"}), 200
        else:
            return jsonify({"message": "Nothing to delete"}), 404
    except InvalidId:
        return jsonify({"message": "Invalid ObjectId format"}), 400
    except Exception as e:
        logging.error("Error deleting user", exc_info=True)
        return jsonify({"message": "Sorry, cannot delete user"}), 500


if __name__ == "__main__":
    app.run(debug=True)
