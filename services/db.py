from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from services.settings import settings

engine = create_engine(settings.DB_CONNECTION, echo=False) # echo means SQL queries are printed in the terminal

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # autoflush means SQLAlchemy will not automatically send changes to db
# Session is a period of time when we interact with the database, and it is used to manage the transactions and the connection to the database.
# It begins when a user connects and logs in and ends when they disconnect or log out

Base = declarative_base()

# Import models after Base is created so their table metadata is registered.
import services.models  # noqa: F401

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()