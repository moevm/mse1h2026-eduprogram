from src.rdf.dependencies import get_rdf, repository

if __name__ == "__main__":
    rdf = get_rdf()
    rdf.open_connection()
    print("Create repo RDF result:", rdf.create_repo(repository))
    rdf.close_connection()