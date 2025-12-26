import os
from flask import request,jsonify,make_response
from flask_restful import Resource

from database.init import db_session
from models.image_model import ImageModel


class ImageResource(Resource):
    def get(self, image_id):
        image = db_session.query(ImageModel).get(image_id)
        if image is None:
            return make_response(jsonify({"message": "Image not found"}), 404)
        return make_response(jsonify(image), 200)

    def put(self, image_id):
        image = db_session.query(ImageModel).get(image_id)
        if image is None:
            return make_response(jsonify({"message": "Image not found"}), 404)
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        for key, value in data.items():
            setattr(image, key, value)
        return make_response(jsonify({"message": "Image updated successfully"}), 200)

    def delete(self, image_id):
        image = db_session.query(ImageModel).get(image_id)
        if image is None:
            return make_response(jsonify({"message": "Image not found"}), 404)
        if os.path.exists(image.path):
            os.remove(image.path)
        db_session.delete(image)
        return make_response(jsonify({"message": "Image deleted successfully"}), 200)

class ImageListResource(Resource):
    def get(self):
        images = db_session.query(ImageModel).all()
        if images is None:
            return make_response(jsonify({"message": "No images found"}), 404)
        return make_response(jsonify(images), 200)