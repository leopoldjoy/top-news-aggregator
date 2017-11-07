import requests
from urlparse import urlparse
from collections import Counter

# This function accesses the reddit API
# INPUT:
#  - limit: the maximum posts to return
#  - subreddit: the subreddit to get the top posts from
#  - last_name: all returned results will be after this post's name (if specified)
# RETURNS:
#  - the JSON result of the API call
def reddit_api(limit, subreddit, last_name=''):
  url = 'https://www.reddit.com/r/' + subreddit + '/top.json?limit=' + str(limit) + '&after=' + (last_name if last_name else '')
  session = requests.Session()
  headers = {'User-agent': 'top_news bot 0.1'} # to avoid "429: Too Many Requests" from Reddit API
  result = session.get(url, headers=headers)  # use headers
  if result.status_code != requests.codes.ok:
    return {'data': {'children': []}} # no articles found, imitate Reddit API response format
  return result.json()

# This function checks if a given URL belogs to a non-image/Reddit source
# INPUT:
#  - url: the url of the post
# RETURNS:
#  - a boolean representing if the post is neither an image or Reddit post
def reddit_url_is_article(url):
  # first we check if domain is a non-image/Reddit/desirable source
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
  bad_domains = ['redd.it', 'youtu.be'] # complete domains that shouldn't be included (with extension)
  bad_domain_words = ['reddit', 'imgur', 'gfycat', 'youtube', 'vevo', 'reddituploads', 'spotify'] # words that should not exist in the domain (without extension)
  if (
         (parsed_url[-2] + '.' + parsed_url[-1] in bad_domains) or # check if in bad domains
         parsed_url[-2] in bad_domain_words or # for one-part TLDs, e.g.: youtube.com
         (len(parsed_url) > 2 and parsed_url[-3] in bad_domain_words) # for two-part TLDs, e.g.: youtube.co.uk
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

# This function sifts through the API data and returns posts that are non-image/Reddit sources
# INPUT:
#  - subreddit: the subreddit to get the top posts from
#  - passed_last_name: all returned results will be after this post's name
# RETURNS:
#  - the articles that are deemed to be non-image/Reddit sources
#  - the last name of the last post that was returned by this API call
def get_hundred_reddit(subreddit, passed_last_name):
  reddit_res = reddit_api(100, subreddit, last_name=passed_last_name)
  reddit_data = reddit_res['data']['children']
  articles = {}
  last_name_seen = ''
  i = 0
  if len(reddit_data) == 0:
    return None # if no articles are returned from the API then return None
  for post in reddit_data:
    if reddit_url_is_article(post['data']['url']): # check if the post should be added
      new_dict = {}
      new_dict[post['data']['url']] = post['data']['score']
      articles = dict(Counter(articles) + Counter(new_dict))
    last_name_seen = post['data']['name'] # update the last seen post name regardless
    if i == len(reddit_data) - 1: # last iteration
      return articles, last_name_seen
    i += 1

# This function calls get_hundred_reddit until all subreddit top posts have been examined (up to 1000)
# INPUT:
#  - subreddit: the subreddit to get the top posts from
# RETURNS:
#  - all of the top articles for this subreddit
def get_subreddit_top(subreddit):
  reddit_last_name = ''
  sub_articles = {}

  while len(sub_articles) < 1000:
    print(str(len(sub_articles)) + ' r/' + subreddit + ' articles found')
    try:
      articles, reddit_last_name = get_hundred_reddit(subreddit, reddit_last_name)
      sub_articles = dict(Counter(sub_articles) + Counter(articles))
    except TypeError: # this happens when None is returned since the tuple can't be unpacked
      break
  return sub_articles
