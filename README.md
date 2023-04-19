# whatsgoingon
LLM powered news briefings

#

## Project Structure
* backend
    * database
        * serverless deployment (Xata)
        * data models

    * scraper  
        * ABC (arc-pub API)
        * UltimaHora (arc-pub API)
        * LaNacion
        * 5Dias
    
    * LLM
        * encoding script
            * encodes every document (a news article)
        * vector database
        * summary script
            * given a date and a prompt, return a summary of the most relevant news that day
            * store summary in cloud (s3 type storage)

* frontend
    * static website

* devops
    * docker
    * github actions