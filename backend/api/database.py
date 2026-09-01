import os
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# Uses DATABASE_URL from environment for production (PostgreSQL on Neon).
# Falls back to local SQLite for development.
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./rag_audit.db")

# check_same_thread is only needed for SQLite
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ReviewLog(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    repo = Column(String, index=True)
    pr_number = Column(Integer)
    file_path = Column(String)
    line_number = Column(Integer)
    category = Column(String)
    severity = Column(String)
    comment = Column(Text)
    # Storing the trace: what chunks were cited
    cited_chunks = Column(JSON) 

# Create tables
Base.metadata.create_all(bind=engine)
