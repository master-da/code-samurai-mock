DROP TABLE IF EXISTS users;
DROP TAbLE IF EXISTS stations;

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
)