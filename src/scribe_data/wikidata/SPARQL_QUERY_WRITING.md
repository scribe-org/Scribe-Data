# SPARQL Query Writing for Wikidata Lexemes
Wikidata is a free and open knowledge base that provides structured data to support a wide range of applications, including linguistic data through lexemes. SPARQL queries enable powerful searches and extraction of specific data from this repository, such as lexeme forms and their grammatical features.

To learn more, visit the [Wikidata Guide](https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md).
This document outlines how to write effective SPARQL queries for Wikidata lexemes, with a focus on guiding new contributors in identifying lexeme forms and using them in queries to return unique values.

## Contents
1. [Key Steps for Querying Wikidata Lexemes](#key-steps-for-querying-wikidata-lexemes)
2. [Example Query](#example-query)
   - [Step 1: Run the Query](#step-1-run-the-query)
   - [Step 2: Analyze the Results](#step-2-analyze-the-results)
   - [Step 3: Identify Forms](#step-3-identify-forms)
   - [Step 4: Construct Queries for Forms](#step-4-construct-queries-for-forms)
3. [Best Practices](#best-practices)

---

## Key Steps for Querying Wikidata Lexemes

1. Run the base query for the chosen language and lexical category on the [Wikidata Query Service](https://query.wikidata.org)
2. Use the result to identify forms associated with the language
3. Use the identified forms to create optional selections in the query that return unique values.

---

## Example Query

Let’s consider an example using Slovak adjectives. The base query returns the Wikidata lexeme ID and lemma. Note that you can easily modify this base query to point to another language (e.g Italian:Q652) or another lexical category (e.g verb:Q24905).

### Step 1: Run the Query

1. Navigate to the [Wikidata Query Service](https://query.wikidata.org).
2. Enter and run the following SPARQL query, which returns all Slovak adjectives:

    ```bash
    # tool: scribe-data
    # All Slovak (Q9058) adjectives.
    # Enter this query at https://query.wikidata.org/.

    SELECT
      ?lexeme
      (REPLACE(STR(?lexeme), "http://www.wikidata.org/entity/", "") AS ?lexemeID)
      ?adjective

    WHERE {
      ?lexeme dct:language wd:Q9058 ;
        wikibase:lexicalCategory wd:Q34698 ;
        wikibase:lemma ?adjective .
    }
    ```

### Step 2: Analyze the Results

1. Click on the first result (which could be any word) to view the lexeme page. For example, you might land on:
   - [wikidata.org/wiki/Lexeme:L238355](https://wikidata.org/wiki/Lexeme:L238355)
2. This lexeme represents the Slovak adjective "slovenský" (meaning "Slovak").

### Step 3: Identify Forms

On the lexeme page, scroll down to find the various forms associated with Slovak adjectives, such as:

- **Gender**: Masculine vs. Feminine
- **Number**: Singular vs. Plural
- **Case**: Nominative, Accusative, etc.

The forms vary depending on the language and the lexical category. For some languages, forms may not exist. Be sure to check for these before proceeding.

### Step 4: Construct Queries for Forms

To construct queries for specific forms:

- Identify the relevant properties for a form (e.g., masculine, nominative case, singular).
- Locate the Wikidata QIDs for these properties. You can get the QID of a form by hovering over it on the Wikidata lexeme page.
- Use these QIDs in your SPARQL query, incorporating them with optional selections to ensure unique and accurate results.

For example, if you're querying for Estonian adjectives, and you want to retrieve forms in the ***Nominative plural***, you could use the following optional selection:

```bash
OPTIONAL {
    ?lexeme ontolex:lexicalForm ?nominativePluralForm .
    ?nominativePluralForm ontolex:representation ?nominativePlural ;
      wikibase:grammaticalFeature wd:Q131105 ; # Nominative case
      wikibase:grammaticalFeature wd:Q146786 . # Plural
  }
  ```

This optional selection retrieves forms that are **Nominative** and **Plural**.

For a detailed example involving multiple forms, see:

[src/scribe_data/language_data_extraction/Estonian/adverbs/query_adverbs_1.sparql](https://github.com/scribe-org/Scribe-Data/blob/c64ea865531ff2de7fe493266d0be0f6be7e5518/src/scribe_data/language_data_extraction/Estonian/adverbs/query_adverbs_1.sparql)


---

## Best Practices

- **Understand Lexeme Structures**: Study how lexemes and their properties are structured in Wikidata for each language.
- **Use Optional Selections**: Leverage optional selections in queries to account for various grammatical properties without generating duplicates.
- **Verify Forms**: Always verify the forms listed on the lexeme page to ensure you're capturing all variations in your query results.
- **Test Your Query**: Ensure that your query runs on the [Wikidata Query Service](https://query.wikidata.org) without errors.
