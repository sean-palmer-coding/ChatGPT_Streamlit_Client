from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import uuid

DATABASE_URL = "sqlite:///conversations.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    title = Column(String, nullable=True)  # Add title field
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation")
    summary = relationship("Summary", uselist=False, back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="summary")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_conversation(db, conversation_id):
    print(f"Getting conversation with ID: {conversation_id}")
    return db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()

def create_conversation(db, conversation_id, user_id, title):
    try:
        print(f"Creating conversation with ID: {conversation_id}")
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        print(f"Created conversation: {conversation}")
        return conversation
    except Exception as e:
        print(f"Error creating conversation: {e}")
        db.rollback()

def add_message(db, conversation_id, role, content):
    try:
        print(f"Adding message to conversation ID: {conversation_id}")
        conversation = get_conversation(db, conversation_id)
        if conversation:
            message = Message(
                conversation_id=conversation.id,
                role=role,
                content=content
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            print(f"Added message: {message}")
            return message
    except Exception as e:
        print(f"Error adding message: {e}")
        db.rollback()

def get_all_conversations(db):
    try:
        print("Getting all conversations")
        return db.query(Conversation).all()
    except Exception as e:
        print(f"Error getting conversations: {e}")

def get_messages(db, conversation_id):
    try:
        print(f"Getting messages for conversation ID: {conversation_id}")
        conversation = get_conversation(db, conversation_id)
        if conversation:
            return db.query(Message).filter(Message.conversation_id == conversation.id).all()
    except Exception as e:
        print(f"Error getting messages: {e}")

def add_summary(db, conversation_id, summary_text):
    try:
        print(f"Adding summary to conversation ID: {conversation_id}")
        conversation = get_conversation(db, conversation_id)
        if conversation:
            summary = Summary(
                conversation_id=conversation.id,
                summary=summary_text
            )
            db.add(summary)
            db.commit()
            db.refresh(summary)
            print(f"Added summary: {summary}")
            return summary
    except Exception as e:
        print(f"Error adding summary: {e}")
        db.rollback()
