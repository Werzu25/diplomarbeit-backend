from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from database.init import db_session
from models.user_model import UserModel


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        sqla_session = db_session
        include_fk = True
        include_relationships = False
