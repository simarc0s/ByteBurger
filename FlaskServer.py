import datetime
import sqlite3
from functools import wraps

import jwt
from flask import Flask, jsonify, make_response, request

# Inicializa a aplicação Flask e configura a chave secreta
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
DATABASE = "database.db"


# Função para obter a conexão com a base de dados
def getdb():
    conn = sqlite3.connect(DATABASE)
    return conn


# Decorador para exigir token de autenticação nas rotas protegidas
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("x-access-tokens")
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = data["username"]
        except:  # noqa: E722
            return jsonify({"message": "Token is invalid!"}), 403
        return f(current_user, *args, **kwargs)

    return decorated


# Rota para fazer login e obter um token
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth["username"]
    password = auth["password"]

    conn = getdb()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM empregados WHERE username = ? AND password = ?",
        (username, password),
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required!"'},
        )

    token = jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        },
        app.config["SECRET_KEY"],
    )
    return jsonify({"token": token})


# Rota para adicionar clientes, protegida por token
@app.route("/clientes", methods=["POST"])
@token_required
def addcliente(current_user):
    data = request.get_json()
    conn = getdb()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
        (data["nome"], data["morada"], data["telefone"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201


# Rota para adicionar pedidos, protegida por token
@app.route("/pedidos", methods=["POST"])
@token_required
def add_pedido(current_user):
    data = request.get_json()
    app.logger.info(f"Received data: {data}")
    conn = getdb()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_cliente FROM clientes WHERE telefone = ?", (data["telefone"],)
    )
    cliente = cursor.fetchone()
    if cliente is None:
        cursor.execute(
            "INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
            (data["nome_cliente"], data["morada"], data["telefone"]),
        )
        conn.commit()
        cliente_id = cursor.lastrowid
    else:
        cliente_id = cliente[0]

    valor_total = calcular_valor_total(
        data["nome_hamburguer"], data["quantidade"], data["tamanho"]
    )

    cursor.execute(
        "INSERT INTO pedidos (id_cliente, nome_hamburguer, quantidade, tamanho, valor_total) VALUES (?, ?, ?, ?, ?)",
        (
            cliente_id,
            data["nome_hamburguer"],
            data["quantidade"],
            data["tamanho"],
            valor_total,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201


# Função para calcular o valor total de um pedido
def calcular_valor_total(nome_hamburguer, quantidade, tamanho):
    preco_base = 5.0
    multiplicador_tamanho = {"infantil": 0.75, "normal": 1.0, "duplo": 1.5}
    return preco_base * int(quantidade) * multiplicador_tamanho.get(tamanho, 1.0)


# Inicializa o servidor Flask
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")
