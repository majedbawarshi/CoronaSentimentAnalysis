import re
import twint
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
from collections import Counter
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


def make_search(username):
	c = twint.Config()
	c.Username = username
	c.Get_replies = True
	# choose search term (optional)
	c.Search = ["corona", "virus"]
	# choose beginning time (narrow results)
	c.Since = "2020-01-01"
	c.Until = "2020-04-30"
	# set limit on total tweets
	c.Limit = 100000
	# no idea, but makes the csv format properly
	c.Store_csv = True
	# c.Pandas = True
	# format of the csv
	c.Custom['user'] = ["date", "time", "username", "tweet", "link", "likes", "retweets", "replies", "mentions",
						"hashtags"]
	# change the name of the csv file
	c.Output = "new_tweets.csv"
	twint.run.Search(c)


def create_file():
	usernames = ["cnn", "foxnews", "bbcworld", "ajenglish", "who"]
	for username in usernames:
		make_search(username)


create_file()


def get_tweet_sentiment(clean_tweets):
	clean_tweets_df = pd.DataFrame(columns=['tweet', 'sentiment'])
	for clean_tweet in clean_tweets:
		sentiment = ''
		analysis = TextBlob(clean_tweet)
		# set sentiment
		if analysis.sentiment.polarity > 0:
			sentiment = 'positive'
		elif analysis.sentiment.polarity == 0:
			sentiment = 'neutral'
		else:
			sentiment = 'negative'
		clean_tweets_df = clean_tweets_df.append({'tweet': clean_tweet, 'sentiment': sentiment}, ignore_index=True)
	return clean_tweets_df


def column_sum_value(column_name):
	sum = 0
	for i in range(len(tweets)):
		sum += tweets[column_name][i]
	return sum


def engagement_in_month(month):
	count = 0
	engagement = 0
	timeArray = []
	for row in tweets['date']:
		timeArray.append(row.split('-'))
	for i in range(len(timeArray)):
		if int(timeArray[i][1]) == month:
			engagement += tweets['likes_count'][i]
			engagement += tweets['retweets_count'][i]
			engagement += tweets['replies_count'][i]
			count += 1
	engagement += count
	return engagement


def engagement_in_months():
	engagement = []
	max = 0
	for i in range(1, 5):
		engagement.append(engagement_in_month(i))
	return engagement


# split based on words only

tweets = pd.read_csv("new_tweets.csv")

clean_tweets = []
for index, tweet in tweets.iterrows():
	text = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet.tweet)
	text = re.sub(r"http\S+", "", text)
	text = text.replace('twitter', '')
	text = text.replace('com', '')
	text = text.replace('pic', '')
	words = re.split(r'\W+', text)
	# convert to lower case
	words = [word.lower() for word in words]
	# remove remaining tokens that are not alphabetic
	words = [word for word in words if word.isalpha()]
	# remove stopwords
	stop_words = set(stopwords.words('english'))
	words = [w for w in words if not w in stop_words]
	clean_tweets.append(' '.join(words))

all_tweets = get_tweet_sentiment(clean_tweets)
# picking positive tweets from tweets
ptweets = []
for index, tweet in all_tweets.iterrows():
	if tweet['sentiment'] == 'positive':
		ptweets.append(tweet['tweet'])


# percentage of positive tweets
positive_tweets_percentage = 100 * len(ptweets) / len(all_tweets)
print("1) Positive tweets percentage: {} %".format(positive_tweets_percentage))

ntweets = []
for index, tweet in all_tweets.iterrows():
	if tweet['sentiment'] == 'negative':
		ntweets.append(tweet['tweet'])

# percentage of negative tweets
negative_tweets_percentage = 100 * len(ntweets) / len(all_tweets)
print("2) Negative tweets percentage: {} %".format(negative_tweets_percentage))

print(
	"Neutral tweets percentage: {} %".format(100 * (len(all_tweets) - (len(ntweets) + len(ptweets))) / len(all_tweets)))

# WordCloud
# Create and generate a word cloud image:
wordcloud_positive = WordCloud().generate(' '.join(ptweets))
# Display the generated image:
plt.imshow(wordcloud_positive, interpolation='bilinear')
plt.axis("off")
plt.show()
wordcloud_positive.to_file("positive_review.png")

# split() returns list of all the words in the string
ptweets_split_it = (' '.join(ptweets)).split()

# Pass the split_it list to instance of Counter class.
ptweets_counter = Counter(ptweets_split_it)
ptweets_most_occur = ptweets_counter.most_common(1)
print('3) The most occurred word in positive tweets is: ', ptweets_most_occur)

# Create and generate a word cloud image:
wordcloud_negative = WordCloud().generate(' '.join(ntweets))
# Display the generated image:
plt.imshow(wordcloud_negative, interpolation='bilinear')
plt.axis("off")
plt.show()
wordcloud_negative.to_file("negative_review.png")

# split() returns list of all the words in the string
ntweets_split_it = (' '.join(ntweets)).split()

# Pass the split_it list to instance of Counter class.
ntweets_counter = Counter(ntweets_split_it)
ntweets_most_occur = ntweets_counter.most_common(1)
print('4) The most occurred word in negative tweets is: ', ntweets_most_occur)

# most and least tweeted month
engagement_list = engagement_in_months()
highest_tweeted_month = engagement_list.index(max(engagement_list)) + 1
leaset_tweeted_month = engagement_list.index(min(engagement_list)) + 1

# total engagement
jan = 1
apr = 4
engaement_in_jan = engagement_in_month(jan)
engaement_in_apr = engagement_in_month(apr)
difference = engaement_in_apr - engaement_in_jan

like_column = "likes_count"
retweet_column = "retweets_count"
replies_column = "replies_count"
total_likes = column_sum_value(like_column)
total_retweets = column_sum_value(retweet_column)
total_comments = column_sum_value(replies_column)
total_tweets = len(tweets)
total_engagement = total_likes + total_retweets + total_comments

net_tweets = total_tweets + total_comments

print("5) net count of positive tweets: ", int(positive_tweets_percentage*net_tweets/100))
print("6) net count of negative tweets: ", int(negative_tweets_percentage*net_tweets/100))
print("7) The month that the people tweeted about the virus the most is: ", highest_tweeted_month)
print("8) The month that the people tweeted about the virus the least is: ", leaset_tweeted_month)

print("9) Total amount of engagement")
print("Total likes: ", total_likes)
print("Total comments: ", total_comments)
print("Total retweets: ", total_retweets)
print("Total engagement: ", total_engagement)

print("10) Difference between people tweeted in april and january")
print("Tweets engagements in January: ", engaement_in_jan)
print("Tweets engagements in April: ", engaement_in_apr)
print("Difference: ", difference)
