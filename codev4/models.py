from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MangoItem(Base):
    __tablename__ = 'mango_analysis_mangoitem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mango_id = Column(String(50), unique=True, nullable=False)
    folder_path = Column(String(255), nullable=False)

    images = relationship("Image", back_populates="mango_item", cascade="all, delete-orphan")
    detected_areas = relationship("DetectedArea", back_populates="mango_item", cascade="all, delete-orphan")
    conclusion = relationship("Conclusion", back_populates="mango_item", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MangoItem(id={self.id}, mango_id='{self.mango_id}')>"

class Image(Base):
    __tablename__ = 'mango_analysis_image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mango_item_id = Column(Integer, ForeignKey('mango_analysis_mangoitem.id'), nullable=False)
    image_type = Column(String(10), nullable=False)
    position = Column(String(10), nullable=False)
    image_path = Column(String(255), nullable=False)

    mango_item = relationship("MangoItem", back_populates="images")

    def __repr__(self):
        return f"<Image(id={self.id}, mango_item_id={self.mango_item_id}, type='{self.image_type}', position='{self.position}')>"

class DetectedArea(Base):
    __tablename__ = 'mango_analysis_detectedarea'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mango_item_id = Column(Integer, ForeignKey('mango_analysis_mangoitem.id'), nullable=False)
    image = Column(String(50), nullable=False)
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    area_size = Column(Float, nullable=False)
    disease = Column(String(100), nullable=False)

    mango_item = relationship("MangoItem", back_populates="detected_areas")

    def __repr__(self):
        return f"<DetectedArea(id={self.id}, mango_item_id={self.mango_item_id}, disease='{self.disease}', position=({self.position_x}, {self.position_y}))>"

class Conclusion(Base):
    __tablename__ = 'mango_analysis_conclusion'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mango_item_id = Column(Integer, ForeignKey('mango_analysis_mangoitem.id'), unique=True, nullable=False)
    total_disease_area = Column(Float, nullable=False)
    total_mango_surface_area = Column(Float, nullable=False)
    disease_area_percentage = Column(Float, nullable=False)
    conclusion = Column(Text, nullable=False)

    mango_item = relationship("MangoItem", back_populates="conclusion")

    def __repr__(self):
        return f"<Conclusion(id={self.id}, mango_item_id={self.mango_item_id})>"