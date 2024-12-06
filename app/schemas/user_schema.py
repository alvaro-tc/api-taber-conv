from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.String()
    name = fields.String()
    lastname = fields.String()
    cellphone = fields.String()
    email = fields.String()
