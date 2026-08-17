# =============================================================
# Name:              Addison (addsmi1720)
# Date:              August 16, 2026
# Assignment:        3.6 Guided Practice: Python Application
#                    Securing a Cassandra Database
# Objective:         Connect to a local Cassandra cluster using SASL
#                    PlainText authentication, build a secured keyspace
#                    and table, insert a record identified by a UUID, and
#                    read that record back to confirm the authenticated
#                    session can access the secured data.
# =============================================================

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from uuid import uuid4
from os import getlogin

# Authentication Details
auth = PlainTextAuthProvider(username="cassUser", password="cassPass")

# Connect to Cassandra with Authentication
cluster = Cluster(["localhost"], port=9042, auth_provider=auth)
session = cluster.connect()

# Create a new keyspace
query = """
    CREATE KEYSPACE IF NOT EXISTS SecuredKeyspace WITH
    REPLICATION = { 'class':'SimpleStrategy',
    'replication_factor':1 };
    """
session.execute(query)

query = "USE SecuredKeyspace;"
session.execute(query)

# Create a new table
query = """
    CREATE TABLE IF NOT EXISTS SecuredTable
    (id UUID PRIMARY KEY, data TEXT);
    """
session.execute(query)

# Insert data into the table
user = getlogin()
dataID = uuid4()
data = user
data += ", this data is secured with SASL authentication!"

query = "INSERT INTO SecuredTable (id, data) VALUES (%s, %s);"
session.execute(query, (dataID, data))

# Query the data from the table
query = "SELECT * FROM SecuredTable;"
result = session.execute(query)

for row in result:
    print(row.id, row.data)

# Close the connection and cluster
session.shutdown()
cluster.shutdown()
