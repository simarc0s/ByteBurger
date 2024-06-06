import sqlite3

# Função para recriar a tabela 'pedidos' com ON DELETE CASCADE
def recriar_tabela_pedidos(cursor):
    # Desativar temporariamente as restrições de chave estrangeira
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Criar a nova tabela 'pedidos' com ON DELETE CASCADE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos_new (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER,
        nome_hamburguer TEXT,
        quantidade INTEGER,
        tamanho TEXT CHECK(tamanho IN ('infantil', 'normal', 'duplo')),
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        valor_total REAL,
        FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY(nome_hamburguer) REFERENCES hamburgueres(nome_hamburguer) ON DELETE CASCADE
    );
    """)
    
    # Copiar os dados da tabela antiga 'pedidos' para a nova
    cursor.execute("INSERT INTO pedidos_new SELECT * FROM pedidos")
    
    # Eliminar a tabela antiga 'pedidos'
    cursor.execute("DROP TABLE pedidos")
    
    # Renomear a nova tabela para 'pedidos'
    cursor.execute("ALTER TABLE pedidos_new RENAME TO pedidos")
    
    # Reativar as restrições de chave estrangeira
    cursor.execute("PRAGMA foreign_keys = ON")

# Conectar à base de dados
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Desativar temporariamente as restrições de chave estrangeira
cursor.execute("PRAGMA foreign_keys = OFF")

# Criar as tabelas se ainda não existirem
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

# Criar a tabela 'pedidos' inicial sem ON DELETE CASCADE
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

# Guardar (commit) as mudanças na base de dados
conn.commit()

# Inserir um utilizador na tabela 'empregados'
try:
    cursor.execute(
        "INSERT OR IGNORE INTO empregados (username, password) VALUES (?, ?)",
        ("user1", "password1"),
    )
except sqlite3.IntegrityError:
    print("Erro ao inserir empregado. Username já existe.")

# Inserir alguns hambúrgueres na tabela 'hamburgueres'
hamburgueres = [
    ("Big Tasty", "Pão, Carne, Alface, Tomate, Queijo"),
    ("Big Mac", "Pão, Carne, Queijo, Alface, Carne, Pão"),
    ("Mc Royal", "Pão, Tomate, Queijo, Cogumelos, Bacon"),
]

for hamburguer in hamburgueres:
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO hamburgueres (nome_hamburguer, ingredientes) VALUES (?, ?)",
            hamburguer,
        )
    except sqlite3.IntegrityError:
        print(f"Erro ao inserir hambúrguer: {hamburguer[0]} já existe.")

# Guardar (commit) as mudanças na base de dados
conn.commit()

# Recriar a tabela 'pedidos' com ON DELETE CASCADE
recriar_tabela_pedidos(cursor)

# Guardar (commit) as mudanças na base de dados
conn.commit()

# Reativar as restrições de chave estrangeira
cursor.execute("PRAGMA foreign_keys = ON")

# Fechar a conexão com a base de dados
conn.close()