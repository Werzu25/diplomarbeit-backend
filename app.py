import uuid
import io
import os
import base64

from flask import Flask, request,jsonify,make_response
from flask_restful import Resource, Api
from PIL import Image
from sqlalchemy import select
from datetime import datetime

from models.device_model import DeviceModel

from models.image_model import ImageModel
from models.prediction_model import PredictionModel
from services.image_service import ImageResource,ImageListResource
from services.device_service import DeviceResource,DeviceListResource
from services.prediction_service import PredictionResource,PredictionListResource
from services.fill_level_service import FillLevelResource,FillLevelListResource
from database.init import init_db, db_session

from image_classification.modelTools import predict, train_model

app = Flask(__name__)
api = Api(app)

init_db()

def get_current_device():
    device_name = os.getenv("DEVICE_NAME", "device-unknown")
    location = os.getenv("DEVICE_LOCATION", "unknown-location")

    device = db_session.execute(
        select(DeviceModel).where(DeviceModel.device_name == device_name)
    ).scalar_one_or_none()

    now = datetime.now()

    if device is None:
        device = DeviceModel(
            id=0,
            unique_device_id= unique_device_id,
            device_name=device_name,
            location=location,
            device_up=True,
            last_update=now
        )
        db_session.add(device)
    else:
        device.device_up = True
        device.last_update = now
        if location is not None:
            device.location = location
    return device

with app.app_context():
    get_current_device()

api.add_resource(ImageResource, '/api/image/<int:image_id>','/api/image')
api.add_resource(ImageListResource, '/api/images')

api.add_resource(DeviceResource, '/api/device/<string:unique_device_id>','/api/device')
api.add_resource(DeviceListResource, '/api/devices')

api.add_resource(PredictionResource, '/api/prediction/<int:prediction_id>','/api/prediction')
api.add_resource(PredictionListResource, '/api/predictions')

api.add_resource(FillLevelResource, '/api/fill_level/<int:fill_level_id>','/api/fill_level')
api.add_resource(FillLevelListResource, '/api/fill_levels')

@app.route('/')
def home():
    return "Welcome to the Image Classification API"

def decode_image(image_data):
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    return image

def get_image_predictions(image, model_path="image_classification/models/model v3.pth"):
    prediction = predict(decode_image(image), model_path)
    return prediction

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
        prediction = get_image_predictions(image)
        predictions.append(prediction)

    if save_images:
        save_image(zip(image_list, predictions))
    return make_response(jsonify(predictions), 200)

@app.route('/api/images/save', methods=['POST'])
def save_image(content = None):
    image_list = []
    if content is None:
        content = request.get_json(silent=True)
        if not content:
            return make_response(jsonify({"message": "No input data provided"}), 400)
        
        if 'images' not in content:
            return make_response(jsonify({"message": "No images provided"}), 400)
        image_list = content['images']
        for image in image_list:
            prediction = get_image_predictions(image)
            decoded_image = decode_image(image)
            image_save_path = os.getenv("IMAGE_SAVE_PATH", "./images")
            if not os.path.exists(image_save_path):
                os.makedirs(image_save_path)
            
            top_prediction = prediction[0]
            filename = f"{top_prediction}_{uuid.uuid4().hex}.png"
            decoded_image.save(os.path.join(image_save_path, filename))
            new_image = ImageModel(
                id=0,
                path=filename,
                width=decoded_image.width,
                height=decoded_image.height,
                creation_date= datetime.now()
            )
            db_session.add(new_image)

            new_prediction = PredictionModel(
                id=0,
                image_id=new_image.id,
                device_id=get_current_device().id,
                prediction_label=top_prediction[0],
                confidence=top_prediction[1],
                real_label=None,
            )
            db_session.add(new_prediction)

            return make_response(jsonify({"message": "Images saved successfully"}), 201)
        else:
            for image, prediction in image_list:
                decoded_image = decode_image(image)
                image_save_path = os.getenv("IMAGE_SAVE_PATH", "./images")
                if not os.path.exists(image_save_path):
                    os.makedirs(image_save_path)
                
                top_prediction = prediction[0]
                filename = f"{top_prediction}_{uuid.uuid4().hex}.png"
                decoded_image.save(os.path.join(image_save_path, filename))
                new_image = ImageModel(
                    id=0,
                    path=filename,
                    width=decoded_image.width,
                    height=decoded_image.height,
                    creation_date= datetime.now()
                )
                db_session.add(new_image)

                new_prediction = PredictionModel(
                    id=0,
                    image_id=new_image.id,
                    device_id=get_current_device().id,
                    prediction_label=top_prediction[0],
                    confidence=top_prediction[1],
                    real_label=None,
                )
                db_session.add(new_prediction)
        return make_response(jsonify({"message": "Images saved successfully"}), 201)



if __name__ == "__main__":
    app.run(debug=True)

@app.teardown_request
def shutdown_session(exception=None):
    db_session.close()