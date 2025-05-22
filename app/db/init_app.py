# import logging
# from sqlalchemy.orm import Session

# from app.db.init_db import init_db
# from app.db.session import SessionLocal

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def init() -> None:
#     db = SessionLocal()
#     try:
#         init_db(db)
#     except Exception as e:
#         logger.error(f"Error initializing database: {e}")
#     finally:
#         db.close()
