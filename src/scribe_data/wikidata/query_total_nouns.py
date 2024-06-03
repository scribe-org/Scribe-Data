"""
Derives the total nouns available for a language on Wikidata by querying the count.
"""

import urllib

from SPARQLWrapper import JSON, SPARQLWrapper


def query_total_nouns(language):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)

    # SPARQL query template
    query_template = """
    SELECT (COUNT(DISTINCT ?lexeme) as ?total)
    WHERE {{
        VALUES ?language {{ wd:{} }}
        ?lexeme dct:language ?language ;
            wikibase:lexicalCategory ?category .
        FILTER(?category IN (wd:Q1084, wd:Q147276))
    }}
    """

    # Replace {} in the query template with the language value.
    query = query_template.format(language)

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = None
    try:
        results = sparql.query().convert()
    except urllib.error.HTTPError as err:
        print(f"HTTPError with query_total_nouns for {language}: {err}")

    if results is not None:
        return int(results["results"]["bindings"][0]["total"]["value"])

    else:
        return results
