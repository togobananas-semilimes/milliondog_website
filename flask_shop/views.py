# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, redirect, session, url_for, request, g
from flask_login import login_required, current_user
from flask_shop import app
from .forms import LoginForm, ContactForm, CheckoutForm
from proteus import config, Model, Wizard, Report
from flask.ext.babel import gettext, refresh
from flask_shop import babel
from .models import User
from werkzeug.datastructures import ImmutableOrderedMultiDict
import time
import requests
from decimal import *

CONFIG = "./tryton.conf"
config.set_trytond("tryton_dev3", config_file=CONFIG)

@babel.localeselector
def get_locale():
    try:
        if session['lang_code'] is not None:
            return session['lang_code'];
    except KeyError:
        # session is not initialized
        return 'de'
    return app.config['BABEL_DEFAULT_LOCALE']

@babel.timezoneselector
def get_timezone():
    user = g.get('user', None)
    if user is not None:
        return user.timezone

@app.before_request
def before_request():
    g.user = current_user
    g.user.locale = get_locale()

def getProductFromSession():
    try:
        if session['productid'] is not None:
            Product = Model.get('product.product')
            product = Product.find(['id', '=', session['productid']])
            return product
    except KeyError:
        # session is not initialized
        return None


@app.route("/about/")
def about():
    page_topic = gettext(u'About us')
    page_content = gettext(u'''
                We created Milliondog because we love dogs. Milliondog symbolizes the importance of a dog for his owner and our philosophy reflects just that. Each Milliondog Cosy is unique in material and colour and emphasises the individual personality and uniqueness of your pawesome darling.
                <br><br>We love our work and you can see this in every Cosy.
                ''')
    return render_template('about.html', pt=page_topic, pc=page_content, title="Milliondog", page='About')

@app.route("/home/")
def home():
    page_topic = gettext(u'Gallery')
    page_content = gettext(u'Gallery:')
    return render_template('home.html', pt=page_topic, pc=page_content, title="Milliondog", page='Home')

@app.route("/products/")
def products():
    config.set_trytond("tryton_dev3", config_file=CONFIG)
    Product = Model.get('product.product')
    product = Product.find(['id', '>=', '0']);
    return render_template('products.html', db_model='Products', db_list=product, title="Milliondog", page='Products')

@app.route("/")
@app.route('/index/')
def index():
    try:
        if session['lang_code'] is None:
            session['lang_code'] = 'de'
    except KeyError:
        # session not initialized
        session['lang_code'] = 'de'
        session['currency_code'] = 'CHF'
    page_topic = gettext(u'Start')
    print gettext(u'Payment')
    page_content = gettext(u'exclusive accessoires for your awesome darling')
    return render_template('index.html', pt=page_topic, pc=page_content, title="Milliondog", page='the cosy-company')


@app.route('/productcategories/')
def product_categories():
    config.set_trytond("tryton_dev3", config_file=CONFIG)
    ProductCategory = Model.get('product.category')
    categories = ProductCategory.find(['id', '>=', '0'])
    idlist = [c.name for c in categories]
    return render_template('productcategories.html', db_model='Product Categories', db_list=idlist, title="Milliondog", page='Product Categories')



@app.route('/cart/')
def cart():
    config.set_trytond("tryton_dev3", config_file=CONFIG)
    User = Model.get('res.user')
    user = User.find(['id', '=', '1'])
    product = getProductFromSession()
    session['user_name'] = 'paypal_testuser'
    return render_template('cart.html', message=user[0].name, id=user[0].id, product=product, title="Milliondog", page='Einkaufswagen')


@app.route('/cart/add/<productid>')
def cart_add(productid=None):
    session['productid'] = productid
    return redirect("/cart")

@app.route('/account/')
def account():
    config.set_trytond("tryton_dev3", config_file=CONFIG)
    User = Model.get('res.user')
    user = User.find(['id', '=', '1'])
    Party = Model.get('party.party')
    partyList = Party.find(['id', '>=', '0'])
    return render_template('account.html', message=user[0].name, id=user[0].id, db_list=partyList, title="Milliondog", page='Account')


@app.route('/setlang/<language>')
def setlang(language=None):
    setattr(g, 'lang_code', language)
    session['lang_code'] = language
    refresh()
    return redirect("/")

