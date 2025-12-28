from flask import Flask
from flask_restful import Resource, Api

from services.image_service import ImageResource,ImageListResource
from database.init import init_db, db_session

from image_classification.modelTools import predict, train_model

app = Flask(__name__)
api = Api(app)

api.add_resource(ImageResource, '/api/images/<int:image_id>')
api.add_resource(ImageListResource, '/api/images')

@app.route('/api/images/predict', methods=['POST'])
def predict_image():
    pass

@app.route('/api/images/save', methods=['POST'])
def save_image():
    pass

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()