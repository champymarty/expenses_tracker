from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.Models import *


engine = create_engine('sqlite:///expenses_tracker.db', echo=True)
Base.metadata.create_all(engine)
SessionLocal: sessionmaker = sessionmaker(bind=engine)



def create_default_users():
    """Create default users if they do not exist."""
    with SessionLocal() as session:
        session: Session
        raph = User(username="Raphael")
        prinPrin = User(username="Prin Prin")

        for user in (raph, prinPrin):
            if not session.query(User).filter_by(username=user.username).first():
                session.add(user)
                print(f"Added user: {user.username}")
        session.commit()

def create_default_sources():
    """Create default sources if they do not exist."""
    with SessionLocal() as session:
        session: Session
        sources = [
            ("BNC World Elite Mastercard", "BNC"),
            ("ROGER Mastercard Raph", "ROGER"),
            
        ]
        for source_name, type in sources:
            if not session.query(Source).filter_by(name=source_name).first():
                source = Source(name=source_name, type=type)
                session.add(source)
                print(f"Added source: {source.name}")
        session.commit()

create_default_users()
create_default_sources()