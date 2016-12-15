from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')
import numpy as np
import urllib
import json
import bson
import numpy
"""
TODO:
        -> Make queries on the transform dbs to get result
        -> Find way to combine road to borough
        -> Visualization on maps
"""


def getData(url):
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data


def cleanDatabase(db):
    db.houses.drop()
    db.airQuality.drop()
    db.health.drop()
    db.entertainment.drop()
    db.bikeCounts.drop()


def loadData2Database(client, data, collection):
    """ Function to load the Data in the MongoDB"""

    db = client['local']
    if collection == "housing":
        db.houses.insert(data)
    elif collection == "airQuality":
        db.airQuality.insert(data)
    elif collection == "health":
        db.health.insert(data)
    elif collection == "bikeCountsManhattan":
        db.bikeCounts.insert(data)


def loadData(client, housingData, airQualityData, healthData, bikeCountsManhattanData):
    loadData2Database(client, housingData, "housing")
    loadData2Database(client, airQualityData, "airQuality")
    loadData2Database(client, healthData, "health")
    loadData2Database(client, bikeCountsManhattanData, "bikeCountsManhattan")


def downloadData():
    housingData = getData(
        "https://data.cityofnewyork.us/resource/k673-vwre.json")
    airQualityData = getData(
        "https://data.cityofnewyork.us/resource/ah89-62h9.json")
    healthData = getData(
        "https://data.cityofnewyork.us/resource/w7a6-9xrz.json")
    bikeCountsManhattanData = getData(
        "https://data.cityofnewyork.us/resource/kcgm-jvs7.json")
    return housingData, airQualityData, healthData, bikeCountsManhattanData


def transformAirQuality(client):
    db = client['local']
    for item in db.airQuality.find(projection={"data_valuemessage": 1, "_id": 1}):
        item['data_valuemessage'] = float(item['data_valuemessage'])
        db.airQuality.update_one(
            {"_id": item['_id']},
            {
                '$set': {
                    'data_valuemessage': item['data_valuemessage']
                }},
            upsert=False)

    db.airQuality.aggregate(
        [{
            '$group': {
                '_id': '$geo_entity_name',
                'avgPollution': {'$avg': '$data_valuemessage'}
            }}, {'$out': 'airQuality'}
         ])


def transformHealth(client):
    db = client['local']
    db.health.aggregate(
        [
            {'$group': {
                '_id': '$borough',
                'health_facilities': {'$addToSet': '$facility_name'}
            }
            }, {'$out': 'health'}])


def transformBikeCounts(client):
    db = client['local']

    for item in db.bikeCounts.find(projection={"totalusers": 1, "_id": 1}):
        item['totalusers'] = round(float(item['totalusers']))
        db.bikeCounts.update_one(
            {"_id": item['_id']},
            {
                '$set': {
                    'totalusers': item['totalusers']
                }},
            upsert=False)
    db.bikeCounts.aggregate(
        [{'$project': {
            '_id': 1, 'location_long': 1, 'location_lat': 1, 'location': 1, 'totalusers': 1
        }},
            {'$group': {
                '_id': '$location',
                'total_users': {'$avg': '$totalusers'},
                'location_long': {'$first': '$location_long'},
                'location_lat': {'$first': '$location_lat'}
            }
        }, {'$out': 'bikeCounts'}])

# TODO
    # def transformHouses(client):


def air_health_combination(client):
    db = client['local']

    air_qualilty_list = db.airQuality.find()
    health_list = db.health.find()
    total = 0
    cnt = 0
    for item in air_qualilty_list:
        total += item['avgPollution']
        cnt += 1

    avg_pollution = round((total / float(cnt)), 3)

    cnt = 0
    total = 0
    for item in health_list:
        total += len(item['health_facilities'])
        cnt += 1

    avg_health_facilities = total / cnt
    boroughs = []
    selection = {}
    health_list = db.health.find()
    for item in health_list:
        if len(item['health_facilities']) >= avg_health_facilities:
            boroughs.append(item['_id'])
            selection[item['_id']] = {}
            selection[item['_id']]['health_facilities'] = len(
                item['health_facilities'])

    for borough in boroughs:
        filterAirQuality = db.airQuality.find({'_id': borough})
        for item in filterAirQuality:
            if item['avgPollution'] <= avg_pollution + 5:
                selection[item['_id']]['avg_pollution'] = round(
                    item['avgPollution'], 2)
    return selection


