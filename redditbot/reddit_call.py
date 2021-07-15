from bs4 import BeautifulSoup as bs
import requests
import praw
from redditbot import mutator as m
import os

reddit = praw.Reddit(client_id=os.getenv('client_id'),
                     client_secret=os.getenv('client_secret'),
                     user_agent='WWOTDbot',
                     username='WWOTDbot',
                     password=os.getenv('Reddit_password'))


def get_words(my_result):
    row = my_result[0]
    Singular = row[1].capitalize()
    SingularTranslation = f'_{row[2].capitalize()}_'
    if row[3] != 'None':
        Plural = f'**{row[3].capitalize()}:**\n\n_{row[4].capitalize()}_'
    else:
        Plural = ''
    if row[5] != 'None':
        Gender = f'**Gender:** {row[5].capitalize()}'
    else:
        Gender = ''
    return Singular, SingularTranslation, Plural, Gender


def get_soup(singular):
    ''' gets page content, referenced as soup '''
    page = requests.get('https://en.wiktionary.org/wiki/{}'.format(singular))
    src = page.content
    soup = bs(src, 'lxml')
    return soup


def get_word_class(soup):
    ''' checks for h3 section with a name equal to a word class '''
    try:
        for tag in soup.find(id='Welsh').parent.find_next_siblings('h3'):
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
    '''
    finds the IPA in the Pronunciation section and creates a variable from it,
    if IPA is non existent then both the IPA Var and Pronunciation Var are made into empty strings
    '''
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
    ''' Mutates the word according to the Welsh mutation rules and creates a table '''

    mutations = f'''
**Mutations:**\n\n
|soft|aspirate|nasal|h_pros|
:--|:--|:--|:--|
|{m.soft(singular)}|{m.aspirate(singular)}|{m.nasal(singular)}|{m.h_proth(singular)}|'''
    return mutations


def WWOTDpost(word_class, pronunciation, mutation_table, Singular, SingularTranslation, Plural, Gender):
    ''' Posts to reddit '''
    reddit.validate_on_submit = True
    selftext = f'{SingularTranslation}\n\n{Plural}\n\n{Gender}\n\n{word_class}\n\n{pronunciation}\n\n{mutation_table}'
    title = 'WWOTD: {}'.format(Singular.capitalize())
    reddit.subreddit('learnwelsh').submit(title, selftext)


if __name__ == '__main__':
    print('dunno')
