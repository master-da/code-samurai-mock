import sqlite3
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
    
    elif request.method == 'GET':
                
                db = sqlite3.connect('sqlite.db')
                cursor = db.cursor()
                cursor.execute('SELECT * FROM stops')
                stops = cursor.fetchall()
                db.close()
                
                stops = [{'train_id': stop[0], 'station_id': stop[1], 'arrival_time': stop[2], 'departure_time': stop[3], 'fare': stop[4]} for stop in stops]
                
                return {'stops': stops}, 200


if __name__ == '__main__':
    app.run(debug=True, port=8000)
