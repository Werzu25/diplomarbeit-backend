import base64
import io
import os
import uuid
from datetime import datetime

from flask import Flask, jsonify, make_response, request, send_file
from flask_restful import Api
from PIL import Image
from sqlalchemy import select

from database.init import db_session, init_db
from image_classification.modelTools import predict
from models.device_model import DeviceModel
from models.image_model import ImageModel
from models.prediction_model import LabelTypes, PredictionModel
from services.device_service import DeviceListResource, DeviceResource
from services.fill_level_service import FillLevelListResource, FillLevelResource
from services.image_service import ImageListResource, ImageResource
from services.prediction_service import PredictionListResource, PredictionResource

app = Flask(__name__)
api = Api(app)

init_db()

MODEL_PATH = os.getenv("MODEL_PATH", "image_classification/models/model.pth")
IMAGE_SAVE_PATH = os.getenv("IMAGE_SAVE_PATH", "./images")


def _resolve_device_identifiers():
    """Return identifiers used to upsert the current device record."""
    device_name = os.getenv("DEVICE_NAME", "device-unknown")
    location = os.getenv("DEVICE_LOCATION", "unknown-location")
    return device_name, location


def get_current_device():
    device_name, location = _resolve_device_identifiers()
    device = db_session.execute(
        select(DeviceModel).where(DeviceModel.device_name == device_name)
    ).scalar_one_or_none()

    now = datetime.now()

    if device is None:
        device = DeviceModel(
            device_name=device_name,
            location=location,
            device_up=True,
            last_update=now,
        )
        db_session.add(device)
    else:
        device.device_name = device_name
        device.device_up = True
        device.last_update = now
        if location is not None:
            device.location = location

    db_session.commit()
    return device


with app.app_context():
    device = get_current_device()
    device.device_up = True
    device.last_update = datetime.now()
    db_session.commit()

api.add_resource(ImageResource, "/api/image/<int:image_id>", "/api/image")
api.add_resource(ImageListResource, "/api/images")

api.add_resource(DeviceResource, "/api/device/<int:device_id>", "/api/device")
api.add_resource(DeviceListResource, "/api/devices")

api.add_resource(PredictionResource, "/api/prediction/<int:prediction_id>", "/api/prediction")
api.add_resource(PredictionListResource, "/api/predictions")

api.add_resource(FillLevelResource, "/api/fill_level/<int:fill_level_id>", "/api/fill_level")
api.add_resource(FillLevelListResource, "/api/fill_levels")

@app.route("/")
def home():
    return "Welcome to the Image Classification API"


def decode_image(image_data):
    image_bytes = base64.b64decode(image_data)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def get_image_predictions(decoded_image, model_path=MODEL_PATH):
    return predict(decoded_image, model_path)


def save_predictions(image_prediction_pairs):
    os.makedirs(IMAGE_SAVE_PATH, exist_ok=True)
    device = get_current_device()
    saved_images = 0

    for decoded_image, prediction in image_prediction_pairs:
        top_label, confidence = prediction[0]
        label_name = str(top_label).upper()
        try:
            label_enum = LabelTypes[label_name]
        except KeyError:
            db_session.rollback()
            raise ValueError(f"Unknown label '{top_label}'")

        label_dir = os.path.join(IMAGE_SAVE_PATH, label_name.lower())
        os.makedirs(label_dir, exist_ok=True)

        filename = f"{label_name.lower()}_{uuid.uuid4().hex}.png"
        decoded_image.save(os.path.join(label_dir, filename))

        new_image = ImageModel(
            path=os.path.join(label_name.lower(), filename),
            width=decoded_image.width,
            height=decoded_image.height,
            creation_date=datetime.now(),
        )
        db_session.add(new_image)
        db_session.flush()  # ensure we can reference new_image.id

        new_prediction = PredictionModel(
            image_id=new_image.id,
            device_id=device.id if device else None,
            prediction_label=label_enum,
            confidence=confidence,
            real_label=None,
        )
        db_session.add(new_prediction)
        saved_images += 1

    db_session.commit()
    return saved_images


def _parse_images_from_request():
    content = request.get_json(silent=True) or {}
    images = content.get("images")
    if images is None:
        return None, make_response(jsonify({"message": "No images provided"}), 400)
    if not isinstance(images, list) or len(images) == 0:
        return None, make_response(jsonify({"message": "Images must be a non-empty list"}), 400)
    return images, content


@app.route("/api/images/predict", methods=["POST"])
def predict_image():
    images, payload_or_response = _parse_images_from_request()
    if images is None:
        return payload_or_response  # already a response object
    content = payload_or_response

    decoded_images = [decode_image(image) for image in images]
    predictions = [get_image_predictions(image) for image in decoded_images]

    if content.get("save_images", True):
        save_predictions(zip(decoded_images, predictions))

    return make_response(jsonify(predictions), 200)


@app.route("/api/images/save", methods=["POST"])
def save_image():
    images, payload_or_response = _parse_images_from_request()
    if images is None:
        return payload_or_response

    decoded_images = [decode_image(image) for image in images]
    predictions = [get_image_predictions(image) for image in decoded_images]
    save_predictions(zip(decoded_images, predictions))

    return make_response(jsonify({"message": "Images saved successfully"}), 201)


@app.teardown_request
def shutdown_session(exception=None):
    device = get_current_device()
    device.device_up = False
    device.last_update = datetime.now()
    db_session.commit()
    db_session.close()

@app.route("/api/image/<path:image_path>", methods=["GET"])
def get_image(image_path):
    if os.path.exists(os.path.join(IMAGE_SAVE_PATH, image_path)):
        image = Image.open(os.path.join(IMAGE_SAVE_PATH, image_path))
        return send_file(os.path.join(IMAGE_SAVE_PATH, image_path), mimetype='image/png')
    return make_response(jsonify({"message": "Image not found"}), 404)

if __name__ == "__main__":
    app.run(debug=True)
