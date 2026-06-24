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
            cost_row = df[df['Technology'] == t]
            cost = int(cost_row['Science_cost'].iloc[0]) if not cost_row.empty else 0
            tx.run("""
                MERGE (a:Technology {name: $tech})
                MERGE (b:Technology {name: $target})
                MERGE (a)-[r:LEADS_TO]->(b)
                SET r.cost = $cost
            """, tech=tech, target=t, cost=cost)
        

def setup(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    print("Dane załadowane!")

with driver.session() as session:
    session.execute_write(setup)
    session.execute_write(create_techs)

driver.close()