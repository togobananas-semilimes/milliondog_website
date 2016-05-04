import kivy
kivy.require('1.9.1') # replace with your current kivy version !

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.dictadapter import ListAdapter
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
import json
import urllib2
#from escpos import *

class ImageButton(ButtonBehavior, Image):
    pass

TRYTON_HOST = "http://192.168.1.102:5000/pos/products"
TRYTON_HOST_SEARCH = "http://192.168.1.102:5000/pos/product/"

class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    label_wid = ObjectProperty()
    info = StringProperty()
    list_adapter = ListAdapter(data=["Item #{0}".format(i) for i in range(10)], cls=ListItemButton, sorted_keys=[])
    products_widgets = []

    def do_action(self):
        if len(self.products_widgets) > 0:
            for n in self.products_widgets:
                self.grid_layout_wid.remove_widget(n)
        self.products_widgets = []
        self.label_wid.text = 'My label after button press'
        self.info = 'New info text'
        data = json.load(urllib2.urlopen(TRYTON_HOST))
        print (data)
        for i in data['result']:
            code = i['code']
            if code == '':
                code = '200001'
            btn = ImageButton(source='./products/'+code+'-small.png', text=str(i['id']),
                              size_hint_y=None, width=300, height=100)
            btn.bind(on_press=self.do_add_item)
            #btn = Button(text=str(i.id), size_hint_y=None, height=40)
            #btn.bind(on_press=self.do_add_item)
            self.products_widgets.append(btn)
            self.grid_layout_wid.add_widget(btn)
        self.grid_layout_wid.height = (len(data['result'])/4+4)*100
        #self.scroll_view_wid.add_widget(layout)

    def do_search(self):
        if len(self.products_widgets) > 0:
            for n in self.products_widgets:
                self.grid_layout_wid.remove_widget(n)
        self.products_widgets = []
        data = json.load(urllib2.urlopen(TRYTON_HOST_SEARCH+self.text_input_wid.text))
        print (data)
        for i in data['result']:
            code = str(i['code'])
            if code == '':
                code = '200001'
            btn = ImageButton(source='./products/'+code+'-small.png')
            btn.bind(on_press=self.do_add_item)
            #btn = Button(text=str(i.id), size_hint_y=None, height=40)
            #btn.bind(on_press=self.do_add_item)
            self.products_widgets.append(btn)
            self.grid_layout_wid.add_widget(btn)
        self.grid_layout_wid.height = (len(data['result'])/4+4)*100
        #self.scroll_view_wid.add_widget(layout)

    def do_add_item(self, event):
        print('My button <%s> state is <%s>' % (self, event))
        self.list_adapter = ListAdapter(data=["Item #{0}".format(i) for i in range(10)], cls=ListItemButton, sorted_keys=[])
        self.list_adapter.bind(on_selection_change=self.selection_change)
        self.item_list_wid.my_list_view = ListView(adapter=self.list_adapter)

    def selection_change(self, adapter, *args):
        if self.change_from_code:
            print "selection change from code"
        else:
            print "selection changed by click"

    def build(self):
        data = json.load(urllib2.urlopen(TRYTON_HOST_SEARCH+'200018'))
        product = data['result'][0]
        layout = BoxLayout(orientation='vertical')
        # use a (r, g, b, a) tuple
        blue = (0, 0, 1.5, 2.5)
        red = (2.5, 0, 0, 1.5)
        btn = Button(text='Touch me!'+product['name'], background_color=blue, font_size=40)
        btn.bind(on_press=self.callback)
        self.label = Label(text="------------", font_size='50sp')
        layout.add_widget(btn)
        layout.add_widget(self.label)
        return layout

'''    def callback(self, event):
        data = json.load(urllib2.urlopen(TRYTON_HOST_SEARCH+'200018'))
        product = data['result'][0]
        """ Seiko Epson Corp. Receipt Printer M129 Definitions (EPSON TM-T88IV) """
        Epson = printer.Usb(0x04b8,0x0202)
        # Print text
        Epson.text(str(product[0].id) + ' ' + product['name'] + ' ' + str(product[0].list_price) + '\n')
        # Print image
        Epson.image("logo.gif")
        # Print QR Code
        Epson.qr("http://www.milliondog.com")
        # Print barcode
        Epson.barcode('1324354657687','EAN13',64,2,'','')
        # Cut paper
        Epson.cut()
        print("button touched")  # test
        self.label.text = "button touched"
'''



class ControllerApp(App):

    def build(self):
        Window.clearcolor = (0.6, 0.6, 0.6, 1)
        return Controller(info='Hello world')

if __name__ == '__main__':
    ControllerApp().run()
