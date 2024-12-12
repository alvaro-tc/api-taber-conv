from app.extensions import db

class Directive(db.Model):
    __tablename__ = 'directives'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)

    guests = db.relationship('Guest', back_populates='directive')

    @staticmethod
    def get_all():
        return Directive.query.all()

    @staticmethod
    def get_by_id(directive_id):
        return Directive.query.get(directive_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, nombre):
        self.nombre = nombre
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }