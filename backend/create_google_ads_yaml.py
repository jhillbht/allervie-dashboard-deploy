import os
import yaml

# This script creates a google-ads.yaml file from environment variables
# It's intended to be used in the Digital Ocean environment

def create_google_ads_yaml():
    """Create google-ads.yaml file from environment variables."""
    config = {
        'client_id': os.environ.get('GOOGLE_ADS_CLIENT_ID', ''),
        'client_secret': os.environ.get('GOOGLE_ADS_CLIENT_SECRET', ''),
        'developer_token': os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', ''),
        'login_customer_id': os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', ''),
        'refresh_token': os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', ''),
        'token_uri': 'https://oauth2.googleapis.com/token',
        'use_proto_plus': os.environ.get('GOOGLE_ADS_USE_PROTO_PLUS', 'true').lower() == 'true',
        'api_version': os.environ.get('GOOGLE_ADS_API_VERSION', 'v17')
    }
    
    # Create the yaml file
    with open('google-ads.yaml', 'w') as f:
        yaml.dump(config, f)
    
    print("Created google-ads.yaml from environment variables")

if __name__ == "__main__":
    create_google_ads_yaml()