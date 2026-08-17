# =============================================================
# Name:              Addison (addsmi1720)
# Date:              August 16, 2026
# Assignment:        3.5 Performance Assessment: Python Application
#                    Accessing a Column Family Database
# Purpose:           A menu driven Python application that performs CRUD
#                    operations against a Cassandra column family database.
#                    The program builds the Amazon keyspace, creates the
#                    Reviews and ProductCategories tables, imports review
#                    data from a JSON file, and then lets the user query,
#                    alter, and drop that data from a menu.
# =============================================================

import json
from cassandra.cluster import Cluster

JSON_FILE = 'dataset_en_dev.json'


# *Connect to the local Cassandra cluster
def connect_to_cassandra():
    print("Connecting to local Cassandra database...")
    cluster = Cluster()
    session = cluster.connect()
    return cluster, session


# *Create the Amazon keyspace and both tables
def create_keyspace_and_tables(session):
    print("Creating the Amazon keyspace...")
    session.execute('''
        CREATE KEYSPACE IF NOT EXISTS Amazon WITH replication =
        {'class':'SimpleStrategy','replication_factor':1};
        ''')
    session.execute('USE Amazon;')

    print("Creating the Reviews table...")
    session.execute('''
        CREATE TABLE IF NOT EXISTS Reviews(
            review_id text PRIMARY KEY,
            product_id text,
            reviewer_id text,
            stars int,
            review_body text,
            review_title text,
            product_category text
        );
        ''')

    # ProductCategories is keyed on category so the count queries below can
    # filter on stars without a full table scan
    print("Creating the ProductCategories table...")
    session.execute('''
        CREATE TABLE IF NOT EXISTS ProductCategories(
            product_category text,
            stars int,
            product_id text,
            language text,
            PRIMARY KEY((product_category), stars, product_id)
        );
        ''')


# *Insert the JSON data into both tables
def import_data(session):
    print("Importing data from file...")

    insert_reviews = session.prepare('''
        INSERT INTO Reviews(review_id, product_id, reviewer_id, stars,
        review_body, review_title, product_category)
        VALUES(?, ?, ?, ?, ?, ?, ?);
        ''')

    insert_categories = session.prepare('''
        INSERT INTO ProductCategories(product_category, stars, product_id, language)
        VALUES(?, ?, ?, ?);
        ''')

    for line in open(JSON_FILE, 'r'):
        record = json.loads(line)

        session.execute(insert_reviews, [record["review_id"], record["product_id"],
                        record["reviewer_id"], int(record["stars"]),
                        record["review_body"], record["review_title"],
                        record["product_category"]])

        session.execute(insert_categories, [record["product_category"],
                        int(record["stars"]), record["product_id"],
                        record["language"]])

    print("Data imported successfully!\n")


# *Menu option 1: show every distinct product category
def display_categories(session):
    results = session.execute('SELECT DISTINCT product_category FROM ProductCategories;')
    print("\nProduct Category List:")
    for row in results:
        print(row)


# *Menu option 2: count the 4 star and higher reviews in a category
def display_high_star_count(session):
    category = input("\nEnter a product category: ").strip().lower()
    query = session.prepare('''
        SELECT COUNT(*) FROM ProductCategories
        WHERE product_category = ? AND stars > 3;
        ''')
    result = session.execute(query, [category])
    print("Number of 4 star and higher reviews for " + category + ": " + str(result.one()))


# *Menu option 3: count the 1 star reviews in a category
def display_low_star_count(session):
    category = input("\nEnter a product category: ").strip().lower()
    query = session.prepare('''
        SELECT COUNT(*) FROM ProductCategories
        WHERE product_category = ? AND stars = 1;
        ''')
    result = session.execute(query, [category])
    print("Number of 1 star reviews for " + category + ": " + str(result.one()))


# *Menu option 4: run a CQL SELECT statement typed in by the user
def run_user_query(session):
    query = input("\nEnter a CQL SELECT statement: ").strip()

    if not query.lower().startswith('select'):
        print("Only SELECT statements are allowed here.")
        return

    try:
        results = session.execute(query)
        print()
        for row in results:
            print(row)
    except Exception as error:
        print("Query failed: " + str(error))


# *Menu option 5: add or remove a column on either table
def alter_table(session):
    table = input("\nWhich table, Reviews or ProductCategories? ").strip()
    action = input("Add or Remove a column? ").strip().lower()
    column = input("Column name: ").strip()

    try:
        if action == 'add':
            data_type = input("Column data type (text, int): ").strip()
            session.execute('ALTER TABLE ' + table + ' ADD ' + column + ' ' + data_type + ';')
            print("Added " + column + " to " + table + ".")
        elif action == 'remove':
            session.execute('ALTER TABLE ' + table + ' DROP ' + column + ';')
            print("Removed " + column + " from " + table + ".")
        else:
            print("Enter either Add or Remove.")
    except Exception as error:
        print("Alter failed: " + str(error))


# *Menu option 6: drop both tables
def drop_tables(session):
    print("\nRemoving the Reviews table...")
    session.execute('DROP TABLE IF EXISTS Reviews;')
    print("Complete!")

    print("Removing the ProductCategories table...")
    session.execute('DROP TABLE IF EXISTS ProductCategories;')
    print("Complete!")


# *Menu option 7: drop the keyspace
def drop_keyspace(session):
    print("\nRemoving the Amazon keyspace...")
    session.execute('DROP KEYSPACE IF EXISTS Amazon;')
    print("Complete!")


# *Display the menu and return the user's choice
def show_menu():
    print("\nType in a number and press enter to execute the menu option.")
    print("1. Display product category list")
    print("2. Display high (4+) star review count")
    print("3. Display low (1) star review count")
    print("4. Enter a query")
    print("5. Add/Remove table columns")
    print("6. Delete tables")
    print("7. Delete keyspace")
    print("8. Exit the program")
    return input().strip()


# *Main program loop
def main():
    cluster, session = connect_to_cassandra()
    create_keyspace_and_tables(session)
    import_data(session)

    while True:
        choice = show_menu()

        if choice == '1':
            display_categories(session)
        elif choice == '2':
            display_high_star_count(session)
        elif choice == '3':
            display_low_star_count(session)
        elif choice == '4':
            run_user_query(session)
        elif choice == '5':
            alter_table(session)
        elif choice == '6':
            drop_tables(session)
        elif choice == '7':
            drop_keyspace(session)
        elif choice == '8':
            print("\nExiting the program...")
            cluster.shutdown()
            break
        else:
            print("\nThat is not a valid menu option. Enter a number from 1 to 8.")


main()
