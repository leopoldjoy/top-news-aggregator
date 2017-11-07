import requests
from urlparse import urlparse
import json
from collections import Counter
import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
import twitter

api = twitter.Api(consumer_key='',
                  consumer_secret='',
                  access_token_key='',
                  access_token_secret='')

# This function accesses the reddit API
# INPUT:
#  - limit: the maximum posts to return
#  - last_id: all returned results will be after this post's id (if specified)
# RETURNS:
#  - the JSON result of the API call
def twitter_api(limit, keyword, last_id=''):
  results = api.GetSearch(raw_query='max_id=' + str(last_id) + '&count=' + str(limit) + '&q=http&result_type=popular&lang=en')
  return results

# This function checks if a given URL belogs to a non-image
# INPUT:
#  - url: the url of the post
# RETURNS:
#  - a boolean representing if the post is not an iamge
def twitter_url_is_article(url):
  # first we check if domain is a desirable source
  request_url = url
  try:
    # we use requests.get so that shortened domains are redirected...
    request_url = requests.get(url).url
  except requests.exceptions.Timeout:
    print('There was a Timeout exception while trying to get the URL.')
  except requests.exceptions.TooManyRedirects:
    print('There was a TooManyRedirects exception while trying to get URL.')
  except requests.exceptions.RequestException as e:
    print('There was a RequestException exception while trying to get the URL:')
    print(e)
  parsed_url = urlparse(request_url)[1].split('.')
  badDomains = ['twitter.com', 'youtu.be'] # complete domains that shouldn't be included (with extension)
  badDomainWords = ['imgur', 'gfycat', 'youtube', 'vevo'] # words that should not exist in the domain (without extension)
  if (
         (parsed_url[-2] + '.' + parsed_url[-1] in badDomains) or # check if in bad domains
         parsed_url[-2] in badDomainWords or # for one-part TLDs, e.g.: youtube.com
         (len(parsed_url) > 2 and parsed_url[-3] in badDomainWords) # for two-part TLDs, e.g.: youtube.co.uk
     ):
    return False

  # next we check if the url leads to an image
  try:
    response = requests.head(url)
    content_type = response.headers.get('content-type')
    if content_type != None and content_type.startswith("image/"):
      return False
  except requests.exceptions.Timeout:
    print('There was a Timeout exception while trying to get the URL\'s content-type.')
    return False
  except requests.exceptions.TooManyRedirects:
    print('There was a TooManyRedirects exception while trying to get the URL\'s content-type.')
    return False
  except requests.exceptions.RequestException as e:
    print('There was a RequestException exception while trying to get the URL\'s content-type:')
    print(e)
    return False
  return True

# This function sifts through the API data and returns posts that are non-image sources
# INPUT:
#  - passed_last_id: all returned results will be after this post's id
# RETURNS:
#  - the articles that are deemed to be non-image/Reddit sources
#  - the last id of the last post that was returned by this API call
def get_hundred_tweets(passed_last_id, keyword):
  twitter_res = twitter_api(100, keyword, last_id=passed_last_id)
  articles = {}
  last_id_seen = ''
  i = 0
  if len(twitter_res) == 0:
    return None # if no articles are returned from the API then return None
  for post_json in twitter_res:
    post = dict(json.loads(str(post_json)))
    # now we loop over all of the URLs in this particular tweet
    for x in xrange(0,len(post['urls'])):
      # check if this post URL should be included
      if twitter_url_is_article(post['urls'][x]['expanded_url']):
        new_dict = {}
        new_dict[post['urls'][x]['expanded_url']] = (post['favorite_count'] if ('favorite_count' in post) else 1)
        articles = dict(Counter(articles) + Counter(new_dict))
        # articles[post['urls'][x]['expanded_url']] = (post['favorite_count'] if ('favorite_count' in post) else 0)

    last_id_seen = post['id'] # update the last seen post id regardless
    if i == len(twitter_res) - 1: # last iteration
      if last_id_seen == passed_last_id:
        return None # the last_id isn't changing, thus no more articles for this keyword
      return articles, last_id_seen
    i += 1

# This function calls get_hundred_tweets until all top posts have been examined (up to 1000)
# RETURNS:
#  - all of the top articles
def get_keyword_top(keyword):
  last_id = ''
  twitter_articles = {}

  while len(twitter_articles) < 1000:
    print(str(len(twitter_articles)) + ' ' + keyword + ' articles found')
    try:
      articles, last_id = get_hundred_tweets(last_id, keyword)
      twitter_articles = dict(Counter(twitter_articles) + Counter(articles))
    except TypeError as e: # this happens when None is returned since the tuple can't be unpacked
      break
  return twitter_articles
