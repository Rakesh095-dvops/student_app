from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from bson.regex import Regex
from dotenv import load_dotenv
import os

# Initialize Flask app
app = Flask(__name__)


# Load environment variables from .env file
load_dotenv()
# Read variables from .env
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")

try:
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]
    students_collection = db[collection_name]
    print(f"Connected to collection: {collection_name} in database: {db_name}") 
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

def requestvalidation(_data):
    if not any([
        _data.get("name"), 
        _data.get("age")
        ]):
        return False  # At least one of name, price, or quantity is required
    else:
        return True

# Database functions
def add_student(data):
    try:
        data=request.get_json()
        student = {"name": data["name"], "age": data["age"]}
        result = students_collection.insert_one(student)
        student["_id"] = str(result.inserted_id)  # Convert ObjectId to string
        return student
    except Exception as e :
        return jsonify({'error': "request body in not correct " + str(e)}), 500 

def get_students():
    return [{"_id": str(student["_id"]), "name": student["name"], "age": student["age"]} for student in students_collection.find()]

def get_student_by_id(student_id):
    student = students_collection.find_one({"_id": ObjectId(student_id)})
    if student:
        student["_id"] = str(student["_id"])  # Convert ObjectId to string
    return student

def delete_student(student_id):
    result = students_collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count > 0:
        return {"message": "Deleted"}
    return {"error": "Student not found"}

# Flask routes
@app.route('/')
def home():
    return "Welcome to the Student Management System API!", 200

@app.route('/students', methods=['POST'])
def add():
    data = request.get_json()
    if "name" not in data or "age" not in data:
        return jsonify({"error": "Missing 'name' or 'age'"}), 400
    return jsonify(add_student(data)), 201

@app.route('/students', methods=['GET'])
def get_all():
    return jsonify(get_students()), 200

@app.route('/students/<string:student_id>', methods=['GET'])
def get_by_id(student_id):
    student = get_student_by_id(student_id)
    if student:
        return jsonify(student), 200
    return jsonify({"error": "Student not found"}), 404

@app.route('/students/<string:student_id>', methods=['DELETE'])
def delete(student_id):
    return jsonify(delete_student(student_id)), 200

@app.route('/students/name/<string:name>', methods=['GET'])
def get_by_name(name):
    # Use regex to find students by name
    students = students_collection.find({"name": {"$regex": f".*{name}.*", "$options": "i"}})
    students_list = [{"_id": str(student["_id"]), "name": student["name"], "age": student["age"]} for student in students]
    if students_list:
        return jsonify(students_list), 200
    return jsonify({"error": "No students found with the given name"}), 404

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)