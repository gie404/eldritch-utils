try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
    
import requests

url = 'https://eldritchhorror.fandom.com/wiki/Conditions'
r = requests.get(url)
#~ print(r.text)

html = r.text
parsed_html = BeautifulSoup(html, 'html.parser')

table = parsed_html.body.find('table', attrs={'class':'article-table sortable'})
rows = table.find_all('tr')[1:]
#~ print(table.prettify())
print(len(rows))
print(rows[1].prettify())
assets = []
for i, row in enumerate(rows):
	cells = row.find_all('td')
	#~ if len(cells) != 5:
		#~ print(row.prettify())
	td = cells[1]
	#~ print(cells[4].text.strip())
	asset = {}
	asset['id'] = i
	asset['name'] = cells[1].text.strip()
	asset['traits'] = [x.strip() for x in cells[2].text.split('—')]
	asset['variants'] = int(cells[4].text.strip())
	asset['set'] = int(cells[3].find('span').text.strip()) - 1
	asset['pic'] = cells[0].find('a', 'image')['href']
	assets.append(asset)
	
for a in assets:
	print(a['id'], a['name'], a['traits'], a['set'], a['variants'], a['pic'], sep=';')
	#~ print(a['id'], a['name'], a['traits'], a['value'], a['set'], a['pic'] , sep=';')
