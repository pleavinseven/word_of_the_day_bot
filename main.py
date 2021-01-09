import praw
import os
import schedule
import time
import random
import translators as ts
from PyDictionary import PyDictionary

dictionary = PyDictionary()

word_list = open('word_list.text', 'r').read().split(' ')


def WWOTDpost():
    reddit = praw.Reddit(client_id=os.getenv('client_id'),
                         client_secret=os.getenv('client_secret'),
                         user_agent='WWOTDbot',
                         username='WWOTDbot',
                         password=os.getenv('Reddit_password'))

    reddit.validate_on_submit = True
    eng_word = random.choice(word_list)
    welsh_word = ts.google(eng_word, 'en', 'cy')
    dict_word = dictionary.meaning(eng_word)
    for nav in dict_word:
        if nav in ['Noun', 'Verb', 'Adjective', 'Adverb']:
            Nav = nav
    title = 'WWOTD: {}'.format(welsh_word)
    selftext = '{0}  \n\n{1}'.format(eng_word, Nav)
    reddit.subreddit('learnwelsh').submit(title, selftext)


schedule.every().day.at("10:30").do(WWOTDpost)

while True:
    schedule.run_pending()
    time.sleep(1)
