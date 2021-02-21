import praw
import os
import schedule
import time
import random


def get_dict():
    '''creates dictionary from word-list text document'''
    with open('word_list.txt', 'r') as f:
        f = f.readlines()
        word_dict = {k:v for k,v in (line.split(':') for line in f)}
    return word_dict


def popped_words(welsh_word, english_word, used=bool):
    '''
     if word is not in wiktionary(used= False),
     word is written to non_words.txt,
     else word is written to use_words.txt.
     Word is then removed from word list
    '''
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
    '''finds welsh word in dict'''
    Welsh_word = random.choice(list(word_dict.keys()))
    return Welsh_word


def get_soup(Welsh_word):
    ''' gets page content, referenced as soup '''
    page = requests.get('https://en.wiktionary.org/wiki/{}'.format(Welsh_word))
    src = page.content
    soup = bs(src, 'lxml')
    return soup


def get_word_class(soup, welsh_word):
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
                Word_class = section
                return Word_class
            else:
                continue
    except AttributeError:
        popped_words(welsh_word, used=False)




def get_IPA(soup):
    '''
    finds the IPA in the Pronunciation section and creates a variable from it,
    if IPA is non existent then both the IPA Var and Pronunciation Var are made into empty strings
    '''
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
    return IPA


def get_mutations(soup):
    ''' Finds the mutation table and creates a dictionary from it '''

    for tag in soup.find(id='Welsh').parent.find_next_siblings('h3'):
        sibling = tag.find_next_sibling()
        if sibling.name == 'table':
            keys = [
                th.text.strip() for th in
                sibling.find_all('th')[-1].find_parent().find_all('th')
            ]
            values = [td.text.strip() for td in sibling.find_all('td')]
            Mutation_dict = dict(zip(keys, values))
            return Mutation_dict


def WWOTDpost(Welsh_word, English_word, Word_class, Pronunciation, IPA, Mutation, Mutation_dict):
    ''' Posts to reddit '''
    reddit = praw.Reddit(client_id=os.getenv('client_id'),
                         client_secret=os.getenv('client_secret'),
                         user_agent='WWOTDbot',
                         username='WWOTDbot',
                         password=os.getenv('Reddit_password'))

    reddit.validate_on_submit = True
    selftext = '{0}\n\n{1}\n\n{2}{3}\n\n{4}{5}' \
        .format(English_word, Word_class,
                Pronunciation, ''.join(IPA), Mutation, Mutation_dict)
    title = 'WWOTD: {}'.format(Welsh_word.capitalize())
    reddit.subreddit('testingground4bots').submit(title, selftext)


def main():
    word_dict = get_dict()
    Welsh_word = 'agos' #get_welsh_word(word_dict)
    English_word = word_dict[Welsh_word].capitalize()
    soup = get_soup(Welsh_word)
    Word_class = get_word_class(soup, Welsh_word)
    IPA = get_IPA(soup)
    Mutation = 'Mutations: '
    Mutation_dict = get_mutations(soup)
    if not IPA:
        IPA = ''
        Pronunciation = ''
    else:
        Pronunciation = 'Pronunciation: '
    popped_words(Welsh_word, English_word, used=True)
    WWOTDpost(Welsh_word, English_word, Word_class, Pronunciation, IPA, Mutation, Mutation_dict)


if __name__ == '__main__':
    main()

schedule.every().day.at("10:30").do(WWOTDpost)


while True:
    schedule.run_pending()
    time.sleep(1)