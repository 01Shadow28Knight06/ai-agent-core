from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    cliente_nombre = Column(String, index=True)
    mensaje_cliente = Column(Text)
    respuesta_ia = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)