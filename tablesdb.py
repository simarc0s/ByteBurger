import sqlite3

# Conectar a base de dados
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Criar tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    morada TEXT NOT NULL,
    telefone TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS hamburgueres (
    nome_hamburguer TEXT PRIMARY KEY,
    ingredientes TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
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
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS empregados (
    id_empregado INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
""")

# Guardar (commit) as mudanças
conn.commit()

# Inserir um usuário na tabela empregados
cursor.execute("INSERT INTO empregados (username, password) VALUES (?, ?)", ("user1", "password1"))
conn.commit()

# Fechar a conexão
conn.close()