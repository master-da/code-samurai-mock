import sqlite3
from collections import defaultdict
from functools import cmp_to_key
from flask import Flask, request
from queue import PriorityQueue
app = Flask(__name__)

@app.route('/api/users', methods=['POST'])
def create_user():

    data = request.get_json()

    db = sqlite3.connect('sqlite.db')
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (user_id, user_name, balance) VALUES (?, ?, ?)', (data['user_id'], data['user_name'], data['balance']))
    db.commit()
    db.close()

    return data, 201

@app.route('/api/stations', methods=['GET', 'POST'])
def create_station():

    if request.method == 'POST':

        data = request.get_json()

        db = sqlite3.connect('sqlite.db')
        cursor = db.cursor()
        cursor.execute('INSERT INTO stations (station_id, station_name, longitude, latitude) VALUES (?, ?, ?, ?)', (data['station_id'], data['station_name'], data['longitude'], data['latitude']))
        db.commit()
        db.close()

        return data, 201
    
    elif request.method == 'GET':
            
            db = sqlite3.connect('sqlite.db')
            cursor = db.cursor()
            cursor.execute('SELECT * FROM stations')
            stations = cursor.fetchall()
            db.close()

            stations = [{'station_id': station[0], 'station_name': station[1], 'longitude': station[2], 'latitude': station[3]} for station in stations]
    
            return {'stations': stations}, 200

@app.route('/api/trains', methods=['GET', 'POST'])
def create_train():

    if request.method == 'POST':
        data = request.get_json()
        stops = data['stops']

        db = sqlite3.connect('sqlite.db')
        cursor = db.cursor()
        cursor.execute('INSERT INTO trains (train_id, train_name, capacity) VALUES (?, ?, ?)', (data['train_id'], data['train_name'], data['capacity']))
        
        for stop in stops:
            print(data['train_id'], stop['station_id'], stop['arrival_time'], stop['departure_time'], stop['fare'])
            cursor.execute('INSERT INTO stops (train_id, station_id, arrival_time, departure_time, fare) VALUES (?, ?, ?, ?, ?)', (data['train_id'], stop['station_id'], stop['arrival_time'], stop['departure_time'], stop['fare']))

        db.commit()
        db.close()
        return {
            "train_id": data['train_id'], 
            "train_name": data['train_name'], 
            "capacity": data['capacity'], 
            "service_start": stops[0]['departure_time'], 
            "service_ends": stops[-1]['arrival_time'], 
            "num_stations": len(stops)
        }, 201



def stop_compare(stop1, stop2):
    
    arrival1 = stop1[2]
    arrival2 = stop2[2]
    
    departure1 = stop1[3]
    departure2 = stop2[3]
    
    if arrival1 is None : arrival1 = ""
    if arrival2 is None : arrival2 = ""

    if departure1 is None : departure1 = ""
    if departure2 is None : departure2 = ""
    
    if departure1 != departure2:
        return departure1 < departure2
    elif arrival1 != arrival2:
        return arrival1 < arrival2
    elif stop1[0] != stop2[0]:
        return stop1[0] < stop2[0]

@app.route('/api/stations/<station_id>/trains', methods=['GET'])
def get_station(station_id):
    db = sqlite3.connect('sqlite.db')
    cursor = db.cursor()
    
    cursor.execute("select * from stations where station_id = ?", (station_id,))
    staions = cursor.fetchall()
    if len(staions) == 0:
        return {
            'message': f"station with id: {station_id} was not found"
        }, 404
    
    cursor.execute('SELECT DISTINCT * FROM stops WHERE station_id = ?', (station_id,))
    stops = cursor.fetchall()
    db.close()
    
    stops = sorted(stops, key = cmp_to_key(stop_compare))
    stops = [{'train_id': stop[0], 'arrival_time': stop[2], 'departure_time': stop[3]} for stop in stops]
    
    return {
        'station_id': station_id,
        'trains': stops
    }, 200
    
@app.route('/api/wallets/<wallet_id>', methods=['GET', 'PUT'])
def get_balance(wallet_id):
    
    if request.method == 'PUT':
        data = request.get_json()
        
        if data["recharge"] < 100 or data["recharge"] > 10000:
            return {
                "message": f"invalid amount: {data['recharge']}"
            }, 400

        db = sqlite3.connect('sqlite.db')
        cursor = db.cursor()
        cursor.execute('select * from users where user_id = ?', (wallet_id,))
        user = cursor.fetchall()
        
        if len(user) == 0:
            return {
                "message": f"wallet with id: {wallet_id} was not found"
            }, 404
        
        user = user[0]
        cursor.execute('update users set balance = ? where user_id = ?', (user[2] + data["recharge"], wallet_id))
        db.commit()
        db.close()
        
        return {
            "wallet_id": wallet_id,
            "balance": user[2] + data["recharge"],
            "wallet_user":
            {
                "user_id": user[0],
                "user_name": user[1]
            }
        }
        
    elif request.method == 'GET':
        db = sqlite3.connect('sqlite.db')
        cursor = db.cursor()
        
        cursor.execute("select * from users where user_id = ?", (wallet_id,))
        wallet = cursor.fetchall()
        db.close()
        if len(wallet) == 0:
            return {
                'message': f"wallet with id: {wallet_id} was not found"
            }, 404
            
        return {
            "wallet_id": wallet_id,
            "balance": wallet[0][2],
            "wallet_user":
            {
                "user_id": wallet[0][0],
                "user_name": wallet[0][1]
            }
        }

