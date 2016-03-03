import sqlite3 as sqlite
import sys

def main():
	if len(sys.argv[1:]) != 2:
		print 'Please enter genre and k\nsi601_w16_hw4_part2_dcamerik.py genre k'
		sys.exit(1)

	genre = sys.argv[1]
	k = int(sys.argv[2])

	con = sqlite.connect('si601_w16_hw4_part1_dcamerik.db')
	cur = con.cursor()

	cur.execute("SELECT movie_actor.actor, COUNT(*) as Count FROM movie_actor JOIN movie_genre ON (movie_actor.id=movie_genre.id) WHERE movie_genre.genre=? GROUP BY movie_actor.actor ORDER BY Count DESC, movie_actor.actor ASC LIMIT ?", (genre,k))
	rows = cur.fetchall()
	print 'Top ' + str(k) + ' actors who played in most ' + genre + ' movies\nActor, ' + genre + ' Movies Played in'
	for row in rows:
		print row[0] + ', ' + str(row[1])

if __name__ == "__main__":
	main()