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

api.add_resource(ImageResource, '/api/image/<int:image_id>','/api/image')
api.add_resource(ImageListResource, '/api/images')

api.add_resource(DeviceResource, '/api/device/<int:device_id>','/api/device')
api.add_resource(DeviceListResource, '/api/devices')

api.add_resource(PredictionResource, '/api/prediction/<int:prediction_id>','/api/prediction')
api.add_resource(PredictionListResource, '/api/predictions')

api.add_resource(FillLevelResource, '/api/fill_level/<int:fill_level_id>','/api/fill_level')
api.add_resource(FillLevelListResource, '/api/fill_levels')

@app.route('/')
def home():
    return "Welcome to the Image Classification API"

@app.route('/api/images/predict', methods=['POST'])
def predict_image():
    content = request.get_json(silent=True)
    predictions = []
    if not content:
        return make_response(jsonify({"message": "No input data provided"}), 400)
    
    if 'images' not in content:
        return make_response(jsonify({"message": "No images provided"}), 400)
    
    save_images = content["save_images"] if "save_images" in content else True
    image_list = content['images']
    for image in image_list:
        decoded_image = Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))
        prediction = predict(decoded_image, "image_classification/models/model v3.pth")
        predictions.append({
            "image": image_list.index(image),
            "prediction": prediction
        })
    if save_images:
        save_image(zip(image_list, predictions))
    return make_response(jsonify(predictions), 200)

@app.route('/api/images/save', methods=['POST'])
def save_image(content = None):
    if content is None:
        content = request.get_json(silent=True)
    if not content:
        return make_response(jsonify({"message": "No input data provided"}), 400)
    

if __name__ == "__main__":
    app.run(debug=True)

@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()