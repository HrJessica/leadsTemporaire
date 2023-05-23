from flask import jsonify, request
from methodes.connexion import connexionLeaBD
import json
from datetime import datetime
from methodes.ChartMethode import tri,GeneralRepartition,LegendXSector,forPareto,getSectors,RiskPerSector,SectorsLabels,getDonutsData,getCompareData,horizontalChart

def convertStrToDate(date):
 
    date_obj = datetime.strptime(date,'%Y-%m-%dT%H:%M:%S.%fZ')
    date_obj = date_obj.strftime('%Y-%m-%d')
    return date_obj

def getAllAnalysis():
    conn = connexionLeaBD()
    cur = conn.cursor()
    cur.execute(" SELECT JSON_ARRAYAGG(JSON_OBJECT('id',id,'secteur',secteur_id,'date',created_at,'neck_g',rula_neck_green,'neck_or',rula_neck_orange,'neck_red',rula_neck_red,'trunk_g',rula_trunk_green,'trunk_or',rula_trunk_orange,'trunk_red',rula_trunk_red,'sl_g',rula_slgreen,'sl_or',rula_slorange,'sl_red',rula_slred,'sr_g',rula_srgreen,'sr_or',rula_srorange,'sr_red',rula_srred,'el_g',rula_elgreen,'el_or',rula_elorange,'el_red',rula_elred,'er_g',rula_ergreen,'er_or',rula_erorange,'er_red',rula_erred)) AS users_json FROM analyse WHERE titre not like '%test%' and statut!=0")
    analyses = cur.fetchall()[0][0]
    analyses = eval(analyses)
    conn.close()
    return analyses

def ParetoChart():
    analyses = getAllAnalysis()
    t = tri(analyses)
    r = GeneralRepartition(t)
    sector = getSectors()
    pareto = LegendXSector(r,sector)
    pareto = forPareto(pareto)
    return jsonify(pareto)

def RisksChart():
    analyses = getAllAnalysis()
    t = tri(analyses)
    SectorRisk = RiskPerSector(t)
    data = SectorsLabels(SectorRisk)
    return jsonify(data)

def SpecificAnalysis(sector,part,start,end):
    fieldName = [part+'_g',part+'_or',part+'_red']
    columnName = ['rula_'+part+'_green','rula_'+part+'_orange','rula_'+part+'_red']
    conn = connexionLeaBD()
    cur = conn.cursor()
    query = " SELECT JSON_ARRAYAGG(JSON_OBJECT('id',id,'secteur',secteur_id,'date',created_at,'neck_g',rula_neck_green,'neck_or',rula_neck_orange,'neck_red',rula_neck_red,'trunk_g',rula_trunk_green,'trunk_or',rula_trunk_orange,'trunk_red',rula_trunk_red,'sl_g',rula_slgreen,'sl_or',rula_slorange,'sl_red',rula_slred,'sr_g',rula_srgreen,'sr_or',rula_srorange,'sr_red',rula_srred,'el_g',rula_elgreen,'el_or',rula_elorange,'el_red',rula_elred,'er_g',rula_ergreen,'er_or',rula_erorange,'er_red',rula_erred)) AS users_json FROM analyse WHERE statut!=0 and titre NOT LIKE %s and secteur_id=%s and created_at BETWEEN %s AND %s"
    args = ('%test%',sector,start,end)
    cur.execute(query, args)
    conn.close()
    analyses = cur.fetchall()[0][0]
    if analyses is not None:
        analyses = eval(analyses)
        
    else :
        analyses = []
    return analyses

def DonutsChart():
    datas = (request.data).decode("utf-8")
    datas = eval(datas)
    sector = datas['secteur']['id']
    partie = datas['part']['id']
    start =  convertStrToDate(datas['datedebut'])
    end = convertStrToDate(datas['datefin'])

    analyses = SpecificAnalysis(sector,partie,start,end)
    if analyses == []:
        donuts = {'labels': ['Risqués', 'Potentiellement risqués', 'Non-risqués'], 'values': []}
    else:
        t = tri( analyses)
        donuts = getDonutsData(t,sector,partie)
    return jsonify(donuts)

def CompareChart():
    datas = (request.data).decode("utf-8")
    datas = eval(datas)
    sector = datas['secteur']['id']
    partie = datas['part']['id']
    start =  convertStrToDate(datas['datedebut'])
    end = convertStrToDate(datas['datefin'])
    analyses = SpecificAnalysis(sector,partie,start,end)
    if analyses == []:
        data = {'risk': [], 'total': [], 'labels': ['Proportion des risques', 'Analyse totale'], 'months': []}
    else:
        t = tri(analyses)
        data = getCompareData(t,sector,partie,start,end)
    return jsonify(data)

def HorizontalChart():
    datas = (request.data).decode("utf-8")
    datas = eval(datas)
    sector = datas['secteur']['id']
    partie = datas['part']['id']
    start =  convertStrToDate(datas['datedebut'])
    end = convertStrToDate(datas['datefin'])
    analyses = SpecificAnalysis(sector,partie,start,end)
    if analyses == []:
        data = {'labels': ['total', 'neck', 'trunk', 'sl', 'sr', 'el', 'er'], 'values': [0, 0, 0, 0, 0, 0, 0]}
    else:
        t = tri(analyses)
        data = horizontalChart(t,sector)
        
    return jsonify(data)

