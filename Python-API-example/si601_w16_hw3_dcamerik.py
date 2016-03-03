import urllib2, json, time, re, csv
from bs4 import BeautifulSoup

page_index = [1, 51, 101, 151]
for index in page_index:
	imdb = urllib2.urlopen('http://www.imdb.com/search/title?at=0&genres=sci_fi&sort=user_rating&start=%s&title_type=feature' % index)
	html = imdb.read()

	html_file = open('step1_top_scifi_movies_%s_to_%s_dcamerik.html' % (index, (index+49)), 'w')
	html_file.write(html)
	html_file.close()

with open('step2_top_200_scifi_movies.tsv', 'w') as outfile_step2:
	writer = csv.writer(outfile_step2, delimiter='\t')
	writer.writerow(['Rank', 'IMDB ID', 'Title', 'Year', 'Rating'])
	rank = 1
	for index in page_index:
		infile = open('step1_top_scifi_movies_%s_to_%s_dcamerik.html' % (index, (index+49)), 'rU')
		html = infile.read()
		soup = BeautifulSoup(html, 'html.parser')

		rank_dict = dict()
		imdbid = ''
		title = ''
		year = 0
		rating = 0.0
		for m in soup.body.find_all('td', class_='title'):
			n = m.find_all('a')[0]
			find_id = re.search(r'(tt[\d]+)', n['href'])
			if find_id != None:
				imdbid = find_id.groups()[0]
				title = n.string
			find_year = m.find_all('span', class_='year_type')
			year = int(re.search(r'([\d]+)', find_year[0].string).groups()[0])
			find_rating = m.find_all('div', class_='rating')
			rating = float(re.search(r'([\d]\.[\d])', find_rating[0]['title']).groups()[0])

			writer.writerow([rank, imdbid, title.encode('utf-8'), year, rating])
			rank += 1
		infile.close()
	outfile_step2.close()

with open('step3.txt', 'w') as outfile_step3:
	infile = open('step2_top_200_scifi_movies.tsv', 'rU')
	reader = csv.DictReader(infile, delimiter='\t')
	for row in reader:
		imdbid = row.get('IMDB ID')
		moviedb = urllib2.urlopen('http://api.themoviedb.org/3/find/%s?api_key=39fd176052bb641b99a24faee17d1e50&external_source=imdb_id' % imdbid)
		json_string = moviedb.read()
		outfile_step3.write(imdbid + '\t' + json_string + '\n')
		time.sleep(7)
	infile.close()
	outfile_step3.close()

with open('step4.csv', 'w') as outfile_step4:
	infile1 = open('step3.txt', 'rU')
	reader1 = csv.DictReader(infile1, delimiter='\t', fieldnames=['id', 'json'])
	mdbratings = dict()
	for row in reader1:
		jstring = json.loads(row.get('json'))
		if jstring['movie_results']:
			mdbratings[row.get('id')] = jstring['movie_results'][0]['vote_average']
	infile1.close()

	infile2 = open('step2_top_200_scifi_movies.tsv', 'rU')
	reader2 = csv.DictReader(infile2, delimiter='\t')
	imdbinfo = dict()
	for row in reader2:
		imdbinfo[row.get('IMDB ID')] = (row.get('Title'), row.get('Year'), row.get('Rating'))
	infile2.close()

	outfile_step4 = open('step4.csv', 'w')
	writer = csv.DictWriter(outfile_step4, delimiter=',', fieldnames=['IMDB ID', 'Title', 'Year', 'IMDB Rating', 'themoviedb Rating'])
	writer.writeheader()
	sort_by_imdb_rating = sorted(imdbinfo.items(), key=lambda x: x[1][2], reverse=True)
	keys = []
	for i in sort_by_imdb_rating:
		if i[0] in mdbratings.keys():
			keys.append(i[0])
	for key in keys:
		if float(imdbinfo[key][2]) != 0.0:
			if mdbratings[key] != 0.0:
				writer.writerow({'IMDB ID': key, 'Title': imdbinfo[key][0], 'Year': imdbinfo[key][1], 'IMDB Rating': imdbinfo[key][2], 'themoviedb Rating': mdbratings[key]})
	outfile_step4.close()

# moviedb API key is 39fd176052bb641b99a24faee17d1e50
