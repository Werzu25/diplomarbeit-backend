from datetime import datetime
from flask import request, jsonify, make_response
from flask_restful import Resource
from marshmallow import ValidationError

from db.init import db_session
from models.fill_level_model import FillLevelModel
from schemas import FillLevelSchema

fill_level_schema = FillLevelSchema()
fill_level_list_schema = FillLevelSchema(many=True)

class FillLevelResource(Resource):
    def get(self, fill_level_id):
        fill_level = db_session.query(FillLevelModel).get(fill_level_id)
        if fill_level is None:
            return make_response(jsonify({"message": "Fill level not found"}), 404)
        return make_response(jsonify(fill_level_schema.dump(fill_level)), 200)

    def post(self):
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            new_fill_level = fill_level_schema.load(data)
        except ValidationError as e:
            return make_response(jsonify({"message": str(e)}), 400)
        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 500)
        new_fill_level.last_update = datetime.now()

        db_session.add(new_fill_level)
        db_session.commit()
        return make_response(jsonify(fill_level_schema.dump(new_fill_level)), 201)

    def put(self, fill_level_id):
        fill_level = db_session.query(FillLevelModel).get(fill_level_id)
        if fill_level is None:
            return make_response(jsonify({"message": "Fill level not found"}), 404)
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            fill_level_schema.load(data, instance=fill_level, partial=True)
        except ValidationError as e:
            return make_response(jsonify({"message": str(e)}), 400)

        fill_level.last_update = datetime.now()
        db_session.commit()
        return make_response(jsonify(fill_level_schema.dump(fill_level)), 200)

    def delete(self, fill_level_id):
        fill_level = db_session.query(FillLevelModel).get(fill_level_id)
        if fill_level is None:
            return make_response(jsonify({"message": "Fill level not found"}), 404)
        db_session.delete(fill_level)
        db_session.commit()
        return make_response(jsonify({"message": "Fill level deleted successfully"}), 200)

class FillLevelListResource(Resource):
    def get(self):
        fill_levels = db_session.query(FillLevelModel).all()
        return make_response(jsonify(fill_level_list_schema.dump(fill_levels)), 200)
