import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

Base = declarative_base()


class TodoUser(Base):
    __tablename__ = "todo_users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True)

    tasks = relationship("TodoTask", back_populates="user")


class TodoCategory(Base):
    __tablename__ = "todo_categories"

    id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)

    tasks = relationship("TodoTask", back_populates="category")


class TodoTask(Base):
    __tablename__ = "todo_tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("todo_users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("todo_categories.id"), nullable=False)
    title = Column(String, nullable=False)
    done = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("TodoUser", back_populates="tasks")
    category = relationship("TodoCategory", back_populates="tasks")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)