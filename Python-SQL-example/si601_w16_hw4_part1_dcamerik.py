import sqlite3 as sqlite
import sys, json, csv

infile = open('movie_actors_data.txt', 'rU')
reader = csv.DictReader(infile, delimiter='\n', fieldnames=['json'])
jsons = []
for row in reader:
	jsons.append(json.loads(row.get('json')))
infile.close()

# parse json data
lot_genre = []
lot_movies = []
lot_actor = []
for data in jsons:
	for genre in data['genres']:
		lot_genre.append((data['imdb_id'], genre))
	lot_movies.append((data['imdb_id'], data['title'], data['year'], data['rating']))
	for actor in data['actors']:
		lot_actor.append((data['imdb_id'], actor))

con = sqlite.connect('si601_w16_hw4_part1_dcamerik.db')

# create tables
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS movie_genre")
cur.execute("DROP TABLE IF EXISTS movies")
cur.execute("DROP TABLE IF EXISTS movie_actor")
cur.execute("CREATE TABLE movie_genre (id varchar(255), genre varchar(255))")
# uses imdb_id and genre, one row for each genre
cur.execute("CREATE TABLE movies (id varchar(255), title varchar(255), year int, rating real)")
# uses imdb_id, title, year, and rating
cur.execute("CREATE TABLE movie_actor (id varchar(255), actor varchar(255))")
# uses imdb_id and actor, one row for each actor

#insert data into tables
cur.executemany("INSERT INTO movie_genre VALUES (?,?)", lot_genre)
con.commit()
cur.executemany("INSERT INTO movies VALUES (?,?,?,?)", lot_movies)
con.commit()
cur.executemany("INSERT INTO movie_actor VALUES (?,?)", lot_actor)
con.commit()

# count movies for each genre
cur.execute("SELECT movie_genre.genre, COUNT(*) as Count FROM movie_genre GROUP BY movie_genre.genre ORDER BY Count DESC LIMIT 10")
rows = cur.fetchall()
print 'Top 10 genres:\nGenre, Movies'
for row in rows:
	print row[0] + ',' + str(row[1])

# count movies for each year
cur.execute("SELECT movies.year, COUNT(*) as Count FROM movies GROUP BY movies.year ORDER BY movies.year")
rows = cur.fetchall()
print '\nMovies broken down by year:\nYear, Movies'
for row in rows:
	print str(row[0]) + ', ' + str(row[1])

# find all sci-fi movies ordered by decreasing rating (by decreasing year if ratings are same)
cur.execute("SELECT movies.title, movies.year, movies.rating FROM movies JOIN movie_genre ON (movies.id=movie_genre.id) WHERE movie_genre.genre='Sci-Fi' ORDER BY movies.rating DESC, movies.year DESC")
rows = cur.fetchall()
print '\nSci-Fi movies:\nTitle, Year, Rating'
for row in rows:
	print row[0] + ', ' + str(row[1]) + ', ' + str(row[2])

# find top 10 actors who played in most movies in year >= 2000
cur.execute("SELECT movie_actor.actor, COUNT(*) as Count from movie_actor JOIN movies ON (movie_actor.id=movies.id) WHERE movies.year>=2000 GROUP BY movie_actor.actor ORDER BY Count DESC, movie_actor.actor ASC LIMIT 10")
rows = cur.fetchall()
print '\nIn and after year 2000, top 10 actors who played in most movies:\nActor, Movies'
for row in rows:
	print row[0] + ', ' + str(row[1])

# find pairs of actors who co-starred in 3 or more movies
cur.execute ("SELECT ActorA, ActorB, COUNT(*) FROM (SELECT DISTINCT a.id, a.actor as ActorA, b.actor as ActorB FROM movie_actor a INNER JOIN movie_actor b on a.id=b.id WHERE a.actor<b.actor) GROUP BY ActorA, ActorB HAVING COUNT(*)>=3 ORDER BY COUNT(*) DESC, ActorA, ActorB")
rows = cur.fetchall()
print '\nPairs of actors who co-starred in 3 or more movies\nActor A, Actor B, Co-starred movies'
for row in rows:
	print row[0] + ', ' + row[1] + ', ' + str(row[2])
