import ast
import pickle
from flask import jsonify, request
import numpy as np
from methodes.connexion import connexion


def addLea():
    conn = connexion()
    cur = conn.cursor()
    if request.method == 'POST' and request.data:
        data = request.data
        data = data.decode(encoding='utf-8')
        data = ast.literal_eval(data)
        
        model = data['PklFile']
        model = bytes(model, 'utf-8')
        model_name = data['angle']+'__'+data['Vue']+'.pkl'
        # write model
        with open('./ModelStore/LeaModel/'+model_name, 'wb') as file:
            pickle.dump(model, file)
        cur.execute("INSERT INTO LeaModels(vue,angle,model_name) VALUES (%s,%s,%s)",
                    (data['Vue'], data['angle'], model_name))
        conn.commit()
        conn.close()
        return jsonify('add with success')
    else:
        conn.close()
        return jsonify('verify your entry'), 302

def LeaModelAction(id):
    conn = connexion()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute("DELETE FROM LeaModels WHERE model_id=%s", id)
        conn.commit()
        conn.close()
        return jsonify('delete successfull!'), 200
    elif request.method == 'PUT':
        data = request.data
        data = data.decode(encoding='utf-8')
        data = ast.literal_eval(data)
        model = data['PklFile']

        name = data['angle']+'__'+data['Vue']+'.pkl'
        cur.execute("UPDATE LeaModels SET vue=%s ,angle=%s , model_name=%s WHERE model_id=%s",
                    (data['Vue'], data['angle'], name, id))
        conn.commit()
        conn.close()
        return jsonify('Update successfull!'), 202
    else:
        return jsonify('Method not allowed!'), 402

def useLeaModel(id):
    data = request.data
    data = data.decode(encoding='utf-8')
    data = eval(data)
    X = np.array(data)
    X = X.reshape(-1, 1)

    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT model_name FROM LeaModels WHERE model_id=%s", id)
    model = cur.fetchone()
    conn.close()
    name = model[0]
    n = name.replace('.pkl', "")
    #scaler = joblib.load('./ModelStore/scaler/'+n+'_'+str(id)+'.sav')
    with open('./ModelStore/LeaModel/'+n+'.pkl', "rb") as f:
        md = pickle.load(f)
    #X = scaler.transform(X)

    y_predict = md.predict(X)
    return jsonify(list(y_predict))

def searchLeaModel():
    data = eval(request.data)
    name = data['value']
    conn = connexion()
    cur = conn.cursor()
    cur.execute('SELECT * FROM LeaModels WHERE model_name LIKE %s', '%'+name+'%')
    liste = cur.fetchall()
    new_liste = []
    conn.close()
    for item in liste:
        new_liste.append(
            {'id': item[0], 'vue': item[1], 'angle': item[2], 'model_name': item[3]})

    return jsonify(new_liste)