# mcp-server-google-ads
An MCP server for Google Ads

## Background

Google Ads is a paid search advertising platform that allows users to create and manage their own advertising campaigns. It provides a REST API that allows users to access and manage their advertising campaigns, including creating and managing campaigns, ad groups, and ads.

   * [Google Ads API](https://developers.google.com/google-ads/api)
   * [Introduction](https://developers.google.com/google-ads/api/docs/get-started/introduction)
   * [Authentication](https://developers.google.com/google-ads/api/docs/oauth/overview), we are using [service account authentication](https://developers.google.com/google-ads/api/docs/oauth/service-accounts)
   * [REST API Code Examples](https://developers.google.com/google-ads/api/rest/examples): in this repository, we are mostly using REST APIs. There are also libraries supporting different languages, for examples using the libraries, see [Google Ads API Libraries Examples](https://developers.google.com/google-ads/api/samples)
  

## Google Ads API Setup

We are using service account authentication to access Google Ads API. All the details including screenshots are available in the service account authentication section of the [Google Ads API documentation](https://developers.google.com/google-ads/api/docs/oauth/service-accounts).

### Create a Google Ads Account and Get a Developer Token

1. Go to the [Google Ads Console](https://ads.google.com/home)
2. Click on 'Get started'
3. Follow the instructions to create a Google Ads account, this will be your manager account.
4. Apply for a developer token by following the instructions here: [Google Ads API Token Application](https://support.google.com/adspolicy/contact/new_token_application). Initially, you can automatically get a test developer token, which only allows you to access test accounts. To get a production developer token, you need to submit a request (using this form) to Google Ads API Console and wait a few days for approval before you can get the official developer token that works with all the accounts.
5. Create a test manager account. The test developer token allows you to access test accounts only.

### Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project selector in the top left corner
3. Click on 'New Project'
4. Enter a project name
5. Click on 'Create'
6. Wait for the project to be created
7. Click on the project name
8. Click on 'Enable APIs and Services'
9. Search for 'Google Ads API'
10. Click on 'Enable'
11. Click on 'Credentials'
12. Click on 'Create Credentials'
13. Select 'Service Account'
14. Enter a service account name
15. Click on 'Create'
16. Click on 'Keys'
17. Click on 'Add Key'
18. Select 'JSON'
19. Click on 'Create'
20. Save the JSON file to a secure location
21. Set the environment variable `GOOGLE_ADS_CREDENTIALS_PATH` to the path of the JSON file
22. Set the environment variable `GOOGLE_ADS_LOGIN_CUSTOMER_ID` to the login customer ID
23. Set the environment variable `GOOGLE_ADS_DEVELOPER_TOKEN` to the developer token

### Add the Service Account to the Google Ads Account

1. When you only have the test developer token, it can only access test accounts. Add your service account email to the test manager account. 
2. When you have the production developer token, you can add your service account email to the production manager account. 

## Project Setup

### Download and Save the Service Account JSON File
When you set up the service account, download the JSON file `service_account_key.json` and save it to a secure location. This file will be used to authenticate your requests to the Google Ads API.

Copy `service_account_key.json` to the root directory of the project.

Note: if you use a different name for the service account key file, please make sure you add it to `.gitignore`.

### Environment Variables
Copy from .env.example to .env and fill in the empty values.

   1. `GOOGLE_ADS_CREDENTIALS_PATH (required)`: Path to the service account JSON file, e.g. `service_account_key.json`
   2. `GOOGLE_ADS_LOGIN_CUSTOMER_ID (required)`: Login customer ID, this could be the manager account id, or the client account id under a manager account
   3. `GOOGLE_ADS_DEVELOPER_TOKEN (required)`: Developer token, this could be the test developer token, or the production developer token
   4. `GOOGLE_ADS_IMPERSONATION_EMAIL (optional)`: Email to impersonate with the service account (typically your admin email)

### Double Check .gitignore

Make sure secret file `service_account_key.json`, environment file `.env`, virtual environment `.venv` are included in `.gitignore` and not checked into version control system.

### Enter the Virtual Environment and Install Dependencies

```bash
uv venv .venv
source venv/bin/activate
uv sync
```

### Run the Tests
```bash
uv run test_server.py
```

## Set up MCP Server and Client (Using Claude Desktop on MacOS as the Example)

1. Download and install [Claude Desktop](https://claude.ai/download)
2. Go to settings -> Developer -> Local MCP servers -> Edit Config
3. It will locate `caldude_desktop_config.json`, use your favorite text editor to open it and edit it
4. Add the following content to the file:
```json
{
    "mcpServers": {
      "googleAdsServer": {
        "command": "<path_to_this_git_repo>/mcp-server-google-ads/.venv/bin/python",
        "args": ["<path_to_this_git_repo>/mcp-server-google-ads/server.py"],
        "env": {
          "GOOGLE_ADS_AUTH_TYPE": "service_account",
          "GOOGLE_ADS_CREDENTIALS_PATH": "<path_to_this_git_repo>/mcp-server-google-ads/service_account_key.json",
          "GOOGLE_ADS_DEVELOPER_TOKEN": "<your_developer_token>",
          "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "<your_login_customer_id>"
        }
      }
    }
  }
```
5. Save the file
6. Restart Claude Desktop
7. Go to settings -> Connectors, you will see a new connector named `googleAdsServer`, you can configure the tools in Configure


## References and Credits

   1. [mcp-google-ads](https://github.com/cohnen/mcp-google-ads): borrowed some code and ideas from this repository. Instead of supporting both user-login based oauth, this repo only supports service account authentication.
   2. [Google Ads API](https://developers.google.com/google-ads/api)
   3. [Google Ads REST API Examples](https://developers.google.com/google-ads/api/rest/overview)


   
   