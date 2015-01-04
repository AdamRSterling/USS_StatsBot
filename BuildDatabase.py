import praw
import unicodecsv
import BuildDatabase
import datetime
import re
from collections import OrderedDict

# TODO: Keep refactoring. Use more descriptive variable names

# Function which completely rebuilds the database
def build_database(reddit, youtube):
    sub_dates = get_sub_threads(reddit)
    res_dates = get_res_threads(reddit)

    # Incorporate AfrowJow
    manual_entries(reddit, sub_dates, res_dates)

    # Match subs and results
    # OrderedDict remembers insertion order
    # This means we can iterate from first to last in order
    unsucky_events = OrderedDict()
  
    for date in sorted(sub_dates):
        try:
            unsucky_events[date] = process_unsucky_event(youtube, sub_dates[date], res_dates[date])
        # Silently supress errors.
        except KeyError:
            pass

    # Output results!
    write_database(unsucky_events)

# Returns a map of dates to submission threads
def get_sub_threads(reddit):
    # Create the white and blacklist for submission threads
    # Whitelist includes threads which are hard to find
    whitelist = re.compile('(submi(ssions?|t))|(edition)|(October 19)'
                           , re.IGNORECASE)

    # Blacklist blocks threads which are known false positives
    blacklist = re.compile('(proposal)|(wasn\'t)|(left)' +
                           '|(showdown)|(results)'
                           , re.IGNORECASE)

    search_results = reddit.search('unsucky sunday', 'letsplay', limit=None)
    dates_to_sub_threads = {}

    for thread in search_results:
        # Look at threads which pass the white and black lists 
        if whitelist.search(thread.title)and not blacklist.search(thread.title):
            # Get the date the submission thread was posted
            sub_date = datetime.date.fromtimestamp(thread.created_utc)

            # Find the nearest Sunday which occurs after the thread was posted
            # First, this correction fixes sub threads posted on Sundays
            sub_date += datetime.timedelta(days=1)

            # Find nearest Sunday
            sub_date += datetime.timedelta(days=7-sub_date.isoweekday())
           
            # Map sunday to thread reddit thread
            dates_to_sub_threads[sub_date] = thread

    return dates_to_sub_threads

# Returns a map of dates to result threads
def get_res_threads(reddit):
    # Create the white and blacklist for result threads
    whitelist = re.compile('(unsucky).*((\(?)[0-9])|(wintertime)' +
                           '|(winners)|(results)'
                           , re.IGNORECASE)
    blacklist = re.compile('(submi(ssions?|t))|(year)|(reminder)' + 
                           '|(spreadsheet)|(list)|(showdown)'
                           , re.IGNORECASE)

    search_results = reddit.search('unsucky sunday', 'letsplay', limit = None)
    result_dates = {}
   
    # Similar process for result threads
    for thread in search_results:
        if whitelist.search(thread.title)and not blacklist.search(thread.title):
            result_date = datetime.date.fromtimestamp(thread.created_utc)
           
            # Sometimes result threads are posted on Sundays
            if result_date.isoweekday() <= 5:
                result_date -= datetime.timedelta(days=result_date.isoweekday())

            # Correct for early USS result threads
            if result_date.isoweekday() == 6:
                result_date += datetime.timedelta(days=1)

            result_dates[result_date] = thread

    return result_dates

# Some threads are not reachable by search. This drags up threads by direct links 
# and places them in the proper dictionaries
def manual_entries(reddit, sub_dates, res_dates):
    AfrowJow_sub = reddit.get_submission(submission_id='1tm5a0')
    AfrowJow_res = reddit.get_submission(submission_id='1txm3v')
    AfrowJow_sub.author = 'TheAfrowJow'
    AfrowJow_res.author = 'TheAfrowJow'
    date = datetime.date(2013, 12, 29)
    sub_dates[date] = AfrowJow_sub
    res_dates[date] = AfrowJow_res

def process_unsucky_event(youtube, sub_thread, res_thread):
    host = res_thread.author

    sub_thread_analytics = get_submissions_from_sub_thread(youtube, sub_thread)
    submissions = sub_thread_analytics[0]
    submit_ids = sub_thread_analytics[1]

    res_thread_analytics = get_mentions_from_res_thread(youtube, res_thread, submit_ids)

    status = ""
    res_length = len(res_thread_analytics)

    if res_length < 5:
        status = "INCOMPLETE"
    if res_length == 0:
        status = "NO MENTION LIST FOUND"

    # Tuple of host, sub_thread, res_thread, set of submit tuples,
    # number of submissions, and set of mentioned submits
    num_subs = len(submissions)
    return (host, sub_thread, res_thread, num_subs, submissions, res_thread_analytics, status)


