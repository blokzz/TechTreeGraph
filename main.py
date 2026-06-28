from neo4j import GraphDatabase
import dotenv
import os
import data
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

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
        

def get_all_techs():
    with driver.session() as s:
        result = s.run("MATCH (t:Technology) RETURN t.name AS name ORDER BY name")
        return [r["name"] for r in result]


def setup(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    print("Dane załadowane!")

with driver.session() as session:
    session.execute_write(setup)
    session.execute_write(create_techs)


def get_path(start, end):
    with driver.session() as s:
        result = s.run("""
            MATCH path = shortestPath(
                (a:Technology {name: $start})-[:LEADS_TO*]->(b:Technology {name: $end})
            )
            RETURN [n IN nodes(path) | n.name] AS nodes
        """, start=start, end=end)
        record = result.single()
        return record["nodes"] if record else []


def get_full_graph():
    with driver.session() as s:
        result = s.run("MATCH (a:Technology)-[:LEADS_TO]->(b:Technology) RETURN a.name AS a, b.name AS b")
        return [(r["a"], r["b"]) for r in result]


def render_graph(edges, highlighted_path=None):
    net = Network(height="650px", width="100%", bgcolor="#1e1e1e", font_color="white", directed=True)
    net.barnes_hut(gravity=-3000, spring_length=120)
    
    highlighted = set(highlighted_path or [])
    highlight_edges = set()
    if highlighted_path:
        for i in range(len(highlighted_path) - 1):
            highlight_edges.add((highlighted_path[i], highlighted_path[i+1]))
    
    nodes = set()
    for a, b in edges:
        nodes.add(a); nodes.add(b)
    
    for n in nodes:
        if n in highlighted:
            net.add_node(n, label=n, color="#ff4444", size=25)
        else:
            net.add_node(n, label=n, color="#3a86ff", size=15)
    
    for a, b in edges:
        if (a, b) in highlight_edges:
            net.add_edge(a, b, color="#ff4444", width=4)
        else:
            net.add_edge(a, b, color="#666666", width=1)
    
    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        return f.read()

st.set_page_config(page_title="Civ VI Tech Tree", layout="wide")
st.title("🏛️ Civ VI Tech Tree Explorer")

techs = get_all_techs()

col1, col2 = st.columns(2)
with col1:
    start = st.selectbox("Z technologii:", techs, index=techs.index("Pottery") if "Pottery" in techs else 0)
with col2:
    end = st.selectbox("Do technologii:", techs, index=techs.index("Computers") if "Computers" in techs else len(techs)-1)

if st.button("Znajdź ścieżkę", type="primary"):
    path = get_path(start, end)
    if not path:
        st.error(f"Nie ma drogi z {start} do {end}")
    else:
        st.success(f"Ścieżka ({len(path)-1} kroków): {' → '.join(path)}")
        st.session_state["path"] = path

edges = get_full_graph()
html = render_graph(edges, st.session_state.get("path"))
components.html(html, height=700)