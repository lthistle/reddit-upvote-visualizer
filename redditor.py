import requests
import datetime, time
import matplotlib.pyplot as plt
#
API_URL = "https://api.pushshift.io/reddit/search/submission"
#
current_time = int(time.time())
time_diff = 7 * 24 * 60 * 60 #days * hours * minutes * seconds
min_time = current_time - time_diff #oldest time we want to scrape after
#
#arguments for the request to the API
arguments = {'subreddit' : 'pcmasterrace',
             'sort' : 'asc',
             'sort_type' : 'created_utc',
             'after' : min_time,
             'size' : 1000}
#
#loop to keep calling the API (at a max of 1000 requests per call) until time condition is met
has_results = True
poll_time = min_time
upvote_data = []
while has_results:
    arguments['after'] = poll_time
    response = requests.get(API_URL, params = arguments)
    posts = response.json()['data']
    for post in posts:
        upvote_data.append((post['num_comments'], post['created_utc']))
    poll_time = posts[-1]['created_utc']
    if poll_time > current_time or len(posts) < 1000:
        has_results = False

xlist = []
ylist = []
for x,y in upvote_data:
    xlist.append(x)
    ylist.append(y)
plt.scatter(ylist, xlist)
plt.show()
