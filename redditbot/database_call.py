import os
import mysql.connector

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


def DB_query():
    my_cursor = mydb.cursor(buffered=True)
    sql = "SELECT * FROM words WHERE USED is False"
    my_cursor.execute(sql)
    mydb.commit()
    my_result = my_cursor.fetchall()
    return my_result


def used_word(singular):
    cursor = mydb.cursor(buffered=True)
    reset = f"UPDATE words\
            SET Used = True\
            WHERE Singular = '{singular}';"
    cursor.execute(reset)
    mydb.commit()


if __name__ == '__main__':
    pass
