import sqlite3


# Função para recriar a tabela 'pedidos' com ON DELETE CASCADE
def recriar_tabela_pedidos(cursor):
    cursor.execute("PRAGMA foreign_keys = OFF")

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

    cursor.execute("INSERT INTO pedidos_new SELECT * FROM pedidos")

    cursor.execute("DROP TABLE pedidos")

    cursor.execute("ALTER TABLE pedidos_new RENAME TO pedidos")

    cursor.execute("PRAGMA foreign_keys = ON")


# Função para adicionar a coluna imagem_url à tabela hamburgueres se não existir
def adicionar_coluna_imagem_url(cursor):
    cursor.execute("PRAGMA table_info(hamburgueres)")
    columns = [column[1] for column in cursor.fetchall()]
    if "imagem_url" not in columns:
        cursor.execute("ALTER TABLE hamburgueres ADD COLUMN imagem_url TEXT")


# Função para inserir dados de um cliente
def inserir_cliente(cursor, nome, morada, telefone):
    cursor.execute(
        "INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
        (nome, morada, telefone),
    )
    return cursor.lastrowid


# Função para inserir um pedido
def inserir_pedido(
    cursor, id_cliente, nome_hamburguer, quantidade, tamanho, valor_total
):
    cursor.execute(
        """
        INSERT INTO pedidos (id_cliente, nome_hamburguer, quantidade, tamanho, valor_total)
        VALUES (?, ?, ?, ?, ?)
        """,
        (id_cliente, nome_hamburguer, quantidade, tamanho, valor_total),
    )


# Conectar à base de dados
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = OFF")

# Criação da tabela clientes se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    morada TEXT NOT NULL,
    telefone TEXT NOT NULL
);
""")

# Criação da tabela hamburgueres se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS hamburgueres (
    nome_hamburguer TEXT PRIMARY KEY,
    ingredientes TEXT NOT NULL,
    imagem_url TEXT
);
""")

# Adicionar a coluna imagem_url se não existir
adicionar_coluna_imagem_url(cursor)

# Criação da tabela pedidos se não existir
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

# Criação da tabela users se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id_empregado INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
""")

# Commit das alterações
conn.commit()

# Inserção de um utilizador
try:
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        ("user1", "password1"),
    )
except sqlite3.IntegrityError:
    print("Erro ao inserir empregado. Username já existe.")

# Dados dos hambúrgueres
hamburgueres = [
    (
        "Big-Tasty",
        "Pão, Carne, Alface, Tomate, Queijo",
        "Big-Tasty.png",
    ),
    (
        "Big-Mac",
        "Pão, Carne, Queijo, Alface, Carne, Pão",
        "Big-Mac.png",
    ),
    (
        "Mc-Royal",
        "Pão, Tomate, Queijo, Cogumelos, Bacon",
        "Mc-Royal.png",
    ),
]

# Verificação e inserção de hambúrgueres
for hamburguer in hamburgueres:
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO hamburgueres (nome_hamburguer, ingredientes, imagem_url) VALUES (?, ?, ?)",
            hamburguer,
        )
        # Confirma se os dados foram inseridos
        cursor.execute(
            "SELECT * FROM hamburgueres WHERE nome_hamburguer = ?", (hamburguer[0],)
        )
        print(cursor.fetchone())
    except sqlite3.IntegrityError:
        print(f"Erro ao inserir hambúrguer: {hamburguer[0]} já existe.")

# Commit das alterações
conn.commit()

# Recriar a tabela pedidos com ON DELETE CASCADE
recriar_tabela_pedidos(cursor)

# Commit das alterações
conn.commit()

cursor.execute("PRAGMA foreign_keys = ON")

# Commit das alterações
conn.commit()

# Verificar se o cliente foi inserido corretamente
cursor.execute("SELECT * FROM clientes")
print(cursor.fetchall())

# Verificar se o pedido foi inserido corretamente
cursor.execute("SELECT * FROM pedidos")
print(cursor.fetchall())

# Fechar a conexão com o banco de dados
conn.close()

print("Banco de dados atualizado com sucesso.")
