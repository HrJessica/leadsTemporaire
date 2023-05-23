import pymysql
import MySQLdb

def connexion():
    db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="HR0910hssmj*/",
    db='leadsDB'
)

    
    return db
   

def connexionLeaBD():
    host = 'localhost'
    user = 'root'
    password = 'HR0910hssmj*/'
    db = 'leaergosante'
    conn = pymysql.connect(host=host,user=user,password=password,database=db)
    return conn

def createDatabase():
    db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="HR0910hssmj*/",
)
    cur = db.cursor()
    # Créer la base de données si elle n'existe pas déjà
    cur.execute('CREATE DATABASE IF NOT EXISTS  leadsDB')
    cur.execute("USE leadsDB")

    # Sélectionner la base de données
   
   # Créer la table Users
    cur.execute('CREATE TABLE IF NOT EXISTS Users (id_user INT AUTO_INCREMENT, email VARCHAR(35) NOT NULL, username VARCHAR(25) NOT NULL, password VARCHAR(200) NOT NULL, sector VARCHAR(35), role VARCHAR(7) NOT NULL, PRIMARY KEY (id_user))')

    # Créer la table Models
    cur.execute('CREATE TABLE IF NOT EXISTS Models (id_model INT  AUTO_INCREMENT, model_name VARCHAR(25) NOT NULL,model VARCHAR(200), score_train FLOAT, architecture VARCHAR(25), scale VARCHAR(300),user_id INT, PRIMARY KEY(id_model), FOREIGN KEY (user_id) REFERENCES Users(id_user))')

    # Créer la table LeaModels
    cur.execute('CREATE TABLE IF NOT EXISTS LeaModels (model_id INT  AUTO_INCREMENT, vue VARCHAR(1), angle VARCHAR(5), model_name VARCHAR(12),user_id INT, PRIMARY KEY(model_id), FOREIGN KEY (user_id) REFERENCES Users(id_user))')

    # Créer la table Videos
    cur.execute('CREATE TABLE IF NOT EXISTS Videos (id_video INT AUTO_INCREMENT, nom_vid VARCHAR(35), video LONGBLOB,user_id INT, PRIMARY KEY(id_video), FOREIGN KEY (user_id) REFERENCES Users(id_user))')

    # Fermer la connexion à la base de données
    db.close()
    

  
   

    





