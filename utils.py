import os
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
from pydantic import Field
from typing import Dict, List

def format_customer_id(
    customer_id: str = Field(description="Customer ID")
    ) -> str:
    """
    Remove any leading or trailing whitespace and any hyphens from the customer ID.

    Args:
        customer_id: Customer ID
    
    Returns:
        str: Formatted customer ID, without leading or trailing whitespace and without hyphens
    """
    customer_id = customer_id.strip()
    customer_id = customer_id.replace("-", "")
    return customer_id


def get_service_account_credentials(
    credentials_path: str = Field(description="Path to service account credentials file"),
    scopes: List[str] = Field(description="Scopes for service account credentials")
    ) -> Credentials:
    """
    Load service account credentials from a file.

    Args:
        credentials_path: Path to service account credentials file
    
    Returns:
        Credentials: Service account credentials
    """
    if not credentials_path:
        raise ValueError("credentials_path is required")
    
    if not os.path.exists(credentials_path):
        raise ValueError(f"credentials_path does not exist: {credentials_path}")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
    except ValueError as e:
        raise ValueError(f"Failed to load credentials from {credentials_path}: {e}")    
    
    return credentials


def generated_request_headers(
    developer_token: str = Field(description="Developer token"), 
    login_customer_id: str = Field(description="Login customer ID"), 
    credentials: Credentials = Field(description="Service account credentials")) -> Dict[str, str]:
    """
    Generate request headers for Google Ads API.
    For more information, see: https://developers.google.com/google-ads/api/rest/auth

    Args:
        developer_token: Developer token
        login_customer_id: Login customer ID
        credentials: Service account credentials
    
    Returns:
        Dict[str, str]: Request headers
    """
    if not developer_token:
        raise ValueError("developer_token is required")
    
    if not login_customer_id:
        raise ValueError("login_customer_id is required")
    
    if not credentials:
        raise ValueError("credentials is required")
    
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    token = credentials.token

    headers = {
        'Authorization': f'Bearer {token}',
        'developer-token': developer_token,
        'login-customer-id': login_customer_id,
        'content-type': 'application/json',
    }

    return headers


