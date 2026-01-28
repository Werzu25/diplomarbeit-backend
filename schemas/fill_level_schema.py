from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from db.init import db_session
from models.fill_level_model import FillLevelModel
# Import related model so the registry is aware during mapping
from models.device_model import DeviceModel  # noqa: F401


class FillLevelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FillLevelModel
        load_instance = True
        sqla_session = db_session
        include_fk = True
        include_relationships = False
