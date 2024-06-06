import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Classe responsável pelo formulário de login
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
            response = requests.post(
                "http://127.0.0.1:5000/login", json=data
            )
            if response.status_code == 200:
                token = response.json()["token"]
                self.parent.token = token
                self.parent.show_order_form()
            else:
                print("Falha ao fazer login. Código de estado:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

# Classe responsável pelo formulário de pedidos
class OrderForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        self.add_widget(Label(text="Nome do Cliente"))
        self.cliente_input = TextInput()
        self.add_widget(self.cliente_input)

        self.add_widget(Label(text="Morada"))
        self.morada_input = TextInput()
        self.add_widget(self.morada_input)

        self.add_widget(Label(text="Telefone"))
        self.telefone_input = TextInput()
        self.add_widget(self.telefone_input)

        self.search_by_phone = Button(text="Procurar por Telefone")
        self.search_by_phone.bind(on_press=self.search_client_by_phone)
        self.add_widget(self.search_by_phone)

        self.search_by_name = Button(text="Procurar por Nome")
        self.search_by_name.bind(on_press=self.search_client_by_name)
        self.add_widget(self.search_by_name)

        self.add_widget(Label(text="Nome do Hamburguer"))
        self.hamburguer_input = TextInput()
        self.add_widget(self.hamburguer_input)

        self.add_widget(Label(text="Quantidade"))
        self.quantidade_input = TextInput()
        self.add_widget(self.quantidade_input)

        self.add_widget(Label(text="Tamanho"))
        self.tamanho_input = TextInput()
        self.add_widget(self.tamanho_input)

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
        headers = {"x-access-tokens": self.parent.token}
        try:
            response = requests.post(
                "http://127.0.0.1:5000/pedidos", json=data, headers=headers
            )
            if response.status_code == 201:
                print("Pedido registado com sucesso!")
            else:
                print("Falha ao registar o pedido. Código de estado:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

    def search_client_by_phone(self, instance):
        telefone = self.telefone_input.text
        headers = {"x-access-tokens": self.parent.token}
        try:
            response = requests.get(f"http://127.0.0.1:5000/clientes/{telefone}", headers=headers)
            if response.status_code == 200:
                cliente = response.json()
                self.cliente_input.text = cliente["nome"]
                self.morada_input.text = cliente["morada"]
            else:
                print("Cliente não encontrado. Código de estado:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

    def search_client_by_name(self, instance):
        nome = self.cliente_input.text
        headers = {"x-access-tokens": self.parent.token}
        try:
            response = requests.get(f"http://127.0.0.1:5000/clientes/nome/{nome}", headers=headers)
            if response.status_code == 200:
                clientes = response.json()
                if clientes:
                    cliente = clientes[0]
                    self.cliente_input.text = cliente["nome"]
                    self.morada_input.text = cliente["morada"]
                else:
                    print("Nenhum cliente encontrado com esse nome.")
            else:
                print("Falha ao buscar cliente. Código de estado:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

# Classe principal que contém os formulários de login e de pedidos
class MainApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = None
        self.login_form = LoginForm()
        self.order_form = OrderForm()
        self.add_widget(self.login_form)

    def show_order_form(self):
        self.clear_widgets()
        self.add_widget(self.order_form)

# Classe da aplicação Kivy
class OrderApp(App):
    def build(self):
        return MainApp()

# Executa a aplicação
if __name__ == "__main__":
    OrderApp().run()