@app.route('/setcurrency/<currency>')
def setcurrency(currency=None):
    setattr(g, 'currency_code', currency)
    session['currency_code'] = currency
    return redirect("/")

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for name="%s", remember_me=%s' %
              (form.name.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/')

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    page_topic = gettext(u'Contact')
    page_content = gettext(u'You can send us a message here:')
    form = ContactForm()
    if form.validate_on_submit():
        flash('Send message for name="%s", email=%s, message=%s, answer=%s' %
              (form.name.data, form.email.data, form.message.data, form.answer.data))
        return redirect('/index')
    return render_template('contact.html',
                           pt=page_topic, pc=page_content, title="Milliondog", page='Contact',
                           form=form)

# Checkout process
@app.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    config.set_trytond("tryton_dev3", config_file=CONFIG)
    page_topic = gettext(u'Checkout')
    page_content = gettext(u'Please enter your address here:')
    product = getProductFromSession()
    form = CheckoutForm()
    if form.validate_on_submit():
        Party = Model.get('party.party')
        party = Party()
        if (party.id < 0):
            party.name = form.name.data
            Lang = Model.get('ir.lang')
            (en,) = Lang.find([('code', '=', 'en_US')])
            party.lang = en
            party.addresses[0].name = form.name2.data
            party.addresses[0].street = form.street.data
            party.addresses[0].streetbis = form.street2.data
            party.addresses[0].zip = form.zip.data
            party.addresses[0].city = form.city.data
            Country = Model.get('country.country')
            (ch, ) = Country.find([('code', '=', 'CH')])
            party.addresses[0].country = ch
            # address.subdivision = None
            party.addresses[0].invoice = form.invoice.data
            party.addresses[0].delivery = form.delivery.data
            party.save()

            Sale = Model.get('sale.sale')
            sale = Sale()
            if (sale.id < 0):
                sale.party = party
                line = sale.lines.new(quantity=1)
                line.product = product[0]
                line.description = product[0].name
                line.quantity = 1;
                line.sequence = 1;
                sale.save()
                session['sale_id'] = sale.id
        flash('Checkout started successfully name="%s", name2=%s, saleid=%s' %
              (form.name.data, str(form.name2.data), sale.id))

        return redirect('/payment')
    return render_template('checkout.html',
                           pt=page_topic, pc=page_content, product=product, title="Milliondog", page='Checkout',
                           form=form)


#Paypal
@app.route('/payment/')
def payment():
    try:
        session['logged_in'] = 'user1'
        page_topic = gettext(u'Payment')
        page_content = gettext(u'Please follow the link to pay with Paypal:')
        return render_template("payment.html", pt=page_topic, pc=page_content, title="Milliondog", page='Payment')
    except Exception, e:
        return(str(e))


@app.route('/success/', methods=['POST', 'GET'])
def success():
    try:
        flash('Paypal payment completed successfully.')
        return render_template("success.html")
    except Exception, e:
        return(str(e))

@app.route('/cancel/', methods=['POST', 'GET'])
def cancel():
    try:
        flash('Paypal payment failed..')
        return render_template("paymentfailed.html")
    except Exception, e:
        return(str(e))


@app.route('/testpayment/')
def testpayment():
    config.set_trytond("tryton_dev3", config_file=CONFIG)
    Sale = Model.get('sale.sale')
    saleid = 15
    payment_gross = 55.00
    saleList = Sale.find(['id', '=', saleid]);
    if saleList is not None:
        check_order = True
        if (saleList[0].state != 'draft'):
            check_order = False
        if (saleList[0].currency.symbol != 'CHF'):
            check_order = False

        SaleLine = Model.get('sale.line')
        saleLine = SaleLine.find(['sale', '=', saleid])
        saleTotal = Decimal(0.00)
        for n in saleLine:
            saleTotal += n.unit_price * Decimal(n.quantity)
        if (Decimal(payment_gross) < saleTotal):
            check_order = False
        if check_order:
            # change sale state to 'confirmed'
            saleList[0].comment += 'PAYPAL IPN DATA\n'+'\n'
            saleList[0].save()
            saleList[0].click('quote')
        else:
            # add note that something failed in payment
            saleList[0].comment = 'ERROR WITH PAYPAL IPN DATA\n'+'\n'
            saleList[0].save()


@app.route('/ipn/', methods=['POST'])
def ipn():
    try:
        arg = ''
        request.parameter_storage_class = ImmutableOrderedMultiDict
        values = request.form
        for x, y in values.iteritems():
            arg += "&{x}={y}".format(x=x,y=y)

        validate_url = 'https://www.sandbox.paypal.com' \
                        '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
                        .format(arg=arg)
        r = requests.get(validate_url)
        if r.text == 'VERIFIED':
            try:
                payer_email = request.form.get('payer_email')
                unix = int(time.time())
                payment_date = request.form.get('payment_date')
                saleid = request.form.get('custom')
                last_name = request.form.get('last_name')
                payment_gross = request.form.get('mc_gross')
                payment_fee = request.form.get('mc_fee')
                payment_currency = request.form.get('mc_currency')
                payment_net = float(payment_gross) - float(payment_fee)
                payment_status = request.form.get('payment_status')
                txn_id = request.form.get('txn_id')
            except Exception as e:
                with open('/tmp/ipnout.txt','a') as f:
                    data = 'ERROR WITH IPN DATA\n'+str(values)+'\n'
                    f.write(data)

            with open('/tmp/ipnout.txt','a') as f:
                data = 'SUCCESS\n'+str(values)+'\n'
                f.write(data)

            # user_name, mc_gross, mc_fee, mc_currency need to be checked in database
            # mark order in tryton as paid
            # c.execute("INSERT INTO ipn (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            #           (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id))
            config.set_trytond("tryton_dev3", config_file=CONFIG)
            Sale = Model.get('sale.sale')
            saleList = Sale.find(['id', '=', saleid]);
            if saleList is not None:
                check_order = True
                if (saleList[0].state != 'draft'):
                    check_order = False
                if (saleList[0].currency.symbol != payment_currency):
                    check_order = False

                saleLine = saleList[0].lines
                saleTotal = Decimal(0.00)
                for n in saleLine:
                    saleTotal += n.unit_price * Decimal(n.quantity)
                if (Decimal(payment_gross) < saleTotal):
                    check_order = False
                if check_order:
                    # change sale state to 'confirmed'
                    if saleList[0].comment is None:
                        saleList[0].comment = 'PAYPAL IPN DATA\n'+str(values)+'\n'
                    else:
                        saleList[0].comment += '\nPAYPAL IPN DATA\n'+str(values)+'\n'
                    saleList[0].save()
                    try:
                        saleList[0].click('quote')
                    except Exception as e:
                        print 'Exception: Could not update sale state '+str(e)
                else:
                    # add note that something failed in payment
                    saleList[0].comment = 'ERROR WITH PAYPAL IPN DATA\n'+str(values)+'\n'
                    saleList[0].save()
        else:
            with open('/tmp/ipnout.txt','a') as f:
                data = 'FAILURE\n'+str(values)+'\n'
                f.write(data)

        return r.text
    except Exception as e:
        return str(e)