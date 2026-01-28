from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from db.init import db_session
from models.device_model import DeviceModel
# Import related models so SQLAlchemy can configure relationships
from models.fill_level_model import FillLevelModel  # noqa: F401
from models.prediction_model import PredictionModel  # noqa: F401


class DeviceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DeviceModel
        load_instance = True
        sqla_session = db_session
        include_fk = True
        include_relationships = False
