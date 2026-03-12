import sqlite3


# Recreates the 'pedidos' table with ON DELETE CASCADE
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


# Adds the imagem_url column to the hamburgueres table if it does not exist
def adicionar_coluna_imagem_url(cursor):
    cursor.execute("PRAGMA table_info(hamburgueres)")
    columns = [column[1] for column in cursor.fetchall()]
    if "imagem_url" not in columns:
        cursor.execute("ALTER TABLE hamburgueres ADD COLUMN imagem_url TEXT")


# Inserts a customer record and returns the new row id
def inserir_cliente(cursor, nome, morada, telefone):
    cursor.execute(
        "INSERT INTO clientes (nome, morada, telefone) VALUES (?, ?, ?)",
        (nome, morada, telefone),
    )
    return cursor.lastrowid


# Inserts an order record
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


# Connect to the database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = OFF")

# Create the clientes table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    morada TEXT NOT NULL,
    telefone TEXT NOT NULL
);
""")

# Create the hamburgueres table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS hamburgueres (
    nome_hamburguer TEXT PRIMARY KEY,
    ingredientes TEXT NOT NULL,
    imagem_url TEXT
);
""")

# Add the imagem_url column if it does not already exist
adicionar_coluna_imagem_url(cursor)

# Create the pedidos table if it does not exist
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

# Create the users table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id_empregado INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
""")

# Commit table creation
conn.commit()

# Insert a default user
try:
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        ("user1", "password1"),
    )
except sqlite3.IntegrityError:
    print("Erro ao inserir empregado. Username já existe.")

# Burger seed data
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

# Insert burgers (skip duplicates)
for hamburguer in hamburgueres:
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO hamburgueres (nome_hamburguer, ingredientes, imagem_url) VALUES (?, ?, ?)",
            hamburguer,
        )
        # Verify the row was inserted
        cursor.execute(
            "SELECT * FROM hamburgueres WHERE nome_hamburguer = ?", (hamburguer[0],)
        )
        print(cursor.fetchone())
    except sqlite3.IntegrityError:
        print(f"Error inserting burger: {hamburguer[0]} already exists.")

# Commit burger inserts
conn.commit()

# Recreate the pedidos table with ON DELETE CASCADE
recriar_tabela_pedidos(cursor)

# Commit after table recreation
conn.commit()

cursor.execute("PRAGMA foreign_keys = ON")

# Final commit
conn.commit()

# Verify customers were inserted correctly
cursor.execute("SELECT * FROM clientes")
print(cursor.fetchall())

# Verify orders were inserted correctly
cursor.execute("SELECT * FROM pedidos")
print(cursor.fetchall())

# Close the database connection
conn.close()

print("Database updated successfully.")
