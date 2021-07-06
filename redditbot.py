import schedule
import time
from bs4 import BeautifulSoup as bs
import requests
import praw
import mutator as m
import mysql.connector
import os

Singular = ''
SingularTranslation = ''
Plural = ''
PluralTranslation = ''
Gender = ''
mydb = mysql.connector.connect(
    host=os.getenv('db_host'),
    user=os.getenv('db_username'),
    password=os.getenv('db_password'),
    database=os.getenv('db_name')
    )


def reset_database():
    my_cursor = mydb.cursor(buffered=True)
    reset_all = "update words set Used = false where Used = true"
    my_cursor.execute(reset_all)
    mydb.commit()
    main()


def DB_query():
    global Singular
    global SingularTranslation
    global Plural
    global PluralTranslation
    global Gender
    my_cursor = mydb.cursor(buffered=True)
    sql = "SELECT * FROM words WHERE USED is False"
    my_cursor.execute(sql)
    mydb.commit()
    my_result = my_cursor.fetchall()
    if not my_result:
        reset_database()
    else:
        row = my_result[0]
        Singular = row[1].capitalize()
        SingularTranslation = f'_{row[2].capitalize()}_'
        if row[3] != 'None':
            Plural = f'**{row[3].capitalize()}:**\n\n_{row[4].capitalize()}_'
        else:
            Plural = ''
            PluralTranslation = ''
        if row[5] != 'None':
            Gender = f'**Gender:** {row[5].capitalize()}'
        else:
            Gender = ''


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


def WWOTDpost(word_class, pronunciation, mutation_table):
    ''' Posts to reddit '''
    global Singular
    global SingularTranslation
    global Plural
    global PluralTranslation
    global Gender

    reddit = praw.Reddit(client_id=os.getenv('client_id'),
                         client_secret=os.getenv('client_secret'),
                         user_agent='WWOTDbot',
                         username='WWOTDbot',
                         password=os.getenv('Reddit_password'))

    reddit.validate_on_submit = True
    selftext = f'{SingularTranslation}\n\n{Plural}\n\n{Gender}\n\n{word_class}\n\n{pronunciation}\n\n{mutation_table}'
    title = 'WWOTD: {}'.format(Singular.capitalize())
    reddit.subreddit('learnwelsh').submit(title, selftext)


def used_word():
    global Singular
    cursor = mydb.cursor(buffered=True)
    reset = f"UPDATE words\
            SET Used = True\
            WHERE Singular = '{Singular}';"
    cursor.execute(reset)
    mydb.commit()


def main():
    global Singular
    global SingularTranslation
    global Plural
    global PluralTranslation
    global Gender
    DB_query()
    soup = get_soup(Singular)
    pronunciation = get_IPA(soup)
    mutation_table = get_mutations(Singular)
    word_class = get_word_class(soup)
    WWOTDpost(word_class, pronunciation, mutation_table)
    used_word()


if __name__ == '__main__':
    schedule.every().day.at("10:30").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
