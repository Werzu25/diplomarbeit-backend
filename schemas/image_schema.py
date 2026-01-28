from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from db.init import db_session
from models.image_model import ImageModel
# Import related model for relationship registration
from models.prediction_model import PredictionModel  # noqa: F401


class ImageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ImageModel
        load_instance = True
        sqla_session = db_session
        include_fk = True
        include_relationships = False
