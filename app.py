import json

import pymongo
from bson.json_util import ObjectId
from flask import Flask, Response, jsonify, request

app = Flask(__name__)
connection_string = "mongodb://root:root@localhost:27017/?authSource=admin"
app.config['MONGO_URI'] = "mongodb://root:root@localhost:27017/?authSource=admin"

# Use a try-except block to handle connection errors more gracefully
try:
    mongo = pymongo.MongoClient(
        host='localhost',
        port=27017,
        username='root',
        password='root',
        serverSelectionTimeoutMS=1000
    )
    db = mongo.company
    mongo.server_info()  # ServerSelectionTimeoutError if we cannot connect to the database
    print("Successfully connected to the database")

except pymongo.errors.ServerSelectionTimeoutError:
    print("Couldn't connect to the database. Please check your MongoDB connection settings.")

#################################################

# Use the correct syntax for creating a list of dictionaries in JSON


@app.route("/users", methods=["GET"])
def get_some_users():
    try:
        print("Sample")
        data = list(db.users.find())
        print(data)
        for user in data:
            user["_id"] = str(user["_id"])
        return Response(
            response=json.dumps(data),
            status=200,  # Use 200 for success
            mimetype="application/json"
        )
    except Exception as e:
        print(e)
        return Response(
            response=json.dumps({"message": "Cannot read users"}),
            status=500,
            mimetype="application/json"
        )

#################################################

# Use the correct syntax for creating a dictionary in JSON


@app.route("/users", methods=["POST"])
def create_user():
    try:
        user = {
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"]
        }
        db_response = db.users.insert_one(user)
        print(db_response.inserted_id)
        return Response(
            response=json.dumps(
                {"message": "User Created", "id": str(db_response.inserted_id)}),
            status=201,  # Use 201 for resource creation
            mimetype="application/json"
        )
    except Exception as e:
        print("**************")
        print(e)
        print("**************")


######################################################
@app.route('/users/<id>', methods=['PATCH'])
def update_user(id):
    try:
        dbResponse = db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": request.form["name"]}}
            # {'$set': {"email": request.form["email"]}}
            # {'$set': {"password": request.form["password"]}}
        )
        # for attr in dir(dbResponse):
        #     print(f"**********{attr}********")
        if dbResponse.modified_count == 1:
            return Response(
                response=json.dumps(
                    {"message": "User Updates"}),
                status=200,  # Success
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps(
                    {"message": "Nohing to update"}),
                status=200,  # Internal Server Error
                mimetype="application/json"
            )
        return Response(
            response=json.dumps(
                {"message": "unable to update"}),
            status=200,  # Internal Server Error
            mimetype="application/json"
        )
    except Exception as e:
        print("**************")
        print(e)
        print("**************")
        return Response(
            response=json.dumps(
                {"message": "Unable to update user"}),
            status=500,  # Internal Server Error
            mimetype="application/json"
        )
######################################################


@app.route("/users/<id>", methods=['DELETE'])
def delete_user(id):
    try:
        dbResponse = db.users.delete_one({"_id": ObjectId(id)})
        # for attr in dir(dbResponse):
        #     print(f"**********{attr}********")
        if dbResponse.deleted_count == 1:
            return Response(
                response=json.dumps(
                    {"message": "User Deleted"}),
                status=200,  # Success
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps(
                    {"message": "Nohing to delete"}),
                status=200,  # Internal Server Error
                mimetype="application/json"
            )
        return Response(
            response=json.dumps(
                {"message": "User Deleted", "id": f"{id}"}),
            status=200,  # Success
            mimetype="application/json"
        )
    except Exception as e:
        print("**************")
        print(e)
        print("**************")
        return Response(
            response=json.dumps(
                {"message": "Sorry Cannot Delete a User"}),
            status=500,  # Internal Server Error
            mimetype="application/json"
        )


#######################################################
if __name__ == "__main__":
    app.run(debug=True)
