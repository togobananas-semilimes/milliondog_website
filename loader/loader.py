import csv
import sys
from proteus import config, Model, Wizard, Report

CONFIG = "../tryton.conf"
DATABASE_NAME = "tryton_dev"


def main():
    config.set_trytond(DATABASE_NAME, config_file=CONFIG)
    f = open(sys.argv[1], 'rb')
    countrycode = sys.argv[2]
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


if __name__ == '__main__':
    main()