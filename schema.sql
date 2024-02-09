DROP TABLE IF EXISTS users;
DROP TAbLE IF EXISTS stations;
DROP TABLE IF EXISTS trains;
DROP TABLE IF EXISTS stops;

create table users (
  user_id INTEGER primary key,
  user_name varchar(255) not null,
  balance INTEGER not null
);

create table stations (
    station_id INTEGER primary key,
    station_name VARCHAR(255) not null,
    longitude FLOAT not null,
    latitude FLOAT not null
);

create table trains (
    train_id INTEGER primary key,
    train_name VARCHAR(255) not null,
    capacity INTEGER not null
);

create table stops(
    train_id INTEGER,
    station_id INTEGER,
    arrival_time varchar(255),
    departure_time varchar(255),
    fare INTEGER not null,
    foreign key (train_id) references trains(train_id)
    foreign key (station_id) references stations(station_id)
);
