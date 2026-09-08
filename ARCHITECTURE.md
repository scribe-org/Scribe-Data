# [Architecture](https://github.com/scribe-org/Scribe-Data/blob/main/ARCHITECTURE.md)

This markdown file documents the architecture for the Scribe-Data CLI - including all processes and the external systems and sources with which it interacts. The diagram details the CLI [convert](./src/scribe_data/cli/convert/), [download](./src/scribe_data/cli/download/), [get](./src/scribe_data/cli/get.py), [list](./src/scribe_data/cli/list/), [total](./src/scribe_data/cli/total/) and [contact](./src/scribe_data/cli/contracts/) commands, with [interactive](./src/scribe_data/cli/interactive/) being a command itself and also an option within other commands via the `--interactive` (`-i`) option.

CLI outputs that are used in multiple flows appear as nodes outside of any nodes for clarity. As the file is meant to be a living document, edits are welcome to expand and update it!

> [!NOTE]
> You can see the architecture diagram for all of [Scribe](https://github.com/scribe-org) [here](https://github.com/scribe-org/Organization/blob/main/ARCHITECTURE.md).

## Architecture Diagram

```mermaid
graph LR
    %% CLI

    DATA[[Scribe-Data CLI]]
    LEXEME_QUERIES[Internal generated\nlexeme queries]
    PROFANITY_QUERY[Internal template\nprofanity query]
    TOTAL_QUERY[Internal template\ntotal query]
    CONTRACTS(Internal data contracts)

    %% Data sources

    WD[(Wikidata lexemes)]
    WDQS{{Wikidata Query Service}}
    WK[(Wiktionary translations)]
    UNI((Unicode emojis))

    %% Outputs

    JSON(JSON files)
    FILTJSON(Filtered JSON files)
    CTSV(CSV / TSV files)
    SQLITE(SQLITE DB)
    TERM(Terminal output)
    WDDUMP(Wikidata lexeme dump)
    WKDUMP(Wiktionary dump)

    %% Commands

    DLWD{{Wikidata\ndownload command}}
    DLWK{{Wiktionary\ndownload command}}
    LIST{{list command}}
    GET{{get command}}
    TOT{{total command}}
    CONV{{convert command}}
    INT{{interactive mode}}
    EXPORTC{{export_contracts command}}
    FILTERC{{filter_data command}}

    %% General flow

    WD ---> |Download| DLWD
    WK ---> |Download| DLWK

    DLWD ---> |Save locally| WDDUMP
    DLWK ---> |Save locally| WKDUMP

    WD ---> |Return SPARQL request| WDQS

    WDQS ---> |Run\nSPARQL queries| LEXEME_QUERIES
    WDQS ---> |Run\nSPARQL query| PROFANITY_QUERY
    WDDUMP ---> |Parse\nWikidata dump| GET
    WKDUMP ---> |Parse\nWiktionary dump| GET

    WDQS ---> |Run\nSPARQL query| TOTAL_QUERY
    WDDUMP ---> |Parse\nWikidata dump| TOT
    WKDUMP ---> |Parse\nWiktionary dump| TOT

    GET ---> |Save locally| JSON
    JSON ---> |Need different format| CONVERT_FLOW

    LIST ---> |Print output| TERM
    TOT ---> |Print output| TERM

    EXPORTC ---> |Save locally| CONTRACTS
    CONTRACTS ---> |Read contract rules| FILTERC
    JSON ---> |Filter to contract fields| FILTERC
    FILTERC ---> |Save locally| FILTJSON

    %% Subgraphs

    subgraph DOWNLOAD_FLOW [download flow]
    DLWD
    DLWK
    end

    subgraph GET_FLOW [get flow]
    UNI ---> |Derive emojis\nfrom included files| GET
    LEXEME_QUERIES ---> |Return\nquery response| GET
    PROFANITY_QUERY ---> |Return\nquery response| GET
    end

    subgraph CONVERT_FLOW [convert flow]
    CONV ---> |Convert local files| CTSV
    CONV ---> |Convert local files| SQLITE
    end

    subgraph TOTAL_FLOW [total flow]
    TOTAL_QUERY ---> |Return\nquery response| TOT
    end

    subgraph LIST_FLOW [list flow]
    DATA ---> |Read CLI\ninternal data| LIST
    end

    subgraph CONTRACTS_FLOW [data contracts flow]
    EXPORTC
    FILTERC
    CONTRACTS
    end
```

> [!NOTE]
> The architecture diagram above was created using the diagramming tool [Mermaid](https://github.com/mermaid-js/mermaid), with rendering supported in GitHub markdown.
