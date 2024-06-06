from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

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
        pass

class OrderApp(App):
    def build(self):
        return OrderForm()

if __name__ == '__main__':
    OrderApp().run()