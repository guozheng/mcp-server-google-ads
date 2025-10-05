import asyncio
from server import list_client_accounts, list_campaigns, is_manager_account
import json
import logging

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


if __name__ == "__main__":
    # test_is_manager_account()
    # test_list_client_accounts()
    test_list_campaigns()