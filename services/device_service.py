from datetime import datetime
from flask import request, jsonify, make_response
from flask_restful import Resource
from marshmallow import ValidationError

from db.init import db_session
from models.device_model import DeviceModel
from schemas import DeviceSchema

device_schema = DeviceSchema()
device_list_schema = DeviceSchema(many=True)

class DeviceResource(Resource):
    def get(self, device_id):
        device = db_session.query(DeviceModel).get(device_id)
        if device is None:
            return make_response(jsonify({"message": "Device not found"}), 404)
        return make_response(jsonify(device_schema.dump(device)), 200)
    """
    def post(self):
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            new_device = device_schema.load(data)
        except ValidationError as err:
            return make_response(jsonify({"errors": err.messages}), 400)

        db_session.add(new_device)
        db_session.commit()
        return make_response(jsonify(device_schema.dump(new_device)), 201)
    """
    def put(self, device_id):
        device = db_session.query(DeviceModel).get(device_id)
        if device is None:
            return make_response(jsonify({"message": "Device not found"}), 404)

        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            device_schema.load(data, instance=device, partial=True)
        except ValidationError as err:
            return make_response(jsonify({"errors": err.messages}), 400)

        device.last_update = datetime.now()
        db_session.commit()
        return make_response(jsonify(device_schema.dump(device)), 200)

    def delete(self, device_id):
        device = db_session.query(DeviceModel).get(device_id)
        if device is None:
            return make_response(jsonify({"message": "Device not found"}), 404)

        db_session.delete(device)
        db_session.commit()
        return make_response(jsonify({"message": "Device deleted successfully"}), 200)

class DeviceListResource(Resource):
    def get(self):
        devices = db_session.query(DeviceModel).all()
        return make_response(jsonify(device_list_schema.dump(devices)), 200)
