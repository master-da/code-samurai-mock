import sqlite3
from functools import cmp_to_key
from flask import Flask, request

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
    
    # elif request.method == 'GET':
                
    #             db = sqlite3.connect('sqlite.db')
    #             cursor = db.cursor()
    #             cursor.execute('SELECT * FROM stops')
    #             stops = cursor.fetchall()
    #             db.close()
                
    #             stops = [{'train_id': stop[0], 'station_id': stop[1], 'arrival_time': stop[2], 'departure_time': stop[3], 'fare': stop[4]} for stop in stops]
                
    #             return {'stops': stops}, 200

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
                "message": f"invalid amount: {data["recharge"]}"
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

def optimalRoute(jsonData):
    pass

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    
    # data = request.get_json()
    db = sqlite3.connect('sqlite.db')
    cursor = db.cursor()

    cursor.execute("select * from stops")
    stops = cursor.fetchall()
    
    db.close()

    stops = [{'train_id': stop[0], 'station_id': stop[1], 'arrival_time': stop[2], 'departure_time': stop[3], 'fare': stop[4]} for stop in stops]
    
    
    
    return stops, 200


if __name__ == '__main__':
    app.run(debug=True, port=8000)
