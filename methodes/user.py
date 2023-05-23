import hashlib
from flask import jsonify, request
from methodes.connexion import connexion


def getUsers():
    conn = connexion()
    cur = conn.cursor()

    cur.execute(
        "SELECT id_user,email,username,role FROM Users")
    users = cur.fetchall()
    conn.close()
    datas = []
    for user in users:
        user = {'ID': user[0], 'email': user[1],
                'name': user[2], 'role': user[3]}
        datas.append(user)
    return jsonify(datas)

def getAnUser(id):
    conn = connexion()
    cur = conn.cursor()
    if request.method == 'GET':
        cur.execute(
            "SELECT id_user,email,username,role FROM Users WHERE id_user=%s", (id,))
        user = cur.fetchone()
        conn.close()
        user = {'ID': user[0], 'email': user[1],
                'name': user[2], 'role': user[3]}
        return jsonify(user)
    elif request.method == 'PUT':
        data = request.data
        cur.execute(
            "UPDATE Users SET role = %s WHERE id_user=%s", (data, id))
        conn.commit()
        conn.close()
        return jsonify('update successfull')
    elif request.method == 'DELETE':
        cur.execute(
            "DELETE from Users WHERE id_user=%s", (id,))
        conn.commit()
        conn.close()
        return jsonify('delete successfull')


def UpdateUser(id):
    data = eval(request.data)
    #print(data)
    conn = connexion()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET  username= %s,sector=%s WHERE id_user=%s",
                (data['name'], data['secteur'], id))
    conn.commit()
    conn.close()
    return jsonify('Update successfull')

def updatePsw(id):
    data = eval(request.data)
    old_psw = data['old_psw']
    old_psw = hashlib.md5(old_psw.encode()).hexdigest()
    new_psw = data['new_psw']
    new_psw = hashlib.md5(new_psw.encode()).hexdigest()
    conn = connexion()
    cur = conn.cursor()
    cur.execute("SELECT password FROM Users WHERE id_user=%s", (id,))
    psw = cur.fetchone()[0]
    if(psw == old_psw):
        cur.execute(
            "UPDATE Users SET password=%s WHERE id_user=%s", (new_psw, id))
        conn.commit()
        conn.close()
        return jsonify('pasword updated')
    else:
        return jsonify('Wrong old password'), 400

def searchUser():
    data = eval(request.data)
    email = data['searchValue']
    conn = connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT id_user,email,username,sector,role FROM Users WHERE email LIKE %s", '%'+email+'%')
    users = cur.fetchall()
    conn.close()
    datas = []
    for user in users:
        user = {'ID': user[0], 'email': user[1],
                'name': user[2], 'role': user[3]}
        datas.append(user)
    return jsonify(datas)