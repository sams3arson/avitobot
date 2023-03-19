CREATE TABLE IF NOT EXISTS user (
	id integer PRIMARY KEY AUTOINCREMENT,
	telegram_id integer
);

CREATE TABLE IF NOT EXISTS city (
	id integer PRIMARY KEY AUTOINCREMENT,
	name varchar,
    human_name varchar,
	user_id integer
);

CREATE TABLE IF NOT EXISTS ping(
    id integer PRIMARY KEY AUTOINCREMENT,
    user_id integer
);

CREATE TABLE IF NOT EXISTS request (
	id integer PRIMARY KEY AUTOINCREMENT,
	query varchar,
    is_tracked integer,
	url varchar,
	user_id integer,
	min_price integer,
	max_price integer,
    page_limit integer,
    sorting integer
);

CREATE TABLE IF NOT EXISTS product (
	id integer PRIMARY KEY AUTOINCREMENT,
	name varchar,
	description varchar,
	price integer,
	avito_id varchar,
	url varchar,
	request_id integer
);

CREATE TABLE IF NOT EXISTS interval (
	id integer PRIMARY KEY AUTOINCREMENT,
	interval_len integer,
	user_id integer
);

CREATE TABLE IF NOT EXISTS request_result (
	id integer PRIMARY KEY AUTOINCREMENT,
	request_id integer,
	avg_price integer,
	min_price integer,
	max_price integer
);

