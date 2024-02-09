DROP TABLE IF EXISTS users;

create table users (
  user_id INTEGER primary key,
  user_name varchar(255) not null,
  balance INTEGER not null
);