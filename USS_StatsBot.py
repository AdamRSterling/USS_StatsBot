import sys
import praw
import AccountDetails
from BuildDatabase import build_database
from AnalyzeDatabase import analyze_database
import apiclient.discovery

def main():
    build = False 
    analyze = True
    
    # Login to Reddit
    reddit = praw.Reddit(user_agent='USS_Stats 0.8.5 by u/birdcatchergames')
    reddit.login(AccountDetails.USS_STATS_UNAME, AccountDetails.USS_STATS_PWORD)

    # Login to YouTube
    youtube = apiclient.discovery.build(AccountDetails.YOUTUBE_API_SERVICE_NAME,
                                        AccountDetails.YOUTUBE_API_VERSION,
                                        developerKey=AccountDetails.YOUTUBE_KEY)

    # TODO: Get arguments from cli 
    if build:
        build_database(reddit, youtube)

    if analyze:
        analyze_database()
if __name__ == '__main__':
    main()
