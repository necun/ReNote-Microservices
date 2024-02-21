import json

import pymongo
from bson.json_util import ObjectId
from flask import Flask, Response, request

app = Flask(__name__)

connection_string = "mongodb://root:root@localhost:27017/?authSource=admin"
app.config['MONGO_URI'] = "mongodb://root:root@localhost:27017/?authSource=admin"

try:
    mongo = pymongo.MongoClient(
        host='localhost',
        port=27017,
        username='root',
        password='root',
        serverSelectionTimeoutMS=1000
    )
    db = mongo.company
    mongo.server_info()
    print("Successfully connected to the database")
except pymongo.errors.ServerSelectionTimeoutError:
    print("Couldn't connect to the database. Please check your MongoDB connection settings.")


@app.route("/users", methods=["GET"])
def get_some_users():
    try:
        data = list(db.users.find())
        for user in data:
            user["_id"] = str(user["_id"])
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


@app.route("/users", methods=["POST"])
def create_user():
    try:
        user_data = request.get_json()
        user = {
            "name": user_data["name"],
            "email": user_data["email"],
            "password": user_data["password"]
        }
        db_response = db.users.insert_one(user)
        return Response(
            response=json.dumps(
                {"message": "User Created", "id": str(db_response.inserted_id)}),
            status=201,
            mimetype="application/json"
        )
    except Exception as e:
        print("**************")
        print(e)
        print("**************")


@app.route('/users/<id>', methods=['PATCH'])
def update_user(id):
    try:
        user_data = request.get_json()
        update_data = {}
        if "name" in user_data:
            update_data["name"] = user_data["name"]
        if "email" in user_data:
            update_data["email"] = user_data["email"]
        if "password" in user_data:
            update_data["password"] = user_data["password"]

        if update_data:
            dbResponse = db.users.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
            if dbResponse.modified_count == 1:
                return Response(
                    response=json.dumps(
                        {"message": "User Updated"}),
                    status=200,
                    mimetype="application/json"
                )
            else:
                return Response(
                    response=json.dumps(
                        {"message": "Nothing to update"}),
                    status=200,
                    mimetype="application/json"
                )
        else:
            return Response(
                response=json.dumps(
                    {"message": "No valid fields to update"}),
                status=400,
                mimetype="application/json"
            )
    except Exception as e:
        print("**************")
        print(e)
        print("**************")
        return Response(
            response=json.dumps(
                {"message": "Unable to update user"}),
            status=500,
            mimetype="application/json"
        )


@app.route("/users/<id>", methods=['DELETE'])
def delete_user(id):
    try:
        dbResponse = db.users.delete_one({"_id": ObjectId(id)})
        if dbResponse.deleted_count == 1:
            return Response(
                response=json.dumps(
                    {"message": "User Deleted"}),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps(
                    {"message": "Nothing to delete"}),
                status=200,
                mimetype="application/json"
            )
    except Exception as e:
        print("**************")
        print(e)
        print("**************")
        return Response(
            response=json.dumps(
                {"message": "Sorry Cannot Delete a User"}),
            status=500,
            mimetype="application/json"
        )


if __name__ == "__main__":
    app.run(debug=True)
# C:\Users\s_RvN\OneDrive\Desktop\Flask-Mongo-CRUD API\run.py
