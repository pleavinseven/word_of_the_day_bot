import schedule
import time
from redditbot.reddit_call import get_soup, get_IPA, get_mutations, get_word_class, WWOTDpost, get_words
from redditbot.database_call import DB_query, used_word, reset_database


def redditbot_run():
    result = DB_query()
    if not result:
        reset_database()
        redditbot_run()
    Singular, SingularTranslation, Plural, Gender = get_words(result)
    soup = get_soup(Singular)
    pronunciation = get_IPA(soup)
    mutation_table = get_mutations(Singular)
    word_class = get_word_class(soup)
    WWOTDpost(word_class, pronunciation, mutation_table, Singular, SingularTranslation, Plural, Gender)
    used_word(Singular)


if __name__ == '__main__':
    schedule.every().day.at("10:30").do(redditbot_run)

    while True:
        schedule.run_pending()
        time.sleep(1)
