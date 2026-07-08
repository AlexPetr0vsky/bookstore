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
        return jsonify({'success': 'OK'}), 200

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
