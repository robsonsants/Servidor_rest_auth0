from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from jose import jwt
import requests
import os

app = Flask(__name__)
CORS(app)

# Carregar variáveis de ambiente
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_IDENTIFIER = os.getenv('API_IDENTIFIER')
ALGORITHMS = ["RS256"]

# Verificar o token JWT
def verify_jwt(token):
    try:
        headers = jwt.get_unverified_header(token)
        rsa_key = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json').json()
        rsa_key = next(key for key in rsa_key['keys'] if key['kid'] == headers['kid'])
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)
        payload = jwt.decode(token, public_key, algorithms=ALGORITHMS, audience=API_IDENTIFIER)
        return payload
    except Exception as e:
        print(f"Token error: {e}")
        return None

@app.before_request
def check_auth():
    if request.path.startswith('/swagger') or request.path == '/swagger.yaml':
        return
    token = request.headers.get('Authorization')
    if token:
        token = token.split(' ')[1]
        payload = verify_jwt(token)
        if not payload:
            return jsonify({"msg": "Invalid token"}), 401
        request.user = payload
    else:
        return jsonify({"msg": "Token not provided"}), 401

# Dados simulados
users = [{'id': '1', 'email': 'user@example.com', 'name': 'John Doe'}]
favorites = []

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    if not email or not name:
        return jsonify({"msg": "Invalid data"}), 400
    new_user = {'id': str(len(users) + 1), 'email': email, 'name': name}
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/favorites', methods=['GET'])
def get_favorites():
    return jsonify(favorites)

@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    item_id = data.get('item_id')
    user_id = data.get('user_id')
    if not item_id or not user_id:
        return jsonify({"msg": "Invalid data"}), 400
    favorite = {'item_id': item_id, 'user_id': user_id}
    favorites.append(favorite)
    return jsonify(favorite), 201

@app.route('/favorites', methods=['DELETE'])
def remove_favorite():
    item_id = request.args.get('item_id')
    user_id = request.args.get('user_id')
    global favorites
    favorites = [fav for fav in favorites if not (fav['item_id'] == item_id and fav['user_id'] == user_id)]
    return '', 204

@app.route('/swagger.yaml', methods=['GET'])
def swagger_yaml():
    return send_from_directory('swagger', 'swagger.yaml')

@app.route('/swagger', methods=['GET'])
def swagger_ui():
    return send_from_directory('static/swagger-ui', 'index.html')

@app.route('/swagger/<path:path>', methods=['GET'])
def swagger_ui_files(path):
    return send_from_directory('static/swagger-ui', path)

if __name__ == '__main__':
    app.run(port=5000)
