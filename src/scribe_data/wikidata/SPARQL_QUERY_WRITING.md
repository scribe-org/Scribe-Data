# SPARQL Query Writing for Wikidata Lexemes

[Wikidata](https://www.wikidata.org/) is a free and open knowledge base that provides structured data to support a wide range of applications, including linguistic data through lexemes. SPARQL queries enable powerful searches and extraction of specific data from this repository, such as lexeme forms and their grammatical features.

If you're totally new to [Wikidata](https://www.wikidata.org/) and SPARQL, we'd suggest you read the [Scribe community Wikidata Guide](https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md). After that you'll be ready to follow along here.

<a id="contents"></a>

## **Contents**

1. [Key Steps](#key-steps)
2. [Example Process](#example-process)
   - [Exploration Query](#exploration-query)
   - [Identify Forms](#identify-forms)
   - [Select Forms](#select-forms)
3. [Example Query](#example-query)
4. [Best Practices](#best-practices)

<a id="key-steps"></a>

## Key Steps [`⇧`](#contents)

The general steps to creating a SPARQL query of [Wikidata](https://www.wikidata.org/) lexemes for Scribe-Data are:

1. Run the base query for the chosen language and lexical category on the [Wikidata Query Service](https://query.wikidata.org)
2. Use the result to identify forms associated with the language
3. Create optional selections of the identified forms via all of their properties to

At the end the goal is to have a query that returns unique values for all lexemes for the given language and word type.

<a id="example-process"></a>

## Example Process [`⇧`](#contents)

Let’s consider an example using Spanish adjectives. The base query returns the [Wikidata](https://www.wikidata.org/) lexeme and lemma so we can inspect the forms. Note that you can easily modify this base query to point to another language (e.g [Italian (Q652)](https://www.wikidata.org/wiki/Q652)) or another lexical category (e.g [verb (Q24905)](<](https://www.wikidata.org/wiki/Q652)>)).

<a id="exploration-query"></a>

### Exploration Query [`⇧`](#contents)

1. Navigate to the [Wikidata Query Service](https://query.wikidata.org)
2. Enter and run the following SPARQL query, which returns all Spanish adjectives:

   ```sparql
   SELECT
     ?lexeme  # unique ID for the data entry
     ?adjective  # lemma or label of the ID

   WHERE {
     ?lexeme dct:language wd:Q1321 ;  # Spanish language
       wikibase:lexicalCategory wd:Q34698 ;  # adjectives
       wikibase:lemma ?adjective .
   }
   ```

<a id="identify-forms"></a>

### Identify Forms [`⇧`](#contents)

Click on the first result (which could be any Spanish adjective) to view the lexeme page. For example, you might land on [wikidata.org/wiki/Lexeme:L55756](https://wikidata.org/wiki/Lexeme:L55756). This lexeme represents the Spanish adjective "español" meaning "Spanish".

On the lexeme page, scroll down to find the various forms associated with Spanish adjectives, such as:

- **Gender**: [masculine](https://www.wikidata.org/wiki/Q499327) vs. [feminine](https://www.wikidata.org/wiki/Q1775415)
- **Number**: [singular](https://www.wikidata.org/wiki/Q110786) vs. [plural](https://www.wikidata.org/wiki/Q146786)

The forms vary depending on the language and the lexical category. For other languages there could be forms for cases (nominative, accusative, etc) or there could be other genders (neuter, common, etc). Forms may not exist for some languages, but please check a few lexemes before sending along a query that just returns the lexeme ID and the lemma. For this example we'll look into the combination of each of the above two properties.

<a id="select-forms"></a>

### Select Forms [`⇧`](#contents)

To construct queries for specific forms:

- Identify the relevant properties for a form (e.g., masculine + singular)
- Locate the [Wikidata](https://www.wikidata.org/) QIDs for these properties
  - You can get the QID of a property by opening the link in a new page so it's easy for you to copy it
- Use these QIDs in your SPARQL query, incorporating them with optional selections to ensure unique and accurate results
  - We specifically do an `OPTIONAL` selection so that lexemes that don't have the form - either because the data is incomplete or maybe it just doesn't exist - will also be returned

For example, if you wanted to retrieve form for feminine singular, you could use the following optional selection:

```sparql
OPTIONAL {
  # A unique identifier for the form defined below.
  ?lexeme ontolex:lexicalForm ?feminineSingularForm .
  # Convert it to its literal representation that we'll return.
  ?feminineSingularForm ontolex:representation ?feminineSingular ;
    # This form is defined by feminine and singular QIDs.
    wikibase:grammaticalFeature wd:Q1775415, wd:Q110786 .
}
```

Putting this optional selection in your query and adding `?feminineSingular` to your return statement in the query above will retrieve the given forms for all of the lexemes.

<a id="example-query"></a>

## Example Query [`⇧`](#contents)

The following is an example query for Spanish adjectives. The full query is a bit more complex as there are more forms possible in Spanish adjectives, but this should give you an impression of a query that returns all possible forms for a word type of a language:

```sparql
SELECT
  (REPLACE(STR(?lexeme), "http://www.wikidata.org/entity/", "") AS ?lexemeID)
  ?adjective
  ?femSingular
  ?femPlural
  ?masSingular
  ?masPlural

WHERE {
  ?lexeme dct:language wd:Q1321 ;
    wikibase:lexicalCategory wd:Q34698 ;
    wikibase:lemma ?adjective .

  # MARK: Feminine

  OPTIONAL {
    ?lexeme ontolex:lexicalForm ?femSingularForm .
    ?femSingularForm ontolex:representation ?femSingular ;
      wikibase:grammaticalFeature wd:Q1775415, wd:Q110786 .
  }

  OPTIONAL {
    ?lexeme ontolex:lexicalForm ?femPluralForm .
    ?femPluralForm ontolex:representation ?femPlural ;
      wikibase:grammaticalFeature wd:Q1775415, wd:Q146786 .
  }

  # MARK: Masculine

  OPTIONAL {
    ?lexeme ontolex:lexicalForm ?masSingularForm .
    ?masSingularForm ontolex:representation ?masSingular ;
      wikibase:grammaticalFeature wd:Q499327, wd:Q110786 .
  }

  OPTIONAL {
    ?lexeme ontolex:lexicalForm ?masPluralForm .
    ?masPluralForm ontolex:representation ?masPlural ;
      wikibase:grammaticalFeature wd:Q499327, wd:Q146786 .
  }
}
```

We return the `?lexemeID` so that Scribe and other downstream data reusers can easily identify the lexeme that this data came from. From there we also get the given forms so that these can be used for all kinds of language based applications.

<a id="best-practices"></a>

## Best Practices [`⇧`](#contents)

- **Understand Lexeme Structures**: Study how lexemes and their forms are structured in [Wikidata](https://www.wikidata.org/) for each language
- **Verify Forms**: Always verify the forms listed on the lexeme page to ensure you're capturing all variations in your query results
- **Use Optional Selections**: Leverage optional selections in queries to account for various grammatical properties without data loss
- **No Complex Operations**: Please do not include `ORDER BY` or `SELECT DISTINCT` as these operations make the queries take longer and don't add value to the output
- **Filter Out Results**: Using `FILTER NOT EXISTS` can make sure that forms are not overlapping
- **MARK Your Queries**: Including `MARK:` comments allows easy navigation of queries by adding labels to the minimaps in many development IDEs
- **Identify Scribe-Data**: [Wikidata](https://www.wikidata.org/) is a common resource, so please add the following to the top of all queries to assure that people can see our impact on the servers

  ```
  # tool: scribe-data
  # All LANGUAGE_NAME (LANGUAGE_QID) DATA_TYPE (DATA_TYPE_QID) and the given forms.
  # Enter this query at https://query.wikidata.org/.
  ```

- **Assure Unique Results**: Your query should return only one entry for each lexeme
- **Test Your Query**: Ensure that your query runs on the [Wikidata Query Service](https://query.wikidata.org) without errors

Thanks for your interest in expanding Scribe-Data's Wikidata queries! We look forward to working with you :)
