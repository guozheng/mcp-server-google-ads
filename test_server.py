import asyncio
from server import list_client_accounts

if __name__ == "__main__":
    manager_customer_id = "2857151978"
    result = asyncio.run(list_client_accounts(manager_customer_id))
    print(result)