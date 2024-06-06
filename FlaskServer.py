from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

def getdb():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/clientes', methods=['POST'])
def addcliente():
    data = request.get_json()
    conn = getdb()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
                   (data['nome'], data['morada'], data['telefone']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

@app.route('/pedidos', methods=['POST'])
def add_pedido():
    data = request.get_json()
    app.logger.info(f'Received data: {data}')
    conn = getdb()
    cursor = conn.cursor()

    cursor.execute("SELECT id_cliente FROM clientes WHERE telefone = ?", (data['telefone'],))
    cliente = cursor.fetchone()
    if cliente is None:
        cursor.execute("INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
                       (data['nome_cliente'], data['morada'], data['telefone']))
        conn.commit()
        cliente_id = cursor.lastrowid
    else:
        cliente_id = cliente[0]

    valor_total = calcular_valor_total(data['nome_hamburguer'], data['quantidade'], data['tamanho'])

    cursor.execute("INSERT INTO pedidos (id_cliente, nome_hamburguer, quantidade, tamanho, valor_total) VALUES (?, ?, ?, ?, ?)",
                   (cliente_id, data['nome_hamburguer'], data['quantidade'], data['tamanho'], valor_total))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

def calcular_valor_total(nome_hamburguer, quantidade, tamanho):
    preco_base = 5.0
    multiplicador_tamanho = {'infantil': 0.75, 'normal': 1.0, 'duplo': 1.5}
    return preco_base * int(quantidade) * multiplicador_tamanho.get(tamanho, 1.0)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')