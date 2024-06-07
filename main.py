# Importa as bibliotecas necessárias
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


# Classe para o formulário de login
class LoginForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Campos de entrada para usuário e senha
        self.add_widget(Label(text="Usuário"))
        self.username_input = TextInput()
        self.add_widget(self.username_input)

        self.add_widget(Label(text="Senha"))
        self.password_input = TextInput(password=True)
        self.add_widget(self.password_input)

        # Botão de submissão do login
        self.submit = Button(text="Login")
        self.submit.bind(on_press=self.submit_login)
        self.add_widget(self.submit)

    # Função para submeter o login
    def submit_login(self, instance):
        # Dados do formulário de login
        data = {
            "username": self.username_input.text,
            "password": self.password_input.text,
        }
        try:
            # Envio da requisição POST para o servidor
            response = requests.post("http://127.0.0.1:5000/login", json=data)
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                # Armazena o token recebido do servidor
                App.get_running_app().token = response.json()["token"]
                # Exibe o formulário de registo de pedidos
                App.get_running_app().show_order_form()
            else:
                print("Falha no login. Código de estado:", response.status_code)
                print("Resposta do servidor:", response.text)
                # Exibe uma mensagem de erro caso o login falhe
                self.show_error_message("Falha no login. Verifique usuário/senha.")
        except requests.ConnectionError:
            print("Falha na conexão com o servidor.")
            # Exibe uma mensagem de erro caso haja falha na conexão com o servidor

    # Função para exibir mensagens de erro
    def show_error_message(self, message):
        if not hasattr(self, "error_label"):
            self.error_label = Label(text=message, color=(1, 0, 0, 1))
            self.add_widget(self.error_label)
        else:
            self.error_label.text = message


# Classe para o formulário de seleção de hambúrgueres
class HamburgerSelectionForm(BoxLayout):
    def __init__(self, order_form, **kwargs):
        super().__init__(**kwargs)
        self.order_form = order_form
        self.orientation = "vertical"

        # ScrollView para a lista de hambúrgueres
        scrollview = ScrollView()
        inner_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        inner_layout.bind(minimum_height=inner_layout.setter("height"))

        # Requisição GET para obter a lista de hambúrgueres do servidor
        headers = {"x-access-tokens": App.get_running_app().token}
        try:
            response = requests.get(
                "http://127.0.0.1:5000/hamburgueres", headers=headers
            )
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                hamburgueres = response.json()
                # Cria um bloco para cada hambúrguer
                for hamburguer in hamburgueres:
                    box = BoxLayout(
                        orientation="horizontal", size_hint_y=None, height=150
                    )

                    # Adiciona a imagem do hambúrguer
                    image = Image(source=hamburguer["imagem_url"], size_hint_x=0.3)
                    box.add_widget(image)

                    # Adiciona o nome e ingredientes do hambúrguer
                    label = Label(
                        text=f"{hamburguer['nome']}\n\nIngredientes: {hamburguer['ingredientes']}",
                        halign="left",
                        valign="middle",
                        size_hint_x=0.6,
                    )
                    label.bind(size=label.setter("text_size"))
                    box.add_widget(label)

                    # Botão para selecionar o hambúrguer
                    select_btn = Button(text="Selecionar", size_hint_x=0.1)
                    select_btn.bind(
                        on_release=lambda btn,
                        h=hamburguer["nome"]: self.select_hamburguer(h)
                    )
                    box.add_widget(select_btn)

                    inner_layout.add_widget(box)

            else:
                print(
                    "Falha ao buscar hambúrgueres. Código de estado:",
                    response.status_code,
                )
                print("Resposta do servidor:", response.text)
                # Exibe uma mensagem de erro caso falhe ao obter a lista de hambúrgueres
                self.show_error_message("Falha ao buscar hambúrgueres.")
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
            # Exibe uma mensagem de erro caso haja erro na conexão com o servidor
            self.show_error_message("Erro ao conectar ao servidor.")

        scrollview.add_widget(inner_layout)
        self.add_widget(scrollview)

    # Função para selecionar um hambúrguer
    def select_hamburguer(self, nome):
        self.order_form.hamburguer_button.text = nome
        App.get_running_app().show_order_form(with_data=True)

    # Função para exibir mensagens de erro
    def show_error_message(self, message):
        if not hasattr(self, "error_label"):
            self.error_label = Label(text=message, color=(1, 0, 0, 1))
            self.add_widget(self.error_label)
        else:
            self.error_label.text = message


