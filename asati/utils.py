import logging

from boto3 import client

logger = logging.getLogger(__name__)


def parse_accession_number(accession_record: dict) -> str:
    """Parse accession number from components in 4 fields.

    Filter logic is applied to ensure that blank or non-existent fields are not
    incorporated into the accession number.

    Args:
        accession_record: An ArchivesSpace accession record serialized as JSON.
    """
    ids = [accession_record.get(f"id_{x}", "") for x in range(4)]
    return "-".join(filter(None, ids))


def parse_extent_data(accession_record: dict) -> dict:
    """Parse extent data according to requested business logic.

    The Department of Distinctive Collections (DDC) has requested the following business
    logic for exporting extent data. Linear feet and gigabytes are the preferred extent
    types for physical and digital accessions respectively and each has a dedicated column
    in Airtable. If extent data is recorded with a different extent type, the 'Extent
    Number' and 'Extent Type' columns are used.

    Args:
        accession_record: An ArchivesSpace accession record serialized as JSON.
    """
    extent_data = {}
    if extents := accession_record.get("extents"):
        extent_number = extents[0].get("number", "")
        extent_type = extents[0].get("extent_type", "")
        if extent_type == "linear_feet":
            extent_data["Pre-accessioning extent (linear feet)"] = float(extent_number)
        elif extent_type == "gigabytes":
            extent_data["Pre-accessioning extent (GB)"] = float(extent_number)
        else:
            extent_data["Extent Number"] = float(extent_number)
            extent_data["Extent Type"] = extent_type
    return extent_data


class SSMClient:
    def __init__(self) -> None:
        self.client = client("ssm", region_name="us-east-1")

    def get_parameter(self, parameter_name: str) -> str:
        parameter = self.client.get_parameter(Name=parameter_name)
        parameter_value = parameter["Parameter"]["Value"]
        logger.info(f"SSM parameter '{parameter_name}' retrieved: '{parameter_value}'")
        return parameter_value

    def update_parameter(self, parameter_name: str, parameter_value: str) -> str:
        self.client.put_parameter(
            Name=parameter_name,
            Value=parameter_value,
            Overwrite=True,
        )
        updated_parameter = self.client.get_parameter(Name=parameter_name)
        updated_parameter_value = updated_parameter["Parameter"]["Value"]
        if parameter_value == updated_parameter_value:
            logger.info(
                f"Updated SSM parameter '{parameter_name}' to '{parameter_value}'"
            )
        else:
            message = "SSM parameter update failed: '{parameter_value}' was not set"
            raise RuntimeError(message)
        return updated_parameter_value
