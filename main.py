import sys
import datefinder
import re

import pandas as pd
import dateutil.parser as dt_parser
from os.path import exists

from datetime import datetime, timedelta

def filter_data(tweet_file):
    csv_file = pd.read_csv(tweet_file)
    data_twit = csv_file[["Content", "Date"]]
    data_t = data_twit.values.tolist()
    temp_filtered_data = []

    singkatan = [["jakpus", "Jakarta Pusat"], ["jl.", "Jalan"], ["Jakpus", "Jakarta Pusat"], ["Jl.", "Jalan"]]
    URL_PATTERN = r'[A-Za-z0-9]+://[A-Za-z0-9%-_]+(/[A-Za-z0-9%-_])*(#|\\?)[A-Za-z0-9%-_&=]*'
    regx = re.compile(URL_PATTERN)

    for tfd in data_t:
        # Index 0 = Content
        # Index 1 = Date
        str = tfd[0][5:].strip()
        # Select content that 24 char from start equal to "situasi arus lalu lintas" and
        # content that have word "jakpus"
        if "situasi arus lalu lintas" in str[:24].lower() and "jakpus" in str.lower():
            # Exclude content that have "kawasan" and "sekitar" word
            if "kawasan" in str.lower() or "sekitar" in str.lower():
                pass
            else:
            # Remove any link from content
                if regx.search(str):
                    str = re.sub(URL_PATTERN, '', str)
                # Find abbreviation in content and change it
                for sngk in singkatan:
                    str_temp = str
                    if sngk[0] in str_temp:
                        str = str_temp.replace(sngk[0], sngk[1])
                # Change date to GMT +7
                tfd[1] = to_gmt7(tfd[1])
                # Remove "&amp;" in content
                if "&amp;" in str:
                    str = str.replace("&amp;",'')
                # Append new data
                tfd[0] = str.strip()
                temp_filtered_data.append(tfd)

    return temp_filtered_data

def convert_time_and_loc(filtered_data):
    filtered_data = filtered_data
    data_from = []
    data_to = []
    data_time = []
    data_day = []
    data_date = []

    for tfd in filtered_data:
        if "menuju" in tfd[0]:
            str_from = tfd[0][28:tfd[0].find("menuju")]
        else:
            str_from = tfd[0][28:tfd[0].find("Jakarta Pusat")]

        str_to = tfd[0][tfd[0].lower().find("pusat"):tfd[0].lower().find("terpantau")]

        str_from_temp = ""

        if "traffic light" in str_from.lower() and "jalan" in str_from.lower():
            str_from_temp = str_from[str_from.lower().find("jalan"):len(str_from) - 1]
            data_from.append(str_from_temp)
            # print(str_from[str_from.lower().find("jalan"):len(str_from)-1])
        elif "traffic light" in str_from.lower() and "dari arah" in str_from.lower():
            str_from_temp = str_from[str_from.lower().find("arah "):str_from.lower().find(" menuju")]
            data_from.append(str_from_temp)
        else:
            if "jalan" in str_from.lower():
                str_from_temp = str_from[str_from.lower().find("jalan"):str_from.lower().find("jakarta pusat")]
                data_from.append(str_from_temp)
                # print(str_from[str_from.lower().find("jalan"):len(str_from)-1])
            else:
                data_from.append(str_from)
                # print(str_from)

        if "menuju" in str_to.lower():
            if "maupun arah" in str_to.lower():
                str1 = str_to[str_to.find("arah"):str_to.find("maupun")]
                str2 = str_to[str_to.find("maupun"):len(str_to) - 1]

                if str_from_temp in str1:
                    str1 = str1.replace(str_from_temp, '')

                data_to.append(str1.strip() + ", " + str2.strip())
            else:
                data_to.append(str_to[str_to.find("menuju"):len(str_to) - 1])
        else:
            data_to.append("-")

    for i in range(len(data_from)):
        if "arah" in data_from[i]:
            data_from[i] = data_from[i].replace("arah", '').strip()
        if "Jakarta Pusat" in data_from[i]:
            data_from[i] = data_from[i].replace("Jakarta Pusat", '').strip()

    for i in range(len(data_to)):
        if "-" in data_to[i]:
            pass
        else:
            for dt in data_to[i].split(" "):
                if dt == "arah":
                    data_to[i] = data_to[i].replace("arah", '')
                if dt == "maupun":
                    data_to[i] = data_to[i].replace("maupun", '')
                if dt == "menuju":
                    data_to[i] = data_to[i].replace("menuju", '')

            data_to[i] = re.sub("\s\s+", " ", data_to[i]).strip()

    for time in filtered_data:
        date = datetime.strptime(time[1], "%d %B %Y %H:%M:%S")
        data_day.append(date.strftime("%A"))
        data_time.append(date.time())
        data_date.append(date.strftime("%d %B %Y"))

    return data_from, data_to, data_day, data_time, data_date



    # i = 0
    # for df in data_from:
    #     print(df)
    #     i += 1
    #
    # print("="*100)
    #
    # i = 0
    # for df in data_to:
    #     print(df)
    #     i += 1

def to_gmt7(twitter_date):
    to_timestamp = dt_parser.parse(twitter_date).timestamp()
    d_add = to_timestamp + 25200 #7 Hours
    to_date = datetime.fromtimestamp(d_add)

    return to_date.strftime("%d %B %Y %H:%M:%S")

def main():
    csv_file = "files/PoldaMetroJaya.csv"
    filtered_data = filter_data(csv_file)
    dfrom, dto, dday, dtime, ddate = convert_time_and_loc(filtered_data)
    tweet = []

    for fd in filtered_data:
        tweet.append(fd[0])

    if not exists("files/result.csv"):
        file = open("files/result.csv", "w+")
        file.close()

    dataframe = pd.DataFrame(list(zip(tweet, dfrom, dto, dday, dtime, ddate)),
                             columns=['Tweet', 'From', 'To', 'Day', 'Time', 'Date'])

    dataframe.to_csv("files/result.csv", encoding="utf-8", index=False)

if __name__ == '__main__':
    main()
