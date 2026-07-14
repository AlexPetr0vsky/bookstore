from flask import request, jsonify
from db_setup import Book, Author
from app import app, with_session


@app.route('/api/books', methods=['GET', 'POST'])
@with_session
def handle_books(db):
    if request.method == 'POST':
        if not request.json:
            return jsonify({'error': 'Empty request'}), 400
        if not all(key in request.json for key in ['book']):
            return jsonify({'error': 'Bad request'}), 400

        author = Author(
            name=request.json['name'],
            photo=request.json['photo'],
            wiki=request.json['wiki']
        )
        author_id = db.query(Author.id).filter(Author.name == request.json['name'])
        book = Book(
            book=request.json['book'],
            description=request.json['description'],
            icon_book=request.json['icon_book'],
            author_id=author_id
        )
        db.add_all([author, book])
        db.commit()
        return jsonify({
            'id': book.id,
            'book': book.book,
            'description': book.description,
            'icon_book': book.icon_book,
            'author_id': book.author_id
        }), 201

    books = db.query(Book).all()
    result = []
    for book in books:
        result.append({
            'id': book.id,
            'book': book.book,
            'description': book.description,
            'icon_book': book.icon_book,
            'author_id': book.author_id
        })
    return jsonify(result), 200


@app.route('/api/books/<int:book_id>', methods=['GET'])
@with_session
def get_book_by_id(db, book_id):
    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({
        'id': book.id,
        'book': book.book,
        'description': book.description,
        'icon_book': book.icon_book,
        'author_id': book.author_id
    })


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@with_session
def delete_book(db, book_id):
    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    db.delete(book)
    db.commit()
    return '', 204


@app.route('/api/authors', methods=['GET'])
@with_session
def get_authors_api(db):
    authors = db.query(Author).all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'photo': a.photo,
        'wiki': a.wiki
    } for a in authors])


@app.route('/api/authors/<int:author_id>', methods=['DELETE'])
@with_session
def delete_author_api(db, author_id):
    author = db.query(Author).filter_by(id=author_id).first()
    if not author:
        return jsonify({'error': 'Author not found'}), 404

    books = db.query(Book).filter_by(author_id=author_id).all()
    for book in books:
        db.delete(book)

    db.delete(author)
    db.commit()
    return '', 204
