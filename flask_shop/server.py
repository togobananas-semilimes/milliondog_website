# -*- coding: utf-8 -*-
from flask_shop import app
from flask import Flask, jsonify, request
from proteus import config, Model, Wizard, Report

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
            Product = Model.get('product.product')
            product = Product.find(['id', '=', '21'])
            line = sale.lines.new(quantity=1)
            line.product = product[0]
            line.description = product[0].name
            line.quantity = 1
            line.sequence = 1
            sale.save()
            saleId = sale.id

    # create response
    config.set_trytond(DATABASE_NAME, config_file=CONFIG)
    Product = Model.get('product.product')
    product = Product.find(['id', '>=', '11'])
    list = []
    Attachments = Model.get('ir.attachment')
    Template = Model.get('product.template')
    for n in product:
        list.append({'id': str(n.id), 'code': n.code, 'name': n.name, 'price': str(n.list_price)})
    return jsonify(result=list)
