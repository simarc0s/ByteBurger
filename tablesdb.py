import sqlite3

# Conectar a base de dados
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Criar tabelas
cursor.execute('''
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    morada TEXT NOT NULL,
    telefone TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE hamburgueres (
    nome_hamburguer TEXT PRIMARY KEY,
    ingredientes TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE pedidos (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER,
    nome_hamburguer TEXT,
    quantidade INTEGER,
    tamanho TEXT CHECK(tamanho IN ('infantil', 'normal', 'duplo')),
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    valor_total REAL,
    FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY(nome_hamburguer) REFERENCES hamburgueres(nome_hamburguer)
);
''')

# Guardar (commit) as mudanças
conn.commit()

# Fechar a conexão
conn.close()