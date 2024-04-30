from SPARQLWrapper import SPARQLWrapper, JSON

def get_total_nouns(language):
    # Endpoint
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)

    # SPARQL query template
    query_template = """
    SELECT (COUNT(DISTINCT ?lexeme) as ?total)
    WHERE {{
      VALUES ?language {{ wd:{} }}
      ?lexeme a ontolex:LexicalEntry ;
              dct:language ?language ;
              wikibase:lexicalCategory ?category .
      FILTER(?category IN (wd:Q1084, wd:Q147276))
    }}
    """

    # Replace {} in the query template with the language value
    query = query_template.format(language)

    # query
    sparql.setQuery(query)

    # Set the query return format
    sparql.setReturnFormat(JSON)

    # Execute the query and parse the results
    results = sparql.query().convert()

    # Extract the total count from the results
    total_nouns = int(results["results"]["bindings"][0]["total"]["value"])

    return total_nouns