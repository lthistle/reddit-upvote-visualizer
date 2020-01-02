import praw
import requests
import yaml
import sys
import time
import pandas as pd
CONFIG = "config.yml"
API_URL = "https://api.pushshift.io/reddit/search/submission"

class Redditor:
    def __init__(self):
        #initialize the praw.Reddit object
        with open(CONFIG, 'r') as f:
            try:
                data = yaml.safe_load(f)
                self.reddit = praw.Reddit(client_id = data['client_id'],
                                          client_secret = data['client_secret'],
                                          user_agent = data['user_agent'])
            except yaml.YAMLError as error:
                print(error)
                sys.exit()
        #initialize dataframe
        self.df = pd.DataFrame(columns = ["Author", "Title", "Time Posted", "ID", "Comments", "Score"])
    def scrape_timeframe(self, start_time, end_time, subreddit_name):
        parameters = {'subreddit' : subreddit_name,
                      'sort' : 'asc',
                      'sort_type' : 'created_utc',
                      'after' : start_time,
                      'before' : end_time,
                      'size' : 1000}
        last_poll_time = start_time
        has_more_results = True
        while has_more_results:
            parameters['after'] = last_poll_time
            response = requests.get(API_URL, params = parameters)
            posts = response.json()['data']
            temp_df = pd.DataFrame(columns = ["Author", "Title", "Time Posted", "ID", "Comments", "Score"])
            for i, post in enumerate(posts):
                data = []
                for field in ['author', 'title', 'created_utc', 'id', 'num_comments', 'score']:
                    data.append(post[field])
                temp_df.loc[i] = data
            last_poll_time = posts[-1]['created_utc']
            self.df = self.df.append(temp_df)
            if len(posts) < 1000:
                has_more_results = False
    def scrape_subreddit(self, subreddit_name, num_days):
        daylength = 60 * 60 * 24 #seconds * minutes * hours
        current_time = int(time.time())
        for x in range(num_days):
            print("Scraping day {}".format(x))
            before_time = current_time - x * daylength
            after_time = before_time - daylength
            self.scrape_timeframe(after_time, before_time, subreddit_name)
    def save_csv(self):
        self.df.to_csv("data.csv")
    def fix_data(self):
        print("Fixing data (this may take a while)")
        for index, row in self.df.iterrows():
            post = self.reddit.submission(id=row['ID'])
            row['Score'] = post.score
            row['Comments'] = post.num_comments

bot = Redditor()
bot.scrape_subreddit("pcmasterrace", 7)
bot.fix_data()
bot.save_csv()