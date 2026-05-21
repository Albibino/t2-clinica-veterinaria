from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base


class Animal(Base):
    __tablename__ = "animais"

    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String(100), nullable=False)
    especie      = Column(String(50), nullable=False)
    raca         = Column(String(100))
    idade        = Column(Integer)
    peso         = Column(Numeric(5, 2))
    nome_dono    = Column(String(100), nullable=False)
    contato_dono = Column(String(20))
    foto_url     = Column(Text)
    observacoes  = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    consultas = relationship("Consulta", back_populates="animal", cascade="all, delete-orphan")


class Consulta(Base):
    __tablename__ = "consultas"

    id             = Column(Integer, primary_key=True, index=True)
    animal_id      = Column(Integer, ForeignKey("animais.id"), nullable=False)
    data_consulta  = Column(DateTime, nullable=False)
    veterinario    = Column(String(100), nullable=False)
    motivo         = Column(Text, nullable=False)
    diagnostico    = Column(Text)
    tratamento     = Column(Text)
    medicamentos   = Column(Text)
    peso_consulta  = Column(Numeric(5, 2))
    retorno        = Column(Date)
    status         = Column(String(20), default="agendada")
    observacoes    = Column(Text)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    animal = relationship("Animal", back_populates="consultas")
