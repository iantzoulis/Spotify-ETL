----- SQL Queries for generating weekly listening summaries -----
-- Total amount of time listening for the last week
select
	floor(sum(tr.duration) / (1000 * 60 * 60)) % 24 as hours,
    floor(sum(tr.duration) / (1000 * 60)) % 60 as minutes
from my_spotify.tracks_played tp
join my_spotify.tracks tr
	on tp.track_id = tr.track_id
where tp.time_played >= DATE(NOW()) - INTERVAL 7 DAY
;

-- Most played songs (and their artist) of the last week
select
	tr.track_name,
    ar.artist_name,
    count(*) as play_count
from my_spotify.tracks_played tp
join my_spotify.tracks tr
	on tp.track_id = tr.track_id
join my_spotify.artists ar
	on tr.artist_id = ar.artist_id
where tp.time_played >= DATE(NOW()) - INTERVAL 7 DAY
group by tr.track_name, ar.artist_name
order by count(*) desc
limit 10
;

-- Most played albums (and their artist) of the last week
select
	al.album_name,
    ar.artist_name,
    count(*) as play_count
from my_spotify.tracks_played tp
join my_spotify.tracks tr
	on tp.track_id = tr.track_id
join my_spotify.albums al
	on tr.album_id = al.album_id
join my_spotify.artists ar
	on al.artist_id = ar.artist_id
where tp.time_played >= DATE(NOW()) - INTERVAL 7 DAY
group by al.album_name, ar.artist_name
order by count(*) desc
limit 10
;

-- Most played artists of the last week
select 
	ar.artist_name,
	count(*) as play_count
from my_spotify.tracks_played tp
join my_spotify.tracks tr
	on tp.track_id = tr.track_id
join my_spotify.artists ar
	on tr.artist_id = ar.artist_id
where tp.time_played >= DATE(NOW()) - INTERVAL 7 DAY
group by ar.artist_name
order by count(*) desc
limit 10
;