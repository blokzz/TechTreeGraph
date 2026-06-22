from neo4j import GraphDatabase
import dotenv
import os

dotenv.load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

if not all([uri, user, password]):
    raise ValueError("brakuje danych w pliku .env")

driver = GraphDatabase.driver(uri, auth=(user, password))

def setup(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    print("Dane załadowane!")

with driver.session() as session:
    session.execute_write(setup)

driver.close()