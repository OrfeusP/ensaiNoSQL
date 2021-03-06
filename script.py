import urllib
import json
from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

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
    if collection == "airQuality":
        db.airQuality.insert(data)
    elif collection == "health":
        db.health.insert(data)
    elif collection == "bikeCountsManhattan":
        db.bikeCounts.insert(data)


def loadData(client,airQualityData, healthData, bikeCountsManhattanData):
    loadData2Database(client, airQualityData, "airQuality")
    loadData2Database(client, healthData, "health")
    loadData2Database(client, bikeCountsManhattanData, "bikeCountsManhattan")


def downloadData():
    airQualityData = getData(
        "https://data.cityofnewyork.us/resource/ah89-62h9.json")
    healthData = getData(
        "https://data.cityofnewyork.us/resource/w7a6-9xrz.json")
    bikeCountsManhattanData = getData(
        "https://data.cityofnewyork.us/resource/kcgm-jvs7.json")
    return airQualityData, healthData, bikeCountsManhattanData


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
        #print houses[item['_id']]
    return houses


def plotting(roads_to_look,healthy_borough,
             title_roads, xlabel_roads, ylabel_roads,
             title_health, xlabel_health, legend1, legend2):

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
            label='Health Facilities')
    plt.xlabel(xlabel_health)
    plt.title(title_health)
    plt.xticks(range(len(healthy_borough.keys())),
               healthy_borough.keys(), rotation=25)
    plt.legend()
    plt.tight_layout()
    plt.show()
    print "The best borough to leave for your requirements is Manhattan or Brooklyn because:\
    \n\t -> The air pollution is {2}/{3} which is near the average of the five boroughs, and there are {0}/{1} health facilities\
    \n\nPlease see in the next graph some streets in Manhattan that are full of bicyclists."\
    .format(healthy_borough['Manhattan'].values()[0], healthy_borough['Brooklyn'].values()[0],
            healthy_borough['Manhattan'].values()[1], healthy_borough['Brooklyn'].values()[1])

    ######## ROAD WITH BICYCLES ############
    fig, ax = plt.subplots(1)
    plt.bar(range(len(roads_to_look.values())),
            roads_to_look.values(), align='center')
    plt.xticks(range(len(roads_to_look.keys())),
               roads_to_look.keys(), rotation=25)
    plt.title(title_roads, fontsize=16)
    plt.xlabel(xlabel_roads)
    plt.ylabel(ylabel_roads)
    plt.show()

def myPlot(roads_to_look, healthy_borough):
    title_roads = 'Bicyclists in the streets of Manhattan'
    xlabel_roads = 'Street'
    ylabel_roads = 'Bicyclists'


    title_health = 'Best Health Facilities - Air Pollution Combo'
    xlabel_health = 'Borough'
    legend1 = 'Average Pollution'
    legend2 = 'Health Facilities'

    plotting(roads_to_look, healthy_borough,
             title_roads, xlabel_roads, ylabel_roads,
             title_health, xlabel_health, legend1, legend2)

def main():
    
    client = MongoClient('localhost', 27017)
    cleanDatabase(client['local'])
    air_quality, heath, bike_count_manhattan = downloadData()
    loadData(client, air_quality, heath, bike_count_manhattan)
    transformAirQuality(client)
    transformHealth(client)
    transformBikeCounts(client)

    healthy_borough = air_health_combination(client)

    roads_to_look = roads_with_bikes(client)
    myPlot(roads_to_look, healthy_borough)
    


if __name__ == "__main__":
    main()
