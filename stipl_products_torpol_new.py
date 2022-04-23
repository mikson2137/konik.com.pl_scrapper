import requests
from django.core.management.base import BaseCommand, CommandError
import instaloader
import os.path

from deor.settings import MEDIA_ROOT

from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import urllib.request, json
import re, csv
from pprint import pprint

from django.http import HttpResponse


class Command(BaseCommand):
    help = 'Storing data from tre ponti'

    def handle(self, *args, **options):
        print('--- START ---')

        links_to_parse = False
        urls = []
        urls.append(['https://shop.torpol.com/torpol-kolekcja-sport', 'Czpraki', 'torpol, czaprak'])

        except_urls = []

        links_to_parse = False
        # urls.append(['https://balotade.com/produkt/wedzidlo-oliwkowe-podwojnie-lamane-puste-balotade/', 'Wędzidła', 'balotade, wędzidło, wędzidło stal nierdzewna, wędzidło stal'])

        with open('products_torpol.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['ID', 'Type', 'SKU', 'Name', 'Published', 'Is featured?', 'Visibility in catalog', 'Short description',
                 'Description', 'Date sale price starts', 'Date sale price ends', 'Tax status', 'Tax class',
                 'In stock?', 'Stock', 'Backorders allowed?', 'Sold individually?', 'Weight (lbs)', 'Length (in)',
                 'Width (in)', 'Height (in)', 'Allow customer reviews?', 'Purchase note', 'Sale price', 'Regular price',
                 'Categories', 'Tags', 'Shipping class', 'Images', 'Download limit', 'Download expiry days', 'Parent',
                 'Grouped products', 'Upsells', 'Cross-sells', 'External URL', 'Button text', 'Position',
                 'Attribute 1 name', 'Attribute 1 value(s)', 'Attribute 1 visible', 'Attribute 1 global',
                 'Attribute 2 name', 'Attribute 2 value(s)', 'Attribute 2 visible', 'Attribute 2 global',
                 'Meta: _wpcom_is_markdown', 'Download 1 name', 'Download 1 URL', 'Download 2 name', 'Download 2 URL'])

            for url in urls:
                if links_to_parse:
                    single_url_get = url[0]
                    self.add_single_item_to_file(writer, single_url_get, url[1], url[2])

                else:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                    page = requests.get(url[0], headers=headers)
                    soup = BeautifulSoup(page.content, 'html.parser')

                    #  bierze poszczegolne produkty
                    li_list = soup.find_all(class_='product')
                    if not li_list:
                        print('No items on this page')

                    for item in li_list:
                        try:
                            single_url_get = item.find(class_='prodname f-row').get('href')
                            if 'shop.torpol.com' not in single_url_get:
                                single_url_get = 'https://shop.torpol.com' + single_url_get
                            print(single_url_get)
                            if single_url_get in except_urls:
                                continue

                            self.add_single_item_to_file(writer, single_url_get, url[1], url[2])
                        except:
                            print('Something wrong with a product. Skipping it...')
                            print(item)

                    # break
            # break
        print('the end.')

    def add_single_item_to_file(self, writer, single_url_get, categories, tags):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        single_url_get = requests.get(single_url_get, headers=headers)

        soup = BeautifulSoup(single_url_get.content, 'html.parser')
        text_all = soup.find(class_='centercol s-grid-9')

        price = text_all.find(class_='main-price').getText().strip()
        price = price.replace('zł', '').strip()
        price = price.replace(',00', '')
        print(price)
        print('---')
        title = text_all.find(class_='name').getText().strip()
        print(title)
        print('---')

        no_short_desc = False
        try:
            description_all = soup.find(id='box_description').find_all('p')
            description = ''
            for d in description_all:
                if d.getText().strip():
                    description += '<p>' + d.getText().strip() + '</p>'

            print(description)
            print('---')

            description_no_p = description.replace('</p><p>', ', ').replace('<p>', '').replace('</p>', '')
            desc_split = description_no_p.split('.')
            desc_short = desc_split[0] + '.'
            print(desc_short)
            print('---')
        except:
            no_short_desc = True

        img_tag = text_all.find_all(class_='js__open-gallery')
        img = ''
        for i in img_tag:
            try:
                img += 'https://shop.torpol.com' + i.get('data-img-name') + ','
            except:
                pass
        print(img)
        print('---')

        title = title + ' - Torpol'

        # simple product
        writer.writerow(
            ['', 'simple', '', title, 1, 0, 'visible', desc_short, description, '', '', '', '', 1, '', '', '', 0, '',
             '', '', '', '', '', price, categories, tags, '', img, '', '', '', '', '', '', '', '', '', '', '', '', '',
             '', '', ''])

    # variation product
    # writer.writerow(['','variation','',title,1,0,'visible',desc_short,description,'','','','',1,'','','',0,'','','','','','',price,categories,tags,'',img,'','','','','','','','','','','','','','','',''])