# Given a list of comments, discriminate on submissions and parse out videoID
def get_submissions_from_sub_thread(youtube, sub_thread):
    # Regex which matches the many, many variations of youtube links
    regex = re.compile('(https?://)?(www.)?youtu(.be|be.com)/(?!playlist?)'  +
                       '(watch[?]v=)?([a-z0-9_-]*)(&amp)?(;list=[a-z0-9]*)?',
                        re.IGNORECASE)

    # Avoid counting auto-generated entries
    author_blacklist = re.compile('(playlisterbot)|(videolinkbot)|(uss_stats)'
                                  , re.IGNORECASE)

    id_set = set()

    sub_thread.replace_more_comments(limit=None, threshold=0)

    #Get a flat list of all of the comments on a thread
    flat_comments = praw.helpers.flatten_tree(sub_thread.comments) 

    for comment in flat_comments:
        if comment.author and author_blacklist.match(comment.author.name):
            continue

        submissions = get_videos_from_string(youtube, comment)
        for channel in submissions:
            for video in submissions[channel]:
               id_set.add(video['items'][0]['snippet']['id'])
         
    return (submissions, id_set)

# Given a string, return a dict of cID's and video titles
def get_videos_from_string(youtube, string):
    regex = re.compile('(https?://)?(www.)?youtu(.be|be.com)/(?!playlist?)' +
                       '(watch[?]v=)?([a-z0-9_-]*)(&amp)?(;list=[a-z0-9]*)?',
                        re.IGNORECASE)

    videos = {}

    links = re.finditer(regex, string)

    for link in links:
        # Use 1 quota
        video = youtube.videos().list(part='snippet',id=link.group(5)).execute()
        if video['items'] != []:
            channel_title = video['items'][0]['snippet']['channelTitle']
            if channel_title in videos:
                videos[channel_title].append(entry)
            else:
                videos[channel_title] = [] 
                videos[channel_title].append(entry)

    return videos 

def get_mentions_from_res_thread(youtube, res_thread, submit_ids):
    # If the thread is a video link
    if res_thread.media != None:
        desc = res_thread.media['oembed']['description']
        results = get_videos_from_string(youtube, desc)

        prune_results(results[0], submit_ids)

        if len(results[0]) >= 1:
            return results

    # Results either unsatisfactory from video link
    # or self-post
    results = get_videos_from_string(youtube, res_thread.selftext)
    results_video = prune_results(results[0], submit_ids)
    if len(results[0]) >= 1:
        return results   

    # Else, the results video, crack open it's description, and do the exact same thing
    if results_video:
        desc = results_video['items'][0]['snippet']['description']
        results = get_videos_from_string(youtube, desc)

        prune_results(results[0], submit_ids)

        if len(results[0]) >= 1:
            return results

    return {}
            
def prune_results(results, submit_ids):
    sunday = re.compile('sunday', re.IGNORECASE)
    
    prunable = set()
    results_video = None

    for channel in results:
        videos = results[channel]
        for video in videos:

            video_id = video['items'][0]['id']
            if video_id not in submit_ids:
            
                if sunday.search(video['items'][0]['snippet']['title']):
                    results_video = video
            
                prunable.add(channel)
                
    for channel in prunable:
        del results[channel]

    return results_video

def write_database(unsucky_events):
    unsuckywriter = unicodecsv.writer(open('USSDatabase.csv', 'wb'),
                               delimiter=',', quoting=unicodecsv.QUOTE_MINIMAL)

    counter = 0
    for event in unsucky_events:
        event_info = unsucky_events[event]
        counter += 1
        unsuckywriter.writerow(['Unsucky Sunday #' + str(counter)])
        unsuckywriter.writerow(['Date'] + [str(event)])
        unsuckywriter.writerow(['Host'] + [event_info[0]])
        unsuckywriter.writerow(['Status'] + [event_info[6]])
        unsuckywriter.writerow(['Number of Submissions'] + [str(event_info[3])])
        unsuckywriter.writerow(['Submissions'])

        for channel in event_info[4]:
            videos = []

            for video in event_info[4][channel]:
                videos.append(video)

            unsuckywriter.writerow([channel] + videos)

        unsuckywriter.writerow(['Mentions'])

        for channel in event_info[5]:
            videos = []

            for video in event_info[5][channel]:
                title = video['items'][0]['snippet']['title']
                videos.append(title)

            unsuckywriter.writerow([channel] + videos)

        unsuckywriter.writerow([])
