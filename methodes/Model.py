import os
import pickle
import shutil
from flask import jsonify, request
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from methodes.connexion import connexion


def rectify_list(liste):
    for x in range(len(liste)-1):
        #liste[x] = liste[x].strip()
        liste[x] = float(liste[x])
    # pour enlever le ; du dernier element de la liste
    liste[len(liste)-1] = float(liste[len(liste)-1][:-1])

    liste = np.array(liste)
    return liste


def MLPR(X, Y, model_name, architecture):
    scaler = StandardScaler()
    X = X.reshape(-1, 1)
    if(len(X) > 1000):
        solver = 'adam'
    else:
        solver = 'lbfgs'
    # lissage par Savitzky-Golay ou savgol
    np.set_printoptions(precision=2)
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=0)
    scaler = scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    regr = MLPRegressor(hidden_layer_sizes=architecture,
                        random_state=0, max_iter=400000, solver=solver, early_stopping=True, validation_fraction=0.3).fit(X_train, Y_train)
    score_train = regr.score(X_train, Y_train)
    X_test = scaler.transform(X_test)
    regr.predict(X_test)
    # save model

    filename = model_name+'.pkl'
    with open('./ModelStore/Models/'+filename, 'wb') as f:
        pickle.dump(regr, f)
    joblib.dump(scaler, './ModelStore/scaler/'+model_name+'.sav')
    return filename, score_train, regr

def build_model():
    if request.method == 'POST':
        data = request.data
        data = data.decode(encoding='utf-8')
        data = eval(data)
        print(data)
        modelName = data['modelName']
        file = data['file']
        layers = data['layers']
        user_id = data['user']

        X = []
        Y = []
        for i in file:
            if(type(i) is list and i != ['']):
                X.append((float(i[0])))
                Y.append((float(i[1])))
            elif(type(i) is str):
                headers = i
                headers = headers.split(',')
        X = np.array(X)
        X = X.reshape(1, -1)
        Y = np.array(Y)
        filename, score, model = MLPR(X, Y, modelName, layers)

        # save
        conn = connexion()
        cur = conn.cursor()
        cur.execute("INSERT INTO Models(model_name,model,score_train,architecture,user_id) VALUES(%s,%s,%s,%s,%s)",
                    (filename, model, score, str(layers), user_id))
        conn.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        id = cur.fetchone()
        conn.close()
        new_filename = filename.replace('.pkl', "")+'_'+str(id[0])+'.pkl'
        os.rename('./ModelStore/Models/'+filename,
                  './ModelStore/Models/'+new_filename)
        scalerOldName = 'ModelStore/scaler/' + \
            filename.replace('.pkl', "")+'.sav'
        scalerNewName = 'ModelStore/scaler/' + \
            filename.replace('.pkl', "")+'_'+str(id[0])+'.sav'
        os.rename(scalerOldName, scalerNewName)
        model = str(model)
    return ({'id': id[0], 'score': score, 'model': model, 'filename': filename})


'''forme de l identification personnalisé: filename+id_000+id_model'''

def use_model(id):
    data = request.data
    data = data.decode(encoding='utf-8')
    data = eval(data)
    X = np.array(data)
    X = X.reshape(-1, 1)

    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT model_name,scaler FROM Models WHERE id_model=%s", id)
    model = cur.fetchone()
    conn.close()
    name = model[0]
    n = name.replace('.pkl', "")
    scaler = joblib.load('./ModelStore/scaler/'+n+'_'+str(id)+'.sav')
    with open('./ModelStore/Models/'+n+'_'+str(id)+'.pkl', "rb") as f:
        md = pickle.load(f)
    X = scaler.transform(X)
    y_predict = md.predict(X)
    return jsonify({'predict_file': list(y_predict)})

def trainModel(model_id):
    data = request.data
    data = data.decode(encoding='utf-8')
    data = eval(data)
    file = data['file']

    X = []
    Y = []
    for i in file:
        if(type(i) is list and i != ['']):
            X.append((float(i[0])))
            Y.append((float(i[1])))
        elif(type(i) is str):
            headers = i
            headers = headers.split(',')
    X = np.array(X).reshape(-1, 1).tolist()
    Y = np.array(Y)

    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT model,score_train,model_name FROM Models WHERE id_model=%s",
                (model_id))
    model = cur.fetchone()

    model_byte = model[0]
    score = model[1]  # le score du model
    model_name = model[2]
    n = model_name.replace('.pkl', "")
    model = eval(model_byte)
    # load model
    with open('./ModelStore/Models/'+n+'_'+str(model_id)+'.pkl', "rb") as f:
        m = pickle.load(f)
    scaler = joblib.load('./ModelStore/scaler/'+n+'_'+str(model_id)+'.sav')
    # re-train model
    X = scaler.transform(X)
    m = m.fit(X, Y)
    new_score = m.score(X, Y)

    # reecrire le nouveau model dans un dossier temporaire
    with open('./ModelStore/temporaryFitModel/'+model_name.replace('.pkl', "")+'_'+str(model_id)+'.pkl', 'wb') as file:
        pickle.dump(m, file)

    # update column model_name in database

    cur.execute("UPDATE Models SET model_name=%s WHERE id_model =%s",
                (model_name, model_id))
    conn.commit()
    conn.close()

    return ({'id': model_id, 'score': new_score})


