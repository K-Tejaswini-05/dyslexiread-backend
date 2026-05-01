from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_profile = Column(String(50), index=True) # child, teen, adult, custom
    session_time_seconds = Column(Integer, default=0)
    words_highlighted = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
