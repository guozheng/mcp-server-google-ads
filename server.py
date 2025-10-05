import logging
import os
import utils
import requests
from pydantic import Field
from typing import List, Dict, Any

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


############## MCP Tools ##############

@mcp.tool()
async def run_gaql(
    customer_id: str = Field(description="Customer ID"), 
    gaql: str = Field(description="GAQL query")
    ) -> List[Dict[str, Any]]:
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
            return []

        return results.get("results")

    except Exception as e:
        logger.error(f"Error running GAQL: {e}")
        raise e


@mcp.tool()
async def is_manager_account(customer_id: str = Field(description="Customer ID")) -> bool:
    """
    Check if a customer account is a manager account.
    If the given customer ID is a manager account, the query returns a list of accounts under the manager account,
    including the manager account itself at the first position. The manager account manager field is true.
    For example:
    [
        {
            "customerClient": {
            "resourceName": "customers/2857151978/customerClients/2857151978",
            "timeZone": "America/Los_Angeles",
            "manager": true,
            "descriptiveName": "test manager account",
            "currencyCode": "USD",
            "id": "2857151978",
            "status": "CLOSED"
            }
        },
        {
            "customerClient": {
            "resourceName": "customers/2857151978/customerClients/9711179739",
            "timeZone": "America/Los_Angeles",
            "manager": false,
            "descriptiveName": "test123",
            "currencyCode": "USD",
            "id": "9711179739",
            "status": "CLOSED"
            }
        }
    ]

    If the given customer ID is a client account, the query returns the client account only, the manager field is false.
    For example:
    [
        {
            "customerClient": {
            "resourceName": "customers/9711179739/customerClients/9711179739",
            "timeZone": "America/Los_Angeles",
            "manager": false,
            "descriptiveName": "test123",
            "currencyCode": "USD",
            "id": "9711179739",
            "status": "CLOSED"
            }
        }
    ]

    Args:
        customer_id: Customer ID
    
    Returns:
        bool: True if the customer account is a manager account, False otherwise
    """

    query = """
    SELECT
        customer_client.id,
        customer_client.descriptive_name,
        customer_client.manager,
        customer_client.status,
        customer_client.currency_code,
        customer_client.time_zone
    FROM customer_client
    """

    results = await run_gaql(customer_id, query)

    # if the query returns an empty list, the given customer ID is a client account
    if not results:
        logger.info(f"Customer account {customer_id} is a client account")
        return False
    
    # check the manager field of the first element to determine if the given customer ID is a manager account or client account
    result = results[0].get("customerClient").get("manager")
    if result:
        logger.info(f"Customer account {customer_id} is a manager account")
    else:
        logger.info(f"Customer account {customer_id} is a client account")
    return result


@mcp.tool()
async def list_client_accounts(manager_customer_id: str = Field(description="Manager account ID")) -> str:
    """
    List all client accounts for a manager account.

    Args:
        manager_customer_id: Manager account ID
    
    Returns:
        str: List of client accounts
    """

    logger.info(f"Listing client accounts for manager account: {manager_customer_id}")

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


@mcp.tool()
async def list_campaigns(customer_id: str = Field(description="Customer account ID")) -> str:
    """
    List all campaigns for a customer account.

    Args:
        customer_id: Customer account ID
    
    Returns:
        str: List of campaigns
    """

    # first check if the account is a manager account or a client account
    is_manager = await is_manager_account(customer_id)
    if is_manager:
        logger.info(f"Listing campaigns for manager account: {customer_id}")
        query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.start_date,
            campaign.end_date,
            campaign.bidding_strategy_type,
            campaign.advertising_channel_type,
            campaign_budget.amount_micros
        FROM campaign
        ORDER BY campaign.start_date DESC
        """
    else:
        logger.info(f"Listing campaigns for client account: {customer_id}")
        query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.start_date,
            campaign.end_date,
            campaign.bidding_strategy_type,
            campaign.advertising_channel_type,
            campaign_budget.amount_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        ORDER BY campaign.start_date DESC
        """

    return await run_gaql(customer_id, query)





############## Other MCP Resources and Prompts ##############

