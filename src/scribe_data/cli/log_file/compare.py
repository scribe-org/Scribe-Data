# SPDX-License-Identifier: GPL-3.0-or-later
"""
Compare two Scribe-Data log files and output the differences in data.
"""

import json

from scribe_data.utils import DEFAULT_LOG_FILES_EXPORT_DIR


def compare_log_files(
    include_fields: bool = False,
    earlier_timestamp: int | None = None,
    later_timestamp: int | None = None,
    fail_under: int | None = None,
    only_positive: bool = False,
) -> None:
    """
    Compare two Scribe-Data log files and print the difference in the total data.

    Parameters
    ----------
    include_fields : bool, optional, default=False
        Whether to compare total data type field log files rather than just data types.

    earlier_timestamp : int, optional, default=None
        The timestamp of the first logfile to compare.

    later_timestamp : int, optional, default=None
        The timestamp of the second logfile to compare.

    fail_under : int, optional, default=None
        A threshold under which to fail the comparison such that data updates can be canceled.

    only_positive : bool, optional, default=False
        Only include positive increases in data in the output for use in social posts.
    """
    # MARK: Check Args

    all_log_files = list(DEFAULT_LOG_FILES_EXPORT_DIR.glob("*.json"))
    log_type_identifier = "data_type_fields" if include_fields else "data_types"
    all_log_files_of_desired_type = [
        f for f in all_log_files if log_type_identifier in str(f)
    ]
    all_log_timestamps = [
        int(str(f).split(f"{log_type_identifier}_")[-1].split(".json")[0])
        for f in all_log_files_of_desired_type
    ]

    assert all_log_files_of_desired_type, (
        "There are currently no Scribe-Data log files to compare for the desired type (data types or data type fields). Generate log files with the --generate-log-file (-glf) command to compare log files."
    )
    assert len(all_log_files_of_desired_type) > 1, (
        "There is only one Scribe-Data log file for the desired type (data types or data type fields). Generate another with the --generate-log-file (-glf) command to compare log files."
    )

    # MARK: With Timestamps

    if earlier_timestamp or later_timestamp:
        assert earlier_timestamp and later_timestamp, (
            "Please provide a value for both --earlier-timestamp (-et) and --later-timestamp (-lt) and not just one. You can also not pass values to these arguments to compare the two most recent log files."
        )

        assert earlier_timestamp in all_log_timestamps, (
            "The timestamp passed to --earlier-timestamp (-et) does not exist in the log files for the desired log type."
        )
        assert later_timestamp in all_log_timestamps, (
            "The timestamp passed to --later-timestamp (-lt) does not exist in the log files for the desired log type."
        )

        earlier_log_to_compare = next(
            path
            for path in all_log_files_of_desired_type
            if str(earlier_timestamp) in path.name
        )
        later_log_to_compare = next(
            path
            for path in all_log_files_of_desired_type
            if str(later_timestamp) in path.name
        )

    # MARK: Most Recent

    else:
        log_files_to_compare = sorted(all_log_files_of_desired_type)[-2:]
        earlier_log_to_compare = log_files_to_compare[0]
        later_log_to_compare = log_files_to_compare[1]

    # MARK: Compare Logs

    with earlier_log_to_compare.open(encoding="utf-8") as file:
        earlier_log_contents = json.load(file)

    with later_log_to_compare.open(encoding="utf-8") as file:
        later_log_contents = json.load(file)

    log_field_diffs_dict = {}
    threshold_fail_bool = False
    log_field_fail_percents_dict = {}
    for lang in later_log_contents.keys():
        log_field_diffs_dict[lang] = {}
        log_field_fail_percents_dict[lang] = {}
        for dt in later_log_contents[lang]:
            if not include_fields:
                if (
                    lang not in earlier_log_contents.keys()
                    or dt not in earlier_log_contents[lang]
                ):
                    prior_value = 0

                else:
                    prior_value = earlier_log_contents[lang][dt]

                log_field_diffs_dict[lang][dt] = (
                    later_log_contents[lang][dt] - prior_value
                )

                if fail_under:
                    percent_change = (
                        (later_log_contents[lang][dt] / prior_value * 100)
                        if prior_value != 0
                        else 100
                    )
                    if percent_change < fail_under:
                        log_field_fail_percents_dict[lang][dt] = percent_change
                        threshold_fail_bool = True

            else:
                log_field_diffs_dict[lang][dt] = {}
                log_field_fail_percents_dict[lang][dt] = {}
                for field in later_log_contents[lang][dt]:
                    if (
                        lang not in earlier_log_contents.keys()
                        or dt not in earlier_log_contents[lang]
                        or field not in earlier_log_contents[lang][dt]
                    ):
                        prior_value = 0

                    else:
                        prior_value = earlier_log_contents[lang][dt][field]

                    log_field_diffs_dict[lang][dt][field] = (
                        later_log_contents[lang][dt][field] - prior_value
                    )

                    if fail_under:
                        percent_change = (
                            (later_log_contents[lang][dt][field] / prior_value * 100)
                            if prior_value != 0
                            else 100
                        )
                        if percent_change < fail_under:
                            log_field_fail_percents_dict[lang][dt][field] = (
                                percent_change
                            )
                            threshold_fail_bool = True

    # MARK: Fail Threshold

    if fail_under and threshold_fail_bool:
        error_fields = ""
        for lang in log_field_fail_percents_dict:
            for dt in log_field_fail_percents_dict[lang]:
                if not include_fields:
                    error_fields += f"\n- {lang.capitalize()} {dt}: {log_field_fail_percents_dict[lang][dt]}%"

                else:
                    for field in log_field_fail_percents_dict[lang][dt]:
                        error_fields += f"\n- {lang.capitalize()} {dt} {field}: {log_field_fail_percents_dict[lang][dt][field]}%"

        error_str = (
            f"There is a decrease in data that is below the {fail_under}% --fail-under (-fu) threshold.\n"
            + f"The following fields have had a drop in data to less than {fail_under}% of the earlier logged data."
            + "\n"
            + error_fields
            + "\n"
        )
        raise ValueError(error_str)

    elif fail_under:
        print(
            f"All data totals in the later log meet the required {fail_under}% --fail-under (-fu) threshold."
        )

    # MARK: Print Comparison

    later_datetime = later_log_to_compare.name.split("_")[-1].split(".json")[0]
    later_date = f"{later_datetime[:4]}-{later_datetime[4:6]}-{later_datetime[6:8]}"
    earlier_datetime = earlier_log_to_compare.name.split("_")[-1].split(".json")[0]
    earlier_date = (
        f"{earlier_datetime[:4]}-{earlier_datetime[4:6]}-{earlier_datetime[6:8]}"
    )

    comparison_fields = ""
    for lang in log_field_diffs_dict:
        for dt in log_field_diffs_dict[lang]:
            if not include_fields:
                if (
                    not (only_positive and log_field_diffs_dict[lang][dt] < 0)
                    and not log_field_diffs_dict[lang][dt] == 0
                ):
                    comparison_fields += f"\n- {lang.capitalize()} {dt}: {log_field_diffs_dict[lang][dt]}"

            else:
                for field in log_field_diffs_dict[lang][dt]:
                    if (
                        not (
                            only_positive and log_field_diffs_dict[lang][dt][field] < 0
                        )
                        and not log_field_diffs_dict[lang][dt][field] == 0
                    ):
                        comparison_fields += f"\n- {lang.capitalize()} {dt} {field}: {log_field_diffs_dict[lang][dt][field]}"

    if not comparison_fields:
        print(
            f"There is no difference in the total data recorded in the {later_log_to_compare.name} ({later_date}) and {earlier_log_to_compare.name} ({earlier_date}) log files."
        )

    else:
        compare_str = (
            "Files compared:"
            + f"\n- Later log: {later_log_to_compare.name} ({later_date})"
            + f"\n- Earlier log: {earlier_log_to_compare.name} ({earlier_date})"
            + "\n"
            + "\nDifference in total data:"
            + comparison_fields
            + "\n"
        )

        print(compare_str)
