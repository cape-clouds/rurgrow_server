import os
import dotenv
from flask import Flask
from db import Connection
from dotenv import load_dotenv
# from Flask_cors import CORS
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from werkzeug.utils import secure_filename
import json
from bson import ObjectId
import cloudinary
import cloudinary.uploader
from bson import objectid



from uuid import uuid1
from flask import request, jsonify
from utils import my_global_function

load_dotenv()
app = Flask(__name__)
# CORS(app)
CORS(app, origins='*')

# CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://example.com"]}})

db = Connection('rurgrow')
#
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")  #

jwt = JWTManager(app)


UPLOAD_FOLDER = 'uploads'

cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('api_key'),
    api_secret = os.getenv('api_secret')
    )
g_name = os.getenv('NAME')
print(f'Cloud Name: {g_name}')


@app.route('/')
def home():
    return my_global_function()


# @app.route("/token", methods=["POST"])
# def create_token():
#         username = request.json.get("username", None)
#         password = request.json.get("password", None)
#         if username != "test" or password != "test":
#             return jsonify({"msg": "Bad username or password"}), 401
#
#         access_token = create_access_token(identity=username)
#         return jsonify(access_token=access_token, username=username)

#
# @app.route('/get_all_categories', methods=['GET'])
# def get_all_categories():
#     try:
#         # Access the 'categories' collection
#         categories_collection = db['categories']
#
#         # Fetch all documents from the collection
#         categories = list(categories_collection.find({}))
#
#         # Exclude MongoDB object IDs from the response if needed
#         for category in categories:
#             category.pop('_id', None)
#
#         # Return the categories data as a JSON response
#         return jsonify({"data": categories}), 200
#     except Exception as e:
#         print(f"Error fetching data: {e}")
#         return jsonify({"error": "An error occurred while fetching data"}), 500

@app.route('/get_all_categories', methods=['GET'])
def get_all_categories():
    try:
        # Access the 'categories' collection
        categories_collection = db['categories']

        # Fetch all documents from the collection
        categories = list(categories_collection.find({}))

        # Exclude MongoDB object IDs from the response if needed
        for category in categories:
            category.pop('_id', None)

        # Return the categories data as a JSON response
        return jsonify({"data": categories}), 200
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route("/token", methods=["POST"])
def create_token():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = db.user.find_one({"username": username, "password": password})
    if user:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token, username=username), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401



@app.route("/check_token", methods=["POST"])
@jwt_required()
def check_token():
    try:
        # Check if JWT is present in the request
        # verify_jwt_in_request_optional()

        # If JWT is present, get the identity of the current user
        current_user = get_jwt_identity()

        # Return true if the token is valid
        return jsonify(valid=True), 200
    except Exception as e:
        # Return false if the token is not valid or if an error occurred
        return jsonify(valid=False), 200


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

    # @app.post("/user")
    # def insert_user():
    #     _id = str(uuid1().hex)
    #     content = dict(request.json)
    #     content.update({"_id": _id})
    #
    #     result = db.user.insert_one(content)
    #     if not result.inserted_id:
    #         return jsonify({"message": "Failed to insert"}), 500
    #
    #     return jsonify({
    #         "message": "Success",
    #         "data": {"id": str(result.inserted_id)}
    #     }), 200


user_schema = {
    "username": str,
    "password": str
}


# @app.post("/user")
# def insert_user():
#     _id = str(uuid1().hex)
#     content = request.json
#
#     # Validate the incoming data against the schema
#     for field, field_type in user_schema.items():
#         if field not in content:
#             return jsonify({"message": f"Missing required field: {field}"}), 400
#         if not isinstance(content[field], field_type):
#             return jsonify({"message": f"Invalid type for field {field}. Expected {field_type.__name__}"}), 400
#
#     content.update({"_id": _id})
#
#     result = db.user.insert_one(content)
#     if not result.inserted_id:
#         return jsonify({"message": "Failed to insert"}), 500
#
#     return jsonify({
#         "message": "Success",
#         "data": {"id": str(result.inserted_id)}
#     }), 200


