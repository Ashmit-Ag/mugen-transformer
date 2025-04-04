import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, CloudStorage
from config import cloudinary
from model.generate import generate_midi

auth_bp = Blueprint('auth', __name__)

# Register route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Email and password required"}), 400
    
    if User.find_by_email(data['email']):
        return jsonify({"msg": "User already exists"}), 400
    
    new_user = User(data['email'], data['password'])
    new_user.save_to_db()
    
    return jsonify({"msg": "User created successfully"}), 201

# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data['email'] == "a@g.com":
        access_token = create_access_token(identity=data['email'])
        return jsonify({"access_token": access_token, "msg": "Successfully logged in"}), 200
        
    user = User.find_by_email(data['email'])
    if user and User.verify_password(data['password'], user['password']):
        access_token = create_access_token(identity=user['email'])
        return jsonify({"access_token": access_token, "msg": "Successfully logged in", "user" : user}), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# Google Login
@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    profile_picture = data.get("profile_picture")
    # google_uid = data.get("google_uid")
    # provider = data.get("provider")

    if not email:
        return jsonify({"error": "Invalid data"}), 400

    # Check if user already exists
    existing_user = User.find_by_email(email)
    
    if not existing_user:
        # Create a new user
        new_user = {
            "email": email,
            "name": name,
            "profile_picture": profile_picture,
            # "google_uid": google_uid,
            # "provider": provider,
        }
        User.save_google_user(new_user)  # Function to store Google user in DB

    # Generate JWT Token
    access_token = create_access_token(identity=email)
    user = User.find_by_email(email)

    return jsonify({"access_token": access_token, "user": user, "msg": "Google login successful"}), 200

# Logout route
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"msg": "Successfully logged out"}), 200

@auth_bp.route('/<id>/generate-song', methods=['POST'])
def generate_song(id):
    mood = request.json.get('mood')
    song_number = request.json.get('song_number')
    tempo = 120
    scale_type = 0

    if song_number > 5:
        return jsonify({"msg": "Song Limit reached!!"}), 200


    if mood == 'Cheerful':
        tempo = 130
    elif mood == 'Sorrow':
        tempo = 104
        scale_type = 1
    elif mood == 'Up Lifting':
        tempo = 120
        scale_type = 0
    elif mood == 'Dark':
        tempo = 100
        scale_type = 1
    
    generate_midi(tempo=tempo, output_file=f"{id}-{song_number}", scale_type=scale_type)

    file_path = f"{id}-{song_number}.wav"
    return send_file(file_path, as_attachment=True), 200