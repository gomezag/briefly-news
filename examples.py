from scrapers import Scraper

s = Scraper('abc', branch='dev')

# Get some category from the list
category = s.categories[16]

# Print the default endpoints
print(s.endpoints.keys())

# Get the headlines for a category. r is the response object
articles, r = s.get_headlines(category)

#Get an article. r is the response object
article = s.get_article_body(articles[0])

# Make a custom query.
query = s.query('/')

# Make a query to the known headline endpoint (with default payload)
query = s.query(s.endpoints['headlines']['path'], **s.endpoints['headlines']['data'])

