import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import time

postcodes = pd.read_csv("data_static/australian_postcodes.csv")

nsw_postcodes = postcodes[(postcodes["state"] == "NSW") & (postcodes['postcode'] >= 2000) & (postcodes['postcode'] < 3000)]

unique_nsw_postcodes = nsw_postcodes.drop_duplicates(subset=["postcode"], keep="first")

rows_2017 = []
rows_2019 = []


def clean_str_int(text):
    return int(text.strip().replace(',', ''))

for index, row in unique_nsw_postcodes.iterrows():

    print(f"{unique_nsw_postcodes.index.get_loc(index)/len(unique_nsw_postcodes)*100:.2f}% completed")

    postcode = row["postcode"]
    # postcode = 2795

    response = requests.get(f"http://www.toomanyguns.org/{postcode}")
    print(f"{postcode}:{response.status_code}")

    while response.status_code == 429:
        print("Too many requests, waiting 5 seconds")
        time.sleep(5)
        response = requests.get(f"http://www.toomanyguns.org/{postcode}")
        print(f"{postcode}:{response.status_code}")

    data_2017_items = {'postcode': postcode, 'response': response.status_code}
    data_2019_items = {'postcode': postcode, 'response': response.status_code}

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, features="html.parser")

        # Check if there is a reference to year figures
        # if so then there will be two columns
        # otherwise there will be a single column

        multi_col = True if soup.find("h3", text=re.compile("(\d+) Figures")) != None else False

        if multi_col:
            try:

                # parent_2017 = soup.find("h3", text="2017 Figures").parent
                parent_2017 = soup.find_all("div", attrs={'class': 'sqs-col-6'})[0]

                # They use december 2018 figures as 2019 figures
                # They replace the title using javascript
                # parent_2019 = soup.find("h3", text=re.compile("2019 Figures|2018 Figures")).parent
                parent_2019 = soup.find_all("div", attrs={'class': 'sqs-col-6'})[1]

                data_regex = {
                    "Registered Firearms Owners": "Registered firearms owners:(?P<number>.*)",
                    "Registered Firearms": "Registered firearms:(?P<number>.*)",
                    "Largest stockpile": "Largest number of guns held by one registered owner \(excluding collectors\):(?P<number>.*)"
                }

                for k, v in data_regex.items():
                    item_text = str(parent_2017.find(text=re.compile(v)))
                    item_value = clean_str_int(re.search(v, item_text).group('number'))
                    data_2017_items[k] = item_value

                    item_text = str(parent_2019.find(text=re.compile(v)))
                    item_value = clean_str_int(re.search(v, item_text).group('number'))
                    data_2019_items[k] = item_value

                parse_sucess = True

            except:
                print(f"Parsing failed: {postcode}")
                parse_sucess = False

            data_2017_items['parse sucess'] = parse_sucess
            data_2019_items['parse sucess'] = parse_sucess
        else:
            try:
                data_regex = {
                    "Registered Firearms Owners": "Registered firearms owners:(?P<number>.*)",
                    "Registered Firearms": "Registered firearms:(?P<number>.*)",
                    "Largest stockpile": "Largest number of guns held by one registered owner \(excluding collectors\):(?P<number>.*)"
                }

                for k, v in data_regex.items():
                    item_text = str(soup.find(text=re.compile(v)))
                    item_value = clean_str_int(re.search(v, item_text).group('number'))
                    data_2019_items[k] = item_value

                parse_sucess = True

            except:
                print(f"Parsing failed: {postcode}")
                parse_sucess = False

            data_2017_items['parse sucess'] = False
            data_2019_items['parse sucess'] = parse_sucess

    rows_2017.append(data_2017_items)
    rows_2019.append(data_2019_items)

df_2017 = pd.DataFrame(rows_2017)
df_2017.to_csv("data_generated/firearms_2017.csv")

df_2019 = pd.DataFrame(rows_2019)
df_2019.to_csv("data_generated/firearms_2019.csv")



