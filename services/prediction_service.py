from flask import request,jsonify,make_response
from flask_restful import Resource

from database.init import db_session
from models.prediction_model import PredictionModel

class PredictionResource(Resource):
    def get(self, prediction_id):
        prediction = db_session.query(PredictionModel).get(prediction_id)
        if prediction is None:
            return make_response(jsonify({"message": "Prediction not found"}), 404)
        return make_response(jsonify(prediction), 200)
    
    def post(self):
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        new_prediction = PredictionModel(**data)
        db_session.add(new_prediction)
        db_session.commit()
        return make_response(jsonify({"message": "Prediction created successfully", "prediction_id": new_prediction.id}), 201)

    def put(self, prediction_id):
        prediction = db_session.query(PredictionModel).get(prediction_id)
        if prediction is None:
            return make_response(jsonify({"message": "Prediction not found"}), 404)
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        for key, value in data.items():
            setattr(prediction, key, value)
        return make_response(jsonify({"message": "Prediction updated successfully"}), 200)

    def delete(self, prediction_id):
        prediction = db_session.query(PredictionModel).get(prediction_id)
        if prediction is None:
            return make_response(jsonify({"message": "Prediction not found"}), 404)
        db_session.delete(prediction)
        return make_response(jsonify({"message": "Prediction deleted successfully"}), 200)

class PredictionListResource(Resource):
    def get(self):
        predictions = db_session.query(PredictionModel).all()
        if predictions is None:
            return make_response(jsonify({"message": "No predictions found"}), 404)
        return make_response(jsonify(predictions), 200)