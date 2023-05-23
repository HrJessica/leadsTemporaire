from flask import jsonify
from methodes.connexion import connexion


def countEntity():
    conn =connexion()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(id_user) AS numberUser FROM Users")
    nb_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(id_model) AS numberModel FROM Models")
    nb_models = cur.fetchone()[0]
    cur.execute("SELECT COUNT(id_video) AS numberVideos FROM Videos")
    nb_videos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(model_id) AS numberLea FROM LeaModels")
    nb_lea_models = cur.fetchone()[0]
    conn.close()
    reponse = {'user': nb_users, 'model': nb_models,
               'video': nb_videos, 'leaModel': nb_lea_models}
    return jsonify(reponse)

