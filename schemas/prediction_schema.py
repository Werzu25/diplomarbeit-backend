from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from db.init import db_session
from models.prediction_model import LabelTypes, PredictionModel
# Import related models for relationship registration
from models.device_model import DeviceModel  # noqa: F401
from models.image_model import ImageModel  # noqa: F401
from schemas.fields import EnumField


class PredictionSchema(SQLAlchemyAutoSchema):
    prediction_label = EnumField(LabelTypes)
    real_label = EnumField(LabelTypes, allow_none=True)

    class Meta:
        model = PredictionModel
        load_instance = True
        sqla_session = db_session
        include_fk = True
        include_relationships = False
