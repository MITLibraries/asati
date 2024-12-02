import logging
from unittest.mock import patch

from asati.cli import main


@patch("asati.cli.ASnakeClient")
@patch("asati.cli.pyairtable")
def test_cli_new_accessions_success(
    mocked_airtable, mocked_asnake, aspace_record, caplog, runner
):
    mocked_asnake.return_value.get.return_value.json.side_effect = [
        [1234, 5678],
        aspace_record,
    ]
    mocked_airtable.Api.return_value.table.return_value.create.return_value = {
        "fields": {"Accession Number": "2025-014"}
    }
    caplog.set_level(logging.DEBUG)
    result = runner.invoke(main, ["--verbose"])
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=DEBUG" in caplog.text
    assert "Running process" in caplog.text
    assert (
        "Data extracted from ArchivesSpace: {'Accession Title': 'MIT Libraries records "
        "and Bibliotech newsletters 2024 July transfer', 'Accession Number': '2025-014',"
        " 'Current Status': 'Unassigned', 'Extent Number': 1.0, 'Extent Type': 'box(es)'}"
        in caplog.text
    )
    assert "Airtable row created for Accession Number: '2025-014'" in caplog.text
    assert (
        "Updated SSM parameter '/apps/asati/last-accession-uri-id' to '5678'"
        in caplog.text
    )
    assert "Total time to complete process" in caplog.text


@patch("asati.cli.ASnakeClient")
def test_cli_no_accessions_success(mocked_asnake, caplog, runner):
    mocked_asnake.return_value.get.return_value.json.return_value = [1234]
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=INFO" in caplog.text
    assert "Running process" in caplog.text
    assert "No new accessions to add to Airtable." in caplog.text
    assert "Airtable row created for Accession Number:" not in caplog.text
    assert "Updated SSM parameter" not in caplog.text
