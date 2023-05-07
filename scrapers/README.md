# Scrapers

This module provides a unified scraping interface for the different sites.

    from scrapers import Scraper

    s = Scraper('abc', branch='dev')

    category = s.categories[16]
    headlines, r = s.get_headlines(category)
    article, r = s.get_article_body(headlines[0])

    s.save_article(article)

This command will initialize an object that will inherit the query methods 
for site `abc`. Available sites at the moment are `abc` and `lanacion`.

### Base type scraper

e.g. `ArcPublishingScraper`

These methods generate the query for the endpoint by parsing the query arguments 
appropriately. These all go in the `scrapers.base_scrapers` module.

#### query(self, endpoint, **query_args)
    Base query method for the protocol. In the case of ArcPublishing, it returns 
    a response object, but since it should not be used in any higher level 
    implementations, it should not matter much what it responds. 

### Site-specific scraper

e.g. `ABCScraper`

These methods are the ones that should implement site specific logic. They should be 
created inside its own, site-specific, submodule.

The responses of the methods should be standard across all scrapers.

#### get_article_body(self, article)
    Get a full article by parsing the html response
    :param article: an article dictionary with a valid url.
    :return:
        - article: the updated article dictionary
        - article_data: the full dictionary data found.

#### get_categories(self, *args, **kwargs)
    Get the categories as a dataframe with the query parameters to get the headlines.
    :param args:
    :param kwargs:
    :return: a list of categories ready to be added to the parameters of the scraper.

#### get_headlines(self, category, *args, **kwargs)
    Get the latest headlines
    :param category: a dictionary with an 'id' and 'uri' field
    :param kwargs: extra arguments will be updated in the query dictionary, such as limit
    :return:
        - a list with the results.
        - the full json of the response. Useful for debug.


### Common methods 

These are inherited from the `Scraper` class.

#### load_parameters(self)
    Get parameters from the database and update the instance.
    :return: the parameter dictionary

#### save_article(self, article)
    Save an article to the database.
    It will try to match any entry with a possibly different body or subtitle, to get_or_create a new article
    in the database with the input dictionary
    :param article: a valid article dictionary
    :return: response from the database server.

#### save_metadata(self)
    Save the current parameters to the database.
    :return: parameters as they are read from the database after saving

#### set_parameters(self, parameters)
    Sets internal parameters according to the input dictionary.
    It will take apart the categories input and load the json data for each of the elements in the list.
    It will read the endpoints as a list of key=jsonDict elements with a path and data elements.
    Finally, it will update _parameters to the parsed dictionary.
    :param parameters: a parameter dictionary.
    :return: None
