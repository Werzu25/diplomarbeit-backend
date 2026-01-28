import os
from flask import request, jsonify, make_response
from flask_restful import Resource
from marshmallow import ValidationError

from db.init import db_session
from models.image_model import ImageModel
from schemas import ImageSchema

image_schema = ImageSchema()
image_list_schema = ImageSchema(many=True)

class ImageResource(Resource):
    def get(self, image_id):
        image = db_session.query(ImageModel).get(image_id)
        if image is None:
            return make_response(jsonify({"message": "Image not found"}), 404)
        return make_response(jsonify(image_schema.dump(image)), 200)

    def put(self, image_id):
        image = db_session.query(ImageModel).get(image_id)
        if image is None:
            return make_response(jsonify({"message": "Image not found"}), 404)
        data = request.get_json(force=True)
        if not data:
            return make_response(jsonify({"message": "No input data provided"}), 400)

        try:
            image_schema.load(data, instance=image, partial=True)
        except ValidationError as err:
            return make_response(jsonify({"errors": err.messages}), 400)

        db_session.commit()
        return make_response(jsonify(image_schema.dump(image)), 200)

    def delete(self, image_id):
        image = db_session.query(ImageModel).get(image_id)
        if image is None:
            return make_response(jsonify({"message": "Image not found"}), 404)
        if os.path.exists(image.path):
            os.remove(image.path)
        db_session.delete(image)
        db_session.commit()
        return make_response(jsonify({"message": "Image deleted successfully"}), 200)

class ImageListResource(Resource):
    def get(self):
        images = db_session.query(ImageModel).all()
        return make_response(jsonify(image_list_schema.dump(images)), 200)
