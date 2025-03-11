"""
Google Ads API client for Allervie Dashboard
"""

import os
import json
import sys
import logging
import yaml
from datetime import datetime, timedelta
import locale

# Set locale for currency formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_ads.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Mock data for fallback
MOCK_PERFORMANCE_DATA = {
    "impressions": {
        "value": 125789,
        "change": 8.5,
        "note": "MOCK DATA - No API credentials found"
    },
    "clicks": {
        "value": 5432,
        "change": 12.3,
        "note": "MOCK DATA - No API credentials found"
    },
    "conversions": {
        "value": 321,
        "change": 5.7,
        "note": "MOCK DATA - No API credentials found"
    },
    "cost": {
        "value": "$4,567.89",
        "change": 7.8,
        "note": "MOCK DATA - No API credentials found"
    },
    "conversionRate": {
        "value": "5.9%",
        "change": -2.1,
        "note": "MOCK DATA - No API credentials found"
    },
    "clickThroughRate": {
        "value": "4.3%",
        "change": 3.5,
        "note": "MOCK DATA - No API credentials found"
    },
    "costPerConversion": {
        "value": "$14.23",
        "change": 2.1,
        "note": "MOCK DATA - No API credentials found"
    }
}

MOCK_CAMPAIGNS_DATA = [
    {
        "name": "Brand Awareness Campaign",
        "status": "ENABLED",
        "budget": "$1,500.00",
        "impressions": 45672,
        "clicks": 2341,
        "cost": 895.72,
        "conversions": 187,
        "ctr": 5.1,
        "conversion_rate": 7.99,
        "cost_per_conversion": 4.79,
        "note": "MOCK DATA - No API credentials found"
    },
    {
        "name": "Product Promotion",
        "status": "ENABLED",
        "budget": "$2,000.00",
        "impressions": 62189,
        "clicks": 1978,
        "cost": 1245.63,
        "conversions": 98,
        "ctr": 3.2,
        "conversion_rate": 4.95,
        "cost_per_conversion": 12.71,
        "note": "MOCK DATA - No API credentials found"
    },
    {
        "name": "Seasonal Sale",
        "status": "ENABLED",
        "budget": "$1,200.00",
        "impressions": 17928,
        "clicks": 1113,
        "cost": 689.41,
        "conversions": 36,
        "ctr": 6.2,
        "conversion_rate": 3.23,
        "cost_per_conversion": 19.15,
        "note": "MOCK DATA - No API credentials found"
    }
]

