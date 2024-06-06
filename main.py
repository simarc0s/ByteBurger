import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class LoginForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        self.add_widget(Label(text="Nome de Utilizador"))
        self.username_input = TextInput()
        self.add_widget(self.username_input)

        self.add_widget(Label(text="Palavra-passe"))
        self.password_input = TextInput(password=True)
        self.add_widget(self.password_input)

        self.submit = Button(text="Entrar")
        self.submit.bind(on_press=self.login)
        self.add_widget(self.submit)

    def login(self, instance):
        data = {
            "username": self.username_input.text,
            "password": self.password_input.text,
        }
        try:
            response = requests.post("http://127.0.0.1:5000/login", json=data)
            if response.status_code == 200:
                token = response.json()["token"]
                App.get_running_app().token = token
                App.get_running_app().show_order_form()
            else:
                print("Falha ao fazer login. Código de estado:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)


class OrderForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Nome do Cliente
        self.add_widget(Label(text="Nome do Cliente"))
        self.cliente_input = TextInput()
        self.cliente_input.bind(text=self.on_cliente_text)
        self.add_widget(self.cliente_input)

        self.nome_dropdown_button = Button(text="▼")
        self.nome_dropdown_button.bind(on_release=self.show_nome_dropdown)
        self.add_widget(self.nome_dropdown_button)

        # Morada
        self.add_widget(Label(text="Morada"))
        self.morada_input = TextInput()
        self.add_widget(self.morada_input)

        # Telefone
        self.add_widget(Label(text="Telefone"))
        self.telefone_input = TextInput()
        self.telefone_input.bind(text=self.on_telefone_text)
        self.add_widget(self.telefone_input)

        self.telefone_dropdown_button = Button(text="▼")
        self.telefone_dropdown_button.bind(on_release=self.show_telefone_dropdown)
        self.add_widget(self.telefone_dropdown_button)

        # Nome do Hamburguer
        self.add_widget(Label(text="Nome do Hamburguer"))
        self.hamburguer_input = TextInput()
        self.add_widget(self.hamburguer_input)

        # Quantidade
        self.add_widget(Label(text="Quantidade"))
        self.quantidade_input = TextInput()
        self.add_widget(self.quantidade_input)

        # Tamanho
        self.add_widget(Label(text="Tamanho"))
        self.tamanho_input = TextInput()
        self.add_widget(self.tamanho_input)

        # Registar Pedido
        self.submit = Button(text="Registar Pedido")
        self.submit.bind(on_press=self.submit_order)
        self.add_widget(self.submit)

    def submit_order(self, instance):
        try:
            quantidade = int(self.quantidade_input.text)
        except ValueError:
            print("A quantidade deve ser um número inteiro.")
            return

        data = {
            "nome_cliente": self.cliente_input.text,
            "morada": self.morada_input.text,
            "telefone": self.telefone_input.text,
            "nome_hamburguer": self.hamburguer_input.text,
            "quantidade": quantidade,
            "tamanho": self.tamanho_input.text,
        }
        print("Enviando dados para o servidor:", data)
        headers = {"x-access-tokens": App.get_running_app().token}
        try:
            response = requests.post(
                "http://127.0.0.1:5000/pedidos", json=data, headers=headers
            )
            if response.status_code == 201:
                print("Pedido registado com sucesso!")
            else:
                print(
                    "Falha ao registar o pedido. Código de estado:",
                    response.status_code,
                )
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

    def on_cliente_text(self, instance, value):
        headers = {"x-access-tokens": App.get_running_app().token}
        try:
            response = requests.get(
                f"http://127.0.0.1:5000/clientes/nome/{value}", headers=headers
            )
            if response.status_code == 200:
                clientes = response.json()
                if clientes:
                    cliente = clientes[0]
                    self.cliente_input.text = cliente["nome"]
                    self.morada_input.text = cliente["morada"]
                    self.telefone_input.text = cliente["telefone"]
            else:
                print(
                    "Falha ao buscar cliente. Código de estado:", response.status_code
                )
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

    def on_telefone_text(self, instance, value):
        headers = {"x-access-tokens": App.get_running_app().token}
        try:
            response = requests.get(
                f"http://127.0.0.1:5000/clientes/{value}", headers=headers
            )
            if response.status_code == 200:
                cliente = response.json()
                self.cliente_input.text = cliente["nome"]
                self.morada_input.text = cliente["morada"]
            else:
                print("Cliente não encontrado. Código de estado:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

    def show_nome_dropdown(self, instance):
        headers = {"x-access-tokens": App.get_running_app().token}
        dropdown = DropDown()
        try:
            response = requests.get("http://127.0.0.1:5000/clientes", headers=headers)
            if response.status_code == 200:
                clientes = response.json()
                for cliente in clientes:
                    btn = Button(text=cliente["nome"], size_hint_y=None, height=44)
                    btn.bind(on_release=lambda btn: self.select_cliente(btn.text))
                    dropdown.add_widget(btn)
            else:
                print(
                    "Falha ao buscar clientes. Código de estado:", response.status_code
                )
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
        dropdown.open(instance)

    def select_cliente(self, nome):
        self.cliente_input.text = nome

    def show_telefone_dropdown(self, instance):
        headers = {"x-access-tokens": App.get_running_app().token}
        dropdown = DropDown()
        try:
            response = requests.get("http://127.0.0.1:5000/clientes", headers=headers)
            if response.status_code == 200:
                clientes = response.json()
                for cliente in clientes:
                    btn = Button(text=cliente["telefone"], size_hint_y=None, height=44)
                    btn.bind(on_release=lambda btn: self.select_telefone(btn.text))
                    dropdown.add_widget(btn)
            else:
                print(
                    "Falha ao buscar clientes. Código de estado:", response.status_code
                )
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
        dropdown.open(instance)

    def select_telefone(self, telefone):
        self.telefone_input.text = telefone


class MyApp(App):
    def build(self):
        self.token = None
        self.login_form = LoginForm()
        return self.login_form

    def show_order_form(self):
        self.order_form = OrderForm()
        self.root.clear_widgets()
        self.root.add_widget(self.order_form)


if __name__ == "__main__":
    MyApp().run()