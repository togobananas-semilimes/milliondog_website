import csv
import sys
from proteus import config, Model, Wizard, Report
from decimal import *
import urllib, cStringIO
from PIL import Image
import StringIO

CONFIG = "../tryton.conf"
DATABASE_NAME = "tryton_dev"


def loadCustomers():
    f = open(sys.argv[2], 'rb')
    countrycode = sys.argv[3]
    if countrycode is None:
        print "Please provide a country code. e.g. 'CH'"
    try:
        reader = csv.DictReader(f)
        Lang = Model.get('ir.lang')
        (en,) = Lang.find([('code', '=', 'en_US')])
        Country = Model.get('country.country')
        (ch, ) = Country.find([('code', '=', countrycode)])
        for row in reader:
            print(row['first_name'], row['last_name'], row['company_name'])
            Party = Model.get('party.party')
            party = Party()
            if party.id < 0:
                party.name = row['company_name']
                party.lang = en
                party.addresses[0].name = row['first_name']+' '+row['last_name']
                party.addresses[0].street = row['address']
                party.addresses[0].streetbis = None
                party.addresses[0].zip = row['zip']
                party.addresses[0].city = row['city']
                party.addresses[0].country = ch
                # party.addresses[0].subdivision = row['state']
                party.addresses[0].invoice = True
                party.addresses[0].delivery = True
                party.save()
    finally:
        f.close()

def loadProducts():
    f = open(sys.argv[2], 'rb')
    csvlisttype = sys.argv[3]
    if csvlisttype is None:
        print "Please provide a listtype 'A' or 'B'"
    try:
        Default_uom = Model.get('product.uom')
        default_uom = Default_uom.find([('symbol', '=', 'u')])
        Category = Model.get('product.category')
        category = Category.find([('name', '=', 'Cosy')])
        reader = csv.DictReader(f)
        if csvlisttype == 'A':
            for row in reader:
                print(row['Price'], row['Shipping'], row['Manufacturer'])
                Product = Model.get('product.product')
                product = Product()
                Producttemplate = Model.get('product.template')
                producttemplate = Producttemplate()
                producttemplate.accounts_category = True
                producttemplate.account_category = category[0]
                producttemplate.taxes_category = True
                producttemplate.category = category[0]
                if product.id < 0:
                    product.code = row['ArtNumber']
                    product.name = row['Title']
                    product.description = row['Description_Short']
                    producttemplate.list_price = Decimal(row['Price'])
                    producttemplate.cost_price = Decimal(row['Price'])
                    producttemplate.purchasable = True
                    producttemplate.saleable = True
                    producttemplate.consumable = False
                    producttemplate.default_uom = default_uom[0]
                    producttemplate.type = 'goods'
                    producttemplate.name = row['Title']
                    producttemplate.save()
                    # product.product_template = producttemplate
                    product.template = producttemplate
                    product.save()
        elif csvlisttype == 'B':
            for row in reader:
                print(row['Price'], row['Name'], row['MerchantCategory'])
                Product = Model.get('product.product')
                product = Product()
                Producttemplate = Model.get('product.template')
                producttemplate = Producttemplate()
                producttemplate.accounts_category = True
                producttemplate.account_category = category[0]
                producttemplate.taxes_category = True
                producttemplate.category = category[0]
                if product.id < 0:
                    product.code = row['SKU']
                    product.name = row['Name']
                    product.description = row['Description']
                    producttemplate.list_price = Decimal(row['Price'])
                    producttemplate.cost_price = Decimal(row['Price'])
                    producttemplate.purchasable = True
                    producttemplate.saleable = True
                    producttemplate.consumable = False
                    producttemplate.default_uom = default_uom[0]
                    producttemplate.type = 'goods'
                    producttemplate.name = row['Name']
                    # producttemplate.save()
                    # product.product_template = producttemplate
                    product.template = producttemplate
                    product.save()

    finally:
        f.close()

def loadImages():
    f = open(sys.argv[2], 'rb')
    csvlisttype = sys.argv[3]
    if csvlisttype is None:
        print "Please provide a listtype 'A' or 'B'"
    try:
        reader = csv.DictReader(f)
        if csvlisttype == 'A':
            for row in reader:
                print(row['ArtNumber'], row['Img180_url'], row['Img60_url'])
                if (row['Img180_url'] == ''):
                    continue
                # image 180px
                imagefile = cStringIO.StringIO(urllib.urlopen(row['Img180_url']).read())
                img = Image.open(imagefile)
                output = StringIO.StringIO()
                img.save(output, format="PNG")
                pngcontents = output.getvalue()
                output.close()
                with open('images180/'+row['ArtNumber']+'.png', 'wb') as imgfile:
                    imgfile.write(pngcontents)
                    imgfile.close()
                    imagefile.close()
                # image 60px
                # image 180px
                imagefile = cStringIO.StringIO(urllib.urlopen(row['Img60_url']).read())
                img = Image.open(imagefile)
                output = StringIO.StringIO()
                img.save(output, format="PNG")
                pngcontents = output.getvalue()
                output.close()
                with open('images60/'+row['ArtNumber']+'.png', 'wb') as imgfile:
                    imgfile.write(pngcontents)
                    imgfile.close()
                    imagefile.close()
        if csvlisttype == 'B':
            for row in reader:
                print(row['SKU'], row['URL to Image'], row['URL to thumbnail image'])
                if (row['URL to Image'] == ''):
                    continue
                # image 180px
                imagefile = cStringIO.StringIO(urllib.urlopen(row['URL to Image']).read())
                img = Image.open(imagefile)
                output = StringIO.StringIO()
                img.save(output, format="PNG")
                pngcontents = output.getvalue()
                output.close()
                with open('images/'+row['SKU']+'.png', 'wb') as imgfile:
                    imgfile.write(pngcontents)
                    imgfile.close()
                    imagefile.close()
                # image 60px
                # image 180px
                imagefile = cStringIO.StringIO(urllib.urlopen(row['URL to thumbnail image']).read())
                img = Image.open(imagefile)
                output = StringIO.StringIO()
                img.save(output, format="PNG")
                pngcontents = output.getvalue()
                output.close()
                with open('images/tn/'+row['SKU']+'.png', 'wb') as imgfile:
                    imgfile.write(pngcontents)
                    imgfile.close()
                    imagefile.close()
    finally:
        f.close()


def main():
    config.set_trytond(DATABASE_NAME, config_file=CONFIG)
    trytontype = sys.argv[1]
    f = open(sys.argv[2], 'rb')
    countrycode = sys.argv[3]
    if trytontype is None:
        print "Please provide a type to load"
    elif trytontype == 'customer':
        loadCustomers()
    elif trytontype == 'product':
        loadProducts()
    elif trytontype == 'image':
        loadImages()


if __name__ == '__main__':
    main()