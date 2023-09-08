from scribe_data import utils


def test_get_language_qid():
    assert utils.get_language_qid("french") == "Q150"
