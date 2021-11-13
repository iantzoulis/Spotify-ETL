create database if not exists my_spotify;

create table if not exists my_spotify.artists(
	artist_id varchar(255) primary key not null,
    name varchar(255),
    url varchar(255)
);

create table if not exists my_spotify.albums(
	album_id varchar(255) primary key not null,
    name varchar(255),
    release_date date,
    url varchar(255),
    artist_id varchar(255)
);

create table if not exists my_spotify.tracks(
	track_id varchar(255) primary key not null,
    name varchar(255),
    duration int,
    url varchar(255),
    album_id varchar(255),
    artist_id varchar(255)
);

create table if not exists my_spotify.tracks_played(
	unique_id varchar(255) primary key not null,
    track_id varchar(255) not null,
    time_played timestamp
);
