import sys


def check_queries():
    # Dummy data simulating query files with incorrect identifiers
    incorrect_language_qids = [
        "English/nouns/query_nouns.sparql",
        "Spanish/verbs/query_verbs.sparql",
    ]

    incorrect_data_type_qids = [
        "English/nouns/query_nouns.sparql",
        "French/verbs/query_verbs_1.sparql",
    ]

    # Check if there are any incorrect queries
    if incorrect_language_qids or incorrect_data_type_qids:
        print(
            "There are queries that have incorrect language or data type identifiers.\n"
        )

        if incorrect_language_qids:
            print("Queries with incorrect languages QIDs are:")
            for file in incorrect_language_qids:
                print(f"- {file}")

        if incorrect_data_type_qids:
            print("\nQueries with incorrect data type QIDs are:")
            for file in incorrect_data_type_qids:
                print(f"- {file}")

        # Exit with a non-zero status code to indicate failure
        sys.exit(1)  # Indicate failure
    else:
        print("All queries are correct.")


if __name__ == "__main__":
    check_queries()