def transformHouses(client):
    db = client['local']
    db.houses.aggregate(
        [
            {'$group': {
                '_id': '$borough',
                'project_ids': {'$addToSet': '$project_id'}
            }
            }, {'$out': 'houses'}])


def roads_with_bikes(client):
    db = client['local']

    roads = {}
    res = db.bikeCounts.find(sort=[('total_users', -1)]).limit(10)

    for item in res:
        roads[item['_id']] = item['total_users']

    return roads


def residences_available(client):
    db = client['local']

    houses = {}
    result = db.houses.find()

    for item in result:
        houses[item['_id']] = len(item['project_ids'])

    return houses


def plotting(roads_to_look, residences, healthy_borough,
             title_roads, xlabel_roads, ylabel_roads,
             title_houses, xlabel_houses, ylabel_houses,
             title_health, xlabel_health, legend1, legend2):

    ######## ROAD WITH BICYCLES ############
    fig, ax = plt.subplots(1)
    plt.bar(range(len(roads_to_look.values())), roads_to_look.values(), align='center')
    plt.xticks(range(len(roads_to_look.keys())), roads_to_look.keys(), rotation=25)
    plt.title(title_roads, fontsize=16)
    plt.xlabel(xlabel_roads)
    plt.ylabel(ylabel_roads)
    plt.show()

    ####### HOUSES #########################
    fig, ax = plt.subplots(1)
    plt.bar(range(len(residences.values())), residences.values(), align='center')
    plt.xticks(range(len(residences.keys())), residences.keys(), rotation=25)
    plt.title(title_houses, fontsize=16)
    plt.xlabel(xlabel_houses)
    plt.ylabel(ylabel_houses)
    plt.show()

    ###### HEALTH ##############

    fig, ax = plt.subplots(1)

    opacity = 0.8
    bar_width = 0.25

    health = (healthy_borough.values()[0]['health_facilities'],
              healthy_borough.values()[1]['health_facilities'])
    pollution = (healthy_borough.values()[0]['avg_pollution'],
                 healthy_borough.values()[1]['avg_pollution'])
    plt.bar(range(len(pollution)), pollution, bar_width, align='center',
            alpha=opacity,
            color='black',
            label='Pollution')

    plt.bar(range(len(health)), health, bar_width, align='center',
            alpha=opacity,
            color='blue',
            label='Health Facilities')
    plt.xlabel(xlabel_health)
    plt.title(title_health)
    plt.xticks(range(len(healthy_borough.keys())), healthy_borough.keys(), rotation=25)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    client = MongoClient('localhost', 27017)
    # cleanDatabase(client['local'])

    # house, airQuality, heath, bikeCountsManhattan = downloadData()
    # loadData(client, house, airQuality, heath, bikeCountsManhattan)
    # transformAirQuality(client)
    # transformHealth(client)
    # transformBikeCounts(client)
    # transformHouses(client)

    healthy_borough = air_health_combination(client)

    roads_to_look = roads_with_bikes(client)

    residences = residences_available(client)

    title_roads = 'Bicyclists in the streets of Manhattan'
    xlabel_roads = 'Street'
    ylabel_roads = 'Bicyclists'

    title_houses = 'Number of houses in each borough '
    xlabel_houses = 'Borough'
    ylabel_houses = 'Houses'

    title_health = 'Best Health Facilities - Air Pollution Combo'
    xlabel_health = 'Borough'
    legend1 = 'Average Pollution'
    legend2 = 'Health Facilities'

    plotting(roads_to_look, residences, healthy_borough,
             title_roads, xlabel_roads, ylabel_roads,
             title_houses, xlabel_houses, ylabel_houses,
             title_health, xlabel_health, legend1, legend2)
if __name__ == "__main__":
    main()
