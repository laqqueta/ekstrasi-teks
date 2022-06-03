import pandas as pd
import time
import re
import time
from datetime import datetime, timedelta

def main():
    csv_file = pd.read_csv('TwitterPoldaMetroJaya.csv')
    data = csv_file[["X.1", "X.2"]]
    data_l = data.values.tolist();

    # i = 1
    # for col in data_l:
    #     print(i, end='. ')
    #     print(col[1])
    #     i += 1

    print('='*100)

    # remove any link
    URL_PATTERN = r'[A-Za-z0-9]+://[A-Za-z0-9%-_]+(/[A-Za-z0-9%-_])*(#|\\?)[A-Za-z0-9%-_&=]*'
    regx = re.compile(URL_PATTERN)

    for data in data_l:
        if regx.search(data[0]):
            data[0] = re.sub(URL_PATTERN, '', data[0])

    # remove empty list
    n = 0
    for data in data_l:
        if not data[0]:
            data_l.pop(n)
        n += 1

    # convert twitter timestamp to gmt +7
    for data in data_l:
        data[1] = to_gmt7(data[1])

    # get data that contain trafic information
    TRAFFIC_PATTERN = r"[0-9]+\.+[0-9]"
    regx = re.compile(TRAFFIC_PATTERN)

    i = 1
    for data in data_l:
        if "arus" in data[0]:
            print(data[0])
        i+=1

    # i = 1
    # for col in data_l:
    #     print(i, end='. ')
    #     print(col)
    #     i += 1


def to_gmt7(twitter_date):
    date = datetime.strptime(twitter_date, "%Y-%m-%d %H:%M:%S")
    to_timestamp = date.timestamp()
    d_add = to_timestamp + 25200 #7 Hours
    to_date = datetime.fromtimestamp(d_add)

    return to_date.strftime("%d %B %Y %H:%M:%S")

if __name__ == '__main__':
    main()