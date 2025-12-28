from flask import Flask
from flask_restful import Resource, Api

from services.image_service import ImageResource,ImageListResource
from services.device_service import DeviceResource,DeviceListResource
from services.prediction_service import PredictionResource,PredictionListResource
from services.fill_level_service import FillLevelResource,FillLevelListResource
from database.init import init_db, db_session

from image_classification.modelTools import predict, train_model

app = Flask(__name__)
api = Api(app)

init_db()

api.add_resource(ImageResource, '/api/images/<int:image_id>')
api.add_resource(ImageListResource, '/api/images')

api.add_resource(DeviceResource, '/api/devices/<int:device_id>')
api.add_resource(DeviceListResource, '/api/devices')

api.add_resource(PredictionResource, '/api/predictions/<int:prediction_id>')
api.add_resource(PredictionListResource, '/api/predictions')

api.add_resource(FillLevelResource, '/api/fill_levels/<int:fill_level_id>')
api.add_resource(FillLevelListResource, '/api/fill_levels')


@app.route('/api/images/predict', methods=['POST'])
def predict_image():
    pass

@app.route('/api/images/save', methods=['POST'])
def save_image():
    pass

if __name__ == "__main__":
    app.run(debug=True)

@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()