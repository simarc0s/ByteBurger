from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests

class LoginForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.add_widget(Label(text='Username'))
        self.username_input = TextInput()
        self.add_widget(self.username_input)

        self.add_widget(Label(text='Password'))
        self.password_input = TextInput(password=True)
        self.add_widget(self.password_input)

        self.submit = Button(text='Login')
        self.submit.bind(on_press=self.login)
        self.add_widget(self.submit)

    def login(self, instance):
        data = {
            'username': self.username_input.text,
            'password': self.password_input.text
        }
        try:
            response = requests.post('http://127.0.0.1:5000/login', json=data)
            if response.status_code == 200:
                token = response.json()['token']
                self.parent.token = token
                self.parent.show_order_form()
            else:
                print("Falha ao fazer login. Codigo de status:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

class OrderForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.add_widget(Label(text='Nome do Cliente'))
        self.cliente_input = TextInput()
        self.add_widget(self.cliente_input)

        self.add_widget(Label(text='Morada'))
        self.morada_input = TextInput()
        self.add_widget(self.morada_input)

        self.add_widget(Label(text='Telefone'))
        self.telefone_input = TextInput()
        self.add_widget(self.telefone_input)

        self.add_widget(Label(text='Nome do Hamburguer'))
        self.hamburguer_input = TextInput()
        self.add_widget(self.hamburguer_input)

        self.add_widget(Label(text='Quantidade'))
        self.quantidade_input = TextInput()
        self.add_widget(self.quantidade_input)

        self.add_widget(Label(text='Tamanho'))
        self.tamanho_input = TextInput()
        self.add_widget(self.tamanho_input)

        self.submit = Button(text='Registrar Pedido')
        self.submit.bind(on_press=self.submit_order)
        self.add_widget(self.submit)

    def submit_order(self, instance):
        try:
            quantidade = int(self.quantidade_input.text)
        except ValueError:
            print("Quantidade deve ser um número inteiro.")
            return

        data = {
            'nome_cliente': self.cliente_input.text,
            'morada': self.morada_input.text,
            'telefone': self.telefone_input.text,
            'nome_hamburguer': self.hamburguer_input.text,
            'quantidade': quantidade,
            'tamanho': self.tamanho_input.text
        }
        print("Enviando dados para o servidor:", data)
        headers = {'x-access-tokens': self.parent.token}
        try:
            response = requests.post('http://127.0.0.1:5000/pedidos', json=data, headers=headers)
            if response.status_code == 201:
                print("Pedido registrado com sucesso!")
            else:
                print("Falha ao registrar o pedido. Codigo de status:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

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

class OrderApp(App):
    def build(self):
        return MainApp()

if __name__ == '__main__':
    OrderApp().run()