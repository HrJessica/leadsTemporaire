from flask import jsonify, request
from methodes.connexion import connexionLeaBD

def countNotVerif():
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(id) FROM analyse WHERE isVerif=0 AND titre NOT LIKE %s",'%test%')
    total_vid = (list(cur.fetchone()))[0]
    return jsonify(total_vid)

def getVerifVideos():
   
    last_id = (request.data).decode("utf-8")
    active = True
    conn = connexionLeaBD()
    cur = conn.cursor()
   
    cur.execute(
        "SELECT id,secteur_id,titre,video FROM analyse WHERE isVerif = 0 AND titre NOT LIKE %s AND id>%s LIMIT 20",('%test%',last_id))
    videos = cur.fetchall()
    new_liste = []

    for item in videos:
        cur.execute("SELECT name FROM secteur WHERE id=%s", item[1])
        secteur = cur.fetchone()[0]
        new_liste.append(
            {'id': item[0], 'secteur': secteur, 'nom': item[2], 'src': item[3], 'isActive': active})
        active = False
    conn.close()
    
    return jsonify(new_liste)

def VideoTest(id):
    data = (request.data).decode("utf-8")
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute("UPDATE analyse SET  titre= %s,isVerif=%s,isValide=%s WHERE id=%s",
                (data, 1,1, id))
    conn.commit()
    conn.close()
    return jsonify('Update successfull')

def ValidVideo(id):
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute("UPDATE analyse SET  isVerif=%s,isValide=%s WHERE id=%s",
                (1,1, id))
    conn.commit()
    conn.close()
    return jsonify('Update successfull')

def signalVideo(id):
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute("UPDATE analyse SET isVerif=%s,isValide=%s WHERE id=%s",(1,0,id))
    conn.commit()
    conn.close()
    return jsonify('Video set such not valid')

def skip():
    page = int((request.data).decode("utf-8"))
    offset = (page-1)*20
    active = True
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute(
        "SELECT id,secteur_id,titre,video FROM analyse WHERE isVerif = 0 LIMIT 20 OFFSET %s",offset)
    videos = cur.fetchall()
    new_liste = []

    for item in videos:
        cur.execute("SELECT name FROM secteur WHERE id=%s", item[1])
        secteur = cur.fetchone()[0]
        new_liste.append(
            {'id': item[0], 'secteur': secteur, 'nom': item[2], 'src': item[3], 'isActive': active})
        active = False
    conn.close()
    return jsonify(new_liste)

    