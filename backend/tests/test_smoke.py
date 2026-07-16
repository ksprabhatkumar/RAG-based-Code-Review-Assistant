import chromadb
from fastapi.testclient import TestClient
from api.main import app
from ingestion.parser import parse_code

client = TestClient(app)

def test_fastapi_health():
    """Verify FastAPI boots."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_tree_sitter_parsing():
    """Verify Tree-sitter parses a file and returns a non-empty AST."""
    sample_code = """
def hello_world():
    print("Hello, RAG!")
"""
    tree = parse_code(sample_code)
    # The root node of a Python file should be a 'module'
    assert tree.root_node.type == "module"
    # It should have children (the function definition)
    assert len(tree.root_node.children) > 0

def test_chroma_embedded():
    """Verify Chroma can boot in-memory, store, and retrieve a document."""
    chroma_client = chromadb.EphemeralClient() # In-memory for testing
    collection = chroma_client.create_collection(name="smoke_test")
    
    collection.add(
        documents=["Use descriptive variable names", "Do not use global variables"],
        ids=["rule_1", "rule_2"]
    )
    
    results = collection.query(
        query_texts=["naming variables"],
        n_results=1
    )
    
    assert len(results["documents"][0]) == 1
    assert "Use descriptive variable names" in results["documents"][0][0]
