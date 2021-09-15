from bs4 import BeautifulSoup as bs
import requests
import praw
from redditbot import mutator as m
import os
from config import config as cfg
cfg_dict = cfg.config_dict

reddit = praw.Reddit(
    client_id=os.getenv(f'{cfg_dict["Reddit"]["client_id"]}'),
    client_secret=os.getenv(f'{cfg_dict["Reddit"]["client_secret"]}'),
    user_agent=f'{cfg_dict["Reddit"]["user_agent"]}',
    username=f'{cfg_dict["Reddit"]["username"]}',
    password=os.getenv(f'{cfg_dict["Reddit"]["password"]}'))


def get_word(my_result):
    """ finds word in database """
    row = my_result[0]
    Singular = row[1].capitalize()
    SingularTranslation = f'_{row[2].capitalize()}_'
    return Singular, SingularTranslation


def get_plural(my_result):
    """ finds plural of word in database"""
    row = my_result[0]
    if row[3] != 'None':
        Plural = f'**{row[3].capitalize()}:**\n\n_{row[4].capitalize()}_'
    else:
        Plural = ''
    return Plural


def get_gender(my_result):
    """ Finds gender of word in database """
    row = my_result[0]
    if row[5] != 'None':
        Gender = f'**Gender:** {row[5].capitalize()}'
    else:
        Gender = ''
    return Gender


def get_soup(singular):
    """ gets wiktionary content for chosen word of the day, referenced as 'soup' """
    page = requests.get(f'{cfg_dict["Reddit"]["page"]}{singular}')
    src = page.content
    soup = bs(src, 'lxml')
    return soup


def get_word_class(soup):
    """ checks for 'h3' section in html of 'soup' with a name equal to a word class an creates a variable,
        if word class is not referenced then the variable will be an empty string """
    try:
        for tag in soup.find(id=f'{cfg_dict["Reddit"]["language_ID"]}').parent.find_next_siblings('h3'):
            section = next(tag.strings)
            if section in [
                'Noun', 'Verb', 'Adjective',
                'Adverb', 'Pronoun',
                'Preposition', 'Conjunction',
                'Determiner', 'Exclamation'
            ]:
                word_class = f'**Word class:** {section}'
            else:
                word_class = ''
    except AttributeError:
        word_class = ''
    finally:
        return word_class


def get_IPA(soup):
    """
    finds the IPA in the Pronunciation section and creates a variable from it,
    if IPA is non existent then the Pronunciation Var is made into an empty string
    """
    IPA = []
    try:
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
                    pronunciation = f'**Pronunciation:**\n\n{IPA}'
                    return pronunciation
    except AttributeError:
        pronunciation = ''
        return pronunciation


def get_mutations(singular):
    """ Mutates the word according to the Welsh mutation rules and creates a table """

    mutations = f'''
**Mutations:**\n\n
|soft|aspirate|nasal|h_pros|
:--|:--|:--|:--|
|{m.soft(singular)}|{m.aspirate(singular)}|{m.nasal(singular)}|{m.h_proth(singular)}|'''
    return mutations


def WWOTDpost(word_class, pronunciation, mutation_table, singular, singular_translation, plural, gender):
    """ Posts word of the day to chosen subreddit """
    reddit.validate_on_submit = True
    selftext = f'{singular_translation}\n\n{plural}\n\n{gender}\n\n{word_class}\n\n{pronunciation}\n\n{mutation_table}'
    title = f'WWOTD: {singular.capitalize()}'
    reddit.subreddit(f'{cfg_dict["Reddit"]["subreddit"]}').submit(title, selftext, flair_id='a6c72efe-162e-11ec-adc4-b26f4ab04a7a')


if __name__ == '__main__':
    pass
