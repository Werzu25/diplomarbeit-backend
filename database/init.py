import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session

class Base(DeclarativeBase):
    pass

load_dotenv()
db_url =  os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(db_url, echo=True)
db_session = Session(engine,autoflush=True,autobegin=True)

def init_db():
    Base.metadata.create_all(bind=engine)