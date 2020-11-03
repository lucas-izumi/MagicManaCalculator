import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE cards (
            card_id SERIAL PRIMARY KEY,
            card_name VARCHAR(255) NOT NULL,
            cmc INTEGER NOT NULL,
            mana_cost VARCHAR(255) NOT NULL
        )
        """)
    try:
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def close_conn():
    if conn is not None:
        conn.close()


def insert_card(card_name, cmc, mana_cost):
    sql = """INSERT INTO cards(card_name, cmc, mana_cost)
             VALUES(%s,%s,%s) RETURNING card_id;"""
    card_id = None
    try:
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (card_name, cmc, mana_cost,))
        # get the generated id back
        card_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return card_id


def get_card(card_name):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM cards WHERE card_name = %s", (card_name,))
        result_row = cur.fetchall()
        for row in result_row:
            print("Id = ", row[0], )
            print("Card Name = ", row[1])
            print("CMC  = ", row[2])
            print("Mana Cost  = ", row[3])
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)

    return result_row
