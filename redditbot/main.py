import schedule
import time
from redditbot.reddit_call import *
from redditbot.database_call import DB_query, used_word, reset_database
from config import config as cfg
cfg_dict = cfg.config_dict


def redditbot_run():
    result = DB_query()
    if not result:
        reset_database()
        redditbot_run()
    Singular, SingularTranslation = get_word(result)
    Plural = get_plural(result)
    Gender = get_gender(result)
    soup = get_soup(Singular)
    pronunciation = get_IPA(soup)
    mutation_table = get_mutations(Singular)
    word_class = get_word_class(soup)
    WWOTDpost(word_class, pronunciation, mutation_table, Singular, SingularTranslation, Plural, Gender)
    used_word(Singular)


if __name__ == '__main__':
    schedule.every().day.at(f"{cfg_dict['Main']['Schedule']}").do(redditbot_run)

    while True:
        schedule.run_pending()
        time.sleep(1)
