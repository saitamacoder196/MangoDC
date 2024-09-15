# Lưu vào file database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from codev4.models import Base

# Địa chỉ kết nối đến cơ sở dữ liệu (ví dụ SQLite)
DATABASE_URL = "sqlite:///db.sqlite3"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Tạo cơ sở dữ liệu nếu chưa tồn tại
Base.metadata.create_all(engine)
