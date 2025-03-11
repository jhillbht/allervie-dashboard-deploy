# Allervie Analytics Dashboard Setup Guide

This guide walks you through the process of setting up the Allervie Analytics Dashboard with Google Ads API integration on DigitalOcean App Platform.

## Prerequisites

Before you begin, make sure you have:

1. **Google Ads API Credentials**:
   - A Google Cloud Platform project with the Google Ads API enabled
   - OAuth credentials (client ID and client secret)
   - A Google Ads developer token
   - A Google Ads account with the appropriate access permissions
   - A refresh token for API access

2. **DigitalOcean Account**:
   - An active DigitalOcean account with billing set up
   - Access to the App Platform service

3. **GitHub Access**:
   - For deployment directly from GitHub, you'll need to connect your DigitalOcean account to your GitHub account

## Step 1: Prepare Your Google Ads API Credentials

1. **Create or use an existing Google Cloud Platform project**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Ads API for this project

2. **Create OAuth credentials**:
   - Go to APIs & Services > Credentials
   - Create OAuth client ID credentials
   - Set application type to "Web application"
   - Add authorized redirect URIs (including `http://localhost:8080/oauth2callback`)
   - Note down your Client ID and Client Secret

3. **Get a Google Ads developer token**:
   - Sign in to your Google Ads account
   - Go to Tools & Settings > Setup > API Center
   - Apply for a developer token or use your existing token

4. **Generate a refresh token**:
   - You can generate this locally using the `get_new_refresh_token.py` script
   - Or follow the OAuth flow manually as described in the Google Ads API documentation

## Step 2: Configure Your Deployment

1. **Edit app.yaml**:
   - Open `app.yaml` in this repository
   - Replace the placeholder values with your actual credentials:
     - `YOUR_CLIENT_ID` with your Google OAuth client ID
     - `YOUR_CLIENT_SECRET` with your Google OAuth client secret
     - `YOUR_DEVELOPER_TOKEN` with your Google Ads developer token
     - `YOUR_REFRESH_TOKEN` with your OAuth refresh token
   - Keep the customer ID as is (8127539892) or change it to your specific Google Ads account ID

2. **Optional: Customize deployment settings**:
   - You can modify other settings in `app.yaml` such as:
     - Instance size (`instance_size_slug`)
     - Instance count for scalability
     - Environment variables for configuration

## Step 3: Deploy to DigitalOcean

### Option 1: Deploy using the Web Interface

1. **Log in to DigitalOcean**:
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"

2. **Configure your source**:
   - Select "GitHub" as your source
   - Connect to GitHub if needed
   - Select the repository and branch containing your code

3. **Configure the service**:
   - Edit the source directory (should be root)
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `python backend/create_google_ads_yaml.py && cp backend/config.py.digital_ocean config.py && python app.py`
   - Set HTTP port: `5002`

4. **Configure environment variables**:
   - Add all environment variables from your `app.yaml` file
   - Mark sensitive variables as "Encrypted"

5. **Choose resources**:
   - Select the appropriate plan size
   - Set the region closest to your users

6. **Finalize and deploy**:
   - Review all settings
   - Click "Create Resources"

### Option 2: Deploy using the CLI (Recommended)

1. **Install the DigitalOcean CLI**:
   ```bash
   # macOS
   brew install doctl
   
   # Windows with Scoop
   scoop install doctl
   
   # Linux
   snap install doctl
   ```

2. **Authenticate with DigitalOcean**:
   ```bash
   doctl auth init
   ```
   Follow the prompts to paste your DigitalOcean API token.

3. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```
   This script will:
   - Verify your doctl installation
   - Create a new app using your `app.yaml` configuration
   - Provide instructions for checking deployment status

## Step 4: Verify Deployment

1. **Check deployment status**:
   ```bash
   doctl apps list
   ```
   Find your app ID, then check the details:
   ```bash
   doctl apps get <app-id>
   ```

2. **Check logs if there are issues**:
   ```bash
   doctl apps logs <app-id>
   ```

3. **Access your dashboard**:
   - Once deployed, access the URL provided by DigitalOcean
   - Navigate to `/ads-dashboard` to see the main interface
   - Test API endpoints: `/api/google-ads/performance` and others

## Next Steps

1. **Configure custom domain (optional)**:
   ```bash
   doctl apps create-domain <app-id> --domain dashboard.yourdomain.com
   ```
   Follow the instructions to set up DNS records.

2. **Monitor your app's performance**:
   - Use the DigitalOcean monitoring features
   - Set up alerts for any critical issues

3. **Update your app**:
   When you need to update:
   ```bash
   doctl apps update <app-id> --spec app.yaml
   ```

## Troubleshooting

If you encounter issues, refer to the `TROUBLESHOOTING.md` file in this repository for common problems and solutions.

For additional help:
- Consult the Google Ads API documentation
- Check the DigitalOcean App Platform documentation
- Refer to the original project repository for more detailed information