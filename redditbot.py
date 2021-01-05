import praw
import os
import schedule
import time
import random
from googletrans import Translator
from PyDictionary import PyDictionary

translator = Translator()
dictionary = PyDictionary()

word_list = open('word_list.text', 'r').read().split(' ')


def test_post():
    # os.getenv variables are 'config vars' (environmental variables) in Heroku.
    reddit = praw.Reddit(client_id=os.getenv('client_id'),
                         client_secret=os.getenv('client_secret'),
                         user_agent='testrobot12345',
                         username='testrobot12345',
                         password=os.getenv('Reddit_password'))

    eng_word = random.choice(word_list)
    translate_word = translator.translate(eng_word, dest='cy',
                                          src='auto')  # all info on translated word, too much info.
    welsh_word = translate_word.text  # translated word only.
    if welsh_word == eng_word:
        test_post()
    dict_word = dictionary.meaning(eng_word)  # noun/verb/adj + description + too much info
    for nav in dict_word:
        if nav in ['Noun', 'Verb', 'Adjective', 'Adverb']:
            Nav = nav  # noun, adj or verb

    title = 'WWOTD: {}'.format(welsh_word)
    selftext = '{0}  \n\n{1}'.format(eng_word, Nav)
    reddit.subreddit('testingground4bots').submit(title, selftext)


schedule.every().day.at("10:30").do(test_post)

while True:
    schedule.run_pending()
    time.sleep(1)
