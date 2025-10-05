import logging
import os
import utils
import requests

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("mcp-server-google-ads")

from dotenv import load_dotenv
load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
]
API_VERSION = "v21"

GOOGLE_ADS_CREDENTIALS_PATH = os.getenv("GOOGLE_ADS_CREDENTIALS_PATH")
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_AUTH_TYPE = "service_account"

@mcp.tool()
async def run_gaql(customer_id: str, gaql: str):
    try:
        credentials = utils.get_service_account_credentials(GOOGLE_ADS_CREDENTIALS_PATH, SCOPES)
        headers = utils.generated_request_headers(GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID, credentials)    

        customer_id = utils.format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{customer_id}/googleAds:search"

        response = requests.post(url, headers=headers, json={"query": gaql})

        if response.status_code != 200:
            raise Exception(f"Error running GAQL: {response.text}")
        
        results = response.json()
        if not results.get("results"):
            raise Exception("No results found")

        return results.get("results")

    except Exception as e:
        logger.error(f"Error running GAQL: {e}")
        raise e


@mcp.tool()
async def list_client_accounts(manager_customer_id: str) -> str:
    query = """
    SELECT
        customer_client.id,
        customer_client.descriptive_name,
        customer_client.manager,
        customer_client.status,
        customer_client.currency_code,
        customer_client.time_zone
    FROM customer_client
    WHERE customer_client.manager = FALSE
    """

    return await run_gaql(manager_customer_id, query)


if __name__ == "__main__":
    mcp.run(transports="stdio")