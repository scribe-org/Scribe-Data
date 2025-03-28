# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the contract export functionality in the CLI.
"""

from pathlib import Path
from unittest.mock import call, mock_open, patch

from scribe_data.cli.contracts.export import (
    export_contracts,
    filter_contract_metadata,
    filter_exported_data,
)


class TestFilterContractMetadata:
    def test_filter_contract_metadata_empty_file(self):
        """
        Test filtering with an empty contract file.
        """
        mock_contract = "{}"
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.json"))
            assert result == {
                "nouns": {"numbers": [], "genders": []},
                "verbs": {"conjugations": []},
            }

    def test_filter_contract_metadata_numbers_dict(self):
        """
        Test filtering numbers as a dictionary.
        """
        mock_contract = """
        {
            "numbers": {"singular": "plural", "dual": "", "": "collective"}
        }
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.json"))
            assert "singular" in result["nouns"]["numbers"]
            assert "plural" in result["nouns"]["numbers"]
            assert "dual" in result["nouns"]["numbers"]
            assert "" not in result["nouns"]["numbers"]
            assert "collective" in result["nouns"]["numbers"]

    def test_filter_contract_metadata_numbers_list(self):
        """
        Test filtering numbers as a list.
        """
        mock_contract = """
        {
            "numbers": ["singular", "plural", "", "dual"]
        }
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.json"))
            assert set(result["nouns"]["numbers"]) == {"singular", "plural", "dual"}

    def test_filter_contract_metadata_numbers_string(self):
        """
        Test filtering numbers as a string.
        """
        mock_contract = """
        {
            "numbers": "singular plural  dual "
        }
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.json"))
            assert set(result["nouns"]["numbers"]) == {"singular", "plural", "dual"}

    def test_filter_contract_metadata_genders(self):
        """
        Test filtering genders.
        """
        mock_contract = """
        {
            "genders": {
                "masculine": ["m", "masc"],
                "feminine": ["f", "fem", "NOT_INCLUDED"],
                "neuter": ["n", ""]
            }
        }
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.json"))
            assert set(result["nouns"]["genders"]) == {"m", "masc", "f", "fem", "n"}
            assert "NOT_INCLUDED" not in result["nouns"]["genders"]
            assert "" not in result["nouns"]["genders"]

    def test_filter_contract_metadata_conjugations_list(self):
        """
        Test filtering conjugations as a list.
        """
        mock_contract = """
        {
            "conjugations": ["run", "runs", "[running]", "ran"]
        }
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.json"))
            assert set(result["verbs"]["conjugations"]) == {"run", "runs", "ran"}
            assert "[running]" not in result["verbs"]["conjugations"]

    def test_filter_contract_metadata_error_handling(self):
        """
        Test error handling for invalid JSON.
        """
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("builtins.print") as mock_print:
                result = filter_contract_metadata(Path("fake_path.json"))
                assert result == {}
                mock_print.assert_called_once()


