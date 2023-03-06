from bs4 import BeautifulSoup
import requests
import praw
import json
import mysql.connector
import boto3

def main(event, context):
    def close_connection():
        cursor.close()
        connection.close()

    def reset_database():
        reset_all = "update words set Used = false where Used = true"
        cursor.execute(reset_all)
        connection.commit()

    def db_query():
        sql = "SELECT * FROM words WHERE Used is False"
        cursor.execute(sql)
        connection.commit()
        my_result = cursor.fetchall()
        return my_result

    def used_word(singular):
        reset = f"UPDATE words\
                SET Used = True\
                WHERE welsh_word = '{singular}';"
        cursor.execute(reset)
        connection.commit()

    def soft_mutation(word):
        soft_dict = {
            "B": "F", "Ch": "Ch", "C": "G", "Dd": "Dd", "D": "Dd", "G": "",
            "Ll": "L", "Ph": "Ph", "P": "B", "M": "F", "Rh": "R", "Th": "Th", "T": "D"}
        for mutation in soft_dict:
            if word.startswith(mutation):
                if mutation != "G":
                    mutated_word = soft_dict[mutation] + word[(len(mutation)):]
                    return mutated_word
                elif mutation == "G":
                    if word in ["Golff", "Gêm"]:
                        return word
                    else:
                        mutated_word = word[1:]
                        return mutated_word
        return word

    def nasal_mutation(word):
        nasal_dict = {"B": "M", "Ch": "Ch", "C": "Ngh", "Dd": "Dd", "D": "N", "G": "Ng",
                      "P": "Mh", "Th": "Th", "T": "Nh"
                      }
        for mutation in nasal_dict:
            if word.startswith(mutation):
                mutated_word = nasal_dict[mutation] + word[(len(mutation)):]
                return mutated_word
        return word

    def aspirate_mutation(word):
        aspirate_dict = {"Ch": "Ch", "C": "Ch", "Ph": "Ph", "P": "Ph", "Th": "Th", "T": "Th"}
        for mutation in aspirate_dict:
            if word.startswith(mutation):
                mutated_word = aspirate_dict[mutation] + word[(len(mutation)):]
                return mutated_word
        return word

    def h_proth_mutation(word):
        mutable_letters = {"A", "E", "I", "O", "W", "Y"}
        do_not_mutate_list = {"A", "Ar", "I", "O", "W", "Y", "Yn"}
        if len(word.split()) == 1:
            if word not in do_not_mutate_list:
                if word[0] in mutable_letters:
                    mutated_word = "H" + word.lower()
                    return mutated_word
        return word

    def get_word(my_result):
        """ returns word from database """
        row = my_result[0]
        singular = row[1].capitalize()
        singular_translation = f'_{row[2].capitalize()}_'
        return singular, singular_translation

    def get_plural(my_result):
        """ returns plural of word from database"""
        row = my_result[0]
        if row[3] != 'null':
            plural = f'**{row[3].capitalize()}:**\n\n_{row[4].capitalize()}_'
        else:
            plural = ''
        return plural

    def get_gender(my_result):
        """ returns gender of word from database """
        row = my_result[0]
        if row[5] != 'null':
            gender = f'**Gender:** {row[5].capitalize()}'
        else:
            gender = ''
        return gender

    def get_soup(singular):
        """ returns wiktionary content for chosen word of the day, referenced as 'soup' """
        page = requests.get(f'https://en.wiktionary.org/wiki/{singular}')
        src = page.content
        soup = BeautifulSoup(src, 'html.parser')
        return soup

    def get_word_class(soup):
        """ checks for 'h3' section in html of 'soup' with a name equal to a word class and returns a variable,
            if word class is not referenced then the variable will be an empty string """
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

    def get_ipa(soup):
        """
        finds the IPA in the Pronunciation section returns it,
        if IPA is non-existent then return an empty string
        """
        ipa: list[str] = []
        try:
            for tag in soup.find(id='Welsh').parent.find_next_siblings('h3'):
                sibling = tag.find_next_sibling()
                if sibling.name == 'ul':
                    if sibling.find('ul'):
                        for li in sibling.find('ul').find_all('li'):
                            sibling.append(li)
                        sibling.find('ul').decompose()
                        for li in sibling.find_all('li'):
                            ipa.append(str(li.text.strip().replace('IPA(key)', '')))
                        ipa = '\n\n'.join(ipa).replace('(', '')
                        ipa = ipa.replace(')', '')
                        pronunciation = f'**Pronunciation:**\n\n{ipa}'
                        return pronunciation
        except AttributeError:
            pronunciation = ''
            return pronunciation

    def get_mutations(singular):
        """ Mutates the word according to the Welsh mutation rules and creates a table """
        mutations_table = f'''
**Mutations:**\n\n
|soft|aspirate|nasal|h_pros|
:--|:--|:--|:--|
|{soft_mutation(singular)}|{aspirate_mutation(singular)}|{nasal_mutation(singular)}|{h_proth_mutation(singular)}|'''
        return mutations_table

    def set_post_content(result):
        singular, singular_translation = get_word(result)
        plural = get_plural(result)
        gender = get_gender(result)
        soup = get_soup(singular)
        pronunciation = get_ipa(soup)
        mutation_table = get_mutations(singular)
        word_class = get_word_class(soup)
        reddit.validate_on_submit = True
        _self_text = f'{singular_translation}\n\n{plural}\n\n{gender}\n\n{word_class}\n\n{pronunciation}\n\n{mutation_table}\n\ncadw\'n heini!'
        _title = f'WWOTD: {singular.capitalize()}'
        used_word(singular)
        return _title, _self_text

    def reddit_post(_title, _self_text):
        reddit.subreddit('learnwelsh').submit(title, self_text, flair_id='a6c72efe-162e-11ec-adc4-b26f4ab04a7a')

    def get_secrets():
        reddit_secret_id = "reddit"
        db_secret_id = "database"
        region_name = "eu-central-1"

        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        get_reddit_secret_value_response = client.get_secret_value(
            SecretId=reddit_secret_id
        )
        get_db_secret_value_response = client.get_secret_value(
            SecretId=db_secret_id
        )

        reddit_secrets = json.loads(get_reddit_secret_value_response['SecretString'])
        db_secrets = json.loads(get_db_secret_value_response['SecretString'])

        return reddit_secrets, db_secrets


    reddit_secret, db_secret = get_secrets()

    hostname = db_secret["host"]
    database = db_secret["dbname"]
    username = db_secret["username"]
    password = db_secret["password"]
    port = db_secret["port"]

    connection = mysql.connector.connect(host=hostname, database=database, user=username, password=password, port=port)
    cursor = connection.cursor(buffered=True)

    reddit = praw.Reddit(
        client_id=reddit_secret["client_id"],
        client_secret=reddit_secret["client_secret"],
        user_agent=reddit_secret["user_agent"],
        username=reddit_secret["username"],
        password=reddit_secret["password"]
    )

    results = db_query()
    if not results:
        reset_database()
        results = db_query()
    title, self_text = set_post_content(results)
    reddit_post(title, self_text)
    close_connection()
