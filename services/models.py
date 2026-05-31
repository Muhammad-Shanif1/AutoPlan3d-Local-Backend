from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from services.db import Base

# So: Model = DB structure, Schema = API input/output validation.

class UserModel(Base):
    __tablename__ = "Users_Table"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20))
    otp = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)


class ProjectModel(Base):
    __tablename__ = "Projects_Table"

    project_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_data = Column(JSONB, nullable=True) 
    user_id=Column(Integer,ForeignKey("Users_Table.id", ondelete="CASCADE")) # if user is deleted then all the tasks of that user will be deleted, 
