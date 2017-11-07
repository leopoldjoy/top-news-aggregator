# top-news-aggregator
Twitter and Reddit top news aggregator from the past 24 hours

## About

This is a news aggregator that uses the Twitter and Reddit APIs to collect the most popular news content from the past 24 hours.

## Features

* Uses Twitter's and Reddit's public APIs
* Works around 100 post/status API limits
* Aggregates content based on numerous customizable keywords
* Writes resulting aggregated content to a CSV file

## Installation

Ensure that you have Python v2.7.x installed.

### 1) Install Dependencies

If you haven't already, install [`pipenv`](https://docs.pipenv.org/) by running:

    pip install pipenv

Then, in the project directory, run:

    pipenv install

Lastly, install [`python-twitter`](https://github.com/bear/python-twitter) by running:

    pip install python-twitter

### 2) Update Twitter API Credentials

If you haven't already, follow [these](https://python-twitter.readthedocs.io/en/latest/getting_started.html#create-your-app) instructions to create a Twitter app. After that, go to the [`top_news.py` file](https://github.com/leopoldjoy/top-news-aggregator/edit/master/top_news.py#L9) and update the API credentials:

    api = twitter.Api(consumer_key=[consumer key],
                      consumer_secret=[consumer secret],
                      access_token_key=[access token],
                      access_token_secret=[access token secret])

### 3) Run The Program

Inside of the project directory, simply run:

    pipenv run python top_news.py

---
Thanks for checking this out.

Created by:
– Leopold Joy, [@leopoldjoy](https://twitter.com/leopoldjoy)
