# Allervie Analytics Dashboard - Update Instructions

## Changes in This Update

This update includes the following improvements to the Allervie Analytics Dashboard:

1. **Fixed Data Refresh Functionality:**
   - Added cache-busting to API requests to ensure fresh data on each refresh
   - Improved data loading with better error handling
   - Added debug logging to help diagnose issues with the API

2. **Added Region and Campaign Type Filtering:**
   - Added a region filter dropdown to filter campaigns by geographical region
   - Added campaign type filter dropdown (Search, Brand, Performance Max, etc.)
   - Added "Active Only" switch to filter active campaigns

3. **Enhanced Campaign Type Detection:**
   - Improved detection of campaign types from campaign names
   - Added support for more campaign types (Display, Video, Shopping)
   - Added visual badges to easily identify campaign types and regions

4. **Improved Error Handling:**
   - Better error handling and user feedback
   - Detailed error messages when API requests fail
   - Consistent response format for all endpoints

## Deployment Instructions

1. Make sure you have the required environment variables set for Google Ads API:
   ```bash
   export GOOGLE_ADS_CLIENT_ID="your-client-id"
   export GOOGLE_ADS_CLIENT_SECRET="your-client-secret"
   export GOOGLE_ADS_DEVELOPER_TOKEN="your-developer-token"
   export GOOGLE_ADS_LOGIN_CUSTOMER_ID="your-customer-id"
   export GOOGLE_ADS_REFRESH_TOKEN="your-refresh-token"
   ```

2. Run the deployment script:
   ```bash
   bash deploy_dashboard_update.sh
   ```

3. The script will:
   - Check if Google Ads API credentials are set
   - Stop any running dashboard instance
   - Start the updated dashboard
   - Provide the URL to access the dashboard

4. Access the dashboard at:
   ```
   http://localhost:8080/ads-dashboard
   ```

## Using the New Features

### Data Refresh

1. Set the start and end dates using the date pickers in the top right
2. Click the "Refresh Data" button to fetch fresh data for the selected date range
3. The dashboard will show a loading indicator while fetching new data

### Filtering Campaigns

1. Use the "Region" dropdown to filter campaigns by geographical region:
   - Southeast
   - Northeast
   - Midwest
   - Southwest
   - West

2. Use the "Campaign Type" dropdown to filter by campaign type:
   - Search
   - Performance Max (PMax)
   - Brand
   - Non-Brand
   - Display
   - Video
   - Shopping

3. Toggle the "Active Only" switch to show only enabled campaigns

### Interpreting Campaign Labels

Campaigns now show helpful badges to identify their characteristics:

- **Campaign Type:** Primary colored badge (blue for Search, green for PMax, yellow for Brand, red for Non-Brand)
- **Region:** Light blue badge showing the geographical region
- **State:** Grey badge showing the state abbreviation
- **Status:** Green badge for ENABLED, yellow for PAUSED, grey for other statuses

## Troubleshooting

If you encounter issues with the dashboard:

1. Check the dashboard log file:
   ```bash
   tail -f dashboard.log
   ```

2. Verify your Google Ads API credentials are correct

3. Use the API status card at the bottom of the dashboard to check if the API connection is working

4. If the dashboard shows "Using Mock Data" in the API status card, check your environment variables

5. To restart the dashboard:
   ```bash
   pkill -f "python dashboard.py"
   python dashboard.py
   ```

For persistent issues, please contact support.