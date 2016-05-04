# -*- coding: utf-8 -*-
from flask_shop import app
from flask import Flask, jsonify
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
