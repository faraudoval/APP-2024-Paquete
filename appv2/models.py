from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
db = SQLAlchemy(app)

class Paquete(db.Model):
    __tablename__ = 'paquete'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    numeroenvio = db.Column(db.Integer, nullable=True)
    peso = db.Column(db.Float, nullable=True)
    nomdestinatario = db.Column(db.String(50), nullable=True)
    dirdestinatario = db.Column(db.String(50), nullable=True)
    entregado = db.Column(db.Boolean, nullable=True)
    observaciones = db.Column(db.String(50), nullable=True)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    idtransporte = db.Column(db.Integer, db.ForeignKey('transporte.id'), nullable=True)    
    idrepartidor = db.Column(db.Integer, db.ForeignKey('repartidor.id'))
class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    provincia = db.Column(db.String(50), nullable=True)
    localidad = db.Column(db.String(50), nullable=True)
    direccion = db.Column(db.String(50), nullable=True)
    repartidores = relationship('Repartidor', backref='sucursal', cascade='all, delete-orphan')   
    transportes = relationship('Transporte', backref='sucursal', cascade='all, delete-orphan')   
    paquetes = relationship('Paquete', backref='sucursal', cascade='all, delete-orphan')  
class Transporte(db.Model):
    __tablename__ = 'transporte'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    numerotransporte = db.Column(db.Integer, nullable=True)
    fechahorasalida = db.Column(db.DateTime, nullable=True)
    fechahorallegada = db.Column(db.DateTime, nullable=True)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    paquetes = db.relationship('Paquete', backref='transporte', lazy=True, cascade='all, delete-orphan')    
class Repartidor(db.Model):
    __tablename__ = 'repartidor'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=True)
    dni = db.Column(db.String(50), nullable=True)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id')) 
    paquetes = db.relationship('Paquete', backref='repartidor', lazy=True, cascade='all, delete-orphan')

