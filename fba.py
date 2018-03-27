from dateutil import parser
from datetime import timedelta
from wordcloud import WordCloud
from bs4 import BeautifulSoup
import plotly as py
import plotly.graph_objs as go
import json
import sys

STOPWORDS = []
FRENCH = False

class LanguageParserInfo(parser.parserinfo):
    WEEKDAYS = [('Lun', 'Lundi'),
                ('Mar', 'Mardi'),
                ('Mer', 'Mercredi'),
                ('Jeu', 'Jeudi'),
                ('Ven', 'Vendredi'),
                ('Sam', 'Samedi'),
                ('Dim', 'Dimanche')]
    MONTHS = [('Jan', 'Janvier'),
              ('Fev', 'Février'),
              ('Mar', 'Mars'),
              ('Avr', 'Avril'),
              ('Mai', 'Mai'),
              ('Jui', 'Juin'),
              ('Jul', 'Juillet'),
              ('Aoû', 'Août'),
              ('Sep', 'Septembre'),
              ('Oct', 'Octobre'),
              ('Nov', 'Novembre'),
              ('Déc', 'Décembre')]

def get_message_data(filename):

    with open(filename, 'r') as html_file:
        soup = BeautifulSoup(html_file.read(), 'lxml')

    messages_div = soup.find_all('div', class_='message')

    print(f'{len(messages_div)} found')

    message_data = []
    for message in messages_div:
        date_text = message.find('span', class_='meta').text
        date = parser.parse(date_text, parserinfo=LanguageParserInfo())

        message_data.append({
            'sender': message.find('span', class_='user').text,
            'date': date,
            'content': message.next_sibling.text
        })

    return message_data

def get_daily_data(messages):
    by_date = {}
    for message in messages:
        key = message['date'].strftime('%Y-%m-%d')
        if key in by_date:
            by_date[key] += 1
        else:
            by_date[key] = 1

    dates = [message['date'] for message in messages]
    min_date = min(dates)
    for i in range((max(dates) - min_date).days):
        date = (min_date + timedelta(i)).strftime('%Y-%m-%d')
        if not date in by_date:
            by_date[date] = 0


    return by_date

def get_word_cloud(messages):
    full_text = " ".join([message['content'] for message in messages])
    wc = WordCloud(stopwords=STOPWORDS, width=1200, height=800)
    frequencies = wc.process_text(full_text)
    return wc.generate_from_frequencies(frequencies)


def main():
    global FRENCH

    if len(sys.argv) < 1:
        print('Please provide a filename', file=sys.stderr)
        exit(1)
    if len(sys.argv) > 2 and sys.argv[2] == 'fr':
        FRENCH = True

    if FRENCH:
        with open('stopwords-fr.json', 'r') as f:
            global STOPWORDS
            STOPWORDS = json.load(f)

    filename = sys.argv[1]
    messages = get_message_data(filename)
    daily_data = get_daily_data(messages)
    word_cloud = get_word_cloud(messages)
    word_cloud.to_file('wordcloud.png')

    del word_cloud
    del messages

    x = sorted(daily_data.keys())
    y = [daily_data[key] for key in x]


    py.offline.plot({
        'data': [
            go.Scatter(x=x, y=y, line={'shape': 'vh'})
        ]
    }, auto_open=False)

if __name__ == "__main__":
    main()
