from .process_unicode import gen_emoji_lexicon
from scribe_data.utils import export_formatted_data


def generate_emoji_keyword(
    language,
    emojis_per_keyword,
    file_path,
    gender=None,
    region=None,
    sub_languages=None,
):
    """
    Generate emoji keywords for a specified language, with optional support for grouped languages (e.g., Hindustani = Hindi + Urdu).

    Parameters:
    - language (str): The language or grouped language for which emoji keywords are generated (e.g., "Hindustani" for Hindi and Urdu).
    - emojis_per_keyword (int): Number of emojis to associate with each keyword.
    - file_path (str): The path to the file where the generated emoji keywords will be saved.
    - gender (str): Gender-based customization for emojis (e.g., "male", "female").
    - region (str): Regional customization for emojis (e.g., "US", "JP").
    - sub_languages (list): A list of specific sub-languages for grouped languages (e.g., ["Hindi", "Urdu"]). If not provided, all sub-languages in the group will be processed.
    """

    # Define grouped languages and their sub-languages
    grouped_languages = {
        "Hindustani": ["Hindi", "Urdu"],
        "Norwegian": ["Bokmål", "Nynorsk"],
        # Add more grouped languages as needed
    }

    # If the language is a grouped language, handle its sub-languages
    if language in grouped_languages:
        # If specific sub-languages are provided, only process those
        sub_languages_to_process = sub_languages or grouped_languages[language]

        for sub_lang in sub_languages_to_process:
            print(f"Processing sub-language: {sub_lang}")

            # Generate emoji keywords for the sub-language
            emoji_keywords_dict = gen_emoji_lexicon(
                language=sub_lang,
                emojis_per_keyword=emojis_per_keyword,
                gender=gender,
                region=region,
            )

            # Export the generated emoji keywords for the sub-language
            if emoji_keywords_dict:
                # Save the file with the sub-language included in the file name
                export_file_path = f"{file_path}_{sub_lang}.json"
                export_formatted_data(
                    file_path=export_file_path,
                    formatted_data=emoji_keywords_dict,
                    query_data_in_use=True,
                    language=sub_lang,
                    data_type="emoji-keywords",
                )

    # If it's not a grouped language, process it as a single language
    else:
        # Generate emoji keywords for the given language
        emoji_keywords_dict = gen_emoji_lexicon(
            language=language,
            emojis_per_keyword=emojis_per_keyword,
            gender=gender,
            region=region,
        )

        # Export the generated emoji keywords for the language
        if emoji_keywords_dict:
            export_formatted_data(
                file_path=file_path,
                formatted_data=emoji_keywords_dict,
                query_data_in_use=True,
                language=language,
                data_type="emoji-keywords",
            )
