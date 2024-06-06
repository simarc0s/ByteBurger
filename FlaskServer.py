from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/clientes', methods=['POST'])
def add_cliente():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
                   (data['nome'], data['morada'], data['telefone']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

@app.route('/pedidos', methods=['POST'])
def add_pedido():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pedidos (id_cliente, nome_hamburguer, quantidade, tamanho, valor_total) VALUES (?, ?, ?, ?, ?)",
                   (data['id_cliente'], data['nome_hamburguer'], data['quantidade'], data['tamanho'], data['valor_total']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

if __name__ == '__main__':
    app.run(debug=True)