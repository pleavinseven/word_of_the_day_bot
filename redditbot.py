import praw
import os
import schedule
import time
import random
from bs4 import BeautifulSoup as bs
import requests
import mutator as m


def get_dict():
    """creates dictionary from word-list text document"""
    with open('word_list.txt', 'r') as f:
        f = f.readlines()
        word_dict = {k: v for k, v in (line.split(':') for line in f)}
    return word_dict


def popped_words(welsh_word, english_word, used=bool):
    """
     if word is not in wiktionary(used= False),
     word is written to non_words.txt,
     else word is written to use_words.txt.
     Word is then removed from word list
    """
    if used:
        with open('used_words.txt', 'a') as f:
            f.write('{}:{}'.format(welsh_word.lower(), english_word.lower()))
        with open("word_list.txt", "r") as f:
            lines = f.readlines()
        with open("word_list.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != '{}:{}'.format(welsh_word.lower(), english_word.lower()):
                    f.write(line)
    else:
        with open('non_words.txt', 'a') as f:
            f.write('{}:{}'.format(welsh_word.lower(), english_word.lower()))
        main()


def get_welsh_word(word_dict):
    """chooses random welsh word from dict"""
    Welsh_word = random.choice(list(word_dict.keys()))
    return Welsh_word


def get_soup(Welsh_word):
    """ gets page content, referenced as soup """
    page = requests.get('https://en.wiktionary.org/wiki/{}'.format(Welsh_word))
    src = page.content
    soup = bs(src, 'lxml')
    return soup


def get_word_class(soup, welsh_word):
    """ checks for h3 section with a name equal to a word class """
    try:
        for tag in soup.find(id='Welsh').parent.find_next_siblings('h3'):
            section = next(tag.strings)
            if section in [
                'Noun', 'Verb', 'Adjective',
                'Adverb', 'Pronoun',
                'Preposition', 'Conjunction',
                'Determiner', 'Exclamation'
            ]:
                Word_class = section
                return Word_class
            else:
                continue
    except AttributeError:
        popped_words(welsh_word, used=False)


def get_IPA(soup):
    """
    finds the IPA in the Pronunciation section and creates a variable from it,
    if IPA is non existent then both the IPA Var and Pronunciation Var are made into empty strings
    """
    IPA = []
    for tag in soup.find(id='Welsh').parent.find_next_siblings('h3'):
        sibling = tag.find_next_sibling()
        if sibling.name == 'ul':
            if sibling.find('ul'):
                for li in sibling.find('ul').find_all('li'):
                    sibling.append(li)
                sibling.find('ul').decompose()
                for li in sibling.find_all('li'):
                    IPA.append(str(li.text.strip().replace('IPA(key)', '')))
                IPA = '\n\n'.join(IPA).replace('(', '')
                IPA = IPA.replace(')', '')
    return IPA


def get_mutations(welsh_word):
    """ Mutates the word according to the Welsh mutation rules and creates a table """

    mutations = f'''
|soft|aspirate|nasal|h_pros|
:--|:--|:--|:--|
|{m.soft(welsh_word)}|{m.aspirate(welsh_word)}|{m.nasal(welsh_word)}|{m.h_proth(welsh_word)}|'''
    return mutations


def WWOTDpost(welsh_word, english_word, word_class, pronunciation, mutation, mutation_table):
    """ Posts to reddit """
    reddit = praw.Reddit(client_id=os.getenv('client_id'),
                         client_secret=os.getenv('client_secret'),
                         user_agent='WWOTDbot',
                         username='WWOTDbot',
                         password=os.getenv('Reddit_password'))

    reddit.validate_on_submit = True
    selftext = '{0}\n\n{1}\n\n{2}\n\n{3}\n\n{4}' \
        .format(english_word, word_class,
                pronunciation, mutation, mutation_table)
    title = 'WWOTD: {}'.format(welsh_word.capitalize())
    reddit.subreddit('learnwelsh').submit(title, selftext)


def main():
    word_dict = get_dict()
    welsh_word = get_welsh_word(word_dict)
    english_word = word_dict[welsh_word].capitalize()
    soup = get_soup(welsh_word)
    pronunciation = get_IPA(soup)
    if not pronunciation:
        pronunciation = ''
    else:
        pronunciation = f'**Pronunciation:**\n\n{pronunciation}'
    mutation = '**Mutations:**\n\n'
    mutation_table = get_mutations(welsh_word)
    word_class = get_word_class(soup, welsh_word)
    popped_words(welsh_word, english_word, used=True)
    WWOTDpost(welsh_word, english_word, word_class, pronunciation, mutation, mutation_table)


if __name__ == '__main__':
    main()

schedule.every().day.at("10:30").do(WWOTDpost)

while True:
    schedule.run_pending()
    time.sleep(1)
