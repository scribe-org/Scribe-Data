import json

from tqdm.auto import tqdm

from scribe_data.utils import get_language_iso
from scribe_data.wikipedia.extract_wiki import download_wiki, parse_to_ndjson
from scribe_data.wikipedia.process_wiki import clean, gen_autosuggestions


def generate_autosuggestions(language):
    """
    Generates autosuggestions from Wikipedia articles for a given language.

    This function downloads a Wikipedia dump, extracts and cleans article texts,
    and generates autosuggestions based on the processed text. If no matching dump is found, the function exits early.

    Parameters
    ----------
    language : str
        The language for which autosuggestions should be generated.

    Returns
    -------
    None
        The function does not return anything but generates autosuggestions
        and updates local data.
    """

    language_abbr = get_language_iso(language)
    files = download_wiki(
        language=language,
        target_dir=f"./{language_abbr}wiki_dump",
        file_limit=1,  # Limiting for development purpose
        dump_id=None,
    )

    print(f"Number of files: {len(files)}")
    if not files:
        print(
            f"Can not generate autosuggestions for {language}. No dump matches the condition."
        )
        return

    parse_to_ndjson(
        output_path=f"./{language_abbr}wiki.ndjson",
        input_dir=f"./{language_abbr}wiki_dump",
        partitions_dir=f"./{language_abbr}wiki_partitions",
        article_limit=None,
        delete_parsed_files=True,
        multicore=True,
        verbose=True,
    )

    with open(f"./{language_abbr}wiki.ndjson", "r") as fin:
        article_texts = [
            json.loads(lang)[1]
            for lang in tqdm(fin, desc="Articles added", unit="articles")
        ]

    print(f"Number of articles: {len(article_texts)}")

    # Define sample size for up to 1 million articles.
    sample_size = 1000000 / len(article_texts)
    sample_size = min(sample_size, 1)

    text_corpus = clean(
        texts=article_texts,
        language=language,
        remove_words=None,
        sample_size=sample_size,
        verbose=True,
    )

    gen_autosuggestions(
        text_corpus,
        language=language,
        num_words=100,  # Limiting for development purpose
        ignore_words=None,
        update_local_data=True,
        verbose=True,
    )