def find_shortest_path(stops, start_station, end_station):
    graph = defaultdict(list)
    for stop in stops:
        train_id, station_id, arrival_time, departure_time, fare = stop

        if arrival_time is None: arrival_time = ""
        if departure_time is None: departure_time = "24:00"

        graph[station_id].append((train_id, arrival_time, departure_time))

    queue = [(start_station, [])]
    visited = set()

    while queue:
        current_station, path = queue.pop(0)
        if current_station == end_station:
            return path + [current_station]
        visited.add(current_station)

        for train_id, arrival_time, departure_time in graph[current_station]:
            for next_train_id, next_arrival_time, next_departure_time in graph[current_station]:
                if next_train_id == train_id and next_arrival_time < arrival_time:
                    next_station = next_arrival_time[0]
                    if next_station not in visited:
                        queue.append((next_station, path + [current_station]))
    return None

def shortest_arrival_sort(stop1, stop2):
    return stop1[1] < stop2[1]

def shortest(stops, src, dest, start_time):
    graph = defaultdict(list)
    graph2 = defaultdict(list)
    trains = defaultdict(list)
    for stop in stops:
        train_id, station_id, arrival_time, departure_time, fare = stop
        
        if arrival_time is None: arrival_time = ""
        if departure_time is None: departure_time = "24:00"

        graph[station_id].append((train_id, arrival_time, departure_time,fare))
        trains[train_id].append((station_id, arrival_time, departure_time))
        
    for station in graph:
        graph[station] = sorted(graph[station], key = cmp_to_key(shortest_arrival_sort))

    for train in trains:
        trains[train] = sorted(trains[train], key = cmp_to_key(shortest_arrival_sort))
        trains[train] = [station[0] for station in trains[train]]
        
    
    #1 -> 3 > 4
    # print(trains)
    for train_no in trains:
        train = trains[train_no]

        # print("train", train)
        
        for i in range(len(train) - 1):
            if train[i] not in graph2:
                graph2[train[i]] = []
            
            print("train no", train[i], "pspsps", train[i+1])
            # print(graph)
            
            """
                station train[i]
                station train[i+1]
                trainno train_no
            """
            
            # arrive, depart, far = "", ""
            # for tp in graph[train[i]]:
            #     tren, arriv, dep, f = tp
            #     if tren == train_no:
            #         arrive, depart, far = arriv, dep, f
            
            # i_depart, i_1_arrival, i_1_fare = "", "", 0
            
            for tp in graph[train[i]]:
                if tp[0] == train_no:
                    i_depart = tp[2]
            for tp in graph[train[i+1]]:
                if tp[0] == train_no:
                    i_1_arrival = tp[1]
                    i_1_fare = tp[3]
            
            graph2[train[i]].append((   train[i+1],     i_depart,     i_1_arrival,       i_1_fare))
            
            
    
    print("graph_____________________-2", graph2)

    pq = PriorityQueue()
    dist = {station: (float('inf'), '') for station in graph2}
    dist[src] = (0, start_time)

    pq.put((0, src, start_time))

    while not pq.empty():
        d, station, arrival_time = pq.get()

        if station == dest:
            return d

        for next_station, departure_time, next_arrival_time, fare in graph2[station]:
            if departure_time > arrival_time and d + fare < dist[next_station][0]:
                dist[next_station] = (d + fare, next_arrival_time)
                pq.put((d + fare, next_station, next_arrival_time))

    return dist[dest]
    
        

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    
    data = request.get_json()
    db = sqlite3.connect('sqlite.db')
    cursor = db.cursor()

    cursor.execute("select * from stops")
    stops = cursor.fetchall()
    
    db.close()
    
    # print("path from", data['station_from'], "to", data['station_to'])
    # path = find_shortest_path(stops, data['station_from'], data['station_to'])
    # print(path)
    my_fare = shortest(stops, data['station_from'], data['station_to'], data['time_after'])
    
    
    return stops, 200


if __name__ == '__main__':
    app.run(debug=True, port=8000)
