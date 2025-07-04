import datetime
import enum # Import the standard enum module
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    points = Column(Integer, default=0, nullable=False)

    tasks = relationship("Task", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', points={self.points})>"

class TaskStatus(enum.Enum): # Changed from SAEnum to enum.Enum
    PENDING = "pending"
    COMPLETED = "completed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    status = Column(SAEnum(TaskStatus, name="task_status_enum"), default=TaskStatus.PENDING, nullable=False)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completion_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, description='{self.description}', status='{self.status}', user_id={self.user_id})>"

# The engine creation and table creation logic is now primarily in app/db.py.
# The __main__ block here can be used for direct model testing if needed,
# but ensure it doesn't conflict with db.py's initialization.

if __name__ == "__main__":
    # This block is for isolated model testing if required.
    # For actual database initialization, run db.py or main.py.
    print("models.py executed directly. For DB setup, run db.py or the main application.")

    # Example of how one might test models in isolation (without full db setup from db.py):
    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker
    #
    # temp_engine = create_engine("sqlite:///:memory:") # Use in-memory DB for isolated test
    # Base.metadata.create_all(bind=temp_engine)
    # TempSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)
    # temp_db = TempSessionLocal()
    #
    # # Create a dummy user
    # user1 = User(username="testuser_isolated", password_hash="hashed_password", points=0)
    # temp_db.add(user1)
    # temp_db.commit()
    # temp_db.refresh(user1)
    # print(f"Created isolated user: {user1}")
    #
    # # Create a dummy task for the user
    # task1 = Task(description="Isolated test task", owner=user1)
    # temp_db.add(task1)
    # temp_db.commit()
    # temp_db.refresh(task1)
    # print(f"Created isolated task: {task1}")
    #
    # temp_db.close()