# bottom works da wise but now stopped .............
# @app.post("/user")
# def insert_user():
#     collection = db["user"]
#     count = collection.count_documents({})
#     new_id = count + 1
#     content = request.json
#     # Validate the incoming data against the schema
#     for field, field_type in user_schema.items():
#         if field not in content:
#             return jsonify({"message": f"Missing required field: {field}"}), 400
#         if not isinstance(content[field], field_type):
#             return jsonify({"message": f"Invalid type for field {field}. Expected {field_type.__name__}"}), 400
#
#     content.update({"_id": new_id})
#
#     result = collection.insert_one(content)
#     if not result.inserted_id:
#         return jsonify({"message": "Failed to insert"}), 500
#
#     return jsonify({
#         "message": "Success",
#         "data": {"id": str(result.inserted_id)}
#     }), 200

@app.post("/user")
def insert_user():
    collection = db["user"]
    content = request.json

    # Validate the incoming data against the schema
    for field, field_type in user_schema.items():
        if field not in content:
            return jsonify({"message": f"Missing required field: {field}"}), 400
        if not isinstance(content[field], field_type):
            return jsonify({"message": f"Invalid type for field {field}. Expected {field_type.__name__}"}), 400

    # Use ObjectId for _id generation
    content["_id"] = ObjectId()

    result = collection.insert_one(content)
    if result.inserted_id:
        # Return a 201 Created status and include the new object ID in the response
        return jsonify({
            "message": "User created successfully",
            "data": {"id": str(content["_id"])}
        }), 201
    else:
        return jsonify({"message": "Failed to insert user"}), 500


# @app.route('/users', methods=['GET'])
# def get_users():
#     users = db.user.find({})
#     return jsonify({"data": list(users)}), 200


