import unicodecsv
import FileDetails
import os
from bokeh.charts import TimeSeries
import datetime

def analyze_databases():
    analyze_USS_database()
#    analyze_channel_database()

def analyze_USS_database():
    file_path = FileDetails.DATA_DIR + '/' + FileDetails.USS_DATABASE_FILENAME
    if not os.path.exists(file_path):
        print "Cannot find database!"
        return

    uss_database = unicodecsv.DictReader(open(file_path, 'rb'))
    plot_submissions_over_time(uss_database)

def plot_submissions_over_time(uss_database):
    sub_counts = []
    events = []
    for event in uss_database:
        sub_counts.append(int(event['# of Submissions']))
        date = event['Date'].split('-')

        events.append(datetime.date(int(date[0]), int(date[1]), int(date[2])))
        
    # Put down data    
    plot = TimeSeries(sub_counts, events)
    
    # label the plot
    plot.title("Submissions over Time").xlabel("Date").ylabel("# of Submissions")
    
    # Save the plot
    plot.filename('test.html')
def analyze_channel_database():
    file_path = FileDetails.DATA_DIR + '/' + FileDetails.CHANNEL_DATABASE_FILENAME
    if not os.path.exists(file_path):
        print "Cannot find database!"
        return

    channel_database = unicodecsv.DictReader(open(file_path, 'rb'))
    
    for channel in channel_database:
        print channel['Channel']
