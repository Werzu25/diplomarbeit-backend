from flask import request, jsonify, make_response
from flask_restful import Resource
from marshmallow import ValidationError

from db.init import db_session
from models.prediction_model import PredictionModel
from schemas import PredictionSchema

prediction_schema = PredictionSchema()
prediction_list_schema = PredictionSchema(many=True)

class PredictionResource(Resource):
    def get(self, prediction_id):
        prediction = db_session.query(PredictionModel).get(prediction_id)
        if prediction is None:
            return make_response(jsonify({"message": "Prediction not found"}), 404)
        return make_response(jsonify(prediction_schema.dump(prediction)), 200)
    
    def post(self):
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            new_prediction = prediction_schema.load(data)
        except ValidationError as err:
            return make_response(jsonify({"errors": err.messages}), 400)

        db_session.add(new_prediction)
        db_session.commit()
        return make_response(jsonify(prediction_schema.dump(new_prediction)), 201)

    def put(self, prediction_id):
        prediction = db_session.query(PredictionModel).get(prediction_id)
        if prediction is None:
            return make_response(jsonify({"message": "Prediction not found"}), 404)
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            prediction_schema.load(data, instance=prediction, partial=True)
        except ValidationError as err:
            return make_response(jsonify({"errors": err.messages}), 400)

        db_session.commit()
        return make_response(jsonify(prediction_schema.dump(prediction)), 200)

    def delete(self, prediction_id):
        prediction = db_session.query(PredictionModel).get(prediction_id)
        if prediction is None:
            return make_response(jsonify({"message": "Prediction not found"}), 404)
        db_session.delete(prediction)
        db_session.commit()
        return make_response(jsonify({"message": "Prediction deleted successfully"}), 200)

class PredictionListResource(Resource):
    def get(self):
        predictions = db_session.query(PredictionModel).all()
        return make_response(jsonify(prediction_list_schema.dump(predictions)), 200)


class PredictionByDeviceListResource(Resource):
    def get(self, device_id):
        predictions = (
            db_session.query(PredictionModel)
            .filter(PredictionModel.device_id == device_id)
            .order_by(PredictionModel.id.desc())
            .all()
        )
        return make_response(jsonify(prediction_list_schema.dump(predictions)), 200)


class PredictionByDeviceLatestResource(Resource):
    def get(self, device_id):
        prediction = (
            db_session.query(PredictionModel)
            .filter(PredictionModel.device_id == device_id)
            .order_by(PredictionModel.id.desc())
            .first()
        )
        if prediction is None:
            return make_response(jsonify({"message": "No predictions found for this device"}), 404)

        return make_response(jsonify(prediction_schema.dump(prediction)), 200)
