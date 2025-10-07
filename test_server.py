import asyncio
from server import (
    list_client_accounts,
    list_campaigns,
    is_manager_account,
    create_campaign_budget,
    create_display_campaign,
    list_ad_groups,
    list_ads,
)
import json
import logging
import datetime
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_is_manager_account():
    # this is a test manager account
    customer_id = "2857151978"
    result = asyncio.run(is_manager_account(customer_id))
    logger.info(json.dumps(result, indent=2))

    # this is a test client account under the test manager account
    customer_id = "9711179739"
    result = asyncio.run(is_manager_account(customer_id))
    logger.info(json.dumps(result, indent=2))

def test_list_client_accounts():
    manager_customer_id = "2857151978"
    result = asyncio.run(list_client_accounts(manager_customer_id))
    logger.info(json.dumps(result, indent=2))


def test_list_campaigns():
    # this is a test manager account, it has no campaigns
    manager_customer_id = "2857151978"
    result = asyncio.run(list_campaigns(manager_customer_id))
    logger.info(json.dumps(result, indent=2))

    # find all the test client accounts under the test manager account
    client_accounts = asyncio.run(list_client_accounts(manager_customer_id))
    for client_account in client_accounts:
        logger.debug(json.dumps(client_account, indent=2))
        client_customer_id = client_account["customerClient"]["id"]
        result = asyncio.run(list_campaigns(client_customer_id))
        logger.info(json.dumps(result, indent=2))


def test_create_campaign_bucket():
    client_customer_id = "9711179739"
    campaign_budget = {
        "name": "Test Campaign Budget: " + str(datetime.datetime.now()),
        "amountMicros": 100000,
        "deliveryMethod": "STANDARD"
    }
    result = asyncio.run(create_campaign_budget(client_customer_id, campaign_budget))
    logger.info(json.dumps(result, indent=2))


def test_create_display_campaign():
    client_customer_id = "9711179739"

    # campaign budget to be filled in by the newly created budget
    campaign = {
        "name": "Test Campaign: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "startDate": "2025-10-05",
        "endDate": "2025-12-05",
        "status": "PAUSED",
        "advertisingChannelType": "DISPLAY",
        "manualCpc": {},
        "networkSettings": {
            "targetSearchNetwork": False,
            "targetContentNetwork": True,
            "targetPartnerSearchNetwork": False
        },
        "contains_eu_political_advertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"
    }
    result = asyncio.run(create_display_campaign(client_customer_id, campaign))
    logger.info(json.dumps(result, indent=2))


def test_list_ad_groups():
    client_customer_id = "9711179739"
    result = asyncio.run(list_ad_groups(client_customer_id))
    logger.info(json.dumps(result, indent=2))


def test_list_ads():
    client_customer_id = "9711179739"
    ad_group_id = "186234441837"
    result = asyncio.run(list_ads(client_customer_id, ad_group_id))
    logger.info(json.dumps(result, indent=2))


if __name__ == "__main__":
    # Map test method names to functions
    test_methods = {
        "test_is_manager_account": test_is_manager_account,
        "test_list_client_accounts": test_list_client_accounts,
        "test_list_campaigns": test_list_campaigns,
        "test_create_campaign_bucket": test_create_campaign_bucket,
        "test_create_display_campaign": test_create_display_campaign,
        "test_list_ad_groups": test_list_ad_groups,
        "test_list_ads": test_list_ads,
    }
    
    # Get method name from command line argument
    method_name = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Execute the test method or log error
    test_method = test_methods.get(method_name)
    if test_method:
        test_method()
    else:
        logger.error(f"Invalid method name: {method_name}. Available methods: {', '.join(test_methods.keys())}")
