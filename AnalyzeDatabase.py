import unicodecsv

# TODO: Refactor module completely.
# TODO: Split function into helper functions
# TODO: Document code

# This is pretty raw code. Read the master database and create
# smaller analytical databases
def analyze_database():
    database = unicodecsv.reader(open('USSDatabase.csv', 'rb'), delimiter=',')

    channels = {}

    total_events = 0
    total_submittors = 0
    total_mentions = 0

    for uss_event in database:
        total_events += 1
        event = uss_event[0]
        date = database.next()[1]
        host = database.next()[1]
        status = database.next()[1]
        number_of_submissions = int(database.next()[1])

        total_submittors += number_of_submissions
        
        # Burn row
        database.next()
        for i in range(0, number_of_submissions):
            submission_row = database.next()
            channel = submission_row[0]

            if channel not in channels:
                channel_stats = {}
                channel_stats['Num Subs'] = 0
                channel_stats['Submissions'] = []
                channel_stats['Num Mentions'] = 0
                channel_stats['Mentioned'] = []

                channels[channel] = channel_stats

            channel_stats = channels[channel]
            channel_stats['Num Subs'] += 1 

            for video in submission_row[1:]:
                if video not in channel_stats['Submissions']:
                    channel_stats['Submissions'].append(video)

        # Burn row
        database.next()
        for row in database:
            if len(row) == 0:
                break

            total_mentions += 1
            channel = row[0]
            channel_stats = channels[channel]
            
            channel_stats['Num Mentions'] += 1
            channel_stats['Mentioned'].append(row[1])

    # Write USS_Event statistics
    uss_sheet = unicodecsv.writer(open('USSStatistics.csv', 'wb'), delimiter=',', quoting=unicodecsv.QUOTE_MINIMAL)
    uss_sheet.writerow(['Number of USS Events'] + [total_events])
    uss_sheet.writerow(['Average # of Participants'] + [float(total_submittors)/total_events])
    uss_sheet.writerow(['Total # of Mentions'] + [total_mentions])
    uss_sheet.writerow(['Average # of Mentions'] + [float(total_mentions)/total_events])

    # Write channel statistics
    channels_sheet = unicodecsv.writer(open('ChannelDatabase.csv', 'wb'), delimiter=',', quoting=unicodecsv.QUOTE_MINIMAL)
    header = ['Channel'] + ['# of Submissions'] + ['# of Mentions'] + \
             ['Mention Percentage'] + ['Submitted Videos'] + \
             ['Mentioned Videos']

    channels_sheet.writerow(header)

    channel_count = 0
    total_submissions = 0
    total_mentions = 0
    total_percentage = 0.0

    for channel in sorted(channels):
        channel_count += 1
        total_submissions += channel_stats['Num Subs']

        total_mentions += channel_stats['Num Mentions']
        channel_stats = channels[channel]

        percentage = float(channel_stats['Num Mentions']) / float(channel_stats['Num Subs']) 

        total_percentage += percentage

        channels_sheet.writerow([channel] + [channel_stats['Num Subs']] +
                                [channel_stats['Num Mentions']] +
                                [percentage] +
                                [channel_stats['Submissions']] +
                                [channel_stats['Mentioned']])

    channels_sheet.writerow([])
    channels_sheet.writerow(['Total Channels'] + [channel_count])
    channels_sheet.writerow(['Total Submissions'] + [total_submissions])
    channels_sheet.writerow(['Average # of Submissions'] + [total_submissions / float(channel_count)])
    channels_sheet.writerow(['Average # of Mentions'] + [total_mentions / float(channel_count)])
    channels_sheet.writerow(['Average Percentage'] + [total_percentage / total_submissions])
