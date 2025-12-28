from flask import request,jsonify,make_response
from flask_restful import Resource

from database.init import db_session
from models.fill_level_model import FillLevelModel

class FillLevelResource(Resource):
    def get(self, fill_level_id):
        fill_level = db_session.query(FillLevelModel).get(fill_level_id)
        if fill_level is None:
            return make_response(jsonify({"message": "Fill level not found"}), 404)
        return make_response(jsonify(fill_level), 200)

    def post(self):
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        new_fill_level = FillLevelModel(**data)
        db_session.add(new_fill_level)
        db_session.commit()
        return make_response(jsonify({"message": "Fill level created successfully", "fill_level_id": new_fill_level.id}), 201)

    def put(self, fill_level_id):
        fill_level = db_session.query(FillLevelModel).get(fill_level_id)
        if fill_level is None:
            return make_response(jsonify({"message": "Fill level not found"}), 404)
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        for key, value in data.items():
            setattr(fill_level, key, value)
        return make_response(jsonify({"message": "Fill level updated successfully"}), 200)

    def delete(self, fill_level_id):
        fill_level = db_session.query(FillLevelModel).get(fill_level_id)
        if fill_level is None:
            return make_response(jsonify({"message": "Fill level not found"}), 404)
        db_session.delete(fill_level)
        return make_response(jsonify({"message": "Fill level deleted successfully"}), 200)

class FillLevelListResource(Resource):
    def get(self):
        fill_levels = db_session.query(FillLevelModel).all()
        if fill_levels is None:
            return make_response(jsonify({"message": "No fill levels found"}), 404)
        return make_response(jsonify(fill_levels), 200)