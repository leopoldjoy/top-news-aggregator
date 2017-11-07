import helpers.reddit_helpers as reddit
import helpers.twitter_helpers as twitter
from collections import Counter
import csv

# first we we get all of the Reddit articles into a dict
print('Finding Reddit articles...')
reddit_articles = (
  Counter(reddit.get_subreddit_top('all')) +
  Counter(reddit.get_subreddit_top('news')) +
  Counter(reddit.get_subreddit_top('worldnews')) +
  Counter(reddit.get_subreddit_top('politics')) +
  Counter(reddit.get_subreddit_top('technology')) +
  Counter(reddit.get_subreddit_top('science')) +
  Counter(reddit.get_subreddit_top('sports')) +
  Counter(reddit.get_subreddit_top('upliftingnews'))
)

# next we we get all of the Twitter articles into a dict
print('Finding Twitter articles...')
twitter_articles = (
  Counter(twitter.get_keyword_top('http')) +
  Counter(twitter.get_keyword_top('news')) +
  Counter(twitter.get_keyword_top('politics')) +
  Counter(twitter.get_keyword_top('tech')) +
  Counter(twitter.get_keyword_top('bbc')) +
  Counter(twitter.get_keyword_top('msnbc')) +
  Counter(twitter.get_keyword_top('al jazeera')) +
  Counter(twitter.get_keyword_top('euronews'))
)

# now create Reddit/Twitter article lists and sort them sorting by popularity
# (we only use this to find the most popular from each website)
reddit_list = sorted(list(reddit_articles.items()), reverse=True, key=(lambda item: item[1]))
twitter_list = sorted(list(twitter_articles.items()), reverse=True, key=(lambda item: item[1]))

# normalize all Reddit/Twitter article popularities by dividing each
# article popularity by the popularity of the most popular article

# first we calculate the popularity of the most popular articles
most_popular_reddit = reddit_list[0][1]
most_popular_twitter = twitter_list[0][1]

most_popular_article = 0
if most_popular_reddit > most_popular_twitter:
  most_popular_article = most_popular_reddit
else:
  most_popular_article = most_popular_twitter

# calculate the number of digits in the most popular article popularity (this
# number is used as an exponent to make all of our popularity ratios positive
# integers)
most_popular_digits_sum = 10 ** len(str(most_popular_article))

for url, pop in reddit_articles.iteritems(): # normalize popularities of all reddit articles
  # first we ensure that the article popularity is non-zero, then we divide by the
  # most popular article, before finally multiplying to create an integer value (non-decimal)
  reddit_articles[url] = int(round((float(pop if (pop > 0) else 1) / float(most_popular_reddit)) * most_popular_digits_sum))
for url, pop in twitter_articles.iteritems(): # normalize popularities of all twitter articles
  # same as above line
  twitter_articles[url] = int(round((float(pop if (pop > 0) else 1) / float(most_popular_twitter)) * most_popular_digits_sum))

# we then merge the two lists into one
final_dict = dict(Counter(reddit_articles) + Counter(twitter_articles))

# we then sort the articles list again with its newly normalized popularities
final_list = sorted(list(final_dict.items()), reverse=True, key=(lambda item: item[1]))

# finally we create an output list for generating the CSV file with the correct formatting
output_data = []
i = 1
for article in final_list[:1000]: # iterate over first 1000 articles only
  output_data.append([i, article[0]])
  i += 1

# lastly we write the results to a CSV file
with open('output.csv', 'w') as fp:
  writer = csv.writer(fp, delimiter=',')
  writer.writerow(["rank", "url"])  # header
  writer.writerows(output_data)
