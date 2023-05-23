import datetime
import hashlib
import secrets
from flask import jsonify, request
import jwt
from methodes.connexion import connexion
secret_key = secrets.token_hex(16)

def login():
    conn = connexion()
    cur = conn.cursor()
    # verifier l'entrée vide
    if request.method == 'POST':
        data = request.data
        data = data.decode(encoding='utf-8')
        data = eval(data)
        email = data['username']
        psw = data['password']
        psw = hashlib.md5(psw.encode()).hexdigest()
        # Check if account exists using MySQL
        cur.execute(
            'SELECT * FROM Users WHERE email = %s AND password = %s', (email, psw))
        # Fetch one record and return result
        account = cur.fetchone()
        conn.close()
     
        # if account exist
        if account is not None:
            # return a jwt token
            try:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30, seconds=5),
                    'iat': datetime.datetime.utcnow(),
                    'sub': account
                }
                return jsonify(message='success login', token=jwt.encode(
                    payload,
                    secret_key,
                    algorithm='HS256'
                ))

            except Exception as e:
                print(e)
                return jsonify('exception')
        else:
            return jsonify('Invalid credentials!'), 302