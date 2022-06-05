import pandas
import pandas as pd
import re
from datetime import datetime, timedelta

def main():
    filtered_data = []
    f_name = ['poldametro31.csv', 'poldametro01.csv', 'poldametro02.csv', 'poldametro03.csv']

    for filename in f_name:
        csv_file = pd.read_csv(filename)
        data = csv_file[["Content", "Date"]]
        data_l = data.values.tolist();
        temp_filtered_data = []

        # Select data that contain "arus" and "lintas"
        for dl in data_l:
            if "arus" in dl[0] and "lintas" in dl[0]:
                temp_filtered_data.append([dl[0], dl[1]])

        # Remove link from text
        URL_PATTERN = r'[A-Za-z0-9]+://[A-Za-z0-9%-_]+(/[A-Za-z0-9%-_])*(#|\\?)[A-Za-z0-9%-_&=]*'
        regx = re.compile(URL_PATTERN)

        for tfd in temp_filtered_data:
            if regx.search(tfd[0]):
                tfd[0] = re.sub(URL_PATTERN, '', tfd[0])

        # Remove empty array
        n = 0
        for tfd in temp_filtered_data:
            if not tfd[0]:
                temp_filtered_data.pop(n)
            n += 1

        # Convert Twitter Timestamp to GMT+7
        for tfd in temp_filtered_data:
            tfd[1] = to_gmt7(tfd[1])

        #
        singkatan = [
            ["Jl.", "Jalan"],
            ["TL", "Traffic Light"],
            ["Tl", "Traffic Light"],
            ["Jaksel", "Jakarta Selatan"],
            ["Jakut", "Jakarta Utara"],
            ["Jakbar", "Jakarta Barat"],
            ["Jaktim", "Jakarta Timur"],
            ["Jakpus", "Jakarta Pusat"]
        ]

        n = 0
        for tfd in temp_filtered_data:
            for s in singkatan:
                if s[0] in tfd[0]:
                    str = temp_filtered_data[n][0]
                    str = str.replace(s[0], s[1])
                    temp_filtered_data[n][0] = str
            n += 1

        for fd in temp_filtered_data:
            filtered_data.append(fd)

    df = pandas.DataFrame(filtered_data, columns=['Content', 'Date'])
    df.to_csv('hasil.csv', encoding='UTF-8', index=False)


def to_gmt7(twitter_date):
    date = datetime.strptime(twitter_date, "%Y-%m-%d %H:%M:%S")
    to_timestamp = date.timestamp()
    d_add = to_timestamp + 25200 #7 Hours
    to_date = datetime.fromtimestamp(d_add)

    return to_date.strftime("%d %B %Y %H:%M:%S")

if __name__ == '__main__':
    main()