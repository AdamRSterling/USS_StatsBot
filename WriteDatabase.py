import unicodecsv
import datetime
import shutil
import os
import FileDetails

# Unsucky Event database is pretty much done as is
# Channel database can be constructed from the unsucky_events
# Construct a channels dict, then write that database
def write_databases(unsucky_events):
   create_backups()

   channel_data = get_channel_data(unsucky_events)

   write_USEvents(unsucky_events)

   write_Channels(channel_data)

# Use the shutil module to copy the databases into a backup folder
def create_backups():
   backup_path = FileDetails.DATA_DIR + '/' + FileDetails.BACKUP_DIR

   databases = [FileDetails.USS_DATABASE_FILENAME, FileDetails.CHANNEL_DATABASE_FILENAME]

   if not os.path.exists(backup_path):
       os.makedirs(backup_path)

   # Backup all the databases
   for file_name in databases:
       if os.path.exists(FileDetails.DATA_DIR + '/' + file_name):
           file_path = FileDetails.DATA_DIR + '/' + file_name
           bkup_file_path = FileDetails.DATA_DIR + '/' + '.' + str(datetime.date.today()) + '-' + file_name
           bkup_file_name = '.' + str(datetime.date.today()) + '-' + file_name
           os.rename(file_path, bkup_file_path)
           shutil.move(bkup_file_path, backup_path + '/' + bkup_file_name)


def get_channel_data(unsucky_events):
    channels = {}

    for event in unsucky_events:
        event_info = unsucky_events[event][0]
        
        for channel in event_info['Submissions']:

            if channel not in channels:
                new_stats = {}
                new_stats['Num Subs'] = 0
                new_stats['Submissions'] = []
                new_stats['Num Mentions'] = 0
                new_stats['Mentioned'] = []

                channels[channel] = new_stats
            
            channel_stats = channels[channel]
            channel_stats['Num Subs'] += 1 

            for video in event_info['Submissions'][channel]:
                if video not in channel_stats['Submissions']:
                    video_title = video['items'][0]['snippet']['title']
                    channel_stats['Submissions'].append(video_title)

        for channel in event_info['Mentions']:
            channel_stats = channels[channel]
            
            channel_stats['Num Mentions'] += 1
            video = event_info['Mentions'][channel][0]
            video_title = video['items'][0]['snippet']['title']
            channel_stats['Mentioned'].append(video_title)

    return channels

def write_USEvents(unsucky_events):
   data_path = FileDetails.DATA_DIR + '/'
    
   if not os.path.exists(data_path):
       os.makedirs(data_path)

   fieldnames = ['Date', 'Host', 'Status', '# of Submissions', 'Submissions',
                 'Mentions']

   data_file = open(data_path + FileDetails.USS_DATABASE_FILENAME, 'wb') 
   unsuckywriter = unicodecsv.DictWriter(data_file, fieldnames=fieldnames,
                                     quoting=unicodecsv.QUOTE_MINIMAL)

   unsuckywriter.writeheader()
   for date in unsucky_events:
       event_info = unsucky_events[date][0]
       
       submissions_list = []
       for channel in event_info['Submissions']:
           for video in event_info['Submissions'][channel]:
               submissions_list.append(video['items'][0]['snippet']['title'])

       mentions_list = []

       for channel in event_info['Mentions']:
           for video in event_info['Mentions'][channel]:
               mentions_list.append(video['items'][0]['snippet']['title'])

       unsuckywriter.writerow({'Date': str(date),
                               'Host': event_info['Host'],
                               'Status': event_info['Status'],
                               '# of Submissions': str(event_info['Number of Submissions']),
                               'Submissions': submissions_list,
                               'Mentions': mentions_list})

def write_Channels(channels):
   data_path = FileDetails.DATA_DIR + '/'
    
   if not os.path.exists(data_path):
       os.makedirs(data_path)

   fieldnames = ['Channel', '# of Submissions', '# of Mentions',
                 'Mention Percentage', 'Submitted Videos',
                 'Mentioned Videos']

   data_file = open(data_path + FileDetails.CHANNEL_DATABASE_FILENAME, 'wb')
   channels_sheet = unicodecsv.DictWriter(data_file, 
                                          quoting=unicodecsv.QUOTE_MINIMAL,
                                          fieldnames=fieldnames)

   channels_sheet.writeheader()

   for channel in sorted(channels):
       channel_stats = channels[channel]

       percentage = float(channel_stats['Num Mentions']) / float(channel_stats['Num Subs']) 

       channels_sheet.writerow({'Channel': channel,
                                '# of Submissions': channel_stats['Num Subs'],
                                '# of Mentions': channel_stats['Num Mentions'], 
                                'Mention Percentage': percentage, 
                                'Submitted Videos':channel_stats['Submissions'],
                                'Mentioned Videos':channel_stats['Mentioned']})
