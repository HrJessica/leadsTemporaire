from flask import jsonify
from methodes.connexion import connexion



def getModel():
    conn = connexion()
    cur = conn.cursor()
    cur.execute('SELECT * FROM LeaModels')
    liste = cur.fetchall()
    new_liste = []
    conn.close()
    for item in liste:
        new_liste.append(
            {'id': item[0], 'vue': item[1], 'angle': item[2], 'model_name': item[3]})

    return jsonify(new_liste)