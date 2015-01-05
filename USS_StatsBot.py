import sys
import praw
import AccountDetails
from BuildDatabase import build_database
from AnalyzeDatabase import analyze_databases
import apiclient.discovery

def main():
    
    # Login to Reddit
    reddit = praw.Reddit(user_agent='USS_Stats 0.8.6 by u/birdcatchergames')
    reddit.login(AccountDetails.USS_STATS_UNAME, AccountDetails.USS_STATS_PWORD)

    # Login to YouTube
    youtube = apiclient.discovery.build(AccountDetails.YOUTUBE_API_SERVICE_NAME,
                                        AccountDetails.YOUTUBE_API_VERSION,
                                        developerKey=AccountDetails.YOUTUBE_KEY)

    for arg in sys.argv:
        if arg == "-build":
            build_database(reddit, youtube)

        if arg == '-analyze':
            analyze_databases()
if __name__ == '__main__':
    main()
