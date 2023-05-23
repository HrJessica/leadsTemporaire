from flask import Flask
import secrets
from flask_cors import CORS
import os
from flask_mysqldb import MySQL


from methodes.getModel import getModel
from methodes.connexion import createDatabase
from methodes.register import register
from methodes.login import login
from methodes.blurring import face_blurring,getAllVideo,getUserVideo,getAVideo,searchVideo
from methodes.LeaModel import addLea,LeaModelAction,useLeaModel,searchLeaModel
from methodes.Model import build_model,use_model,trainModel,saveModel,useTempModel,deleteTempModel,listModel,AllModels,getAModel,searchModel
from methodes.user import getUsers,getAnUser,UpdateUser,updatePsw,searchUser
from methodes.count import countEntity
from methodes.LeaVideos import getVerifVideos,VideoTest,ValidVideo,signalVideo,skip,countNotVerif
from methodes.sector import getSector,changeSector
from methodes.ChartStat import ParetoChart,RisksChart,DonutsChart,CompareChart,HorizontalChart

secret_key = secrets.token_hex(16)

UPLOAD_FOLDER = '/home/jessica/appl_RN/project/static/UploadVideo'
RESULT_FBR_FOLDER = '/home/jessica/appl_RN/project/static/ResultVideo'
ALLOWED_EXTENSIONS = {'mp4', 'mpg', 'avi'}

app = Flask(__name__)
CORS(app)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'HR0910hssmj*/'
app.config['MYSQL_DB'] = 'leadsDB'
app.config['MYSQL_HOST'] = 'localhost'

app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FBR_FOLDER'] = RESULT_FBR_FOLDER

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
SESSION_COOKIE_HTTPONLY = True,
REMEMBER_COOKIE_HTTPONLY = True,
SESSION_COOKIE_SAMESITE = "Strict",

# creating the upload folder
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

mysql = MySQL(app)
@app.before_first_request
def create_db():
    createDatabase()

@app.route('/register', methods=['POST'])
def signup():
    response = register()
    return response


@app.route('/login', methods=['POST'])
def signin():
    response = login()
    return response


@app.route('/blur', methods=['POST'])
def f_blur():
    response = face_blurring(app,RESULT_FBR_FOLDER,UPLOAD_FOLDER)
    return response




@app.route('/addModel', methods=['POST', 'DELETE'])
def addModel():
    response = addLea()
    return response


@app.route('/LeaModel/<id>', methods=['PUT', 'DELETE'])
def LeaMdlAction(id):
    response = LeaModelAction(id)
    return response


@app.route('/LeadModel', methods=['GET'])
def getMdl():
    newList = getModel()
    return newList


@app.route('/useLeaModel/<id>', methods=['POST'])
def useLeaMdl(id):
    response = useLeaModel(id)
    return response


@app.route('/searchLeaModel', methods=['GET', 'POST'])
def searchLeaMdl():
    response = searchLeaModel()
    return response


@app.route('/build', methods=['GET', 'POST'])
def build():
    response = build_model()
    return response


@app.route('/use_model/<id>', methods=['GET', 'POST'])
def use(id):
    response = use_model(id)
    return response

# For trainning a model

@app.route('/train/<model_id>', methods=['POST'])
def train(model_id):
    response = trainModel(model_id)
    return response
    
# For saving a model who has trained or deleting a model
@app.route('/ModelAction/<id>', methods=['PUT', 'DELETE'])
def save(id):
    response = saveModel(id)
    return response


@app.route('/useTemporary/<id>', methods=['POST'])
def useTemp(id):
    response = useTempModel(id)
    return response


@app.route('/deleteTemp/<id>', methods=['GET'])
def deleteTemp(id):
    response = deleteTempModel(id)
    return response

#les liste de model de chaque utilisateur
@app.route('/user_models', methods=['POST'])
def listUModel():
    response = listModel()
    return response

#tous les models de tous les utilisateurs
@app.route('/allModels', methods=['GET'])
def AllModel():
    response = AllModels()
    return response


@app.route('/model/<id>', methods=['GET'])
def getAMdl(id):
    response = getAModel(id)
    return response


@app.route('/searchModel', methods=['GET', 'POST'])
def searchMdl():
    response = searchModel()
    return response

# USERS
#tous les utilisateurs
@app.route('/users', methods=['GET'])
def getU():
   res = getUsers()
   return res

#un utilisateur
@app.route('/user/<id>', methods=['GET', 'PUT', 'DELETE'])
def getAnU(id):
    res = getAnUser(id)
    return res
    

@app.route('/upUserInfo/<id>', methods=['PUT'])
def UpUser(id):
    res = UpdateUser(id)
    return res


@app.route('/upPsw/<id>', methods=['PUT'])
def upPsw(id):
    res = updatePsw(id)
    return res


@app.route('/searchUser', methods=['GET', 'POST'])
def searchU():
    res = searchUser()
    return res
    

#FACE BLURRING VIDEO
@app.route('/AllVideos', methods=['GET', 'POST'])
def getAllVid():
    res = getAllVideo()
    return res
    

@app.route('/videos', methods=['GET', 'POST'])
def getUserVid():
    res = getUserVideo()
    return res

@app.route('/videos/<id>', methods=['GET', 'DELETE'])
def getAVid(id):
    res = getAVideo(id)
    return res


@app.route('/searchVideo', methods=['POST'])
def searchVid():
    res = searchVideo()
    return res


@app.route('/count', methods=['GET'])
def count():
    res = countEntity()
    return(res)
@app.route('/countNotVerif',methods=['GET'])
def countVerif():
    res = countNotVerif()
    return res

@app.route('/VerifyVideo',methods=['POST'])
def verifyVideo():
    res = getVerifVideos()
    return res
    
@app.route('/testVideo/<id>', methods=['PUT'])
def UpVideoName(id):
    res = VideoTest(id)
    return res

@app.route('/validVideo/<id>', methods=['PUT'])
def Valide(id):
    res = ValidVideo(id)
    return res
@app.route('/signal/<id>',methods=['PUT'])
def signale(id):
    res = signalVideo(id)
    return res
    
@app.route('/sector',methods=['GET'])
def sector():
    res = getSector()
    return res

@app.route('/upSector/<id>',methods=['PUT'])
def upSector(id):
    res = changeSector(id)
    return res

@app.route('/skip',methods=['POST'])
def skipVid():
    res = skip()
    return res

#pour le statistique des risques sur les données de LEA
@app.route('/paretoChart',methods=['GET'])
def Pareto():
    return ParetoChart()

@app.route('/riskCurve',methods=['GET'])
def RiskCurve():
    return RisksChart()

@app.route('/donuts',methods=['POST'])
def Donuts():
    return DonutsChart()

@app.route('/compare',methods=['POST'])
def Compare():
    return CompareChart()


@app.route('/horizontal',methods=['POST'])
def Horizontal():
    return HorizontalChart()

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404
    

if __name__ == '__main__':
    
    app.run(debug=True)
