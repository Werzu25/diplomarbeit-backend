from flask import Flask
from flask_restful import Resource, Api

from services.image_service import ImageResource,ImageListResource
from database.init import init_db

app = Flask(__name__)
api = Api(app)

api.add_resource(ImageResource, '/api/images/<int:image_id>')
api.add_resource(ImageListResource, '/api/images')

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    