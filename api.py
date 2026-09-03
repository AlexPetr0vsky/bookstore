from flask import request, jsonify
from db_setup import Book, Author
from app import app, with_session
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError, DataError
from models import User


@app.route('/api/books', methods=['GET', 'POST'])
@with_session
def handle_books(db):
    if request.method == 'POST':
        if not request.json:
            return jsonify({'error': 'Empty request'}), 400
        if not all(key in request.json for key in ['book', 'name']):
            return jsonify({'error': 'Bad request'}), 400

        author = db.query(Author).filter_by(name=request.json['name']).first()
        if not author:
            author = Author(
                name=request.json['name'],
                photo=request.json.get('photo'),
                wiki=request.json.get('wiki')
            )
            db.add(author)
            db.flush()

        book = Book(
            book=request.json['book'],
            description=request.json.get('description', ''),
            icon_book=request.json.get('icon_book', ''),
            author_id=author.id
        )
        db.add(book)
        db.commit()
        return jsonify({
            'id': book.id,
            'book': book.book,
            'description': book.description,
            'icon_book': book.icon_book,
            'author_id': author.id
        }), 201

    books = db.query(Book).all()
    return jsonify([{
        'id': b.id,
        'book': b.book,
        'description': b.description,
        'icon_book': b.icon_book,
        'author_id': b.author_id
    } for b in books]), 200


@app.route('/api/books/<int:book_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
@with_session
def handle_book(db, book_id):
    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': book.id,
            'book': book.book,
            'description': book.description,
            'icon_book': book.icon_book,
            'author_id': book.author_id
        }), 200

    if request.method == 'PUT' or request.method == 'PATCH':
        if not request.json:
            return jsonify({'error': 'Empty request'}), 400

        data = request.json
        if 'book' in data:
            book.book = data['book']
        if 'description' in data:
            book.description = data['description']
        if 'icon_book' in data:
            book.icon_book = data['icon_book']
        if 'author_id' in data:
            author = db.query(Author).filter_by(id=data['author_id']).first()
            if not author:
                return jsonify({'error': 'Author not found'}), 404
            book.author_id = data['author_id']

        db.commit()
        return jsonify({
            'id': book.id,
            'book': book.book,
            'description': book.description,
            'icon_book': book.icon_book,
            'author_id': book.author_id
        }), 200

    if request.method == 'DELETE':
        db.delete(book)
        db.commit()
        return '', 204

    if request.method == 'HEAD':
        return '', 200

    if request.method == 'OPTIONS':
        return '', 200


@app.route('/api/authors', methods=['GET', 'POST'])
@with_session
def handle_authors(db):
    if request.method == 'POST':
        if not request.json:
            return jsonify({'error': 'Empty request'}), 400
        if 'name' not in request.json:
            return jsonify({'error': 'Bad request'}), 400

        author = Author(
            name=request.json['name'],
            photo=request.json.get('photo', ''),
            wiki=request.json.get('wiki', '')
        )
        db.add(author)
        db.commit()
        return jsonify({
            'id': author.id,
            'name': author.name,
            'photo': author.photo,
            'wiki': author.wiki
        }), 201

    authors = db.query(Author).all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'photo': a.photo,
        'wiki': a.wiki
    } for a in authors]), 200


@app.route('/api/authors/<int:author_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
@with_session
def handle_author(db, author_id):
    author = db.query(Author).filter_by(id=author_id).first()
    if not author:
        return jsonify({'error': 'Author not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': author.id,
            'name': author.name,
            'photo': author.photo,
            'wiki': author.wiki
        }), 200

    if request.method == 'PUT' or request.method == 'PATCH':
        if not request.json:
            return jsonify({'error': 'Empty request'}), 400

        data = request.json
        if 'name' in data:
            author.name = data['name']
        if 'photo' in data:
            author.photo = data['photo']
        if 'wiki' in data:
            author.wiki = data['wiki']

        db.commit()
        return jsonify({
            'id': author.id,
            'name': author.name,
            'photo': author.photo,
            'wiki': author.wiki
        }), 200

    if request.method == 'DELETE':
        books = db.query(Book).filter_by(author_id=author_id).all()
        for book in books:
            db.delete(book)
        db.delete(author)
        db.commit()
        return '', 204

    if request.method == 'HEAD':
        return '', 200

    if request.method == 'OPTIONS':
        return '', 200


@app.route('/api/register', methods=['POST'])
@with_session
def api_register(db):
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    existing = db.query(User).filter_by(name=data['username']).first()
    if existing:
        return jsonify({'error': 'User already exists'}), 400

    user = User(name=data['username'], email=data.get('email', ''))
    user.set_password(data['password'])
    db.add(user)
    db.commit()

    return jsonify({
        'id': user.id,
        'username': user.name,
        'email': user.email
    }), 201


@app.route('/api/login', methods=['POST'])
@with_session
def api_login(db):
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    user = db.query(User).filter_by(name=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    login_user(user, remember=True)

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 200


@app.route('/api/logout', methods=['POST'])
def api_logout():
    logout_user()
    return jsonify({'success': 'Logged out'}), 200


@app.errorhandler(IntegrityError)
def integrity_error(e):
    return jsonify({'error': 'Database integrity error'}), 422

@app.errorhandler(DataError)
def data_error(e):
    return jsonify({'error': 'Invalid data format'}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(415)
def unsupported_media_type(e):
    return jsonify({'error': 'Unsupported media type'}), 415
