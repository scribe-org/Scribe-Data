from scribe_data.load import update_utils

def test_get_language_qid():
    assert update_utils.get_language_qid("french") == "Q150"