class GoogleAdsClient:
    """
    Google Ads API client for the Allervie Dashboard.
    Uses the Google Ads API to fetch real campaign performance data.
    """
    def __init__(self):
        # Get credentials from environment variables
        self.client_id = os.environ.get('GOOGLE_ADS_CLIENT_ID', '')
        self.client_secret = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', '')
        self.developer_token = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
        self.login_customer_id = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')
        self.refresh_token = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', '')
        self.use_proto_plus = os.environ.get('GOOGLE_ADS_USE_PROTO_PLUS', 'true').lower() == 'true'
        self.api_version = os.environ.get('GOOGLE_ADS_API_VERSION', 'v17')
        
        # Check if we have the necessary credentials
        self.has_credentials = (
            self.client_id and 
            self.client_secret and 
            self.developer_token and 
            self.login_customer_id and 
            self.refresh_token
        )
        
        # Initialize Google Ads client
        self.client = None
        if self.has_credentials:
            logger.info("Google Ads API credentials found. Initializing client.")
            self._create_yaml_config()
            self._initialize_client()
        else:
            logger.warning("Missing Google Ads API credentials. Using mock data.")
    
    def _create_yaml_config(self):
        """Create a google-ads.yaml file from environment variables."""
        try:
            config = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'developer_token': self.developer_token,
                'login_customer_id': self.login_customer_id.replace('-', ''),
                'refresh_token': self.refresh_token,
                'use_proto_plus': self.use_proto_plus,
                'api_version': self.api_version
            }
            
            with open('google-ads.yaml', 'w') as f:
                yaml.dump(config, f)
                
            logger.info("Created google-ads.yaml config file.")
        except Exception as e:
            logger.error(f"Error creating YAML config: {str(e)}")
    
    def _initialize_client(self):
        """Initialize the Google Ads API client."""
        try:
            # Import here to avoid errors if package is not installed
            from google.ads.googleads.client import GoogleAdsClient as GoogleAdsAPIClient
            
            # Load client from YAML file
            self.client = GoogleAdsAPIClient.load_from_storage("google-ads.yaml")
            logger.info("Successfully initialized Google Ads API client.")
        except ImportError:
            logger.error("Google Ads API client library not installed. Install with 'pip install google-ads'.")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Google Ads API client: {str(e)}")
            self.client = None
    
    def get_default_date_range(self):
        """Get a default date range (last 30 days)."""
        today = datetime.now()
        end_date = today - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=30)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def get_performance_data(self, start_date=None, end_date=None):
        """
        Get performance data from the Google Ads API.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with performance metrics
        """
        # If we don't have credentials or client initialization failed, return mock data
        if not self.has_credentials or not self.client:
            return MOCK_PERFORMANCE_DATA
        
        # Use default date range if not specified
        if not start_date or not end_date:
            start_date, end_date = self.get_default_date_range()
        
        try:
            # Get Google Ads service
            googleads_service = self.client.get_service("GoogleAdsService")
            customer_id = self.login_customer_id.replace('-', '')
            
            # Build query to get account performance metrics
            query = f"""
                SELECT
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion
                FROM customer
                WHERE 
                    segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            # Execute the query
            response = googleads_service.search(customer_id=customer_id, query=query)
            
            # Initialize result variables
            impressions = 0
            clicks = 0
            cost_micros = 0
            conversions = 0
            
            # Aggregate the metrics
            for row in response:
                metrics = row.metrics
                impressions += metrics.impressions
                clicks += metrics.clicks
                cost_micros += metrics.cost_micros
                conversions += metrics.conversions
            
            # Calculate derived metrics
            cost_dollars = cost_micros / 1000000 if cost_micros else 0
            ctr = (clicks / impressions * 100) if impressions else 0
            conversion_rate = (conversions / clicks * 100) if clicks else 0
            cost_per_conversion = (cost_dollars / conversions) if conversions else 0
            
            # Get data from previous period for change calculation
            date_diff = datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')
            days = date_diff.days + 1
            
            prev_end_date = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)
            prev_start_date = prev_end_date - timedelta(days=days-1)
            
            prev_query = f"""
                SELECT
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM customer
                WHERE 
                    segments.date BETWEEN '{prev_start_date.strftime('%Y-%m-%d')}' AND '{prev_end_date.strftime('%Y-%m-%d')}'
            """
            
            prev_response = googleads_service.search(customer_id=customer_id, query=prev_query)
            
            # Initialize previous period metrics
            prev_impressions = 0
            prev_clicks = 0
            prev_cost_micros = 0
            prev_conversions = 0
            
            # Aggregate the previous period metrics
            for row in prev_response:
                metrics = row.metrics
                prev_impressions += metrics.impressions
                prev_clicks += metrics.clicks
                prev_cost_micros += metrics.cost_micros
                prev_conversions += metrics.conversions
            
            # Calculate changes
            impressions_change = ((impressions - prev_impressions) / prev_impressions * 100) if prev_impressions else 0
            clicks_change = ((clicks - prev_clicks) / prev_clicks * 100) if prev_clicks else 0
            cost_change = ((cost_micros - prev_cost_micros) / prev_cost_micros * 100) if prev_cost_micros else 0
            conversions_change = ((conversions - prev_conversions) / prev_conversions * 100) if prev_conversions else 0
            
            # Previous period derived metrics
            prev_ctr = (prev_clicks / prev_impressions * 100) if prev_impressions else 0
            prev_conversion_rate = (prev_conversions / prev_clicks * 100) if prev_clicks else 0
            prev_cost_dollars = prev_cost_micros / 1000000 if prev_cost_micros else 0
            prev_cost_per_conversion = (prev_cost_dollars / prev_conversions) if prev_conversions else 0
            
            # Calculate derived metric changes
            ctr_change = ctr - prev_ctr
            conversion_rate_change = conversion_rate - prev_conversion_rate
            cost_per_conversion_change = ((cost_per_conversion - prev_cost_per_conversion) / prev_cost_per_conversion * 100) if prev_cost_per_conversion else 0
            
            # Format the data for the dashboard
            return {
                "impressions": {
                    "value": int(impressions),
                    "change": round(impressions_change, 1)
                },
                "clicks": {
                    "value": int(clicks),
                    "change": round(clicks_change, 1)
                },
                "conversions": {
                    "value": int(conversions),
                    "change": round(conversions_change, 1)
                },
                "cost": {
                    "value": locale.currency(cost_dollars, grouping=True),
                    "change": round(cost_change, 1)
                },
                "conversionRate": {
                    "value": f"{conversion_rate:.1f}%",
                    "change": round(conversion_rate_change, 1)
                },
                "clickThroughRate": {
                    "value": f"{ctr:.1f}%",
                    "change": round(ctr_change, 1)
                },
                "costPerConversion": {
                    "value": locale.currency(cost_per_conversion, grouping=True),
                    "change": round(cost_per_conversion_change, 1)
                }
            }
        
        except Exception as e:
            logger.error(f"Error fetching performance data from Google Ads API: {str(e)}")
            
            # Return mock data with error note
            error_data = MOCK_PERFORMANCE_DATA.copy()
            for key in error_data:
                error_data[key]["note"] = f"ERROR: {str(e)}"
            return error_data
    
    def get_campaigns_data(self, start_date=None, end_date=None):
        """
        Get campaigns data from the Google Ads API.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of campaign data dictionaries
        """
        # If we don't have credentials or client initialization failed, return mock data
        if not self.has_credentials or not self.client:
            return MOCK_CAMPAIGNS_DATA
        
        # Use default date range if not specified
        if not start_date or not end_date:
            start_date, end_date = self.get_default_date_range()
        
        try:
            # Get Google Ads service
            googleads_service = self.client.get_service("GoogleAdsService")
            customer_id = self.login_customer_id.replace('-', '')
            
            # Build query to get campaign performance
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign_budget.amount_micros,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.conversion_rate,
                    metrics.cost_per_conversion
                FROM campaign
                WHERE 
                    segments.date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY metrics.cost_micros DESC
            """
            
            # Execute the query
            response = googleads_service.search(customer_id=customer_id, query=query)
            
            # Process the results
            campaigns = []
            seen_campaigns = set()
            
            for row in response:
                campaign = row.campaign
                metrics = row.metrics
                budget = row.campaign_budget
                
                # Skip duplicate campaign entries
                if campaign.id in seen_campaigns:
                    continue
                seen_campaigns.add(campaign.id)
                
                # Convert micros to dollars
                budget_dollars = budget.amount_micros / 1000000 if budget.amount_micros else 0
                cost_dollars = metrics.cost_micros / 1000000 if metrics.cost_micros else 0
                
                # Calculate other metrics
                ctr = metrics.ctr
                conversion_rate = metrics.conversion_rate
                cost_per_conversion = metrics.cost_per_conversion
                
                campaigns.append({
                    "name": campaign.name,
                    "status": campaign.status.name,
                    "budget": locale.currency(budget_dollars, grouping=True),
                    "impressions": int(metrics.impressions),
                    "clicks": int(metrics.clicks),
                    "cost": cost_dollars,
                    "conversions": int(metrics.conversions),
                    "ctr": round(ctr, 1),
                    "conversion_rate": round(conversion_rate, 2),
                    "cost_per_conversion": round(cost_per_conversion, 2)
                })
            
            if not campaigns:
                logger.warning("No campaign data found for the specified date range")
                return MOCK_CAMPAIGNS_DATA
                
            return campaigns
            
        except Exception as e:
            logger.error(f"Error fetching campaign data from Google Ads API: {str(e)}")
            
            # Return mock data with error note
            error_data = MOCK_CAMPAIGNS_DATA.copy()
            for campaign in error_data:
                campaign["note"] = f"ERROR: {str(e)}"
            return error_data

# Create a singleton instance of the client
ads_client = GoogleAdsClient()