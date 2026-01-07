from datetime import datetime
from flask import request, jsonify, make_response
from flask_restful import Resource
from marshmallow import ValidationError

from database.init import db_session
from models.user_model import UserModel
from schemas import UserSchema

user_schema = UserSchema()
user_list_schema = UserSchema(many=True)


class UserResource(Resource):
    def get(self, user_id):
        user = db_session.query(UserModel).get(user_id)
        if user is None:
            return make_response(jsonify({"message": "User not found"}), 404)
        return make_response(jsonify(user_schema.dump(user)), 200)

    def post(self):
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            new_user = user_schema.load(data)
        except ValidationError as err:
            return make_response(jsonify({"errors": err.messages}), 400)

        if new_user.creation_date is None:
            new_user.creation_date = datetime.now()

        db_session.add(new_user)
        db_session.commit()
        return make_response(jsonify(user_schema.dump(new_user)), 201)

    def put(self, user_id):
        user = db_session.query(UserModel).get(user_id)
        if user is None:
            return make_response(jsonify({"message": "User not found"}), 404)

        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            user_schema.load(data, instance=user, partial=True)
        except ValidationError as err:
            return make_response(jsonify({"errors": err.messages}), 400)

        db_session.commit()
        return make_response(jsonify(user_schema.dump(user)), 200)

    def delete(self, user_id):
        user = db_session.query(UserModel).get(user_id)
        if user is None:
            return make_response(jsonify({"message": "User not found"}), 404)

        db_session.delete(user)
        db_session.commit()
        return make_response(jsonify({"message": "User deleted successfully"}), 200)


class UserListResource(Resource):
    def get(self):
        users = db_session.query(UserModel).all()
        return make_response(jsonify(user_list_schema.dump(users)), 200)
