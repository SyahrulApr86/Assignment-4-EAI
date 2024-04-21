from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


def get_categories():
    categories_url = "https://books.toscrape.com/"
    response = requests.get(categories_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    categories = {}

    for category in soup.find('div', class_='side_categories').find_all('a')[1:]:
        cat_name = category.get_text().strip()
        cat_url = categories_url + category.get('href')
        if cat_name != 'Erotica':
            categories[cat_name] = cat_url

    return categories


def scrape_books(category_url=None, max_pages=3):
    books = []
    if not category_url:
        category_url = "https://books.toscrape.com/catalogue/category/books_1/index.html"

    current_page = category_url
    for _ in range(max_pages):
        response = requests.get(current_page)
        soup = BeautifulSoup(response.text, 'html.parser')

        for article in soup.findAll('article', class_='product_pod'):
            title = article.find('h3').find('a').get('title')
            category = article.find('p', class_='star-rating').get('class')[1]
            rating = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}[category]
            price = article.find('p', class_='price_color').text
            stock = article.find('p', class_='instock').text.strip()
            image_url = article.find('div', class_='image_container').find('img')['src']
            books.append({
                'title': title,
                'category': category,
                'rating': rating,
                'price': price,
                'stock': stock,
                'image_url': 'https://books.toscrape.com/' + image_url.replace('../../', '')
            })

        next_button = soup.find('li', class_='next')
        if next_button:
            next_page = next_button.find('a').get('href')
            current_page = '/'.join(category_url.split('/')[:-1]) + '/' + next_page
        else:
            break

    return books


@app.route('/', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    categories = get_categories()
    category_query = request.args.get('category', '')

    if category_query and category_query in categories:
        category_url = categories[category_query]
        books = scrape_books(category_url)
    else:
        books = scrape_books()  # Scrape default books page

    title_query = request.args.get('title', '').lower()
    filtered_books = [book for book in books if title_query in book['title'].lower()]

    # Sort books by rating
    filtered_books.sort(key=lambda x: x['rating'], reverse=True)

    return render_template('index.html', books=filtered_books, categories=categories.keys())


if __name__ == '__main__':
    app.run(debug=True)
