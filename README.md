# whatsgoingon
LLM powered news briefings

## Build and test
You need python >=3.9 with venv installed.
    
    make clean
    make venv
    make test

This will create a virtual environment in the `venv` directory
and install the necessary dependencies.

Once you have the Xata workspace created with the tables in their place, you can scrape with

    make scrape LIMIT=10 BRANCH=dev
    
and you can embed the nonembedded articles with

    make embed LIMIT=10
    

## Project Structure
* backend
    * database
        * :heavy_check_mark: XataAPI interface
        * data models in yml/json
        * Automatic first-time table creation.

    * scraper  
        * :heavy_check_mark: ABC (arc-pub API) 
        * :heavy_check_mark: UltimaHora (arc-pub API)
        * LaNacion
        * 5Dias
    
    * LLM
        * Embedder interface
            * :heavy_check_mark: encodes every document (a news article)
            * vector database search
        * summary script
            * given a date and a prompt, return a summary of the most relevant news that day
            * store summary in cloud (s3 type storage)

* frontend
    * static website

* devops
    * docker
    * ✔️ github actions



## Squashing commits

Here are the steps to squash the commits in `alvaro/feature/admin` into `alvaro/dev` and push a single commit from `alvaro/dev` to `main`:

First, make sure you have checked out the alvaro/dev branch:
```
git checkout alvaro/dev
```

Then, merge the `alvaro/feature/admin` branch into `alvaro/dev` with the squash option:
```
git merge --squash alvaro/feature/admin
```

This will merge all the changes from `alvaro/feature/admin` into `alvaro/dev` as a single commit.
Next, commit the changes:
```
git commit -m "Squashed commits from alvaro/feature/admin into alvaro/dev"
```

Now, push the changes to the alvaro/dev branch:
```
git push origin alvaro/dev
```

Finally, merge the changes from alvaro/dev into main with the --no-ff option:
```
git checkout main
git merge --no-ff alvaro/dev -m "Merged alvaro/dev with squashed commits from alvaro/feature/admin"
git push origin main
```
This will create a single commit on the `main` branch with all the changes from `alvaro/dev`, including the squashed changes from `alvaro/feature/admin`.

![heya](https://user-images.githubusercontent.com/12618690/233628803-6d13b39b-839b-479b-9760-da9fe9bfa75f.jpg)
