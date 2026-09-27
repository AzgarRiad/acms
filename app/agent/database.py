from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = "postgresql://postgres:riad@localhost:5432/Riad"

engine = create_engine(db_url)

session = sessionmaker(autoflush= False, bind = engine)