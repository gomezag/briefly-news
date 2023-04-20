* data models
    * news_publisher
        ```
        {
            "publisher_name": str,
            "logo": {
                "url": url,
                "alt": str
            },
            "website": "",
            "categories": [
                {
                    "name": str,
                    "description": str
                }
            ]
        }
        ```

    * news_article: 
        ```
        {
            "title": str,
            "subtitle": str,
            "byline": {
                "author": str,
                "date": date
            },
            "hero_image": {
                "url": url,
                "caption": str
            },
            "content": [
                {
                    "type": "str/image",
                    "value": str/image
                }
            ],
            "related_articles": [
                {
                    "title": str,
                    "url": url
                }
            ],
            "tags": [
                str
            ]
        }
        ```

    * author
        ```
        {
            "news_publisher":
            "author_name": str,
            "author_photo": {
                "url": url,
                "alt": str
            },
            "articles": [
                {
                    "title": str,
                    "url": url,
                    "date_published": date
                }
            ]
        }
        ```