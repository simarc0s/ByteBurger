# Projeto de Gestão de Pedidos de Hambúrgueres

## Introdução

Este projeto é uma aplicação cliente-servidor para gestão de pedidos de hambúrgueres. O servidor é desenvolvido utilizando Flask e SQLite, enquanto o cliente é uma aplicação com interface gráfica construída com Kivy.

## Dependências

- Python 3.7 ou superior
- Flask
- SQLite
- JWT (PyJWT)
- Kivy
- Requests

## Funcionalidades

### Backend (Servidor)

O backend do projeto é desenvolvido em Flask e utiliza SQLite como banco de dados. As principais funcionalidades incluem:

- **Criação de Pedidos**: Permite criar novos pedidos de hambúrgueres com detalhes como nome e ingredientes.
- **Listagem de Pedidos**: Permite listar todos os pedidos feitos.
- **Atualização de Pedidos**: Permite atualizar informações de pedidos existentes.
- **Remoção de Pedidos**: Permite remover pedidos existentes.
- **Autenticação**: Utiliza JWT para autenticação dos utilizadores.

### Frontend (Cliente)

O frontend é uma aplicação gráfica desenvolvida com Kivy, que oferece uma interface amigável para interação com o servidor. As funcionalidades principais incluem:

- **Interface dos utilizadores**: Tela para visualização e gerenciamento dos pedidos de hambúrgueres.
- **Interação com o Servidor**: Envia e recebe dados do servidor Flask utilizando a biblioteca Requests.
- **Formulários de Entrada**: Permite que os utilizadores insiram, atualizem e removam pedidos através de formulários intuitivos.

## Como Executar

### Servidor

Para iniciar o servidor, escreva no terminal o seguinte comando:

```sh
python FlaskServer.py
```

### Cliente

Para iniciar o cliente, escreva no terminal o seguinte comando:

```sh
python main.py
```

## Requisitos

Certifique-se de ter as seguintes bibliotecas instaladas:

```sh
pip install Flask sqlite3 PyJWT kivy requests
```
