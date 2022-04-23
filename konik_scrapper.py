import csv
import re
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup


def main():
    # links = get_links()
    links = [
        'https://konik.com.pl/p/71/7521651/uwiaz-eskadron-z-kolekcji-platinum-2016-panic-coral-uwiazy-kantary-uwiazy-dla-konia.html']
    get_product_info(links)


def get_links():
    """
    Returns list of links to all products from link
    :return:
    """
    URL = "https://konik.com.pl/SPRENGER"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    how_many_pages = soup.select("a[class=\"button button-light\"]")
    how_many_pages = list(how_many_pages)[1]
    how_many_pages = str(how_many_pages).split(" ")[3].replace('href="', "").replace('"', "")
    how_many_pages = re.findall(r'\d+', how_many_pages)

    links = []
    for i in range(0, int(how_many_pages[0]) + 1):
        to_be_fixed = []

        if i != 0:
            URL = f"https://konik.com.pl/eskadron,{i}.html"
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
        products = soup.select("a[data-correct=\"product-photo-1\"]")
        for product in products:
            to_be_fixed.append(str(product).split(" "))
        for el in to_be_fixed:
            links.append(el[3].replace("href=\"", "").replace("\"><img", ""))
    return links


def get_product_info(links):
    """
    Create lists with all the information about products
    :param links:
    :return:
    """
    with open('products.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
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

    for URL in links:
        # URL = "https://konik.com.pl/p/71/7521651/uwiaz-eskadron-z-kolekcji-platinum-2016-panic-coral-uwiazy-kantary
        # -uwiazy-dla-konia.html"
        # URL = "https://konik.com.pl/Worek-do-prania-ochraniaczy-ESKADRON"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        is_available = soup.find(id="pinfo_availability")
        is_available = is_available.getText()
        if is_available == "1 dni":
            title = soup.find(class_="pinfo-name").getText()

            try:
                description = soup.find(class_='product-description')
                print(URL)
                description = str(description.getText())
                description = [line for line in description.split('\n') if line.strip() != '']
                final_description = ''
                for el in description:
                    final_description = final_description + el
            except AttributeError:
                final_description = ''

            is_on_sale = soup.find(class_="view_price")
            is_on_sale = is_on_sale.find_next("div").getText()
            if "PLN" not in is_on_sale:
                price = soup.select_one('span[itemprop="price"]')
                price = price.getText().replace(',', '.')
            else:
                price = is_on_sale
                price = price.replace(',', '.').replace(" PLN", "")
            price = [line for line in price.split('\n') if line.strip() != '']

            categories = soup.find(class_="breadcrumb-ajax")
            categories = categories.getText()
            categories = [line for line in categories.split('\n') if line.strip() != '']
            del categories[0]
            del categories[len(categories) - 1]

            final_categories = ""

            for el in categories:
                final_categories = final_categories + el + ' > '
            categories = final_categories[:-3]

            tags = ''

            img = soup.find(id="img_main_0")
            img = img['data-zoom-image']

            print(render_JS(URL))

            attributes = soup.find(class_="rc-page-pinfo")


            with open('products.csv', 'a', newline='') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(['', 'simple', '', title, 1, 0, 'visible', '', final_description, '', '', '', '', 1, '',
                                 '', '', 0, '',
                                 '', '', '', '', '', price[0], categories, tags, '', img, '', '', '', '', '', '',
                                 'attribute1',
                                 '', '', '', '',
                                 '', '', '', '', ''])

def render_JS(URL):
    session = HTMLSession()
    r = session.get(URL)
    r.html.render()
    return r.html.text


if __name__ == "__main__":
    main()
