#!/usr/bin/env python3
"""
Google Ads API Credentials Test Script

This script helps validate Google Ads API credentials before dashboard deployment.
"""

import os
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_status(label, value, is_valid=None):
    """Print a status line with optional validation"""
    if is_valid is None:
        status = ""
    elif is_valid:
        status = "✅"
    else:
        status = "❌"
    
    print(f"{label}: {value} {status}")

def mask_string(text, visible_start=4, visible_end=4):
    """Mask a string to hide sensitive information"""
    if not text:
        return ""
    
    if len(text) <= visible_start + visible_end:
        return "*" * len(text)
    
    return text[:visible_start] + "*" * (len(text) - visible_start - visible_end) + text[-visible_end:]

def main():
    """Main function to test Google Ads API credentials"""
    print_header("Google Ads API Credentials Test")
    
    # Check environment variables
    client_id = os.environ.get('GOOGLE_ADS_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', '')
    developer_token = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
    login_customer_id = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')
    refresh_token = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', '')
    
    # Validate basic presence
    print_status("Client ID", mask_string(client_id) if client_id else "Not set", bool(client_id))
    print_status("Client Secret", mask_string(client_secret) if client_secret else "Not set", bool(client_secret))
    print_status("Developer Token", mask_string(developer_token) if developer_token else "Not set", bool(developer_token))
    print_status("Login Customer ID", login_customer_id if login_customer_id else "Not set", bool(login_customer_id))
    print_status("Refresh Token", mask_string(refresh_token) if refresh_token else "Not set", bool(refresh_token))
    
    # Check customer ID format
    if login_customer_id:
        login_customer_id = login_customer_id.replace('-', '')
        is_valid_format = len(login_customer_id) == 10 and login_customer_id.isdigit()
        print_status("Customer ID Format", "Valid" if is_valid_format else "Invalid (should be 10 digits)", is_valid_format)
    
    # Check if all required credentials are present
    has_all_credentials = bool(client_id and client_secret and developer_token and login_customer_id and refresh_token)
    
    print_header("Test Result")
    if has_all_credentials:
        print("All required Google Ads API credentials are present.")
        print("The dashboard should be able to connect to the Google Ads API.")
        print("\nTo test the full connection, deploy the dashboard and access the API endpoints.")
    else:
        print("Some Google Ads API credentials are missing.")
        print("The dashboard will use mock data instead of real Google Ads data.")
        print("\nTo use real data, make sure all required environment variables are set.")
    
    # Try to import the google-ads library
    try:
        print_header("Testing Google Ads Library")
        import yaml
        from google.ads.googleads.client import GoogleAdsClient
        print("✅ Google Ads library is installed and importable")
        
        # Create a test yaml file
        print("Creating test YAML config...")
        config = {
            'client_id': client_id,
            'client_secret': client_secret,
            'developer_token': developer_token,
            'login_customer_id': login_customer_id.replace('-', ''),
            'refresh_token': refresh_token,
            'use_proto_plus': True
        }
        
        with open('test_google_ads.yaml', 'w') as f:
            yaml.dump(config, f)
        
        if has_all_credentials:
            print("Attempting to initialize Google Ads client...")
            try:
                client = GoogleAdsClient.load_from_storage("test_google_ads.yaml")
                print("✅ Successfully initialized Google Ads client")
            except Exception as e:
                print(f"❌ Error initializing Google Ads client: {str(e)}")
        else:
            print("Skipping client initialization due to missing credentials")
            
    except ImportError:
        print("❌ Google Ads library is not installed")
        print("Run: pip install google-ads")
    except Exception as e:
        print(f"❌ Error testing Google Ads library: {str(e)}")
    
    print_header("Next Steps")
    if has_all_credentials:
        print("1. Deploy the dashboard to DigitalOcean")
        print("2. Access the dashboard at your deployment URL")
        print("3. Check the API Connection Status section at the bottom of the dashboard")
    else:
        print("1. Obtain the missing Google Ads API credentials")
        print("2. Set them as environment variables")
        print("3. Run this script again to verify")

if __name__ == "__main__":
    main()