# Classe para o formulário de registo de pedidos
class OrderForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Campo de entrada para o nome do cliente
        self.add_widget(Label(text="Nome do Cliente"))
        self.cliente_input = TextInput()
        self.add_widget(self.cliente_input)

        # Dropdown para selecionar o nome do cliente
        self.nome_dropdown_button = Button(text="Lista completa de nomes")
        self.nome_dropdown_button.bind(on_release=self.show_nome_dropdown)
        self.add_widget(self.nome_dropdown_button)

        # Campo de entrada para a morada
        self.add_widget(Label(text="Morada"))
        self.morada_input = TextInput()
        self.add_widget(self.morada_input)

        # Campo de entrada para o telefone
        self.add_widget(Label(text="Telefone"))
        self.telefone_input = TextInput()
        self.telefone_input.bind(text=self.on_telefone_text)
        self.add_widget(self.telefone_input)

        # Dropdown para selecionar o telefone
        self.telefone_dropdown_button = Button(text="Lista completa de telefones")
        self.telefone_dropdown_button.bind(on_release=self.show_telefone_dropdown)
        self.add_widget(self.telefone_dropdown_button)

        # Botão para selecionar o hambúrguer
        self.add_widget(Label(text="Nome do Hambúrguer"))
        self.hamburguer_button = Button(
            text="Selecione o Hambúrguer", size_hint_y=None, height=44
        )
        self.hamburguer_button.bind(on_release=self.show_hamburguer_menu)
        self.add_widget(self.hamburguer_button)

        # Campo de entrada para a quantidade
        self.add_widget(Label(text="Quantidade"))
        self.quantidade_input = TextInput()
        self.add_widget(self.quantidade_input)

        # Campo de entrada para o tamanho
        self.add_widget(Label(text="Tamanho (infantil, normal, duplo)"))
        self.tamanho_input = TextInput()
        self.add_widget(self.tamanho_input)

        # Botão para submeter o pedido
        self.submit = Button(text="Registar Pedido")
        self.submit.bind(on_press=self.submit_order)
        self.add_widget(self.submit)

    # Função chamada quando um telefone é digitado
    def on_telefone_text(self, instance, value):
        print("Telefone digitado:", value)

    # Função para exibir o dropdown com a lista de nomes dos clientes
    def show_nome_dropdown(self, instance):
        headers = {"x-access-tokens": App.get_running_app().token}
        dropdown = DropDown()
        try:
            # Requisição GET para obter a lista de clientes do servidor
            response = requests.get("http://127.0.0.1:5000/clientes", headers=headers)
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                clientes = response.json()
                # Cria um botão para cada cliente na lista
                for cliente in clientes:
                    btn = Button(text=cliente["nome"], size_hint_y=None, height=44)
                    btn.bind(
                        on_release=lambda btn: self.select_cliente(btn.text, cliente)
                    )
                    dropdown.add_widget(btn)
            else:
                print(
                    "Falha ao buscar clientes. Código de estado:", response.status_code
                )
                print("Resposta do servidor:", response.text)
                # Exibe uma mensagem de erro caso falhe ao obter a lista de clientes
                self.show_error_message("Falha ao buscar clientes.")
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
            # Exibe uma mensagem de erro caso haja erro na conexão com o servidor
            self.show_error_message("Erro ao conectar ao servidor.")
        dropdown.open(instance)

    # Função para exibir o dropdown com a lista de telefones dos clientes
    def show_telefone_dropdown(self, instance):
        headers = {"x-access-tokens": App.get_running_app().token}
        dropdown = DropDown()
        try:
            # Requisição GET para obter a lista de clientes do servidor
            response = requests.get("http://127.0.0.1:5000/clientes", headers=headers)
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                clientes = response.json()
                # Cria um botão para cada cliente na lista
                for cliente in clientes:
                    btn = Button(text=cliente["telefone"], size_hint_y=None, height=44)
                    btn.bind(
                        on_release=lambda btn: self.select_telefone(btn.text, cliente)
                    )
                    dropdown.add_widget(btn)
            else:
                print(
                    "Falha ao buscar clientes. Código de estado:", response.status_code
                )
                print("Resposta do servidor:", response.text)
                # Exibe uma mensagem de erro caso falhe ao obter a lista de clientes
                self.show_error_message("Falha ao buscar clientes.")
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
            # Exibe uma mensagem de erro caso haja erro na conexão com o servidor
            self.show_error_message("Erro ao conectar ao servidor.")
        dropdown.open(instance)

    # Função para exibir o formulário de seleção de hambúrgueres
    def show_hamburguer_menu(self, instance):
        App.get_running_app().show_hamburger_selection_form()

    # Função para selecionar um cliente a partir do dropdown de nomes
    def select_cliente(self, nome, cliente):
        self.cliente_input.text = nome
        self.morada_input.text = cliente["morada"]
        self.telefone_input.text = cliente["telefone"]

    # Função para selecionar um cliente a partir do dropdown de telefones
    def select_telefone(self, telefone, cliente):
        self.telefone_input.text = telefone
        self.cliente_input.text = cliente["nome"]
        self.morada_input.text = cliente["morada"]

    # Função para submeter o pedido
    def submit_order(self, instance):
        # Dados do formulário de registo de pedido
        data = {
            "nome_cliente": self.cliente_input.text,
            "morada": self.morada_input.text,
            "telefone": self.telefone_input.text,
            "nome_hamburguer": self.hamburguer_button.text,
            "quantidade": self.quantidade_input.text,
            "tamanho": self.tamanho_input.text,
        }
        headers = {"x-access-tokens": App.get_running_app().token}
        try:
            # Envio da requisição POST para registrar o pedido
            response = requests.post(
                "http://127.0.0.1:5000/pedidos", json=data, headers=headers
            )
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 201:
                print("Pedido registrado com sucesso!")
                self.show_error_message("Pedido registrado com sucesso!")
            else:
                print(
                    "Falha ao registrar pedido. Código de estado:", response.status_code
                )
                print("Resposta do servidor:", response.text)
                # Exibe uma mensagem de erro caso falhe ao registrar o pedido
                self.show_error_message("Falha ao registrar pedido.")
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
            # Exibe uma mensagem de erro caso haja erro na conexão com o servidor
            self.show_error_message("Erro ao conectar ao servidor.")

    # Função para exibir mensagens de erro
    def show_error_message(self, message):
        if not hasattr(self, "error_label"):
            self.error_label = Label(text=message, color=(1, 0, 0, 1))
            self.add_widget(self.error_label)
        else:
            self.error_label.text = message


