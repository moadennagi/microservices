import bcrypt

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_migrate import Migrate

from .utils import create_jwt, validate_jwt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.sqlite'
app.config['DEBUG'] = True
app.config['ENV'] = "development"
app.config['SECRET'] = 'YzNES6zilzLRv0BO'
app.config['JWT_EXPIRATION'] = 60
app.config['JWT_SECRET'] = 'random'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# routes
@app.post('/login')
def login() -> tuple:
	auth = request.authorization
	if not auth:
		return 'missing credentials', 401

	# find the user
	username = auth.username
	q = text('select * from users where username = :username')
	with db.engine.connect() as connection:
		res = connection.execute(q, username=username)
		if not res:
			return 'not found', 404
		# Assuming the query returns 1 row
		user = res.first()

	if not bcrypt.checkpw(auth.password.encode(), user.password):
		return 'Invalid username or password', 401

	# create a token
	token = create_jwt(user)
	return token, 200

@app.post('/validate')
def validate():
	"Validate request"

	auth_header = request.headers.get('Authorization')
	if auth_header:
		parts = auth_header.split(' ')
		if len(parts) == 2 and parts[0] == 'Bearer':
			# validate the token
			token = parts[1]
			if validate_jwt(token):
				return token, 200

	return 'unauthorized', 401
