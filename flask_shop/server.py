# -*- coding: utf-8 -*-
from flask_shop import app
from flask import Flask, jsonify, request
from proteus import config, Model, Wizard, Report
import time
import decimal
from escpos import *

CONFIG = "./tryton.conf"
DATABASE_NAME = "tryton_dev"
config.set_trytond(DATABASE_NAME, config_file=CONFIG)


@app.route("/pos/products/", methods=['GET'])
def get_products():
    config.set_trytond(DATABASE_NAME, config_file=CONFIG)
    Product = Model.get('product.product')
    product = Product.find(['id', '>=', '11'])
    list = []
    Attachments = Model.get('ir.attachment')
    Template = Model.get('product.template')
    for n in product:
        list.append({'id': str(n.id), 'code': n.code, 'name': n.name, 'price': str(n.list_price)})
    return jsonify(result=list)


@app.route('/pos/product/<productid>')
def search_product(productid=None):
    config.set_trytond(DATABASE_NAME, config_file=CONFIG)
    Product = Model.get('product.product')
    product = Product.find(['code', '=', productid])
    list = []
    for n in product:
        list.append({'id': str(n.id), 'code': n.code, 'name': n.name, 'price': str(n.list_price)})
    return jsonify(result=list)


@app.route("/pos/sale/", methods=['GET', 'POST'])
def make_sale():
    payslip = request.get_json(force=True)
    # create sale order
    config.set_trytond(DATABASE_NAME, config_file=CONFIG)
    Party = Model.get('party.party')
    party = Party()
    if (party.id < 0):
        party.name = 'Customer'
        Lang = Model.get('ir.lang')
        (en,) = Lang.find([('code', '=', 'en_US')])
        party.lang = en
        party.addresses[0].name = 'Customer Shop'
        party.addresses[0].street = None
        party.addresses[0].streetbis = None
        party.addresses[0].zip = None
        party.addresses[0].city = None
        Country = Model.get('country.country')
        (ch, ) = Country.find([('code', '=', 'CH')])
        party.addresses[0].country = ch
        # address.subdivision = None
        party.addresses[0].invoice = False
        party.addresses[0].delivery = False
        party.save()

        Sale = Model.get('sale.sale')
        sale = Sale()
        if (sale.id < 0):
            sale.party = party
            Paymentterm = Model.get('account.invoice.payment_term')
            paymentterm = Paymentterm.find([('name', '=', 'cash')])
            sale.payment_term = paymentterm[0]
            for payslip_line in payslip:
                Product = Model.get('product.product')
                product = Product.find(['id', '=', payslip_line['id']])
                line = sale.lines.new(quantity=1)
                line.product = product[0]
                line.description = product[0].name
                line.quantity = 1
                line.sequence = 1
            sale.save()
            saleId = sale.id


    # max line: Epson.text("012345678901234567890123456789012345678901\n")
    Epson = printer.Usb(0x04b8,0x0202)
    # Print image
    Epson.text("\n\n")
    with app.open_resource('logo.gif') as f:
        Epson.image(f)
    # Print Header
    Epson.text("\n\n")
    Epson.set(align='center')
    Epson.text("Milliondog - the cosy company\n")
    Epson.text(time.strftime('%X %x %Z')+"\n")
    # Print text
    Epson.set(align='left')
    Epson.text("\n\n")
    Epson.text("Pos  Beschreibung                Betrag   \n")
    Epson.text("                                          \n")
    total = decimal.Decimal(0.00)
    for counter, payslip_line in enumerate(payslip):
        pos_left = str(counter) + "  " + payslip_line['code'] + " " + payslip_line['name']
        pos_right = payslip_line['price'] + " CHF\n"
        Epson.text(pos_left + pos_right.rjust(42 - len(pos_left)))
        total = total + decimal.Decimal(payslip_line['price'])
    Epson.text("                                          \n")
    Epson.text("------------------------------------------\n")
    payslip_total = str(total) + " CHF\n"
    Epson.text("Total :   " + payslip_total.rjust(42 - 10))
    # Print text
    Epson.text("\n\n")
    Epson.set(font='b', align='center')
    Epson.text("Powered by Semilimes\n")
    # Cut paper
    Epson.text("\n\n")
    Epson.cut()

    # create response
    SaleResult = Model.get('sale.sale')
    saleResult = SaleResult.find(['id', '=', saleId])
    list = []
    for n in saleResult:
        list.append({'id': str(n.id), 'party': str(n.party.id)})
    return jsonify(result=list)
