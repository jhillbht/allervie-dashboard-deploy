# Allervie Analytics Dashboard with Google Ads API

This repository contains the Allervie Analytics Dashboard with Google Ads API integration, a standalone Python application that connects to Google Ads API to display real campaign performance data.

## Features

- **Real-time Google Ads Data**: Connects directly to Google Ads API to fetch current campaign performance metrics
- **Campaign Analytics**: View detailed performance by campaign with real data
- **Interactive Visualizations**: Charts and graphs that visualize key performance indicators
- **Date Range Filtering**: Filter data by custom date ranges
- **Zero Dependencies Dashboard**: Uses only standard Python libraries for the dashboard UI
- **Automatic Fallback**: Uses mock data when API credentials are not available

## How Google Ads Integration Works

This dashboard connects to the Google Ads API using your provided credentials to fetch real campaign performance data. The integration:

1. Reads Google Ads API credentials from environment variables
2. Creates a YAML configuration file for the Google Ads API client
3. Initializes the Google Ads API client library
4. Executes GAQL (Google Ads Query Language) queries to fetch performance metrics
5. Transforms the API data into dashboard-friendly format
6. Falls back to mock data if API credentials are missing or API calls fail

The dashboard automatically detects whether you have provided valid Google Ads API credentials. If credentials are available, it will use real data; otherwise, it will display sample data.

## Deployment to DigitalOcean App Platform

### Prerequisites
- Digital Ocean account with App Platform access
- Google Ads API credentials:
  - Client ID and Client Secret (from Google Cloud Console)
  - Developer Token (from Google Ads account)
  - Login Customer ID (your Google Ads account ID)
  - Refresh Token (for API access)

### Manual Deployment Steps

1. **Access DigitalOcean Dashboard**
   - Log in to your DigitalOcean account at https://cloud.digitalocean.com
   - Navigate to the App Platform section from the left sidebar

2. **Create a New App**
   - Click the "Create App" button
   - Select "GitHub" as your source
   - Connect to GitHub and authorize DigitalOcean to access your repositories
   - Select the repository: `jhillbht/allervie-dashboard-deploy`
   - Select the branch: `main`

3. **Configure App Settings**
   - **Source Directory**: Leave as `/` (root directory)
   - **Type**: Select "Web Service"
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python app.py`
   - **HTTP Port**: `8080`

4. **Configure Resources**
   - Select the "Basic" plan (smallest size is sufficient)
   - Choose the region closest to your users

5. **Add Environment Variables**
   Add the following environment variables:

   | Name | Value | Type |
   |------|-------|------|
   | FLASK_ENV | production | Plain Text |
   | PORT | 8080 | Plain Text |
   | GOOGLE_ADS_CLIENT_ID | [your_client_id] | Plain Text |
   | GOOGLE_ADS_CLIENT_SECRET | [your_client_secret] | Secret |
   | GOOGLE_ADS_DEVELOPER_TOKEN | [your_developer_token] | Secret |
   | GOOGLE_ADS_LOGIN_CUSTOMER_ID | [your_customer_id] | Plain Text |
   | GOOGLE_ADS_REFRESH_TOKEN | [your_refresh_token] | Secret |
   | GOOGLE_ADS_USE_PROTO_PLUS | true | Plain Text |
   | GOOGLE_ADS_API_VERSION | v17 | Plain Text |

6. **Review and Launch**
   - Review all settings
   - Click "Create Resources"
   - Wait for the build and deployment to complete

7. **Access Your Dashboard**
   - Once deployed, the app will be available at the provided URL
   - The main dashboard is available at the root URL or at `/ads-dashboard`

### Deployment with doctl CLI (Alternative)

1. **Install doctl CLI**
   ```bash
   # On macOS
   brew install doctl
   
   # On other platforms, see:
   # https://docs.digitalocean.com/reference/doctl/how-to/install/
   ```

2. **Login to Digital Ocean**
   ```bash
   doctl auth init
   ```

3. **Deploy the application using the app.yaml file**
   ```bash
   doctl apps create --spec app.yaml
   ```

4. **Update environment variables**
   Edit the app.yaml file to include your actual Google Ads API credentials before deploying.

## Google Ads API Setup

To use real Google Ads data, you'll need to set up the Google Ads API:

1. **Create a Google Cloud project**:
   - Go to https://console.cloud.google.com/
   - Create a new project
   - Enable the Google Ads API

2. **Set up OAuth credentials**:
   - Go to APIs & Services > Credentials
   - Create OAuth client ID credentials (Web application type)
   - Note your Client ID and Client Secret

3. **Get a developer token**:
   - Sign in to your Google Ads account
   - Go to Tools & Settings > Setup > API Center
   - Request a developer token

4. **Generate a refresh token**:
   - Use a tool like https://developers.google.com/oauthplayground/
   - Or use the Google Ads API OAuth flow

## API Endpoints

The dashboard provides the following HTTP endpoints:

- **GET /ads-dashboard**: Main analytics dashboard UI
- **GET /api/google-ads/performance**: Performance metrics in JSON format
- **GET /api/google-ads/campaigns**: Campaign-level data in JSON format
- **GET /api/health**: Health check endpoint with API connection status

## Troubleshooting

If you encounter issues with the Google Ads API:

1. **Check API credentials**:
   - Verify all environment variables are set correctly
   - Make sure your refresh token is valid and not expired

2. **Check customer ID format**:
   - The customer ID should be 10 digits without dashes
   - Example: "1234567890" not "123-456-7890"

3. **Developer token issues**:
   - For testing, use a Google Ads test account
   - Production tokens require approval from Google

4. **Using mock data**:
   - If you can't set up the Google Ads API, the dashboard will use mock data automatically
   - You'll see an indicator on the dashboard when mock data is being used