from flask import jsonify, request
from methodes.connexion import connexionLeaBD

def getSector():
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute("SELECT * from secteur")
    secteurs = list(cur.fetchall())
    sector = []
    for item in secteurs:
        item = list(item)
        sector.append(item)
    conn.commit()
    conn.close()
    return jsonify(sector)

def changeSector(id):
    data = int(request.data)
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute("UPDATE analyse SET secteur_id=%s WHERE id=%s",(data,id))
    conn.commit()
    conn.close()
    return jsonify('updated')
