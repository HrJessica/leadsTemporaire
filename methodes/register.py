import hashlib
from flask import jsonify, request
from methodes.connexion import connexion


def register():
    data = request.data
    data = data.decode(encoding='utf-8')
    data = eval(data)
    conn = connexion()
    cur = conn.cursor()
    # verifier si l'adresse mail existe
    email = data['email']
   
    username = data['username']
    psw = data['password']
    role = data['role']
    cur.execute('SELECT * FROM Users WHERE email=%s',(email,))
    isnone = cur.fetchone()

    if isnone is not None:
        return jsonify('User already exist!'), 302
    else:
        # envoie de code de confirmation
        psw = hashlib.md5(psw.encode()).hexdigest()
        cur = conn.cursor()
        cur.execute("INSERT INTO Users(email,username,password,role) VALUES(%s,%s,%s,%s)",
                    (email, data['username'], psw, role))
        conn.commit()
        conn.close()
        return jsonify('You have successfully registered'), 200