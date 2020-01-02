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
        self.df = pd.DataFrame(columns = ["Author", "Title", "Time Posted", "ID", "Number of Comments", "Score"])

    def praw_update(self, data):
        fullnames_to_check = ['t3_' + x[3] for x in data] #'t3_' + x[3] gives us a fullname id (for the post) in the format t3_xxxxxx
        updated_posts = [x for x in self.reddit.info(fullnames=fullnames_to_check)]
        assert len(fullnames_to_check) == len(updated_posts) #we should've received as many posts as we sent. TODO: Add logic to fix data if we don't
        for i, post in enumerate(updated_posts):
            data[i][4] = post.num_comments
            data[i][5] = post.score

    def scrape_timeframe(self, start_time, end_time, subreddit_name):
        data = [] #temporary data buffer that will be appended to dataframe
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
            for i, post in enumerate(posts):
                post_data = []
                for field in ['author', 'title', 'created_utc', 'id', 'num_comments', 'score']:
                    post_data.append(post[field])
                data.append(post_data)
            last_poll_time = posts[-1]['created_utc']
            if len(posts) < 1000:
                has_more_results = False
        self.praw_update(data)
        self.df = self.df.append(data, ignore_index=True)

    def scrape_subreddit(self, subreddit_name, num_days):
        daylength = 60 * 60 * 24 #seconds * minutes * hours
        current_time = int(time.time())
        for x in range(num_days):
            print("Scraping day {}".format(x))
            before_time = current_time - x * daylength
            after_time = before_time - daylength
            self.scrape_timeframe(after_time, before_time, subreddit_name)

    def save_csv(self, filename):
        self.df.to_csv(filename)


if __name__ == "__main__":
    bot = Redditor()

    num_days = int(input("How many days to scrape? "))
    sub_name = input("Scrape what subreddit? /r/")
    save_name = input("Save to where? ")

    bot.scrape_subreddit(sub_name, num_days)
    bot.save_csv(save_name)