from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import ConfigParser
from POSScreen import *


class MainScreen(Screen):
    pass


class PaymentScreen(Screen):
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
            payslip_json = []
            payslip_positions = self.manager.get_screen('posscreen').my_data
            for i in payslip_positions:
                print("selling: " + i)
                next_element = self.getProduct(i)
                if next_element is not None:
                    payslip_json.append(next_element)
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
    def select_customer(self):
        try:
            print("Select Customer")
            # clear customer
            config = ConfigParser.get_configparser(name='app')
            print(config.get('serverconnection', 'server.url'))
            saleurl = config.get('serverconnection', 'server.url') + "pos/sale/"
        except:
            print "Error: Could not load products"

    def do_action(self, args):
        print('Hurray button was ')
        self.label_wid.text = args[0].text


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