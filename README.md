# AUTORIA parsing


App for managing library/

## Technology Stack

- **Backend:** Python 3.12
- **Database:** PostgreSQL
- **Others:** Celery, Redis, Docker, Selenium


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Must have:
- a computer with some operating system 
- some free time

### System Requirements

- Python
- pip (Python package installer)
- Docker


### Installing

A step by step series of examples that tell you how to get a development env running

1. Clone the repository:
    ```
    git clone the-link-from-forked-repo
    ```
2. Open the project folder in your IDE
   
3. If you are using PyCharm - it may propose you to automatically create venv for your project and install requirements in it, but if not:
    ```
    python -m venv venv
    venv\Scripts\activate (on Windows)
    source venv/bin/activate (on macOS)
    pip install -r requirements.txt
    ```
3. Use .env.example to configure the environment.
4. Move to develop branch (i did not megrge it for my future experiments)
    ```
    git checkout develop
    ```

5. Run with Docker.
    ```
    docker compose up --build
    ```
    
## Some description
The Celery worker starts after building the Docker container.
It fetches the first 5 cars from the first 3 pages 
(this is done for testing - you can easily remove these limitations in parse.py).

Before fetching a page, the link is checked against the database 
- if it already exists, the page will not be fetched again.

Links are unique for each advertisement on this site. I belive in it.

After fetching in ./dumps will be .dump file of postrqsql db for reusing 
and .csv file for something (You can easily see the result of scraping).
    
## Scheduling

    Adjust time of running celery worker in celeryconfig.py. 
    Now it set each day at 9 am.
  

## PROBLEMS
It runs very slowly without threading, but when using threads, phone numbers are lost, 
or the Selenium WebDriver eventually breaks down 
(I tried using threads in parse_in_threads.py).

I think Selenium was not a good choice for this task.

Logs are working interactively, 
but /app/logs/scraper.log has some problems with write permissions. 
I don't know what the problem is yet.

When fetching the username from AutoRia, there are many types of users — Pro, Company, etc.
It requires some time to solve this issue.

The same with prices - not all prices in USD someone in EURO
