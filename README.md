# archivesspace-airtable-integration
An application for updating Airtable with ArchivesSpace data.


# asati
The application extracts data from newly-created accession records in ArchivesSpace on a daily basis. It uses an SSM parameter (`/apps/asati/last-accession-uri-id`) to track the last accession that was added to Airtable via the ID in the URI (e.g. "/repositories/2/accessions/**123**"). The application accesses the SSM parameter at the start of each run and calls the ArchivesSpace API's `accessions` endpoint with the `?all_ids=true` parameter to check if a higher ID number has been created. ArchivesSpace increments the IDs and does not reuse IDs, making this a safe method for checking if new accessions have been created.

If no new accessions were create, the run ends. If a new accession has been created, the accession record is retrieved and the necessary data is posted as a new row in Airtable. This is not expected to be high-volume application, only a few accessions at most are expected to be created on a given day and most days will not have any new accessions. 

Sentry will be used for exception monitoring and the application is expected to immediately fail if there is an error. Given the simple structure and logging at potential failure points, troubleshooting should be quick if the application does fail. Furthermore, the application can pick up where it left off on the next daily run, given that the SSM parameter is updated after each row is added to Airtable.


## Development

- To preview a list of available Makefile commands: `make help`
- To install with dev dependencies: `make install`
- To update dependencies: `make update`
- To run unit tests: `make test`
- To lint the repo: `make lint`
- To run the app: `pipenv run asati --help`

## Environment Variables

### Required

```shell
SENTRY_DSN=### If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.
WORKSPACE=### Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.
LAST_ACCESSION_PARAMETER=### The name of the SSM parameter that stores the ID from the URI of the last processed accession.
ARCHIVESSPACE_URL=### The URL of the ArchivesSpace instance to use. Given this app is read-only, the production instance will be used.
ARCHIVESSPACE_USER=### The username to use for authenticating to ArchivesSpace.
ARCHIVESSPACE_PASSWORD=### The password to use for authenticating to ArchivesSpace.
AIRTABLE_TOKEN=### The token to use for authenticating to Airtable.
AIRTABLE_BASE_ID=### The Airtable base containing the table to be updated.
AIRTABLE_TABLE_NAME=### The Airtable table to be updated.
```



