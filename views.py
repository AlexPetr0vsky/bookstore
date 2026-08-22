from flask import request, render_template
from bs4 import BeautifulSoup
import requests
from db_setup import Book, Author
from app import app, with_session
from custom_exception import WikiParseError


@app.route('/')
@with_session
def index(db):
    query = db.query(Book, Author).join(Author, Book.author_id == Author.id)
    query_all = query.all()
    query_list = []
    for book, author in query_all:
        books_dic = book.to_dict(only=('id', 'book', 'description', 'icon_book'))
        authors_dic = author.to_dict(only=('name', 'photo'))
        query_list.append(books_dic | authors_dic)
    return render_template('index.html', books=query_list, title='Bookstore')


@app.route('/authors')
@with_session
def get_authors(db):
    authors = db.query(Author).distinct(Author.name).all()
    return render_template('authors.html', authors=authors)


@app.route('/authors/<int:author_id>/about')
@with_session
def authors_wiki(db, author_id):
    author = db.query(Author).filter_by(id=author_id).one()
    url = db.query(Author.wiki).filter_by(id=author_id).one()[0]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        doc = BeautifulSoup(response.text, 'html.parser')
        intro = doc.body.find_all('p')[2].text
        labels = doc.body.find_all('th', attrs={'class': 'infobox-label'})
        labels_list = []
        data_list = []
        for label in labels:
            labels_list.append(label.text.strip())
            data_cell = label.find_next_sibling('td')
            if data_cell:
                for style_tag in data_cell.find_all('style'):
                    style_tag.decompose()
                for span in data_cell.find_all('span', class_='mw-parser-output'):
                    span.unwrap()
                clean_text = data_cell.get_text(' ', strip=True)
                data_list.append(clean_text)
            else:
                data_list.append('')
    except AttributeError as e:
        if "'NoneType' object has no attribute 'find_all'" in str(e):
            raise WikiParseError(f"Parse error for author {author.name}") from e
        else:
            raise
    return render_template('about.html', author=author, about=intro, data=data_list, labels=labels_list)


@app.route('/search/', methods=['GET'])
@with_session
def search_book(db):
    book_name = request.args.get('book')
    if book_name:
        books = db.query(Book).filter(Book.book.ilike(f"%{book_name}%")).all()
    else:
        books = []
    return render_template('search.html', books=books)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/book/<int:book_id>/<string:filename>', methods=['GET'])
@with_session
def get_book(db, book_id, filename):
    book = db.query(Book).filter_by(id=book_id).one()
    return render_template('book.html', book=book, value=filename)