class TestFilterExportedData:
    def test_filter_exported_data_nouns(self):
        """
        Test filtering exported noun data.
        """
        contract_metadata = {
            "nouns": {
                "numbers": ["singular", "plural"],
                "genders": ["masculine", "feminine"],
            },
            "verbs": {"conjugations": []},
        }

        mock_exported_data = """
        {
            "L1": {
                "lastModified": "2023-01-01",
                "lexemeID": "L1",
                "singular": "cat",
                "plural": "cats",
                "masculine": "male cat",
                "feminine": "female cat",
                "irrelevant": "should be removed"
            },
            "L2": {
                "lastModified": "2023-01-02",
                "lexemeID": "L2",
                "singular": "dog",
                "irrelevant": "should be removed"
            }
        }
        """

        with patch("builtins.open", mock_open(read_data=mock_exported_data)):
            result = filter_exported_data(
                Path("fake_path.json"), contract_metadata, "nouns"
            )

            assert "L1" in result
            assert result["L1"]["lastModified"] == "2023-01-01"
            assert result["L1"]["lexemeID"] == "L1"
            assert result["L1"]["singular"] == "cat"
            assert result["L1"]["plural"] == "cats"
            assert result["L1"]["masculine"] == "male cat"
            assert result["L1"]["feminine"] == "female cat"
            assert "irrelevant" not in result["L1"]

            assert "L2" in result
            assert result["L2"]["singular"] == "dog"
            assert "irrelevant" not in result["L2"]

    def test_filter_exported_data_verbs(self):
        """
        Test filtering exported verb data.
        """
        contract_metadata = {
            "nouns": {"numbers": [], "genders": []},
            "verbs": {"conjugations": ["infinitive", "present", "past"]},
        }

        mock_exported_data = """
        {
            "L3": {
                "lastModified": "2023-01-03",
                "lexemeID": "L3",
                "infinitive": "to run",
                "present": "runs",
                "past": "ran",
                "irrelevant": "should be removed"
            },
            "L4": {
                "lastModified": "2023-01-04",
                "lexemeID": "L4",
                "gerund": "walking",
                "irrelevant": "should be removed"
            }
        }
        """

        with patch("builtins.open", mock_open(read_data=mock_exported_data)):
            result = filter_exported_data(
                Path("fake_path.json"), contract_metadata, "verbs"
            )

            assert "L3" in result
            assert result["L3"]["infinitive"] == "to run"
            assert result["L3"]["present"] == "runs"
            assert result["L3"]["past"] == "ran"
            assert "irrelevant" not in result["L3"]

            # L4 should not be included as it doesn't have enough valid fields.
            assert "L4" not in result

    def test_filter_exported_data_unsupported_type(self):
        """
        Test filtering with unsupported data type.
        """
        contract_metadata = {
            "nouns": {"numbers": [], "genders": []},
            "verbs": {"conjugations": []},
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            result = filter_exported_data(
                Path("fake_path.json"), contract_metadata, "adjectives"
            )
            assert result == {}

    def test_filter_exported_data_error_handling(self):
        """
        Test error handling for invalid JSON.
        """
        contract_metadata = {
            "nouns": {"numbers": [], "genders": []},
            "verbs": {"conjugations": []},
        }

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("builtins.print") as mock_print:
                result = filter_exported_data(
                    Path("fake_path.json"), contract_metadata, "nouns"
                )
                assert result == {}
                mock_print.assert_called_once()


class TestExportContracts:
    @patch("scribe_data.cli.contracts.export.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.export.filter_exported_data")
    @patch("scribe_data.cli.contracts.export.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_export_contracts(
        self,
        mock_json_dump,
        mock_file_open,
        mock_exists,
        mock_mkdir,
        mock_listdir,
        mock_get_language,
        mock_filter_data,
        mock_filter_metadata,
    ):
        """
        Test the export_contracts function full workflow.
        """
        mock_listdir.return_value = [
            "english.json",
            "spanish.json",
            "not_a_contract.txt",
        ]
        mock_get_language.side_effect = lambda lang: {
            "english": "English",
            "spanish": "Spanish",
        }.get(lang)
        mock_exists.return_value = True

        # Mock filtered metadata.
        mock_contract_metadata = {
            "nouns": {
                "numbers": ["singular", "plural"],
                "genders": ["masculine", "feminine"],
            },
            "verbs": {"conjugations": ["infinitive", "present", "past"]},
        }
        mock_filter_metadata.return_value = mock_contract_metadata

        # Mock filtered data.
        mock_filtered_nouns = {
            "L1": {"lastModified": "2023", "lexemeID": "L1", "singular": "cat"}
        }
        mock_filtered_verbs = {
            "L2": {"lastModified": "2023", "lexemeID": "L2", "infinitive": "run"}
        }
        mock_filter_data.side_effect = [
            mock_filtered_nouns,
            mock_filtered_verbs,
        ] * 2  # for both languages

        # Call the function.
        export_contracts(input_dir="test_input", output_dir="test_output")

        assert mock_mkdir.call_count >= 3  # main dir + 2 language dirs
        assert mock_filter_metadata.call_count == 2  # one for each language
        assert mock_filter_data.call_count == 4  # two languages × two data types
        assert (
            mock_json_dump.call_count == 4
        )  # saving filtered data for 2 langs × 2 types

        # Check filter_exported_data calls.
        expected_calls = [
            call(
                Path("test_input/english/nouns.json"), mock_contract_metadata, "nouns"
            ),
            call(
                Path("test_input/english/verbs.json"), mock_contract_metadata, "verbs"
            ),
            call(
                Path("test_input/spanish/nouns.json"), mock_contract_metadata, "nouns"
            ),
            call(
                Path("test_input/spanish/verbs.json"), mock_contract_metadata, "verbs"
            ),
        ]
        mock_filter_data.assert_has_calls(expected_calls, any_order=True)

    @patch("scribe_data.cli.contracts.export.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.export.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    def test_export_contracts_no_language_match(
        self, mock_mkdir, mock_listdir, mock_get_language, mock_filter_metadata
    ):
        """
        Test handling of contracts with no language match.
        """
        mock_listdir.return_value = ["unknown.json"]
        mock_get_language.return_value = None

        with patch("builtins.print") as mock_print:
            export_contracts()

            # Verify warning was printed.
            mock_print.assert_called_with(
                "Warning: Could not find language match for unknown"
            )

        # No metadata should be filtered.
        mock_filter_metadata.assert_not_called()

    @patch("scribe_data.cli.contracts.export.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.export.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_export_contracts_no_input_file(
        self,
        mock_exists,
        mock_mkdir,
        mock_listdir,
        mock_get_language,
        mock_filter_metadata,
    ):
        """
        Test handling when input files don't exist.
        """
        mock_listdir.return_value = ["english.json"]
        mock_get_language.return_value = "English"
        mock_exists.return_value = False
        mock_filter_metadata.return_value = {
            "nouns": {"numbers": [], "genders": []},
            "verbs": {"conjugations": []},
        }

        with patch("builtins.print") as mock_print:
            export_contracts()

            # Verify warning was printed for both noun and verb data.
            assert mock_print.call_count >= 2
            mock_print.assert_any_call("No nouns data found for English")
            mock_print.assert_any_call("No verbs data found for English")

    @patch("scribe_data.cli.contracts.export.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.export.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    def test_export_contracts_empty_metadata(
        self, mock_mkdir, mock_listdir, mock_get_language, mock_filter_metadata
    ):
        """
        Test handling when contract metadata is empty.
        """
        mock_listdir.return_value = ["english.json"]
        mock_get_language.return_value = "English"
        mock_filter_metadata.return_value = {}

        export_contracts()

        # Verify no further processing happens when metadata is empty.
        mock_filter_metadata.assert_called_once()
