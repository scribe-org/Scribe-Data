# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the contract filter functionality in the CLI.
"""

from pathlib import Path
from unittest.mock import MagicMock, call, mock_open, patch

from scribe_data.cli.contracts.filter import (
    export_data_filtered_by_contracts,
    filter_contract_metadata,
    filter_exported_data,
)
from scribe_data.utils import (
    DATA_CONTRACTS_DIR,
    DEFAULT_FILTERED_JSON_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
)


class TestFilterContractMetadata:
    def test_cli_contracts_filter_metadata_empty_file(self) -> None:
        """
        Test filtering with an empty contract file.
        """
        with patch("builtins.open", mock_open(read_data="")):
            result = filter_contract_metadata(Path("fake_path.yaml"))
            assert result == {}

    def test_cli_contracts_filter_metadata_nested_data_types(self) -> None:
        """
        Test that fields are extracted from the data type sections of a contract.
        """
        mock_contract = """
        nouns:
          genders:
            canonical: [gender]
            feminines: []
          numbers:
            1:
              singular: nominativeSingular
              plural: nominativePlural
        verbs:
          conjugations:
            1:
              sectionTitle: Present
              tenses:
                1:
                  tenseTitle: Present
                  tenseForms:
                    1:
                      label: I
                      value: presentFirstPersonSingular
                    2:
                      label: they
                      value: presentThirdPersonPlural
        prepositions:
          case: grammaticalCase
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.yaml"))
            assert result == {
                "nouns": ["gender", "nominativePlural", "nominativeSingular"],
                "verbs": ["presentFirstPersonSingular", "presentThirdPersonPlural"],
                "prepositions": ["grammaticalCase"],
            }

    def test_cli_contracts_filter_metadata_ignores_non_lexeme_sections(self) -> None:
        """
        Test that sections that aren't lexeme data types are not treated as fields.
        """
        mock_contract = """
        nouns:
          numbers:
            1:
              singular: nominativeSingular
              plural: nominativePlural
        translations:
          sectionTitle: Translate
          wordTypes: [Noun, Verb]
        declensions:
          1:
            sectionTitle: Pronouns
            declensionForms:
              1:
                label: M
                value: den
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.yaml"))
            assert result == {"nouns": ["nominativePlural", "nominativeSingular"]}

    def test_cli_contracts_filter_metadata_excludes_bracketed_values(self) -> None:
        """
        Test that [word] values are not included as fields.
        """
        mock_contract = """
        verbs:
          conjugations:
            1:
              tenseForms:
                1:
                  label: I
                  value: "[have] pastParticiple"
        """
        with patch("builtins.open", mock_open(read_data=mock_contract)):
            result = filter_contract_metadata(Path("fake_path.yaml"))
            assert result == {"verbs": ["pastParticiple"]}

    def test_cli_contracts_filter_metadata_real_contracts(self) -> None:
        """
        Test that all data contracts include fields for nouns and verbs.
        """
        for contract_file in DATA_CONTRACTS_DIR.glob("*.yaml"):
            result = filter_contract_metadata(contract_file)
            assert result.get("nouns"), f"No noun fields found in {contract_file.name}"
            assert result.get("verbs"), f"No verb fields found in {contract_file.name}"

        result = filter_contract_metadata(DATA_CONTRACTS_DIR / "de.yaml")
        assert result["nouns"] == ["gender", "nominativePlural", "nominativeSingular"]
        assert result["prepositions"] == ["grammaticalCase"]

    def test_cli_contracts_filter_metadata_error_handling(self) -> None:
        """
        Test error handling for invalid YAML.
        """
        with patch("builtins.open", mock_open(read_data="[invalid yaml")):
            with patch("builtins.print") as mock_print:
                result = filter_contract_metadata(Path("fake_path.yaml"))
                assert result == {}
                mock_print.assert_called_once()


class TestFilterExportedData:
    def test_cli_contracts_filter_exported_data_nouns(self) -> None:
        """
        Test filtering exported noun data.
        """
        contract_metadata = {
            "nouns": ["singular", "plural", "masculine", "feminine"],
            "verbs": [],
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

    def test_cli_contracts_filter_exported_data_verbs(self) -> None:
        """
        Test filtering exported verb data.
        """
        contract_metadata = {
            "nouns": [],
            "verbs": ["infinitive", "present", "past"],
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

    def test_cli_contracts_filter_exported_data_unsupported_type(self) -> None:
        """
        Test filtering with unsupported data type.
        """
        contract_metadata = {"nouns": [], "verbs": []}

        with patch("builtins.open", mock_open(read_data="{}")):
            result = filter_exported_data(
                Path("fake_path.json"), contract_metadata, "adjectives"
            )
            assert result == {}

    def test_cli_contracts_filter_exported_data_error_handling(self) -> None:
        """
        Test error handling for invalid JSON.
        """
        contract_metadata = {"nouns": [], "verbs": []}

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("builtins.print") as mock_print:
                result = filter_exported_data(
                    Path("fake_path.json"), contract_metadata, "nouns"
                )
                assert result == {}
                mock_print.assert_called_once()


class TestExportContracts:
    @patch("scribe_data.cli.contracts.filter.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.filter.filter_exported_data")
    @patch("scribe_data.cli.contracts.filter.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_cli_contracts_export_data_filtered(
        self,
        mock_json_dump: MagicMock,
        mock_file_open: MagicMock,
        mock_exists: MagicMock,
        mock_mkdir: MagicMock,
        mock_listdir: MagicMock,
        mock_get_language: MagicMock,
        mock_filter_data: MagicMock,
        mock_filter_metadata: MagicMock,
    ) -> None:
        """
        Test the export_data_filtered_by_contracts function full workflow.
        """
        mock_listdir.return_value = [
            "english.yaml",
            "spanish.yaml",
            "not_a_contract.txt",
        ]
        mock_get_language.side_effect = lambda lang: {
            "english": "English",
            "spanish": "Spanish",
        }.get(lang)

        # Mock exists to return True for language directories.
        def exists_side_effect() -> bool:
            # This is called on Path instances, check if it's a language directory.
            return True

        mock_exists.side_effect = exists_side_effect

        # Mock filtered metadata.
        mock_contract_metadata = {
            "nouns": ["singular", "plural", "masculine", "feminine"],
            "verbs": ["infinitive", "present", "past"],
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

        def mock_path_glob(self: Path, pattern: str) -> list[Path]:
            """
            Mock glob method that returns files based on the path.
            """
            path_str = str(self)
            if "english" in path_str.lower():
                return [
                    Path("test_input/english/nouns.json"),
                    Path("test_input/english/verbs.json"),
                ]

            elif "spanish" in path_str.lower():
                return [
                    Path("test_input/spanish/nouns.json"),
                    Path("test_input/spanish/verbs.json"),
                ]

            return []

        with patch.object(Path, "glob", mock_path_glob):
            # Call the function.
            export_data_filtered_by_contracts(
                contracts_dir=DATA_CONTRACTS_DIR,
                input_dir="test_input",
                output_dir="test_output",
            )

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

    @patch("scribe_data.cli.contracts.filter.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.filter.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    def test_cli_contracts_export_data_filtered_no_language_match(
        self,
        mock_mkdir: MagicMock,
        mock_listdir: MagicMock,
        mock_get_language: MagicMock,
        mock_filter_metadata: MagicMock,
    ) -> None:
        """
        Test handling of contracts with no language match.
        """
        mock_listdir.return_value = ["unknown.yaml"]
        mock_get_language.return_value = None

        with patch("builtins.print") as mock_print:
            export_data_filtered_by_contracts(
                contracts_dir=DATA_CONTRACTS_DIR,
                input_dir=DEFAULT_JSON_EXPORT_DIR,
                output_dir=DEFAULT_FILTERED_JSON_EXPORT_DIR,
            )

            # Verify warning was printed.
            mock_print.assert_called_with(
                "Warning: Could not find language match for unknown"
            )

        # No metadata should be filtered.
        mock_filter_metadata.assert_not_called()

    @patch("scribe_data.cli.contracts.filter.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.filter.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_cli_contracts_export_data_filtered_no_input_file(
        self,
        mock_exists: MagicMock,
        mock_mkdir: MagicMock,
        mock_listdir: MagicMock,
        mock_get_language: MagicMock,
        mock_filter_metadata: MagicMock,
    ) -> None:
        """
        Test handling when input files don't exist.
        """
        mock_listdir.return_value = ["english.yaml"]
        mock_get_language.return_value = "English"
        mock_exists.return_value = False
        mock_filter_metadata.return_value = {"nouns": [], "verbs": []}

        with patch("builtins.print") as mock_print:
            export_data_filtered_by_contracts(
                contracts_dir=DATA_CONTRACTS_DIR,
                input_dir=DEFAULT_JSON_EXPORT_DIR,
                output_dir=DEFAULT_FILTERED_JSON_EXPORT_DIR,
            )

            # Verify warning was printed - expects "No input directory found for English".
            assert mock_print.call_count >= 1
            mock_print.assert_called_with("No input directory found for English")

    @patch("scribe_data.cli.contracts.filter.filter_contract_metadata")
    @patch("scribe_data.cli.contracts.filter.get_language_from_iso")
    @patch("os.listdir")
    @patch("pathlib.Path.mkdir")
    def test_cli_contracts_export_data_filtered_empty_metadata(
        self,
        mock_mkdir: MagicMock,
        mock_listdir: MagicMock,
        mock_get_language: MagicMock,
        mock_filter_metadata: MagicMock,
    ) -> None:
        """
        Test handling when contract metadata is empty.
        """
        mock_listdir.return_value = ["english.yaml"]
        mock_get_language.return_value = "English"
        mock_filter_metadata.return_value = {}

        export_data_filtered_by_contracts(
            contracts_dir=DATA_CONTRACTS_DIR,
            input_dir=DEFAULT_JSON_EXPORT_DIR,
            output_dir=DEFAULT_FILTERED_JSON_EXPORT_DIR,
        )

        # Verify no further processing happens when metadata is empty.
        mock_filter_metadata.assert_called_once()
