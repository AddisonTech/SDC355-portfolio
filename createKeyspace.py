# =============================================================
# Name:              Addison (addsmi1720)
# Date:              August 16, 2026
# Assignment:        3.3 Guided Practice: Python Application
#                    Accessing a Column Family Database
# Objective:         Connect to a local Cassandra cluster, build the
#                    ReviewData keyspace and its tables, import review
#                    data from a JSON file, then run CRUD operations
#                    against that data before dropping the keyspace.
# =============================================================

import json
from cassandra.cluster import Cluster

# ***CREATE SECTION***
# Notify when script is starting
print("Connecting to local Cassandra database...")

# Connect to a local Cassandra cluster
cluster = Cluster()
session = cluster.connect()

# Create a keyspace and connect to it
keyspace = '''
    CREATE KEYSPACE IF NOT EXISTS ReviewData WITH replication =
    {'class':'SimpleStrategy','replication_factor':1};
    '''
session.execute(keyspace)

query = 'USE ReviewData;'
session.execute(query)

# Create a table within the keyspace
newTable = '''
    CREATE TABLE IF NOT EXISTS Reviews(
        ReviewID text PRIMARY KEY,
        ReviewerID text,
        ProductID text,
        Category text,
        Stars int,
        Title text,
        Content text,
        Language text
    );
    '''
session.execute(newTable)

# Create a table within the keyspace
newTable = '''
    CREATE TABLE IF NOT EXISTS Categories(
        ProductID text,
        Category text,
        Stars int,
        PRIMARY KEY((Category), Stars)
    );
    '''
session.execute(newTable)

# Import data from JSON file
print("Importing data from file...")

for line in open('dataset_en_dev.json', 'r'):
    dataSet = json.loads(line)

    # Prepare INSERT statement to add in new data into Reviews
    insertReviewsPrep = '''
        INSERT INTO Reviews (ReviewID, ReviewerID, ProductID,
        Category, Stars, Title, Content, Language)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
        '''

    # Execute INSERT statement using the JSON dataset
    session.execute(insertReviewsPrep, [dataSet["review_id"], dataSet["reviewer_id"],
                    dataSet["product_id"], dataSet["product_category"], int(dataSet["stars"]),
                    dataSet["review_title"], dataSet["review_body"], dataSet["language"]])

    # Prepare INSERT statement to add in new data into Categories
    insertCategoriesPrep = '''
        INSERT INTO Categories (Category, Stars, ProductID)
        VALUES(%s, %s, %s);
        '''

    # Execute INSERT statement using the JSON dataset
    session.execute(insertCategoriesPrep, [dataSet["product_category"],
                    int(dataSet["stars"]), dataSet["product_id"]])

# Notify when data import is complete
print("Data imported successfully!")

# ***READ SECTION***
# Count the number of rows in the Reviews table
query = 'SELECT COUNT(*) FROM Reviews;'
rowCount = session.execute(query)

# Display the number of rows in the Reviews table
print("Number of rows: " + str(rowCount.one()))

# Count the number of 5 star reviews in the Reviews table
query = 'SELECT COUNT(*) FROM Reviews WHERE stars = 5 ALLOW FILTERING;'
rowCount = session.execute(query)
print("Number of 5 star reviews: " + str(rowCount.one()))

# Display 10 product categories
query = 'SELECT DISTINCT Category FROM Categories LIMIT 10';
results = session.execute(query)
print("\n10 Product Categories: ")
for row in results:
    print(row)

# Display the number of 4 and 5 star reviews for wireless categorized products
query = '''SELECT COUNT(*) FROM Reviews WHERE Category = 'wireless'
        AND stars > 3 ALLOW FILTERING;'''
results = session.execute(query)
print("\nNumber of 4 and 5 star reviews of wireless products: " + str(results.one()))

# Display the min and max number of stars for a specific product
query = '''SELECT MIN(stars), MAX(stars) FROM Reviews WHERE
        productID = 'product_en_0947733' ALLOW FILTERING;'''
rowCount = session.execute(query)
print("\nMinimum and maximum stars for product 0947733: ")
print(rowCount.one())

# ***UPDATE SECTION***
# Remove the Language column from the Reviews table
print("\nRemoving Language from the Reviews table...")
query = 'ALTER TABLE Reviews DROP language;'
results = session.execute(query)
print("Complete!")

# ***DELETE SECTION***
# Remove all 1 star reviews (rows) from the pc category
query = '''DELETE FROM Categories WHERE Stars = 1 and Category = 'pc';'''
print("\nRemoving 1 star reviews from pc products...")
results = session.execute(query)
print("Complete!")

# Remove the ProductID (data) for any 2 star reviews from the pc category
query = '''DELETE ProductID FROM Categories WHERE Stars = 2 and Category = 'pc';'''
print("\nRemoving the ProductID from any 2 star pc reviews...")
results = session.execute(query)
print("Complete!")

# Remove the Categories table
print("\nRemoving Categories table...")
query = 'DROP TABLE IF EXISTS Categories;'
results = session.execute(query)
print("Complete!")

# Remove the ReviewData keyspace
print("Removing ReviewData Keyspace...")
query = 'DROP KEYSPACE IF EXISTS ReviewData;'
results = session.execute(query)
print("Complete!")
