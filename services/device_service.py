import datetime
from flask import request,jsonify,make_response
from flask_restful import Resource

from database.init import db_session
from models.device_model import DeviceModel

class DeviceResource(Resource):
    def get(self, device_id):
        device = db_session.query(DeviceModel).get(device_id)
        if device is None:
            return make_response(jsonify({"message": "Device not found"}), 404)
        return make_response(jsonify(device), 200)
    
    def post(self):
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        new_device = DeviceModel(**data)
        db_session.add(new_device)
        db_session.commit()
        return make_response(jsonify({"message": "Device created successfully", "device_id": new_device.id}), 201)

    def put(self, device_id):
        device = db_session.query(DeviceModel).get(device_id)
        device.last_update = datetime.now()
        if device is None:
            return make_response(jsonify({"message": "Device not found"}), 404)
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        for key, value in data.items():
            setattr(device, key, value)
        return make_response(jsonify({"message": "Device updated successfully"}), 200)

    def delete(self, device_id):
        device = db_session.query(DeviceModel).get(device_id)
        if device is None:
            return make_response(jsonify({"message": "Device not found"}), 404)
        db_session.delete(device)
        return make_response(jsonify({"message": "Device deleted successfully"}), 200)

class DeviceListResource(Resource):
    def get(self):
        devices = db_session.query(DeviceModel).all()
        if devices is None:
            return make_response(jsonify({"message": "No devices found"}), 404)
        return make_response(jsonify(devices), 200)