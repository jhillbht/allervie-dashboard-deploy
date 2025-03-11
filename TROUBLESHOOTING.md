# Troubleshooting Guide for Allervie Analytics Dashboard Deployment

This guide addresses common issues that may arise during the deployment of the Allervie Analytics Dashboard with Google Ads API integration to DigitalOcean App Platform.

## Deployment Issues

### Build Failures

**Issue**: The app deployment fails during the build stage.

**Solutions**:
1. Check the build logs:
   ```bash
   doctl apps logs <app-id> --type build
   ```
2. Ensure all required dependencies are in `requirements.txt`.
3. Verify your repository access settings are correct.

### Runtime Errors

**Issue**: The app deploys but fails when running.

**Solutions**:
1. Check the runtime logs:
   ```bash
   doctl apps logs <app-id> --type run
   ```
2. Verify all environment variables are set correctly in the App Platform settings.
3. Check if `create_google_ads_yaml.py` ran correctly during startup.

## Google Ads API Issues

### Authentication Failures

**Issue**: "Authentication failed" or similar errors in logs.

**Solutions**:
1. Verify the Google Ads API credentials:
   - Check that `GOOGLE_ADS_CLIENT_ID` and `GOOGLE_ADS_CLIENT_SECRET` are correctly set
   - Ensure the `GOOGLE_ADS_REFRESH_TOKEN` is valid and not expired
2. Regenerate a refresh token if needed (see below).

### Developer Token Issues

**Issue**: "Developer token not approved" or similar errors.

**Solutions**:
1. Ensure your developer token is approved for the environment you're using:
   - For testing, use a Google Ads test account
   - For production, ensure the token is approved for production access
2. Check that the `GOOGLE_ADS_DEVELOPER_TOKEN` environment variable is set correctly.

### Customer ID Problems

**Issue**: "Customer not found" or similar errors.

**Solutions**:
1. Verify the `GOOGLE_ADS_LOGIN_CUSTOMER_ID` is correctly formatted (10 digits, no dashes).
2. Ensure you have access to this account in Google Ads.
3. If using a manager account (MCC), ensure the account has proper permissions for child accounts.

### API Version Compatibility

**Issue**: API version compatibility errors.

**Solutions**:
1. Set the `GOOGLE_ADS_API_VERSION` to a supported version (v14-v17 are currently supported).
2. Ensure the Google Ads API client library version in `requirements.txt` is compatible with the API version.

## Regenerating Refresh Tokens

If your refresh token has expired or is invalid, you'll need to generate a new one:

1. Use the included script in the repository:
   ```bash
   python backend/get_new_refresh_token.py
   ```
   This will:
   - Open a web browser for Google authentication
   - Request the necessary OAuth scopes
   - Generate a new refresh token

2. Add the new refresh token to your environment variables:
   - In the DigitalOcean dashboard, update the `GOOGLE_ADS_REFRESH_TOKEN` environment variable
   - Or update `app.yaml` and redeploy

## Checking API Connectivity

To verify that your app can connect to the Google Ads API:

1. Access the API test endpoint:
   ```
   https://your-app-url.ondigitalocean.app/api/test-google-ads
   ```

2. This endpoint will:
   - Test authentication with the Google Ads API
   - Return success or detailed error information
   - Include diagnostic information

## Common Error Codes

- `AUTHENTICATION_ERROR`: Issues with OAuth credentials
- `DEVELOPER_TOKEN_PARAMETER_MISSING`: Developer token not provided
- `DEVELOPER_TOKEN_NOT_APPROVED`: Token not approved for the requested API version
- `CUSTOMER_NOT_FOUND`: Customer ID does not exist or you don't have access
- `QUERY_ERROR`: Issues with the GAQL query syntax
- `RESOURCE_EXHAUSTED`: API quotas exceeded

## Getting Additional Help

If you continue to experience issues:

1. Check the Google Ads API documentation: https://developers.google.com/google-ads/api/docs/start
2. Review the Google Ads API client library documentation: https://developers.google.com/google-ads/api/docs/client-libs/python
3. Check the Google Ads API forum: https://groups.google.com/g/adwords-api