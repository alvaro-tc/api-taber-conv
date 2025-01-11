from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS  # Importa CORS


from app.controllers.product_controller import product_bp
from app.controllers.user_controller import user_bp
from app.controllers.church_controller import church_bp
from app.controllers.event_controller import event_bp
from app.controllers.guest_controller import guest_bp
from app.controllers.position_controller import position_bp
from app.controllers.event_detail_controller import event_detail_bp
from app.controllers.directive_controller import directive_bp
from app.controllers.payment_controller import payment_bp
from app.controllers.payment_concept_controller import payment_concept_bp
from app.controllers.payment_detail_controller import payment_detail_bp

from app.extensions import db, jwt
import json
from app.models.user_model import User
from app.models.token_block_list import TokenBlocklist



app = Flask(__name__)
# Configuración de la clave secreta para JWT
app.config["JWT_SECRET_KEY"] = "tu_clave_secreta_aqui"



# Ruta para servir Swagger UI
SWAGGER_URL = "/api/docs"
# Ruta de tu archivo OpenAPI/Swagger
API_URL = "/static/swagger.json"

# Inicializa el Blueprint de Swagger UI
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Tienda Online  API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://tabernaculo:iiPU9eo9PsY8Nsrj+@209.222.17.103:3306/bd_convencion"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



CORS(app, resources={r"/api/*": {"origins": "*"}})
# initialize exts
db.init_app(app)
jwt.init_app(app)
# Rutas y Blueprints
app.register_blueprint(product_bp, url_prefix="/api")
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(church_bp, url_prefix="/api")
app.register_blueprint(event_bp, url_prefix="/api")
app.register_blueprint(guest_bp, url_prefix="/api")
app.register_blueprint(position_bp, url_prefix="/api")
app.register_blueprint(event_detail_bp, url_prefix="/api")
app.register_blueprint(directive_bp, url_prefix="/api")
app.register_blueprint(payment_bp, url_prefix="/api")
app.register_blueprint(payment_concept_bp, url_prefix="/api")
app.register_blueprint(payment_detail_bp, url_prefix="/api")

# load user
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers, jwt_data):
    identity = jwt_data["sub"]

    # Deserializa el JSON para obtener el email
    identity_data = json.loads(identity)
    email = identity_data.get("email")

    return User.query.filter_by(email=email).one_or_none()


# additional claims

@jwt.additional_claims_loader
def make_additional_claims(identity):
    identity_data = json.loads(identity)  # Deserializa el JSON para acceder a los roles
    email = identity_data["email"]
    roles = identity_data["roles"]  # Esto debería darte la lista de roles

    return {
        "admin": "admin" in roles,
        "user": "user" in roles,
        "viewer": "viewer" in roles
    }


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed", "error": "invalid_token"}
        ),
        401,
    )

@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "message": "Request doesnt contain valid token",
                "error": "authorization_header",
            }
        ),
        401,
    )

@jwt.token_in_blocklist_loader
def token_in_blocklist_callback(jwt_header,jwt_data):
    jti = jwt_data['jti']

    token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()

    return token is not None



# Crea las tablas si no existen
with app.app_context():
    db.create_all()




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)

