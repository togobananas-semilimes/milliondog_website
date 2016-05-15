import kivy
kivy.require('1.9.1') # replace with your current kivy version !

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.dictadapter import ListAdapter
from kivy.app import App
from kivy.config import Config, ConfigParser
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import json
import urllib2
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
#from escpos import *

class ImageButton(ButtonBehavior, Image):
    pass

TRYTON_HOST = "http://192.168.1.102:5000/pos/products"
TRYTON_HOST_SEARCH = "http://192.168.1.102:5000/pos/product/"

class POSScreen(Screen):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    label_wid = ObjectProperty()
    info = StringProperty()
    products_list = []
    products_json = []
    sale_json = []
    customerid = 0
    payslip_items_list = []
    my_data = ListProperty([])
    selected_value = StringProperty('select a button')

    def __init__(self, **kwargs):
        super(Screen,self).__init__(**kwargs)
        Clock.schedule_once(self.post_init, 0)

    def post_init(self, *args):
        print ('post_init...')

    def on_pre_enter(self, *args):
        def on_success(req, result):
            with open('products.json', 'w') as fp:
                json.dump(result, fp)
                fp.close()
            self.products_json = result
            print ('products loaded.')
            for i in result['result']:
                code = i['code']
                if code == '':
                    code = '200001'
                btn = ImageButton(source='./products/'+code+'-small.png', id=code, text=str(i['id']),
                                  size_hint_y=None, width=300, height=100)
                btn.bind(on_press=self.do_add_item)
                self.products_list.append(btn)
                print ('add online product ' + code)
                self.grid_layout_wid.add_widget(btn)
            self.grid_layout_wid.height = (len(result['result'])/4+4)*100

        try:
            config = ConfigParser.get_configparser(name='app')
            print(config.get('serverconnection', 'server.url'))
            producturl = config.get('serverconnection', 'server.url') + "pos/products/"
            if len(self.products_list) == 0:
                UrlRequest(producturl, on_success)
            else:
                return
        except:
            print "Error: Could not load products"
        print "Initialize products selection"
        for key, val in self.ids.items():
            print("key={0}, val={1}".format(key, val))
        if len(self.products_list) > 0:
            for n in self.products_list:
                self.grid_layout_wid.remove_widget(n)
        if len(self.products_list) == 0:
            with open('products.json') as data_file:
                result = json.load(data_file)
                self.products_json = result
            for i in result['result']:
                code = i['code']
                if code == '':
                    code = '200001'
                btn = ImageButton(source='./products/'+code+'-small.png', id=code, text=str(i['id']),
                                  size_hint_y=None, width=300, height=100)
                btn.bind(on_press=self.do_add_item)
                self.products_list.append(btn)
                print ('add local product ' + code)
                self.grid_layout_wid.add_widget(btn)
            self.grid_layout_wid.height = (len(result['result'])/4+4)*100



    def do_search(self):
        def on_success(req, result):
            print ('search success.')
            for i in result['result']:
                code = str(i['code'])
                if code == '':
                    code = '200001'
                btn = ImageButton(source='./products/'+code+'-small.png')
                btn.bind(on_press=self.do_add_item)
                self.products_list.append(btn)
                self.grid_layout_wid.add_widget(btn)
            self.grid_layout_wid.height = (len(result['result'])/4+4)*100

        if len(self.products_list) > 0:
            for n in self.products_list:
                self.grid_layout_wid.remove_widget(n)
        self.products_list = []
        config = ConfigParser.get_configparser(name='app')
        producturl = config.get('serverconnection', 'server.url') + "pos/product/" + self.text_input_wid.text
        UrlRequest(producturl, on_success)

    def getProduct(self, code):
        for i in self.products_json['result']:
            current_code = i['code']
            if current_code == code:
                return i
        return

    def do_clear_item_list(self):
        print('do_clear_item_list')
        del self.my_data[:]
        self.list_view_wid.height = self.height * 0.6

    def do_add_item(self, event):
        print('Add product button <%s> state is <%s>' % (self, event))
        product = self.getProduct(event.id)
        if product is not None:
            newitem = event.id + " " + product['price'] + " " + str(product['id']) + " " + product['name']
        else:
            newitem = event.id
        print('append item')
        self.my_data.append(newitem)
        print('payslip items')
        #self.payslip_items_list = self.item_list_wid.adapter.data
        if (len(self.payslip_items_list) > 10):
            self.list_view_wid.height = (len(self.payslip_items_list)+4) * 15
        else:
            self.list_view_wid.height = self.height * 0.6
        print('do_add_item finished.')


    def selection_change(self, change):
        print("selection_change")
        self.selected_value = 'Selected: {}'.format(change.text)

    def do_action(self):
        print('Hurray button was ')
        self.label_wid.text = 'Not yet implemented'
        self.info = 'New info text'

    def build(self):
        config = ConfigParser.get_configparser(name='app')
        producturl = config.get('serverconnection', 'server.url') + "pos/product/" + '200018'
        data = json.load(urllib2.urlopen(producturl))
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
