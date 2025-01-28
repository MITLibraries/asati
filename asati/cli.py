import logging
import os
from datetime import timedelta
from time import perf_counter

import click
import pyairtable
from asnake.client import ASnakeClient  # type: ignore[import-untyped]

from asati.config import configure_logger, configure_sentry
from asati.utils import SSMClient, parse_accession_number, parse_extent_data

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-v", "--verbose", is_flag=True, help="Pass to log at debug level instead of info"
)
def main(*, verbose: bool) -> None:
    start_time = perf_counter()
    root_logger = logging.getLogger()
    logger.info(configure_logger(root_logger, verbose=verbose))
    logger.info(configure_sentry())
    logger.info("Running process")

    # Get last accession ID from SSM parameter
    ssm_client = SSMClient()
    last_accession_parameter = "/apps/asati/last-accession-uri-id"
    last_accession_uri_id = ssm_client.get_parameter(last_accession_parameter)

    # Retrieve list of all accessions from ArchivesSpace
    asnake_client = ASnakeClient(
        baseurl=os.environ["ARCHIVESSPACE_URL"],
        username=os.environ["ARCHIVESSPACE_USER"],
        password=os.environ["ARCHIVESSPACE_PASSWORD"],
    )
    accession_uri_ids = asnake_client.get(
        "/repositories/2/accessions?all_ids=true"
    ).json()

    # Determine new accessions to add to Airtable, exit early if none
    accessions_to_add = sorted(
        [
            accession_uri_id
            for accession_uri_id in accession_uri_ids
            if accession_uri_id > int(last_accession_uri_id)
        ]
    )
    if not accessions_to_add:
        logger.info("No new accessions to add to Airtable.")
        return
    logger.info(f"Adding the following accessions to Airtable: {accessions_to_add}")

    # Establish connection to Airtable
    airtable_api = pyairtable.Api(os.environ["AIRTABLE_TOKEN"])
    airtable_table = airtable_api.table(
        os.environ["AIRTABLE_BASE_ID"], os.environ["AIRTABLE_TABLE_NAME"]
    )
    logger.info(
        f"Airtable client configured for base '{airtable_table.base}'"
        f" and table '{airtable_table.name}'"
    )

    # Add accessions to Airtable
    for accession_uri_id in accessions_to_add:
        accession_uri = f"/repositories/2/accessions/{accession_uri_id}"
        accession_record = asnake_client.get(accession_uri).json()
        logger.debug(f"Retrieved record: {accession_uri}")
        accession_data = {
            "Accession Title": accession_record["title"],
            "Accession Number": parse_accession_number(accession_record),
            "Current Status": "Unassigned",
            **parse_extent_data(accession_record),
        }
        logger.debug(f"Data extracted from ArchivesSpace: {accession_data}")

        # Post new rows to Airtable
        response = airtable_table.create(accession_data)
        logger.info(
            "Airtable row created for Accession Number: "
            f"'{response["fields"]["Accession Number"]}'"
        )

        # Update SSM parameter
        logger.debug(f"Last accession ID processed: '{accession_uri_id}'")
        ssm_client.update_parameter(last_accession_parameter, str(accession_uri_id))

    elapsed_time = perf_counter() - start_time
    logger.info(
        "Total time to complete process: %s", str(timedelta(seconds=elapsed_time))
    )
