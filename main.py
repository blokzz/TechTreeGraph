from neo4j import GraphDatabase
import dotenv
import os
import data

dotenv.load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

if not all([uri, user, password]):
    raise ValueError("brakuje danych w pliku .env")

driver = GraphDatabase.driver(uri, auth=(user, password))

df = data.preprocess_data()
def create_techs(tx):
    for _, row in df.iterrows():
        tech = row['Technology']
        targets = row['Leads to']
        for t in targets:
            tx.run("""
                MERGE (a:Technology {name: $tech})
                MERGE (b:Technology {name: $target})
                MERGE (a)-[:LEADS_TO]->(b)
            """, tech=tech, target=t)
        

def setup(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    print("Dane załadowane!")

with driver.session() as session:
    session.execute_write(setup)
    session.execute_write(create_techs)

driver.close()