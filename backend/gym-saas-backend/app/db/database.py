from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

_engine = None
_SessionLocal = None

def _get_session_factory():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _SessionLocal

def get_db():
    db: Session = _get_session_factory()()
    try:
        yield db
    finally:
        db.close()