def saveModel(id):

    conn = connexion()
    cur = conn.cursor()
    if request.method == 'PUT':
        data = request.data
        data = data.decode(encoding='utf-8')
        data = eval(data)
        score = data['score']

        cur.execute("UPDATE Models SET score_train=%s WHERE id_model =%s",
                    (score, id))
        conn.commit()
        cur.execute("SELECT model_name FROM Models WHERE id_model=%s", id)
        name = cur.fetchone()[0]
        conn.close()
        source = './ModelStore/temporaryFitModel/' + \
            name.replace('.pkl', "")+'_'+str(id)+'.pkl'
        destination = './ModelStore/Models/' + \
            name.replace('.pkl', "")+'_'+str(id)+'.pkl'
        shutil.copyfile(source, destination)
        os.remove(source)
        return jsonify('Saved!'), 200
    elif request.method == 'DELETE':
        cur.execute("DELETE FROM Models WHERE id_model=%s", id)
        conn.commit()
        conn.close()
        return jsonify('Delete successfull'), 200


def useTempModel(id):
    data = request.data
    data = data.decode(encoding='utf-8')
    data = eval(data)
    X = np.array(data)
    X = X.reshape(-1, 1)
    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT model_name,scaler FROM Models WHERE id_model=%s", id)
    model = cur.fetchone()
    conn.close()
    name = model[0]
    n = name.replace('.pkl', "")
    scaler = joblib.load('./ModelStore/scaler/'+n+'_'+str(id)+'.sav')
    with open('./ModelStore/temporaryFitModel/'+n+'_'+str(id)+'.pkl', "rb") as f:
        md = pickle.load(f)
    X = scaler.transform(X)
    y_predict = md.predict(X)
    return jsonify({'predict_file': list(y_predict)})

def deleteTempModel(id):
    conn = connexion()
    cur = conn.cursor()

    cur.execute("SELECT model_name FROM Models WHERE id_model=%s", id)
    name = cur.fetchone()[0]
    conn.close()
    os.remove('./ModelStore/temporaryFitModel/' +
              name.replace('.pkl', "")+'_'+str(id)+'.pkl')
    return jsonify('deleted')

def listModel():
    data = request.data
    data = eval(data)
    conn = connexion()
    cur = conn.cursor()

    cur.execute(
        "SELECT id_model,model_name,score_train,model,architecture FROM Models WHERE user_id=%s", str(data))
    models = cur.fetchall()
    new_liste = []
    conn.close()
    
    for item in models:
        new_liste.append(
            {'id': item[0], 'name': item[1], 'score': item[2], 'model': item[3], 'layers': item[4], })

    return jsonify(new_liste)

def AllModels():
    conn = connexion()
    cur = conn.cursor()

    cur.execute(
        "SELECT id_model,model_name,score_train,model,architecture,user_id FROM Models")
    models = cur.fetchall()
    new_liste = []
   
    for item in models:
        cur.execute("SELECT username FROM Users WHERE id_user=%s", str(item[5]))
        user = cur.fetchone()[0]
        new_liste.append(
            {'id': item[0], 'name': item[1], 'score': item[2], 'model': item[3], 'layers': item[4], 'user': user})
    conn.close()
    return jsonify(new_liste)

def getAModel(id):
    conn = connexion()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM Models WHERE id_model=%s", id)
    model = cur.fetchone()
    conn.close()
    model = {'id': model[0], 'name': model[1], 'score': model[2],
             'layers': model[3], 'id_user': model[4], 'model': model[5]}
    return jsonify(model)

def searchModel():
    data = eval(request.data)
    name = data['searchValue']

    conn = connexion()
    cur = conn.cursor()

    cur.execute(
        "SELECT id_model,model_name,score_train,model,architecture,user_id FROM Models WHERE model_name LIKE %s", '%'+name+'%')
    models = cur.fetchall()

    new_liste = []

    for item in models:
        cur.execute("SELECT username FROM Users WHERE id_user=%s", item[5])
        user = cur.fetchone()[0]
        new_liste.append(
            {'id': item[0], 'name': item[1], 'score': item[2], 'model': item[3], 'layers': item[4], 'user': user})
    conn.close()
    return jsonify(new_liste)