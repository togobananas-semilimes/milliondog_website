from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import ConfigParser
from POSScreen import *

class MainScreen(Screen):
    pass

class PaymentScreen(Screen):
    def pay(self):
        def on_success(req, result):
            with open('products.json', 'w') as fp:
                json.dump(result, fp)
                fp.close()
            self.products_json = result
            print ('products loaded.')
            self.manager.get_screen('posscreen').do_clear_item_list()
            self.parent.current = "posscreen"

        try:
            print("Pay and clear list")
            payslip_positions = POSScreen.payslip_items_list
            for i in payslip_positions:
                print("selling: " + i)
            # clear list
            config = ConfigParser.get_configparser(name='app')
            print(config.get('serverconnection', 'server.url'))
            saleurl = config.get('serverconnection', 'server.url') + "pos/sale/"
            data_json = json.dumps(payslip_positions)
            headers = {'Content-type': 'application/jsonrequest', 'Accept': 'application/jsonrequest'}
            if len(POSScreen.payslip_items_list) > 0:
                UrlRequest(url=saleurl, on_success=on_success, req_headers=headers, req_body=data_json)
            else:
                return
        except:
            print "Error: Could not load products"

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