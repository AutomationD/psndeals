import requests
import json
from pprint import pprint
import operator
import time
import click
import psndeals.auth

from tabulate import tabulate

class Psndeals(object):
    def __init__(self):
        self.verbose = False

    def __repr__(self):
        return '<Psndeals %r>' % self.home


pass_psndeals = click.make_pass_decorator(Psndeals)

@click.group()
@click.option('--verbose', '-v', is_flag=True,
              help='Enables verbose mode.')
@click.option('--config', nargs=2, multiple=True,
              metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.pass_context
def cli(ctx, config, verbose):
    """Example script."""
    ctx.obj = Psndeals()
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)



@cli.command()
@click.option('--platform', '-p', default='ps4')
@click.option('--country', '-c', default='US')
@click.option('--sort', '-s', type=click.Choice(['savings', 'price']), default='savings')
@click.option('--reverse-sort', '-r', is_flag=True, default=True)
@pass_psndeals
def show(psndeals, platform, country, sort, reverse_sort):
    deals = get_deals(platform, country)
    if deals:
        # Sort
        deals.sort(key=operator.itemgetter(sort), reverse=reverse_sort)
        for i, deal in enumerate(deals):
            if deal['savings'] > 15 or (deal['savings'] > 10 and deal['discount'] == 100):
                click.secho(u"------------------------------------------------------")

                click.secho(u"{name} ({release_date})".format(name=deal['name'], release_date=time.strftime("%b %Y", deal['release_date'])), fg='blue')
                # click.secho(u"Price: ${price}.\nOriginal price: ${orig_price}.\nSavings: ${savings}".format(price=deal['price'],name=deal['name'], discount=deal['discount'], orig_price=deal['orig_price'], savings=deal['savings']))

                if deal['price'] == 0:
                    click.secho(u"Price: {price}".format(price="Free"), fg='green')
                else:
                    click.secho(u"Price: ${price}".format(price=deal['price']))
                click.secho(u"Original price: ${orig_price}.".format(orig_price=deal['orig_price']))
                click.secho(u"Savings: ${savings}".format(savings=deal['savings']))

                # print(i)
                # print(len(deals)-1)
                if i == len(deals)-1:
                    click.secho(u"------------------------------------------------------")



# https://store.playstation.com/kamaji/api/chihiro/00_09_000/user/checkout/cart/items
# [{"sku_id":"UP0700-NPUB31729_00-SSSSDLC01FTP0104-U099"}]

# STORE-MSF77008-PPLAYSTATIONPLUS
# STORE-MSF77008-PSPLUSMEMBER
# STORE-MSF77008-PSPLUSFREEGAMES

def authorize():
    SCOPE = 'kamaji:get_vu_mylibrary,kamaji:get_recs,kamaji:get_internal_entitlements,versa:user_get_payment_instruments,versa:user_get_payment_instrument'
    REDIRECT_URL = 'com.scee.psxandroid.scecompcall://redirect'

    CONSUMER_KEY = 'b0d0d7ad-bb99-4ab1-b25e-afa0c76577b0'
    CONSUMER_SECRET = 'Zo4y8eGIa3oazIEp'

    FORM_URL = 'https://reg.api.km.playstation.net:443/regcam/mobile/sign-in.html'
    OAUTH_URL = 'https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/token'

    #https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/authorize?response_type=token&scope=kamaji:get_vu_mylibrary,kamaji:get_recs,kamaji:get_internal_entitlements,versa:user_get_payment_instruments,versa:user_get_payment_instrument&service_entity=urn:service-entity:psn&prompt=none&signInInput_SignInID=dmitry@kireev.co&signInInput_Password=Boredom87Ps4!
    #https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/authorize?response_type=token
    # signInInput_SignInID
    # signInInput_Password
    pass

def get_store_urls(platform, country):    
    request_data = '{}'
    store_urls = []

    # Load Weekly Deals
    weekly_deals_url = 'https://store.playstation.com/store/api/chihiro/00_09_000/container/US/en/999/STORE-MSF77008-WEEKLYDEALS'
    response = requests.get(weekly_deals_url, data=request_data)
    
    if response.ok:
        response_data = json.loads(response.content)
        for link in response_data['links']:            
            if 'url' in link:
                store_urls.append(link['url'])
        
    additional_stores = [
        'STORE-MSF77008-PSPLUSDISCOUNTS',
        'STORE-MSF77008-PSPLUSFREEGAMES',
    ]

    for additional_store in additional_stores:
        store_urls.append("https://store.sonyentertainmentnetwork.com/store/api/chihiro/00_09_000/container/US/en/999/{additional_store}".format(additional_store=additional_store, platform=platform))
    
    # Add platform and country filters
    for key, store_url in enumerate(store_urls):
        store_urls[key] = store_url + "?platform={platform}&country={country}".format(platform=platform, country=country)

    return store_urls
    
def get_deals(platform, country):    
    urls = get_store_urls(platform, country)
    # exit(0)

    deals = []
    for url in urls:
        request_data = '{}'
        response = requests.get(url, data=request_data)

        if response.ok:
            response_data = json.loads(response.content)
            for item in response_data['links']:
                if 'default_sku' in item:
                    deals.append({
                        'psn_sku_id': item['id'],
                        'name': item['name'],
                        'discount': item['default_sku']['rewards'][0]['discount'],
                        'orig_price': (item['default_sku']['price'] / 100),
                        'price': (item['default_sku']['rewards'][0]['price'] / 100),
                        'savings': round((item['default_sku']['price'] / 100 * item['default_sku']['rewards'][0]['discount'] / 100),2),
                        'release_date': time.strptime(item['release_date'], "%Y-%m-%dT%H:%M:%SZ") # 2015-12-05T00:00:00Z
                    })
        else:
            # If response code is not ok (200), print the resulting http error code with description
            response.raise_for_status()
    return deals

