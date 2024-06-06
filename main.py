from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests

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
        try:
            response = requests.post('http://127.0.0.1:5000/pedidos', json=data)
            if response.status_code == 201:
                print("Pedido registrado com sucesso!")
            else:
                print("Falha ao registrar o pedido. Codigo de status:", response.status_code)
                print("Resposta do servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao conectar ao servidor:", e)

class OrderApp(App):
    def build(self):
        return OrderForm()

if __name__ == '__main__':
    OrderApp().run()