from asati.utils import parse_accession_number, parse_extent_data


def test_parse_accession_number_4_parts_success():
    accession_record = {
        "id_0": "2025",
        "id_1": "214",
        "id_2": "314",
        "id_3": "514",
    }
    assert parse_accession_number(accession_record) == "2025-214-314-514"


def test_parse_accession_number_1_part_success():
    assert parse_accession_number({"id_0": "2025"}) == "2025"


def test_parse_extent_data_no_extents_success():
    assert parse_extent_data({}) == {}


def test_parse_extent_data_physical_linear_feet_success():
    accession_record = {"extents": [{"number": "1.0", "extent_type": "linear_feet"}]}
    assert parse_extent_data(accession_record) == {
        "Pre-accessioning extent (linear feet)": 1.0
    }


def test_parse_extent_data_digital_gigabyes_success():
    accession_record = {"extents": [{"number": "2.0", "extent_type": "gigabytes"}]}
    assert parse_extent_data(accession_record) == {"Pre-accessioning extent (GB)": 2.0}


def test_parse_extent_data_physical_not_linear_feet_success():
    accession_record = {"extents": [{"number": "12.0", "extent_type": "box(es)"}]}
    assert parse_extent_data(accession_record) == {
        "Extent Number": 12.0,
        "Extent Type": "box(es)",
    }


def test_parse_extent_data_digital_not_gigabytes_success():
    accession_record = {"extents": [{"number": "100.0", "extent_type": "megabytes"}]}
    assert parse_extent_data(accession_record) == {
        "Extent Number": 100.0,
        "Extent Type": "megabytes",
    }


def test_parse_extent_data_get_ssm_parameter_success(ssm_client):
    assert ssm_client.get_parameter("/apps/asati/last-accession-uri-id") == "1235"


def test_parse_extent_data_update_ssm_parameter_success(ssm_client):
    assert ssm_client.get_parameter("/apps/asati/last-accession-uri-id") == "1235"
    assert (
        ssm_client.update_parameter("/apps/asati/last-accession-uri-id", "1249") == "1249"
    )
    assert ssm_client.get_parameter("/apps/asati/last-accession-uri-id") == "1249"
