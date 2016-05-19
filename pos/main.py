from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import ConfigParser
from kivy.properties import ObjectProperty
from kivy.app import App
from POSScreen import *


class MainScreen(Screen):
    pass


class PaymentScreen(Screen):
    label_wid = ObjectProperty()

    def on_pre_enter(self, *args):
        print ('PaymentScreen on_pre_enter...')
        self.label_wid.text = 'Due ' + str(self.manager.get_screen('posscreen').get_total())

    def getProduct(self, productstr):
        product_json = self.manager.get_screen('posscreen').products_json
        code = productstr.split()[0]
        for p in product_json['result']:
            if p['code'] == code:
                return p

    def pay(self):
        def on_success(req, result):
            with open('sale.json', 'w') as fp:
                json.dump(result, fp)
                fp.close()
            self.sale_json = result
            print ('on_success: sale returned.')
            self.manager.get_screen('posscreen').do_clear_item_list()
            self.parent.current = "posscreen"

        def on_failure(req, result):
            print ('on_failure: Could not send payment. Save to file instead.')
            #TODO save order to file
            self.manager.get_screen('posscreen').do_clear_item_list()
            self.parent.current = "posscreen"

        def on_error(req, result):
            print ('on_error: Could not send payment. Save to file instead.')
            #TODO save order to file
            self.manager.get_screen('posscreen').do_clear_item_list()
            self.parent.current = "posscreen"

        try:
            print("Pay and clear list")
            payslip_json = dict([])
            payslip_positions = self.manager.get_screen('posscreen').my_data
            customer = dict([])
            customer['customerid'] = self.manager.get_screen('posscreen').customerid
            payslip_json['customer'] = customer
            payslip_items = []
            for i in payslip_positions:
                print("selling: " + i)
                next_element = self.getProduct(i)
                if next_element is not None:
                    payslip_items.append(next_element)
            payslip_json['items'] = payslip_items
            # clear list
            config = ConfigParser.get_configparser(name='app')
            print(config.get('serverconnection', 'server.url'))
            saleurl = config.get('serverconnection', 'server.url') + "pos/sale/"
            data_json = json.dumps(payslip_json)
            headers = {'Content-type': 'application/jsonrequest', 'Accept': 'application/jsonrequest'}
            if len(self.manager.get_screen('posscreen').my_data) > 0:
                UrlRequest(url=saleurl, on_success=on_success, on_failure=on_failure, on_error=on_error, req_headers=headers, req_body=data_json)
            else:
                self.manager.get_screen('posscreen').do_clear_item_list()
                self.parent.current = "posscreen"
        except:
            print "Error: Could not load products"

class CustomerScreen(Screen):
    def on_pre_enter(self):
        def on_success(req, result):
            with open('customers.json', 'w') as fp:
                json.dump(result, fp)
                fp.close()
            self.products_json = result
            print ('customers loaded.')
            for i in result['result']:
                btn = Button(id=str(i['id']), text=i['name'], size_hint_y=None, width=200, height=20)
                btn.bind(on_press=self.do_action)
                print ('add customer ' + str(i['id']))
                self.customer_list_wid.add_widget(btn)

        try:
            print("Select Customer")
            # clear customer
            config = ConfigParser.get_configparser(name='app')
            print(config.get('serverconnection', 'server.url'))
            customerurl = config.get('serverconnection', 'server.url') + "pos/customers/"
            UrlRequest(customerurl, on_success)
        except:
            print "Error: Could not load products"

    def do_action(self, event):
        print('CustomerScreen Button was ' + str(event))
        self.label_wid.text = event.id
        self.manager.get_screen('posscreen').customerid = event.id


class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("main.kv")

class MainApp(App):
    icon = 'icon.png'
    title = 'Semilimes Point-of-Sale'

    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': 'value1',
            'key2': '0'
        })
        config.setdefaults('serverconnection', {
            'server.url': 'http://127.0.0.1:5000/'
        })

    def close_settings(self, settings):
        super(MainApp, self).close_settings(settings)

    def build_settings(self, settings):
        settings.add_json_panel('General settings',
            self.config, 'settings_custom.json')

    def build(self):
        try:
            print (self.config.get('serverconnection', 'server.url'))
        except:
            print ('serverconnection is not set')

        return presentation

if __name__ == "__main__":
    Window.clearcolor = (0.6, 0.6, 0.6, 1)
    MainApp().run()