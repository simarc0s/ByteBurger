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
        self.add_widget(self.cliente_input)

        self.nome_dropdown_button = Button(text="Lista completa de nomes")
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

        self.telefone_dropdown_button = Button(text="Lista completa de telefones")
        self.telefone_dropdown_button.bind(on_release=self.show_telefone_dropdown)
        self.add_widget(self.telefone_dropdown_button)

        # Nome do Hamburguer
        self.add_widget(Label(text="Nome do Hamburguer"))
        self.hamburguer_dropdown_button = Button(text="Escolher Hamburguer")
        self.hamburguer_dropdown_button.bind(on_release=self.show_hamburguer_dropdown)
        self.add_widget(self.hamburguer_dropdown_button)

        # Quantidade
        self.add_widget(Label(text="Quantidade"))
        self.quantidade_input = TextInput()
        self.add_widget(self.quantidade_input)

        # Tamanho
        self.add_widget(Label(text="Tamanho (infantil, normal, duplo)"))
        self.tamanho_input = TextInput()
        self.add_widget(self.tamanho_input)

        # Registar Pedido
        self.submit = Button(text="Registar Pedido")
        self.submit.bind(on_press=self.submit_order)
        self.add_widget(self.submit)

    def on_telefone_text(self, instance, value):
        print("Telefone digitado:", value)

    def show_nome_dropdown(self, instance):
        headers = {"x-access-tokens": App.get_running_app().token}
        dropdown = DropDown()
        try:
            response = requests.get("http://127.0.0.1:5000/clientes", headers=headers)
            if response.status_code == 200:
                clientes = response.json()
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
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
        dropdown.open(instance)

    def show_telefone_dropdown(self, instance):
        headers = {"x-access-tokens": App.get_running_app().token}
        dropdown = DropDown()
        try:
            response = requests.get("http://127.0.0.1:5000/clientes", headers=headers)
            if response.status_code == 200:
                clientes = response.json()
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
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
        dropdown.open(instance)

    def show_hamburguer_dropdown(self, instance):
        headers = {"x-access-tokens": App.get_running_app().token}
        dropdown = DropDown()
        try:
            response = requests.get(
                "http://127.0.0.1:5000/hamburgueres", headers=headers
            )
            if response.status_code == 200:
                hamburgueres = response.json()
                for hamburguer in hamburgueres:
                    btn = Button(text=hamburguer, size_hint_y=None, height=44)
                    btn.bind(on_release=lambda btn: self.select_hamburguer(btn.text))
                    dropdown.add_widget(btn)
            else:
                print(
                    "Falha ao buscar hambúrgueres. Código de estado:",
                    response.status_code,
                )
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)
        dropdown.open(instance)

    def select_cliente(self, nome, cliente):
        self.cliente_input.text = nome
        self.morada_input.text = cliente["morada"]
        self.telefone_input.text = cliente["telefone"]

    def select_telefone(self, telefone, cliente):
        self.telefone_input.text = telefone
        self.cliente_input.text = cliente["nome"]
        self.morada_input.text = cliente["morada"]

    def select_hamburguer(self, nome):
        self.hamburguer_dropdown_button.text = nome

    def submit_order(self, instance):
        data = {
            "nome_cliente": self.cliente_input.text,
            "morada": self.morada_input.text,
            "telefone": self.telefone_input.text,
            "nome_hamburguer": self.hamburguer_dropdown_button.text,
            "quantidade": self.quantidade_input.text,
            "tamanho": self.tamanho_input.text,
        }
        headers = {"x-access-tokens": App.get_running_app().token}
        try:
            response = requests.post(
                "http://127.0.0.1:5000/pedidos", json=data, headers=headers
            )
            if response.status_code == 201:
                print("Pedido registrado com sucesso!")
            else:
                print(
                    "Falha ao registrar pedido. Código de estado:", response.status_code
                )
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)


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
