* data models
    * news_publisher
        ```
        {
            "publisher_name": "",
            "logo": {
                "url": "",
                "alt": ""
            },
            "website": "",
            "categories": [
                {
                    "name": "",
                    "description": ""
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
            "author_name": "",
            "author_photo": {
                "url": "",
                "alt": ""
            },
            "articles": [
                {
                    "title": "",
                    "url": "",
                    "date_published": ""
                }
            ]
        }
        ```