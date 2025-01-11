from app.extensions import db
from sqlalchemy import Enum

class Church(db.Model):
    __tablename__ = 'churchs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    
    # Enum para departamento
    departamento = db.Column(
        Enum(
            'El Alto', 'Chuquisaca', 'La Paz', 'Cochabamba', 'Oruro', 
            'Potosi', 'Tarija', 'Santa Cruz', 'Beni', 'Pando', 'Sucre',
            name='departamento_enum'
        ),
        nullable=False
    )
    
    # Enum para área
    area = db.Column(Enum('URBANO', 'RURAL', name='area_enum'), nullable=False)
    
    localidad = db.Column(db.Text, nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    code = db.Column(db.Integer, unique=True, nullable=True)  # Nuevo campo añadido
    
    guests = db.relationship('Guest', back_populates='church')

    @staticmethod
    def get_all():
        return Church.query.all()

    @staticmethod
    def get_by_id(church_id):
        return Church.query.get(church_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, nombre=None, departamento=None, area=None, localidad=None, direccion=None, code=None):
        if nombre is not None:
            self.nombre = nombre
        if departamento is not None:
            self.departamento = departamento
        if area is not None:
            self.area = area
        if localidad is not None:
            self.localidad = localidad
        if direccion is not None:
            self.direccion = direccion
        if code is not None:
            self.code = code
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre + " ("+ self.departamento + ")",
            'departamento': self.departamento,
            'area': self.area,
            'localidad': self.localidad,
            'direccion': self.direccion,
            'code': self.code  # Nuevo campo añadido
        }