@app.route('/users', methods=['GET'])
def get_users():
    try:
        # Define the fields you want to include in the response
        projection = {
            'firstName': 1,
            'lname': 1,
            'title': 1,
            'email': 1,
            'address': 1,
            # Add other fields you want to include
            '_id': 0  # Exclude the MongoDB ObjectId field
        }

        users = db.clients.find({}, projection)
        user_list = list(users)
        if not user_list:
            return jsonify({"message": "No users found"}), 204

        return jsonify({"data": user_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get_user_name', methods=['GET'])
def get_user_name():
    get_user = db.user.find({})
    usernames = [user.get('username') for user in get_user if 'username' in user]
    return jsonify({"data": usernames}), 200


#  registration save section

register_schema = {
    "name": str,
    "email": str
}





# @app.post("/registerForm")
# def insert_register():
#     # Extract data from the request form
#     name = request.form.get("name")
#     email = request.form.get("email")
#     first_name = request.form.get("firstName")
#     last_name = request.form.get("LastName")
#     serviceType = request.form.get("serviceType")
#     title = request.form.get("title")
#     service_description = request.form.get("service_description")
#     phone = request.form.get("phone")
#     address = request.form.get("address")
#     insta = request.form.get("insta")
#     fb = request.form.get("fb")
#     twitter = request.form.get("twitter")
#
#
#     # Validate the incoming data against the schema
#     for field, field_type in register_schema.items():
#         if field not in request.form:
#             return jsonify({"message": f"Missing required field: {field}"}), 400
#         if not isinstance(request.form[field], field_type):
#             return jsonify({"message": f"Invalid type for field {field}. Expected {field_type.__name__}"}), 400
#
#     # Check if the folder exists for the user based on 'name'
#     user_folder = os.path.join(UPLOAD_FOLDER, secure_filename(name))
#     if not os.path.exists(user_folder):
#         os.makedirs(user_folder)  # Create a new folder if it doesn't exist
#
#     # Save uploaded files to the user's folder
#     for file in request.files.getlist('files'):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(user_folder, filename))
#
#     # Define the filter to check if a document with the same name exists
#     filter_query = {"name": name}
#
#     # Define the update operation to set or update the document
#     update_operation = {
#         "$set": {
#             "name": name,
#             "email": email,
#             "firstName": first_name,
#             "LastName": last_name,
#             "serviceType": serviceType,
#             "title":title,
#             "service_description":service_description,
#             "phone":phone,
#             "address":address,
#             "insta":insta,
#             "fb":fb,
#             "twitter":twitter
#
#
#
#         }
#     }
#
#     # Use update_one with upsert=True to insert or update the document
#     result = db.clients.update_one(filter_query, update_operation, upsert=True)
#
#     if result.modified_count > 0:
#         return jsonify({"message": "Data updated successfully"}), 200
#     elif result.upserted_id:
#         return jsonify({"message": "Data inserted successfully"}), 200
#     else:
#         return jsonify({"message": "Failed to insert or update data"}), 500
#
#



@app.post("/registerForm")
def insert_register():
    # Extract data from the request form
    name = request.form.get("name")
    email = request.form.get("email")
    first_name = request.form.get("firstName")
    last_name = request.form.get("LastName")
    serviceType = request.form.get("serviceType")
    title = request.form.get("title")
    service_description = request.form.get("service_description")
    phone = request.form.get("phone")
    address = request.form.get("address")
    insta = request.form.get("insta")
    fb = request.form.get("fb")
    twitter = request.form.get("twitter")
    whatsapp = request.form.get("whatsapp")

    # Check if the folder exists for the user based on 'name'
    user_folder = os.path.join(UPLOAD_FOLDER, secure_filename(name))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)  # Create a new folder if it doesn't exist

    # Save uploaded files to the user's folder
    for file in request.files.getlist('files'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(user_folder, filename))

    # Define the filter to check if a document with the same name exists
    # filter_query = {"name": name}

    # Define the update operation to set or update the document
    update_operation = {
        "$set": {
            "name": name,
            "email": email,
            "firstName": first_name,
            "LastName": last_name,
            "serviceType": serviceType,
            "title": title,
            "service_description": service_description,
            "phone": phone,
            "address": address,
            "insta": insta,
            "fb": fb,
            "twitter": twitter,
            "whatsapp": whatsapp
        }
    }

    # Use update_one with upsert=True to insert or update the document
    # result = db.clients.update_one(filter_query, update_operation, upsert=True)
    # result = db.clients.update_one( update_operation, upsert=True)
    result = db.clients.update_one({}, update_operation, upsert=True)

    if result.modified_count > 0:
        return jsonify({"message": "Data updated successfully"}), 200
    elif result.upserted_id:
        return jsonify({"message": "Data inserted successfully"}), 200
    else:
        return jsonify({"message": "Failed to insert or update data"}), 500


@app.post("/api/categories")
def add_category():
    data = request.json
    category_name = data.get("name")

    if not category_name:
        return jsonify({"message": "Name is required for adding a category"}), 400

    # Insert the category into the 'categories' collection in MongoDB
    result = db.categories.insert_one({"name": category_name})

    if result.inserted_id:
        return jsonify({"message": "Category added successfully"}), 200
    else:
        return jsonify({"message": "Failed to add category"}), 500

# Route to fetch all categories
@app.get("/api/categories")
def get_categories():
    categories = db.categories.find({}, {"_id": 0, "name": 1})
    category_list = [category.get('name') for category in categories]
    return jsonify({"data": category_list}), 200


# value = objectid()
# def convert_object_ids_to_strings(data):
#     if isinstance(data, dict):
#         for key, value in data.items():
#             if isinstance(value, objectid):
#                 data[key] = str(value)
#             elif isinstance(value, (dict, list)):
#                 convert_object_ids_to_strings(value)
#     elif isinstance(data, list):
#         for i, item in enumerate(data):
#             if isinstance(item, objectid):
#                 data[i] = str(item)
#             elif isinstance(item, (dict, list)):
#                 convert_object_ids_to_strings(item)


# @app.route("/registerDetails", methods=["GET"])
# @jwt_required()
# def get_register():
#     userdetail = db.clients.find({})

@app.route('/services', methods=['GET'])
def get_services():
    slug = request.args.get('slug')
    if not slug:
        return jsonify({"message": "Missing slug parameter"}), 400

    userdetail = db.clients.find({"serviceType": slug})
    userdetail_serialized = []
    for user in userdetail:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        userdetail_serialized.append(user)

    if not userdetail_serialized:
        return jsonify({"message": "No matching services found"}), 404

    return jsonify({"data": userdetail_serialized}), 200

# working all paste work
# @app.route('/registerDetails', methods=['GET'])
# def get_register():
#     userdetail = db.clients.find({})
#     userdetail_serialized = []
#     for user in userdetail:
#         user['_id'] = str(user['_id'])  # Convert ObjectId to string
#         userdetail_serialized.append(user)
#     return jsonify({"data": userdetail_serialized}), 200

# @app.route('/registerDetailsUsername', methods=['GET'])
# def get_register_user():
#     username = request.args.get('username')
#     userdetail_serialized = []
#
#     if username:
#         userdetail = db.clients.find({"username": username})
#         for user in userdetail:
#             user['_id'] = str(user['_id'])  # Convert ObjectId to string
#             userdetail_serialized.append(user)
#     else:
#         return jsonify({"error": "Username is required"}), 400
#
#     # return jsonify({"data": userdetail_serialized}), 200
#     return jsonify({"data": userdetail_serialized}), 200


@app.route('/registerDetails', methods=['POST'])
def register_details():
    data = request.form.to_dict()
    first_name = data.get('firstName', 'default_user')
    profile_picture = request.files.get('profilePicture')
    cover_picture = request.files.get('coverPicture')
    additional_images = request.files.getlist('images')

    # Upload images to Cloudinary and get the URLs
    if profile_picture:
        profile_picture_result = cloudinary.uploader.upload(
            profile_picture,
            folder=f"{first_name}/profile_picture",
            transformation=[
                {'quality': 'good'}
            ]
        )
        profile_picture_url = profile_picture_result['secure_url']
        data['profile_picture'] = profile_picture_url

    if cover_picture:
        cover_picture_result = cloudinary.uploader.upload(
            cover_picture,
            folder=f"{first_name}/cover_picture",
            transformation=[
                {'quality': 'good'}
            ]
        )
        cover_picture_url = cover_picture_result['secure_url']
        data['cover_picture'] = cover_picture_url

    image_urls = []
    for index, image in enumerate(additional_images):
        upload_result = cloudinary.uploader.upload(
            image,
            folder=f"{first_name}/additional_images",
            public_id=f"image_{index + 1}",
            transformation=[
                {'quality': 'good'}
            ]
        )
        image_urls.append(upload_result['secure_url'])
    data['images'] = image_urls

    # Save to MongoDB
    result = db.clients.insert_one(data)
    return jsonify({'status': 'success', 'data': str(result.inserted_id)}), 201

@app.route('/registerDetailsUsername', methods=['GET'])
def get_user_details_by_username():

    username = request.args.get('username')
    if not username:
        return jsonify({"message": "Missing username parameter"}), 400

    userdetail = db.clients.find({"title": username})
    userdetail_serialized = []
    for user in userdetail:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        userdetail_serialized.append(user)

    if not userdetail_serialized:
        return jsonify({"message": "No matching user details found"}), 404

    return jsonify({"data": userdetail_serialized}), 200


@app.route('/get_user_title', methods=['GET'])
def get_user_title():
    title = request.args.get('title')
    if not title:
        return jsonify({'status': 'error', 'message': 'Title parameter is missing'}), 400

    user_detail = db.clients.find_one({'title': title})
    if user_detail:
        user_detail['_id'] = str(user_detail['_id'])  # Convert ObjectId to string
        return jsonify({'status': 'success', 'data': user_detail}), 200
    else:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404


if __name__ == "__main__":
    app.run(port=8887, debug=True)

# if __name__ == "__main__":
#     from waitress import serve
#     serve(app, host="0.0.0.0", port=8887)
