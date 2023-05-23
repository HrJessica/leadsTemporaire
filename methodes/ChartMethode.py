from datetime import datetime
from flask import jsonify, request
from methodes.connexion import connexionLeaBD


def getSectors():
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute("SELECT JSON_ARRAYAGG(JSON_OBJECT('sector_id',id,'sector_name',name)) AS sectors FROM secteur")
    secteur = cur.fetchall()[0][0]
    secteur = (eval(secteur))
    secteurs = {}
    for s in secteur:
        secteurs.update({s['sector_id']: s['sector_name']})
    return secteurs

def stat(data):
    statistiques =[]
    for d in data:
        risques = {'neck':'aucun','trunk':'aucun','sl':'aucun','sr':'aucun','el':'aucun','er':'aucun'}
        
        for partie in risques.keys():
            score = {'green': d[partie+'_g'],'orange': d[partie+'_or'],'red': d[partie+'_red']}
            if score['red'] > 25:
                risques.update( {partie : "élevé"}) 
            else:
                if score['orange'] > 25:
                    risques.update( {partie : "potentiel"})  
                else: 
                    risques.update( {partie : "aucun"})
        statistiques.append({'id': d['id'],'secteur': d['secteur'], 'date': d['date'],'risques': risques})   
    return statistiques
def sectors(analyses):
    listSector = []
    for item in analyses:
        if item['secteur'] not in listSector:
            listSector.append(item['secteur'])
    return listSector
def tri(analyses):
    analyses = stat(analyses)
    sector = sectors(analyses)
    tri = {}
    for elmt in sector:
        tri.update({elmt:[]})
    for analyse in analyses:
        analyse['date'] = datetime. strptime(analyse['date'],'%Y-%m-%d %H:%M:%S.%f').month
        key = analyse['secteur']
        tri[key].append(analyse)
    return tri

def GeneralRepartition(trie):
    repartition = {}
    for k in trie.keys():
        repartition.update({k: len(trie[k])})
    return repartition

def LegendXSector(repartition,secteur):
    data = {}
    for key,value in repartition.items():
            data.update({secteur[key]: value})
    #trier data par ordre décroissant
    data_trie = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    return data_trie

def forPareto(data_trie):
    new_data = {'secteurs':[],'valeurs':[]}
    for k,v in data_trie.items():
        new_data['secteurs'].append(k)
        new_data['valeurs'].append(v)
    return new_data   

def RiskPerSector(rep):
    SectorRisk = {}
    for cle,valeur in rep.items():
        statRisque = {'neck':0,'trunk':0,'sl':0,'sr':0,'el':0,'er':0}
        for elmt in valeur:
            for key,value in elmt['risques'].items():
                if value =="élevé":
                    statRisque[key] +=1
       
        
        SectorRisk.update({cle:statRisque})
    return SectorRisk
def SectorsLabels(risks):
    labels = []
    datas = {'neck': [],'trunk': [],'sl': [], 'sr': [], 'el': [], 'er': []}
    secteurs = getSectors()
    for key in risks.keys():
        labels.append(secteurs[key])
        for k in datas.keys():
            datas[k].append(risks[key][k])
    return {'labels': labels,'values': datas}
    
def getDonutsData(tri,sector_id,part):
    
    donutsData = {'red': 0 , 'orange': 0, 'green': 0}
    data = {'labels':[],'values':[]}
    for el in tri[sector_id]:
        state = el['risques'][part]
        if state == 'élevé':
            donutsData['red'] +=1
        elif state == 'potentiel':
            donutsData['orange'] +=1
        else:
            donutsData['green'] +=1
            
    donuts = {'Risqués': donutsData['red'],'Potentiellement risqués': donutsData['orange'],'Non-risqués': donutsData['green']}
    for key,value in donuts.items():
        data['labels'].append(key)
        data['values'].append(value)
    return data


def getCompareData(tri,sector_id,part,start,end):
    new = []
    datas_intermediaire = {}
    DATA = {'risk':[],'total':[],'labels': ['Proportion des risques','Analyse totale'],'months':[]}
    start =  datetime.strptime(start, '%Y-%m-%d').date().month
    end =  datetime.strptime(end, '%Y-%m-%d').date().month

    for el in tri[sector_id]:
        i = el['date']
        if i not in DATA['months']:
            DATA['months'].append(i)
        
        if i not in datas_intermediaire.keys():
            datas_intermediaire.update({i: {'nbRisk':0,'total':0}})
        datas_intermediaire[i]['total'] +=1
        if el['risques'][part] == 'élevé':
             datas_intermediaire[i]['nbRisk'] +=1
   
            
    #reformater le data
    for key,value in datas_intermediaire.items():
        DATA['risk'].append(value['nbRisk'])
        DATA['total'].append(value['total'])
    
    return(DATA)


def horizontalChart(tri,sector_id):
   
    data = {'total':len(tri[sector_id])}
    DATA = {'labels':[],'values':[]}
    for part in tri[sector_id][0]['risques'].keys():
        data.update({part:0})
    for el in tri[sector_id]:
        for k,v in el['risques'].items():
            if v == 'élevé':
                data[k] +=1
                
    #reformater data
    for key,value in data.items():
        DATA['labels'].append(key)
        DATA['values'].append(value)
    DATA['labels'] = DATA['labels'][::-1]
    DATA['values'] = DATA['values'][::-1]
    return DATA    