# Classe principal da aplicação
class OrderApp(App):
    # Método para construir a interface do aplicativo
    def build(self):
        self.token = None
        self.order_form = None
        self.saved_data = {}
        self.root = BoxLayout(orientation="vertical")
        self.show_login_form()
        return self.root

    # Método para exibir o formulário de login
    def show_login_form(self):
        self.root.clear_widgets()
        login_form = LoginForm()
        self.root.add_widget(login_form)

    # Método para exibir o formulário de registo de pedidos
    def show_order_form(self, with_data=False):
        self.root.clear_widgets()
        if self.order_form is None:
            self.order_form = OrderForm()
        if with_data:
            self.restore_order_form_data()
        self.root.add_widget(self.order_form)
        if not with_data:
            self.load_hamburgueres()

    # Método para exibir o formulário de seleção de hambúrgueres
    def show_hamburger_selection_form(self):
        self.save_order_form_data()
        self.root.clear_widgets()
        hamburger_selection_form = HamburgerSelectionForm(self.order_form)
        self.root.add_widget(hamburger_selection_form)

    # Método para carregar a lista de hambúrgueres
    def load_hamburgueres(self):
        headers = {"x-access-tokens": self.token}
        try:
            # Requisição GET para obter a lista de hambúrgueres do servidor
            response = requests.get(
                "http://127.0.0.1:5000/hamburgueres", headers=headers
            )
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                hamburgueres = response.json()
                dropdown = DropDown()
                for hamburguer in hamburgueres:
                    btn = Button(text=hamburguer["nome"], size_hint_y=None, height=44)
                    btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                    dropdown.add_widget(btn)
                self.order_form.hamburguer_button.bind(on_release=dropdown.open)
                dropdown.bind(
                    on_select=lambda instance, x: setattr(
                        self.order_form.hamburguer_button, "text", x
                    )
                )
            else:
                print(
                    "Falha ao carregar hambúrgueres. Código de estado:",
                    response.status_code,
                )
                print("Resposta do servidor:", response.text)
        except requests.ConnectionError:
            print("Falha na conexão com o servidor.")

    # Método para salvar os dados do formulário de registo de pedidos
    def save_order_form_data(self):
        self.saved_data["nome_cliente"] = self.order_form.cliente_input.text
        self.saved_data["morada"] = self.order_form.morada_input.text
        self.saved_data["telefone"] = self.order_form.telefone_input.text
        self.saved_data["nome_hamburguer"] = self.order_form.hamburguer_button.text
        self.saved_data["quantidade"] = self.order_form.quantidade_input.text
        self.saved_data["tamanho"] = self.order_form.tamanho_input.text

    # Método para restaurar os dados do formulário de registo de pedidos
    def restore_order_form_data(self):
        self.order_form.cliente_input.text = self.saved_data.get("nome_cliente", "")
        self.order_form.morada_input.text = self.saved_data.get("morada", "")
        self.order_form.telefone_input.text = self.saved_data.get("telefone", "")
        self.order_form.hamburguer_button.text = self.saved_data.get(
            "nome_hamburguer", "Selecione o Hambúrguer"
        )
        self.order_form.quantidade_input.text = self.saved_data.get("quantidade", "")
        self.order_form.tamanho_input.text = self.saved_data.get("tamanho", "")


# Execução do aplicativo
if __name__ == "__main__":
    OrderApp().run()
