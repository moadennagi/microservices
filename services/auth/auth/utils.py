""
import jwt
import datetime

from flask import request, current_app
from .models import User

app = current_app

def validate_jwt(token: str) -> bool:
	"Validate jwt token"
	try:
		jwt.decode(token, algorithms=['HS256'], key=app.config['JWT_SECRET'])
	except jwt.InvalidTokenError as e:
		print(e)
		return False
	return True

def create_jwt(user: User) -> str:
	"""Create a JWT token for the given username
	"""
	payload = {
		"sub": user.id,
		"name": user.username,
		"iat": datetime.datetime.utcnow(),
		"exp": datetime.datetime.now(tz=datetime.timezone.utc) + \
			   datetime.timedelta(minutes=app.config['JWT_EXPIRATION'])
	}
	token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')
	return token

def authenticate(func):
	"Decaorator to authenticate requests"

	def wrapper(*args, **kwargs):

		auth_header = request.headers.get('Authorization')
		if auth_header:
			parts = auth_header.split(' ')
			if len(parts) == 2 and parts[0] == 'Bearer':
				token = parts[1]
				if validate_jwt(token):
					return func(*args, **kwargs)
		return 'unauthorized', 401
	return wrapper
