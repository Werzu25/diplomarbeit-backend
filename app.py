import io
import base64

from flask import Flask, request,jsonify,make_response
from flask_restful import Resource, Api
from PIL import Image

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
    content = request.get_json(silent=True)
    predictions = []
    if not content:
        return make_response(jsonify({"message": "No input data provided"}), 400)
    
    if 'images' not in content:
        return make_response(jsonify({"message": "No images provided"}), 400)
    
    for image in content['images']:
        for cam, value in image.items():
            img = Image.open(io.BytesIO(base64.decodebytes(bytes(value, "utf-8"))))
            prediction = predict(img, "image_classification/model_weights.pth")
            predictions.append({
                "camera": cam,
                "prediction": prediction
            })
    return make_response(jsonify(predictions), 200)

@app.route('/api/images/save', methods=['POST'])
def save_image():
    pass

if __name__ == "__main__":
    app.run(debug=True)

@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()