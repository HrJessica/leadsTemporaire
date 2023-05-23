import os
from pathlib import Path
from flask import jsonify, request
import flask
import torch

from methodes.connexion import connexion
from scipy.signal import savgol_filter
import retina_blur as retina
import torch.backends.cudnn as cudnn

def face_blurring(app,result_fbr,u_folder):
    if request.method == 'POST':
        file = request.files

        f = file.get('file')
        fl = f.filename.split(',')
        filename = fl[0]
        id_user = fl[1]
        name = Path(filename).stem
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = connexion()
        cur = conn.cursor()

        if not os.path.exists(result_fbr):
            os.makedirs(result_fbr)
        # load face-detection model
        torch.set_grad_enabled(False)
        retina.args.cpu = 'cpu'
        net = retina.RetinaFace(phase="test")
        net = retina.load_model(
            net, retina.args.trained_model, retina.args.cpu)
        net.eval()
        cudnn.benchmark = True
        device = torch.device("cpu" if retina.args.cpu else "cuda")
        net = net.to(device)
        retina.split_video(u_folder+'/'+filename, device,
                           result_fbr+'/'+name+'_blurred.mp4', net)

        # return the video file blurred
        mp4file = result_fbr+'/'+name+'_blurred.mp4'
        os.remove(u_folder+'/'+filename)
        with open(mp4file, "rb") as handle:
            binary_data = handle.read()
        os.remove(mp4file)
        cur.execute("INSERT INTO Videos(filename,blured,user_id) VALUES (%s,%s,%s)",
                    (filename, binary_data, id_user))
        conn.commit()
        conn.close()
        return flask.Response(binary_data, mimetype='video/mp4')

def getAllVideo():
    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Videos")
    videos = cur.fetchall()

    datas = []
    for file in videos:
        cur.execute("SELECT username FROM Users WHERE user_id=%s", file[3])
        user = cur.fetchone()
        file = {'ID': file[0], 'name': file[1],
                'username': user[0]}
        datas.append(file)
    conn.close()
    return jsonify(datas)


def getUserVideo():
    id = eval(request.data)

    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Videos WHERE user_id=%s", str(id))
    videos = cur.fetchall()
    conn.close()

    datas = []
    for file in videos:
        file = {'ID': file[0], 'name': file[1],
                }
        datas.append(file)
    return jsonify(datas)


def getAVideo(id):
    conn = connexion()
    cur = conn.cursor()
    if request.method == 'GET':
        cur.execute("SELECT blured FROM Videos WHERE id_video=%s", id)
        video = cur.fetchone()[0]
        conn.close()
        return flask.Response(video, mimetype='video/mp4')
    elif request.method == 'DELETE':
        cur.execute("DELETE FROM Videos WHERE id_video=%s", id)
        conn.commit()
        conn.close()
        return jsonify('delete successfully')

def searchVideo():
    data = eval(request.data)
    video_name = data['searchValue']
    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Videos WHERE nom_vid LIKE %s",
                '%'+video_name+'%')
    videos = cur.fetchall()

    datas = []
    for file in videos:
        cur.execute("SELECT username FROM Users WHERE user_id=%s", file[3])
        user = cur.fetchone()
        file = {'ID': file[0], 'name': file[1],
                'username': user[0]}
        datas.append(file)
    conn.close()
    return jsonify(datas)