@mcp.resource("gaql://reference")
def gaql_reference() -> str:
    """Google Ads Query Language (GAQL) reference documentation."""
    return """
    # Google Ads Query Language (GAQL) Reference
    
    GAQL is similar to SQL but with specific syntax for Google Ads. Here's a quick reference:
    
    ## Basic Query Structure
    ```
    SELECT field1, field2, ... 
    FROM resource_type
    WHERE condition
    ORDER BY field [ASC|DESC]
    LIMIT n
    ```
    
    ## Common Field Types
    
    ### Resource Fields
    - campaign.id, campaign.name, campaign.status
    - ad_group.id, ad_group.name, ad_group.status
    - ad_group_ad.ad.id, ad_group_ad.ad.final_urls
    - keyword.text, keyword.match_type
    
    ### Metric Fields
    - metrics.impressions
    - metrics.clicks
    - metrics.cost_micros
    - metrics.conversions
    - metrics.ctr
    - metrics.average_cpc
    
    ### Segment Fields
    - segments.date
    - segments.device
    - segments.day_of_week
    
    ## Common WHERE Clauses
    
    ### Date Ranges
    - WHERE segments.date DURING LAST_7_DAYS
    - WHERE segments.date DURING LAST_30_DAYS
    - WHERE segments.date BETWEEN '2023-01-01' AND '2023-01-31'
    
    ### Filtering
    - WHERE campaign.status = 'ENABLED'
    - WHERE metrics.clicks > 100
    - WHERE campaign.name LIKE '%Brand%'
    
    ## Tips
    - Always check account currency before analyzing cost data
    - Cost values are in micros (millionths): 1000000 = 1 unit of currency
    - Use LIMIT to avoid large result sets
    """

@mcp.prompt("google_ads_workflow")
def google_ads_workflow() -> str:
    """Provides guidance on the recommended workflow for using Google Ads tools."""
    return """
    I'll help you analyze your Google Ads account data. Here's the recommended workflow:
    
    1. First, let's list all the accounts you have access to:
       - Run the `list_accounts()` tool to get available account IDs
    
    2. Before analyzing cost data, let's check which currency the account uses:
       - Run `get_account_currency(customer_id="ACCOUNT_ID")` with your selected account
    
    3. Now we can explore the account data:
       - For campaign performance: `get_campaign_performance(customer_id="ACCOUNT_ID", days=30)`
       - For ad performance: `get_ad_performance(customer_id="ACCOUNT_ID", days=30)`
       - For ad creative review: `get_ad_creatives(customer_id="ACCOUNT_ID")`
    
    4. For custom queries, use the GAQL query tool:
       - `run_gaql(customer_id="ACCOUNT_ID", query="YOUR_QUERY", format="table")`
    
    5. Let me know if you have specific questions about:
       - Campaign performance
       - Ad performance
       - Keywords
       - Budgets
       - Conversions
    
    Important: Always provide the customer_id as a string.
    For example: customer_id="1234567890"
    """

@mcp.prompt("gaql_help")
def gaql_help() -> str:
    """Provides assistance for writing GAQL queries."""
    return """
    I'll help you write a Google Ads Query Language (GAQL) query. Here are some examples to get you started:
    
    ## Get campaign performance last 30 days
    ```
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM campaign
    WHERE segments.date DURING LAST_30_DAYS
    ORDER BY metrics.cost_micros DESC
    ```
    
    ## Get keyword performance
    ```
    SELECT
      keyword.text,
      keyword.match_type,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM keyword_view
    WHERE segments.date DURING LAST_30_DAYS
    ORDER BY metrics.clicks DESC
    ```
    
    ## Get ads with poor performance
    ```
    SELECT
      ad_group_ad.ad.id,
      ad_group_ad.ad.name,
      campaign.name,
      ad_group.name,
      metrics.impressions,
      metrics.clicks,
      metrics.conversions
    FROM ad_group_ad
    WHERE 
      segments.date DURING LAST_30_DAYS
      AND metrics.impressions > 1000
      AND metrics.ctr < 0.01
    ORDER BY metrics.impressions DESC
    ```
    
    Once you've chosen a query, use it with:
    ```
    run_gaql(customer_id="YOUR_ACCOUNT_ID", query="YOUR_QUERY_HERE")
    ```
    
    Remember:
    - Always provide the customer_id as a string
    - Cost values are in micros (1,000,000 = 1 unit of currency)
    - Use LIMIT to avoid large result sets
    - Check the account currency before analyzing cost data
    """


if __name__ == "__main__":
    mcp.run(transports="stdio")