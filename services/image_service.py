from flask import request,jsonify,make_response
from flask_restful import Resource

from database.init import db_session
from models.image_model import ImageModel


class ImageResource(Resource):
    def get(self, image_id):
        pass
    
    def post(self):
        pass

    def put(self, image_id):
        pass

    def delete(self, image_id):
        pass

class ImageListResource(Resource):
    def get(self):
        images = db_session.query(ImageModel).all()
        if images is None:
            return make_response(jsonify({"message": "No images found"}), 404)
        return make_response(jsonify(images), 200)