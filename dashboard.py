"""
Standalone Allervie Analytics Dashboard - Google Ads API Integration

This file is a self-contained Python application that connects to the 
Google Ads API using environment variables and displays the data in a dashboard.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the Google Ads client
try:
    from google_ads_client import ads_client
    logger.info("Successfully imported Google Ads client")
except Exception as e:
    logger.error(f"Failed to import Google Ads client: {str(e)}")
    # Create a dummy client for fallback
    class DummyClient:
        def __init__(self):
            self.has_credentials = False
        
        def get_performance_data(self, start_date=None, end_date=None):
            return PERFORMANCE_DATA
        
        def get_campaigns_data(self, start_date=None, end_date=None):
            return CAMPAIGNS_DATA
    
    ads_client = DummyClient()
    logger.info("Using dummy Google Ads client")

# HTML content for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Allervie Analytics Dashboard</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric-card {
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
            margin-bottom: 20px;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
        }
        .metric-change {
            font-size: 0.9rem;
        }
        .positive-change {
            color: #10b981;
        }
        .negative-change {
            color: #ef4444;
        }
        .header {
            background-color: #f8f9fa;
            padding: 20px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .date-picker {
            max-width: 150px;
        }
        .data-note {
            font-size: 0.8rem;
            color: #666;
            font-style: italic;
        }
        
        /* Funnel Visualization Styles */
        .funnel-container {
            padding: 20px;
            background-color: #222;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
            color: white;
            margin-bottom: 20px;
        }
        .funnel-step {
            position: relative;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        .funnel-step:hover {
            transform: translateX(5px);
        }
        .funnel-bar {
            height: 40px;
            background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
            border-radius: 4px;
            display: flex;
            align-items: center;
            padding-left: 15px;
            color: white;
            font-weight: 500;
            position: relative;
            overflow: hidden;
            box-shadow: 0 3px 5px rgba(0, 0, 0, 0.3);
        }
        .funnel-label {
            z-index: 1;
            display: flex;
            justify-content: space-between;
            width: 100%;
            padding-right: 15px;
        }
        .funnel-value {
            font-weight: bold;
            text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.5);
        }
        .funnel-rate {
            font-size: 0.85rem;
            color: #a1a1aa;
            margin-left: 15px;
        }
        
        /* Badge Styles */
        .badge {
            display: inline-block;
            padding: 0.35em 0.65em;
            font-size: 0.75em;
            font-weight: 700;
            line-height: 1;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.375rem;
        }
        .badge-success { background-color: #28a745; }
        .badge-warning { background-color: #ffc107; color: #212529; }
        .badge-secondary { background-color: #6c757d; }
        .badge-info { background-color: #0dcaf0; }
        .badge-primary { background-color: #0d6efd; }
        .badge-danger { background-color: #dc3545; }
        .badge-dark { background-color: #212529; }
        
        /* Connection status indicators */
        .connection-card {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-green { background-color: #4CAF50; }
        .status-amber { background-color: #FFC107; }
        .status-red { background-color: #F44336; }
        .status-box {
            display: flex;
            align-items: center;
            padding: 8px 16px;
            border-radius: 4px;
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
        }
        .status-box.connected { background-color: #e8f5e9; border-color: #a5d6a7; }
        .status-box.warning { background-color: #fff8e1; border-color: #ffe082; }
        .status-box.disconnected { background-color: #ffebee; border-color: #ef9a9a; }
        
        /* Date Range Styles */
        .date-range-picker {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .date-range-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }
        .date-range-buttons .btn {
            min-width: 90px;
        }
        .date-range-buttons .btn:hover {
            transform: translateY(-2px);
            transition: transform 0.2s;
        }
        .custom-date-label {
            font-size: 0.85rem;
            margin-bottom: 4px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <h1>Allervie Analytics Dashboard</h1>
                    <p class="text-muted">Google Ads Performance Data</p>
                </div>
                <div class="col-md-6">
                    <div class="date-range-picker">
                        <div class="date-range-buttons">
                            <button type="button" class="btn btn-outline-primary btn-sm" data-range="7">Last 7 days</button>
                            <button type="button" class="btn btn-outline-primary btn-sm active" data-range="30">Last 30 days</button>
                            <button type="button" class="btn btn-outline-primary btn-sm" data-range="90">Last 90 days</button>
                            <button type="button" class="btn btn-outline-primary btn-sm" data-range="current-month">This Month</button>
                            <button type="button" class="btn btn-outline-primary btn-sm" data-range="last-month">Last Month</button>
                            <button type="button" class="btn btn-outline-primary btn-sm" data-range="quarter">Last Quarter</button>
                            <button type="button" class="btn btn-outline-primary btn-sm" data-range="ytd">Year to Date</button>
                            <button type="button" class="btn btn-outline-primary btn-sm" data-range="custom">Custom</button>
                        </div>
                        <div class="row">
                            <div class="col-md-8">
                                <div class="d-flex">
                                    <div class="me-2">
                                        <div class="custom-date-label">Start Date</div>
                                        <input type="date" id="start-date" class="form-control form-control-sm date-picker">
                                    </div>
                                    <div class="me-2">
                                        <div class="custom-date-label">End Date</div>
                                        <input type="date" id="end-date" class="form-control form-control-sm date-picker">
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 d-flex align-items-end">
                                <button id="refresh-btn" class="btn btn-primary btn-sm w-100">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-clockwise me-1" viewBox="0 0 16 16">
                                        <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                                        <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                                    </svg>
                                    Refresh Data
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container mt-4">
        <!-- Performance Metrics -->
        <div class="row" id="metrics-container">
            <!-- Metrics will be loaded here -->
            <div class="col-12">
                <div class="d-flex justify-content-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Performance Chart -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Performance Overview</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="performance-chart" height="300"></canvas>
                        <div id="chart-note" class="data-note mt-2"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Conversion Funnel -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="funnel-container">
                    <h5 class="mb-4">Conversion Funnel</h5>
                    <div id="funnel-steps">
                        <div class="d-flex justify-content-center">
                            <div class="spinner-border text-light" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h5>Conversion Metrics</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6 mb-3">
                                <h6 class="text-muted">Click-Through Rate</h6>
                                <div id="ctr-value" class="h3">0.0%</div>
                            </div>
                            <div class="col-6 mb-3">
                                <h6 class="text-muted">Conversion Rate</h6>
                                <div id="conv-rate-value" class="h3">0.0%</div>
                            </div>
                            <div class="col-6">
                                <h6 class="text-muted">Cost per Click</h6>
                                <div id="cpc-value" class="h3">$0.00</div>
                            </div>
                            <div class="col-6">
                                <h6 class="text-muted">Cost per Conversion</h6>
                                <div id="cpa-value" class="h3">$0.00</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Campaign Table -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>Campaign Performance</h5>
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <select id="region-filter" class="form-select form-select-sm">
                                    <option value="all">All Regions</option>
                                    <option value="southeast">Southeast</option>
                                    <option value="northeast">Northeast</option>
                                    <option value="midwest">Midwest</option>
                                    <option value="southwest">Southwest</option>
                                    <option value="west">West</option>
                                </select>
                            </div>
                            <div class="me-3">
                                <select id="campaign-type-filter" class="form-select form-select-sm">
                                    <option value="all">All Campaign Types</option>
                                    <option value="Search">Search</option>
                                    <option value="PMax">Performance Max</option>
                                    <option value="Brand">Brand</option>
                                    <option value="NonBrand">Non-Brand</option>
                                    <option value="Display">Display</option>
                                    <option value="Video">Video</option>
                                    <option value="Shopping">Shopping</option>
                                </select>
                            </div>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="show-active-only">
                                <label class="form-check-label" for="show-active-only">Active Only</label>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover" id="campaigns-table">
                                <thead>
                                    <tr>
                                        <th>Campaign</th>
                                        <th>Status</th>
                                        <th>Budget</th>
                                        <th>Impressions</th>
                                        <th>Clicks</th>
                                        <th>CTR</th>
                                        <th>Conv.</th>
                                        <th>Conv. Rate</th>
                                        <th>Cost</th>
                                        <th>Cost/Conv.</th>
                                    </tr>
                                </thead>
                                <tbody id="campaigns-tbody">
                                    <!-- Campaign data will be loaded here -->
                                    <tr>
                                        <td colspan="10" class="text-center">
                                            <div class="spinner-border text-primary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <div id="campaigns-note" class="data-note mt-2"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- API Status Card -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>API Connection Status</h5>
                        <button id="auth-btn" class="btn btn-sm btn-outline-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-key" viewBox="0 0 16 16">
                                <path d="M0 8a4 4 0 0 1 7.465-2H14a.5.5 0 0 1 .354.146l1.5 1.5a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0L13 9.207l-.646.647a.5.5 0 0 1-.708 0L11 9.207l-.646.647a.5.5 0 0 1-.708 0L9 9.207l-.646.647A.5.5 0 0 1 8 10h-.535A4 4 0 0 1 0 8zm4-3a3 3 0 1 0 2.712 4.285A.5.5 0 0 1 7.163 9h.63l.853-.854a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 0 1 .708 0l.646.647.793-.793-1-1h-6.63a.5.5 0 0 1-.451-.285A3 3 0 0 0 4 5z"/>
                                <path d="M4 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
                            </svg>
                            Authentication
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="connection-card">
                            <div id="ads-api-status" class="status-box">
                                <span class="status-indicator status-amber"></span>
                                <span>Google Ads API: Checking...</span>
                            </div>
                            <div id="data-api-status" class="status-box">
                                <span class="status-indicator status-amber"></span>
                                <span>Performance Data: Checking...</span>
                            </div>
                            <div id="campaign-api-status" class="status-box">
                                <span class="status-indicator status-amber"></span>
                                <span>Campaign Data: Checking...</span>
                            </div>
                        </div>
                        <div id="api-status" class="mt-2" style="display:none;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Auth Instructions Modal -->
        <div class="modal fade" id="authModal" tabindex="-1" aria-labelledby="authModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="authModalLabel">Google Ads API Authentication</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <strong>Authentication Process</strong>
                            <p>This dashboard uses the Google Ads API to fetch real data. You'll need to set up authentication to access your account data.</p>
                        </div>
                        
                        <div class="card mb-3">
                            <div class="card-header">Step 1: Set Up OAuth Credentials</div>
                            <div class="card-body">
                                <p>Ensure you have the following credentials configured as environment variables:</p>
                                <ul>
                                    <li><strong>Client ID</strong> - From Google Cloud Console</li>
                                    <li><strong>Client Secret</strong> - From Google Cloud Console</li>
                                    <li><strong>Developer Token</strong> - From Google Ads account</li>
                                    <li><strong>Refresh Token</strong> - Generated via OAuth flow</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="card mb-3">
                            <div class="card-header">Step 2: Update Environment Variables</div>
                            <div class="card-body">
                                <p>Update your environment variables in DigitalOcean App Platform:</p>
                                <pre><code>GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id</code></pre>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">Step 3: Generate a Refresh Token</div>
                            <div class="card-body">
                                <p>To generate a refresh token, run the token script in your terminal:</p>
                                <pre><code>python backend/get_new_refresh_token.py</code></pre>
                                <p>Follow the browser prompts to authenticate with your Google account.</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Set API base URL
        const API_BASE_URL = '';

        // DOM elements
        const metricsContainer = document.getElementById('metrics-container');
        const campaignsTable = document.getElementById('campaigns-table');
        const campaignsBody = document.getElementById('campaigns-tbody');
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        const refreshBtn = document.getElementById('refresh-btn');
        const apiStatus = document.getElementById('api-status');
        const chartNote = document.getElementById('chart-note');
        const campaignsNote = document.getElementById('campaigns-note');
        const regionFilterSelect = document.getElementById('region-filter');
        const campaignTypeFilterSelect = document.getElementById('campaign-type-filter');
        const showActiveOnlyCheckbox = document.getElementById('show-active-only');
        
        // Chart variables
        let performanceChart = null;
        
        // Store loaded campaign data
        let campaignsData = [];
        
        // Define regions by state abbreviations
        const stateRegions = {
            // Southeast
            'AL': 'southeast', // Alabama
            'AR': 'southeast', // Arkansas
            'FL': 'southeast', // Florida
            'GA': 'southeast', // Georgia
            'KY': 'southeast', // Kentucky
            'LA': 'southeast', // Louisiana
            'MS': 'southeast', // Mississippi
            'NC': 'southeast', // North Carolina
            'SC': 'southeast', // South Carolina
            'TN': 'southeast', // Tennessee
            'VA': 'southeast', // Virginia
            'WV': 'southeast', // West Virginia
            
            // Northeast
            'CT': 'northeast', // Connecticut
            'DE': 'northeast', // Delaware
            'ME': 'northeast', // Maine
            'MD': 'northeast', // Maryland
            'MA': 'northeast', // Massachusetts
            'NH': 'northeast', // New Hampshire
            'NJ': 'northeast', // New Jersey
            'NY': 'northeast', // New York
            'PA': 'northeast', // Pennsylvania
            'RI': 'northeast', // Rhode Island
            'VT': 'northeast', // Vermont
            
            // Midwest
            'IL': 'midwest', // Illinois
            'IN': 'midwest', // Indiana
            'IA': 'midwest', // Iowa
            'KS': 'midwest', // Kansas
            'MI': 'midwest', // Michigan
            'MN': 'midwest', // Minnesota
            'MO': 'midwest', // Missouri
            'NE': 'midwest', // Nebraska
            'ND': 'midwest', // North Dakota
            'OH': 'midwest', // Ohio
            'SD': 'midwest', // South Dakota
            'WI': 'midwest', // Wisconsin
            
            // Southwest
            'AZ': 'southwest', // Arizona
            'NM': 'southwest', // New Mexico
            'OK': 'southwest', // Oklahoma
            'TX': 'southwest', // Texas
            
            // West
            'AK': 'west', // Alaska
            'CA': 'west', // California
            'CO': 'west', // Colorado
            'HI': 'west', // Hawaii
            'ID': 'west', // Idaho
            'MT': 'west', // Montana
            'NV': 'west', // Nevada
            'OR': 'west', // Oregon
            'UT': 'west', // Utah
            'WA': 'west', // Washington
            'WY': 'west'  // Wyoming
        };
        
        // Function to get state abbreviation from campaign name
        function getStateFromCampaignName(campaignName) {
            // Check if campaign name starts with two letters followed by a dash
            if (campaignName && campaignName.length >= 3 && campaignName.charAt(2) === '-') {
                return campaignName.substring(0, 2).toUpperCase();
            }
            
            // Secondary pattern: Check for state code in parentheses like "Campaign Name (TX)"
            if (campaignName && campaignName.includes('(') && campaignName.includes(')')) {
                const match = campaignName.match(/\(([A-Za-z]{2})\)/);
                if (match && match[1]) {
                    return match[1].toUpperCase();
                }
            }
            
            // Third pattern: Check for state name in the campaign name
            const stateNames = {
                'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
                'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
                'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
                'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
                'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
                'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
                'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
                'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
                'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
                'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
                'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
                'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
                'wisconsin': 'WI', 'wyoming': 'WY'
            };
            
            if (campaignName) {
                const lowerName = campaignName.toLowerCase();
                for (const stateName in stateNames) {
                    if (lowerName.includes(stateName)) {
                        return stateNames[stateName];
                    }
                }
            }
            
            return null;
        }
        
        // Function to get region from campaign name
        function getRegionFromCampaignName(campaignName) {
            const state = getStateFromCampaignName(campaignName);
            if (state && stateRegions[state]) {
                return stateRegions[state];
            }
            
            // Additional heuristics for region detection
            if (campaignName) {
                const lowerName = campaignName.toLowerCase();
                
                // Check for direct region mentions
                if (lowerName.includes('southeast') || lowerName.includes('south east')) {
                    return 'southeast';
                } else if (lowerName.includes('northeast') || lowerName.includes('north east')) {
                    return 'northeast';
                } else if (lowerName.includes('midwest') || lowerName.includes('mid west')) {
                    return 'midwest';
                } else if (lowerName.includes('southwest') || lowerName.includes('south west')) {
                    return 'southwest';
                } else if (lowerName.includes('west coast') || lowerName.includes('pacific')) {
                    return 'west';
                }
            }
            
            return 'other';
        }
        
        // Function to detect campaign type from campaign name
        function getCampaignType(campaignName) {
            if (!campaignName) return 'Unknown';
            
            // Check for specific patterns in the campaign name
            const lowerName = campaignName.toLowerCase();
            
            // PMax/Performance Max detection
            if (lowerName.includes('pmax') || 
                lowerName.includes('performance max') || 
                lowerName.includes('performance_max') ||
                lowerName.includes('performancemax')) {
                return 'PMax';
            } 
            
            // Search campaign detection
            else if (lowerName.includes('search') || 
                    lowerName.includes('_srch_') || 
                    lowerName.includes('-srch-')) {
                // Check if it's also a brand campaign
                if (lowerName.includes('brand') || 
                    lowerName.includes('_b_') ||
                    lowerName.includes('-b-')) {
                    return 'Brand';
                } 
                // Check if it's a non-brand campaign
                else if (lowerName.includes('nonbrand') || 
                        lowerName.includes('non-brand') || 
                        lowerName.includes('_nb_') ||
                        lowerName.includes('-nb-')) {
                    return 'NonBrand';
                }
                // Otherwise, just a regular search campaign
                return 'Search';
            } 
            
            // Other brand detection
            else if (lowerName.includes('brand_') || 
                    lowerName.includes('branded') || 
                    lowerName.includes('_brand') || 
                    lowerName.includes('-brand')) {
                return 'Brand';
            } 
            
            // Other non-brand detection
            else if (lowerName.includes('nonbrand') || 
                    lowerName.includes('non-brand') || 
                    lowerName.includes('_non_brand') || 
                    lowerName.includes('-non-brand')) {
                return 'NonBrand';
            }
            
            // G_ pattern Google campaign detection
            if (campaignName.startsWith('G_')) {
                if (campaignName.includes('_Brand_') || campaignName.includes('-Brand-')) {
                    return 'Brand';
                } else if (campaignName.includes('_NonBrand_') || campaignName.includes('-NonBrand-')) {
                    return 'NonBrand';
                }
            }
            
            // Additional campaign type detection
            if (lowerName.includes('display') || lowerName.includes('_dsp_')) {
                return 'Display';
            } else if (lowerName.includes('video') || lowerName.includes('youtube')) {
                return 'Video';
            } else if (lowerName.includes('shopping') || lowerName.includes('_sh_')) {
                return 'Shopping';
            }
            
            // Default to Search if none of the above patterns match
            return 'Search';
        }

        // Set default dates
        const today = new Date();
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(today.getDate() - 30);
        
        startDateInput.value = formatDate(thirtyDaysAgo);
        endDateInput.value = formatDate(today);

        // Set up date range buttons
        function setupDateRangeButtons() {
            const dateRangeButtons = document.querySelectorAll('.date-range-buttons [data-range]');
            
            dateRangeButtons.forEach(button => {
                button.addEventListener('click', () => {
                    // Remove active class from all buttons
                    dateRangeButtons.forEach(btn => btn.classList.remove('active'));
                    
                    // Add active class to clicked button
                    button.classList.add('active');
                    
                    const range = button.getAttribute('data-range');
                    const today = new Date();
                    const end = new Date(today); // Default end date is today
                    const start = new Date(today); // Will be adjusted based on range
                    
                    if (range === 'custom') {
                        // Do nothing, just let user select their custom dates
                        return;
                    } else if (range === 'current-month') {
                        // First day of current month to today
                        start.setDate(1);
                    } else if (range === 'last-month') {
                        // First day of last month to last day of last month
                        end.setDate(0); // Last day of previous month
                        start.setDate(1); // First day of current month
                        start.setMonth(start.getMonth() - 1); // First day of last month
                    } else if (range === 'quarter') {
                        // 90 days ago to today
                        start.setDate(today.getDate() - 90);
                    } else if (range === 'ytd') {
                        // January 1st to today
                        start.setMonth(0);
                        start.setDate(1);
                    } else {
                        // For 7, 30, 90 days ranges
                        start.setDate(end.getDate() - parseInt(range));
                    }
                    
                    // Update date inputs
                    startDateInput.value = formatDate(start);
                    endDateInput.value = formatDate(end);
                    
                    // Automatically refresh data
                    loadPerformanceData();
                    loadCampaigns();
                });
            });
        }

        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            setupDateRangeButtons();
            setupAuthButton();
            loadPerformanceData();
            loadCampaigns();
            checkApiStatus();
        });
        
        // Setup Auth Button
        function setupAuthButton() {
            const authBtn = document.getElementById('auth-btn');
            const authModal = new bootstrap.Modal(document.getElementById('authModal'));
            
            authBtn.addEventListener('click', () => {
                authModal.show();
            });
        }

        refreshBtn.addEventListener('click', () => {
            console.log("Refresh button clicked");
            console.log("Date range:", startDateInput.value, "to", endDateInput.value);
            loadPerformanceData();
            loadCampaigns();
            checkApiStatus();
        });

        // Filter event listeners
        regionFilterSelect.addEventListener('change', () => {
            displayFilteredCampaigns();
        });
        
        campaignTypeFilterSelect.addEventListener('change', () => {
            displayFilteredCampaigns();
        });
        
        showActiveOnlyCheckbox.addEventListener('change', () => {
            displayFilteredCampaigns();
        });

        // Format date helper
        function formatDate(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        // Format number helper
        function formatNumber(num) {
            return new Intl.NumberFormat('en-US').format(num);
        }

        // Format currency helper
        function formatCurrency(num) {
            return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
        }

        // Update API status indicator
        function updateApiStatusIndicator(elementId, status, text) {
            const element = document.getElementById(elementId);
            const indicator = element.querySelector('.status-indicator');
            const statusText = element.querySelector('span:last-child');
            
            // Clear all status classes
            element.classList.remove('connected', 'warning', 'disconnected');
            indicator.classList.remove('status-green', 'status-amber', 'status-red');
            
            // Set new status
            if (status === 'connected') {
                element.classList.add('connected');
                indicator.classList.add('status-green');
            } else if (status === 'warning') {
                element.classList.add('warning');
                indicator.classList.add('status-amber');
            } else {
                element.classList.add('disconnected');
                indicator.classList.add('status-red');
            }
            
            // Update text if provided
            if (text) {
                statusText.textContent = text;
            }
        }
        
        // Check API status
        async function checkApiStatus() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/health?cache_buster=${Date.now()}`);
                const data = await response.json();
                
                if (data.has_google_ads_credentials) {
                    // Update status indicators
                    updateApiStatusIndicator('ads-api-status', 'connected', 'Google Ads API: Connected');
                    updateApiStatusIndicator('data-api-status', 'connected', 'Performance Data: Available');
                    updateApiStatusIndicator('campaign-api-status', 'connected', 'Campaign Data: Available');
                    
                    // Store connection info in hidden element
                    apiStatus.style.display = 'none';
                    apiStatus.innerHTML = `
                        <div class="alert alert-success">
                            <strong>Connected to Google Ads API</strong>
                            <p>Using client ID: ${data.google_ads_client_id || 'Unknown'}</p>
                            <p>Customer ID: ${data.google_ads_customer_id || 'Unknown'}</p>
                        </div>
                    `;
                } else {
                    // Update status indicators for mock data
                    updateApiStatusIndicator('ads-api-status', 'warning', 'Google Ads API: Using Mock Data');
                    updateApiStatusIndicator('data-api-status', 'warning', 'Performance Data: Mock');
                    updateApiStatusIndicator('campaign-api-status', 'warning', 'Campaign Data: Mock');
                    
                    // Store warning info in hidden element
                    apiStatus.style.display = 'none';
                    apiStatus.innerHTML = `
                        <div class="alert alert-warning">
                            <strong>Using Mock Data</strong>
                            <p>Google Ads API credentials not found or incomplete. The dashboard is displaying mock data.</p>
                            <p>To connect to the real API, add your Google Ads API credentials as environment variables.</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error checking API status:', error);
                
                // Update status indicators
                updateApiStatusIndicator('ads-api-status', 'disconnected', 'Google Ads API: Error');
                updateApiStatusIndicator('data-api-status', 'disconnected', 'Performance Data: Unavailable');
                updateApiStatusIndicator('campaign-api-status', 'disconnected', 'Campaign Data: Unavailable');
                
                // Store error info in hidden element
                apiStatus.style.display = 'none';
                apiStatus.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Error Checking API Status</strong>
                        <p>Could not determine API connection status. Please check server logs.</p>
                    </div>
                `;
            }
        }

        // Load performance metrics
        async function loadPerformanceData() {
            try {
                metricsContainer.innerHTML = '<div class="col-12"><div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div></div>';
                
                const params = new URLSearchParams({
                    start_date: startDateInput.value,
                    end_date: endDateInput.value,
                    cache_buster: Date.now() // Prevent caching
                });
                
                const response = await fetch(`${API_BASE_URL}/api/google-ads/performance?${params.toString()}`);
                const data = await response.json();
                
                console.log("Performance data loaded:", data);
                
                // Check if we received an error response
                if (data.error) {
                    console.error('Error response from performance API:', data.message);
                    metricsContainer.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error retrieving performance data: ${data.message}</div></div>`;
                    updateApiStatusIndicator('data-api-status', 'disconnected', 'Performance Data: Error');
                    return;
                }
                
                displayMetrics(data);
                updatePerformanceChart(data);
                updateConversionFunnel(data);
                
                // Update status indicator
                if (data.impressions && data.impressions.note && data.impressions.note.includes("MOCK")) {
                    updateApiStatusIndicator('data-api-status', 'warning', 'Performance Data: Mock');
                } else {
                    updateApiStatusIndicator('data-api-status', 'connected', 'Performance Data: Real');
                }
                
                // Display data note if present
                if (data.impressions && data.impressions.note) {
                    chartNote.textContent = "Note: " + data.impressions.note;
                } else {
                    chartNote.textContent = "";
                }
            } catch (error) {
                console.error('Error loading performance data:', error);
                metricsContainer.innerHTML = '<div class="col-12"><div class="alert alert-danger">Failed to load performance data.</div></div>';
                chartNote.textContent = "";
                updateApiStatusIndicator('data-api-status', 'disconnected', 'Performance Data: Connection Error');
            }
        }

        // Display metrics cards
        function displayMetrics(data) {
            const metrics = [
                { id: 'impressions', label: 'Impressions', format: formatNumber },
                { id: 'clicks', label: 'Clicks', format: formatNumber },
                { id: 'clickThroughRate', label: 'CTR', format: val => val },
                { id: 'conversions', label: 'Conversions', format: formatNumber },
                { id: 'conversionRate', label: 'Conversion Rate', format: val => val },
                { id: 'cost', label: 'Cost', format: val => val }
            ];
            
            let html = '';
            
            metrics.forEach(metric => {
                const value = data[metric.id]?.value || 0;
                const change = data[metric.id]?.change || 0;
                const changeClass = change >= 0 ? 'positive-change' : 'negative-change';
                const changeIcon = change >= 0 ? '↑' : '↓';
                
                html += `
                <div class="col-md-6 col-lg-4">
                    <div class="card metric-card p-3">
                        <h6 class="text-muted">${metric.label}</h6>
                        <div class="metric-value">${metric.format(value)}</div>
                        <div class="metric-change ${changeClass}">
                            ${changeIcon} ${Math.abs(change).toFixed(1)}%
                        </div>
                    </div>
                </div>
                `;
            });
            
            metricsContainer.innerHTML = html;
        }

        // Update performance chart
        function updatePerformanceChart(data) {
            const ctx = document.getElementById('performance-chart').getContext('2d');
            
            // Destroy existing chart if it exists
            if (performanceChart) {
                performanceChart.destroy();
            }
            
            // Create the chart data
            const chartData = {
                labels: ['Impressions', 'Clicks', 'Conversions', 'Cost'],
                datasets: [{
                    label: 'Current Period',
                    data: [
                        data.impressions?.value || 0,
                        data.clicks?.value || 0,
                        data.conversions?.value || 0,
                        parseFloat(String(data.cost?.value || '0').replace(/[^0-9.-]+/g,""))
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(153, 102, 255, 0.5)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            };
            
            // Create the chart
            performanceChart = new Chart(ctx, {
                type: 'bar',
                data: chartData,
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Update conversion funnel
        function updateConversionFunnel(data) {
            // Get values from data
            const impressions = data.impressions?.value || 0;
            const clicks = data.clicks?.value || 0;
            const conversions = data.conversions?.value || 0;
            
            // Parse numeric values and ensure they're numbers
            const impressionsNum = typeof impressions === 'string' ? parseInt(impressions.replace(/,/g, '')) : impressions;
            const clicksNum = typeof clicks === 'string' ? parseInt(clicks.replace(/,/g, '')) : clicks;
            const conversionsNum = typeof conversions === 'string' ? parseInt(conversions.replace(/,/g, '')) : conversions;
            
            // Calculate percentages for visualization width
            const maxWidth = 100; // 100% width for the top bar
            const clicksPercentage = impressionsNum > 0 ? (clicksNum / impressionsNum) * 100 : 0;
            const conversionsPercentage = clicksNum > 0 ? (conversionsNum / clicksNum) * 100 : 0;
            
            // Calculate rates
            const ctr = impressionsNum > 0 ? (clicksNum / impressionsNum) * 100 : 0;
            const convRate = clicksNum > 0 ? (conversionsNum / clicksNum) * 100 : 0;
            
            // Get cost per metrics
            const costStr = data.cost?.value || '$0.00';
            const cost = parseFloat(costStr.replace(/[^0-9.-]+/g, ''));
            const cpc = clicksNum > 0 ? cost / clicksNum : 0;
            const cpa = conversionsNum > 0 ? cost / conversionsNum : 0;
            
            // Update funnel visualization
            document.getElementById('funnel-steps').innerHTML = `
                <div class="funnel-step">
                    <div class="funnel-bar" style="width: ${maxWidth}%">
                        <div class="funnel-label">
                            <span>Impressions</span>
                            <span class="funnel-value">${formatNumber(impressionsNum)}</span>
                        </div>
                    </div>
                </div>
                <div class="funnel-step">
                    <div class="funnel-bar" style="width: ${Math.max(5, clicksPercentage)}%">
                        <div class="funnel-label">
                            <span>Clicks</span>
                            <span class="funnel-value">${formatNumber(clicksNum)}</span>
                        </div>
                    </div>
                    <div class="funnel-rate">CTR: ${ctr.toFixed(2)}%</div>
                </div>
                <div class="funnel-step">
                    <div class="funnel-bar" style="width: ${Math.max(5, conversionsPercentage)}%">
                        <div class="funnel-label">
                            <span>Conversions</span>
                            <span class="funnel-value">${formatNumber(conversionsNum)}</span>
                        </div>
                    </div>
                    <div class="funnel-rate">Conv. Rate: ${convRate.toFixed(2)}%</div>
                </div>
            `;
            
            // Update conversion metrics
            document.getElementById('ctr-value').textContent = `${ctr.toFixed(2)}%`;
            document.getElementById('conv-rate-value').textContent = `${convRate.toFixed(2)}%`;
            document.getElementById('cpc-value').textContent = formatCurrency(cpc);
            document.getElementById('cpa-value').textContent = formatCurrency(cpa);
        }

        // Load campaigns
        async function loadCampaigns() {
            try {
                campaignsBody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></td></tr>';
                
                const params = new URLSearchParams({
                    start_date: startDateInput.value,
                    end_date: endDateInput.value,
                    cache_buster: Date.now() // Prevent caching
                });
                
                const response = await fetch(`${API_BASE_URL}/api/google-ads/campaigns?${params.toString()}`);
                const result = await response.json();
                
                console.log("Campaigns data loaded:", result);
                
                // Check if we received a structured response with status and data
                if (result && result.status === 'success' && Array.isArray(result.data)) {
                    // Store campaigns data globally for filtering
                    campaignsData = result.data;
                    console.log('Received campaign data in standard structure:', campaignsData);
                    
                    // Check if it's mock data by looking at the first item
                    if (campaignsData.length > 0 && campaignsData[0].note && campaignsData[0].note.includes("MOCK")) {
                        updateApiStatusIndicator('campaign-api-status', 'warning', 'Campaign Data: Mock');
                    } else {
                        updateApiStatusIndicator('campaign-api-status', 'connected', 'Campaign Data: Real');
                    }
                } else if (result && Array.isArray(result)) {
                    // Direct array response
                    campaignsData = result;
                    console.log('Received campaign data as direct array:', campaignsData);
                    
                    // Check if it's mock data by looking at the first item
                    if (campaignsData.length > 0 && campaignsData[0].note && campaignsData[0].note.includes("MOCK")) {
                        updateApiStatusIndicator('campaign-api-status', 'warning', 'Campaign Data: Mock');
                    } else {
                        updateApiStatusIndicator('campaign-api-status', 'connected', 'Campaign Data: Real');
                    }
                } else if (result && result.status === 'error') {
                    // Handle error response
                    console.error('Error response from API:', result.message);
                    campaignsBody.innerHTML = `<tr><td colspan="10" class="text-center">Error retrieving campaign data: ${result.message}</td></tr>`;
                    campaignsNote.textContent = "";
                    updateApiStatusIndicator('campaign-api-status', 'disconnected', 'Campaign Data: Error');
                    return;
                } else if (result && result.data && Array.isArray(result.data) && result.data.length === 0) {
                    // Empty data array
                    console.warn('API returned empty data array');
                    campaignsData = [];
                    campaignsBody.innerHTML = '<tr><td colspan="10" class="text-center">No campaign data available from API.</td></tr>';
                    campaignsNote.textContent = "";
                    updateApiStatusIndicator('campaign-api-status', 'warning', 'Campaign Data: Empty');
                    return;
                } else {
                    // Handle unexpected response format
                    console.error('Unexpected response format:', result);
                    campaignsData = [];
                    campaignsBody.innerHTML = '<tr><td colspan="10" class="text-center">Unexpected data format received from API.</td></tr>';
                    campaignsNote.textContent = "";
                    updateApiStatusIndicator('campaign-api-status', 'disconnected', 'Campaign Data: Format Error');
                    return;
                }
                
                // Enhance campaigns with region and type info
                campaignsData.forEach(campaign => {
                    campaign.region = getRegionFromCampaignName(campaign.name);
                    campaign.state = getStateFromCampaignName(campaign.name);
                    campaign.type = getCampaignType(campaign.name);
                });
                
                // Check for note
                if (campaignsData.length > 0 && campaignsData[0].note) {
                    campaignsNote.textContent = "Note: " + campaignsData[0].note;
                } else {
                    campaignsNote.textContent = "";
                }
                
                // Display filtered campaigns
                displayFilteredCampaigns();
                
            } catch (error) {
                console.error('Error loading campaigns:', error);
                campaignsBody.innerHTML = '<tr><td colspan="10" class="text-center">Failed to load campaign data.</td></tr>';
                campaignsNote.textContent = "";
                updateApiStatusIndicator('campaign-api-status', 'disconnected', 'Campaign Data: Connection Error');
            }
        }
        
        // Get filtered campaigns
        function getFilteredCampaigns() {
            if (!campaignsData || campaignsData.length === 0) {
                return [];
            }
            
            let filtered = [...campaignsData];
            
            // Apply active filter
            if (showActiveOnlyCheckbox.checked) {
                filtered = filtered.filter(campaign => campaign.status === 'ENABLED');
            }
            
            // Apply region filter
            const selectedRegion = regionFilterSelect.value;
            if (selectedRegion !== 'all') {
                filtered = filtered.filter(campaign => campaign.region === selectedRegion);
            }
            
            // Apply campaign type filter
            const selectedType = campaignTypeFilterSelect.value;
            if (selectedType !== 'all') {
                filtered = filtered.filter(campaign => campaign.type === selectedType);
            }
            
            return filtered;
        }
        
        // Display filtered campaigns
        function displayFilteredCampaigns() {
            const filteredCampaigns = getFilteredCampaigns();
            
            if (filteredCampaigns.length === 0) {
                campaignsBody.innerHTML = '<tr><td colspan="10" class="text-center">No campaigns match the selected filters.</td></tr>';
                return;
            }
            
            let html = '';
            
            filteredCampaigns.forEach(campaign => {
                const statusClass = campaign.status === 'ENABLED' ? 'bg-success' : 
                                  campaign.status === 'PAUSED' ? 'bg-warning' : 'bg-secondary';
                
                // Add region indicator
                const regionBadge = campaign.region && campaign.region !== 'other' ? 
                    `<span class="badge bg-info ms-2">${campaign.region.charAt(0).toUpperCase() + campaign.region.slice(1)}</span>` : '';
                
                // Add state indicator
                const stateBadge = campaign.state ? 
                    `<span class="badge bg-secondary ms-1">${campaign.state}</span>` : '';
                
                // Add campaign type indicator with different colors for different types
                let typeBadgeClass = 'bg-secondary';
                if (campaign.type === 'Search') typeBadgeClass = 'bg-primary';
                if (campaign.type === 'PMax') typeBadgeClass = 'bg-success';
                if (campaign.type === 'Brand') typeBadgeClass = 'bg-warning';
                if (campaign.type === 'NonBrand') typeBadgeClass = 'bg-danger';
                if (campaign.type === 'Display') typeBadgeClass = 'bg-info';
                if (campaign.type === 'Video') typeBadgeClass = 'bg-dark';
                if (campaign.type === 'Shopping') typeBadgeClass = 'bg-success';
                
                const typeBadge = `<span class="badge ${typeBadgeClass} ms-1">${campaign.type}</span>`;
                
                html += `
                <tr>
                    <td>
                        ${campaign.name}
                        ${typeBadge}
                        ${regionBadge}
                        ${stateBadge}
                    </td>
                    <td><span class="badge ${statusClass}">${campaign.status}</span></td>
                    <td>${campaign.budget || '$0.00'}</td>
                    <td>${formatNumber(campaign.impressions || 0)}</td>
                    <td>${formatNumber(campaign.clicks || 0)}</td>
                    <td>${(campaign.ctr || 0).toFixed(2)}%</td>
                    <td>${formatNumber(campaign.conversions || 0)}</td>
                    <td>${(campaign.conversion_rate || 0).toFixed(2)}%</td>
                    <td>${formatCurrency(campaign.cost || 0)}</td>
                    <td>${formatCurrency(campaign.cost_per_conversion || 0)}</td>
                </tr>
                `;
            });
            
            campaignsBody.innerHTML = html;
        }
    </script>
</body>
</html>
"""

# Dashboard data - Mock data in case Google Ads client fails
PERFORMANCE_DATA = {
    "impressions": {
        "value": 125789,
        "change": 8.5,
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    },
    "clicks": {
        "value": 5432,
        "change": 12.3,
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    },
    "conversions": {
        "value": 321,
        "change": 5.7,
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    },
    "cost": {
        "value": "$4,567.89",
        "change": 7.8,
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    },
    "conversionRate": {
        "value": "5.9%",
        "change": -2.1,
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    },
    "clickThroughRate": {
        "value": "4.3%",
        "change": 3.5,
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    },
    "costPerConversion": {
        "value": "$14.23",
        "change": 2.1,
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    }
}

CAMPAIGNS_DATA = [
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
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
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
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
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
        "note": "FALLBACK MOCK DATA - Failed to load Google Ads client"
    }
]

class DashboardHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the Allervie dashboard
    """
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Route to appropriate handler based on path
        if path == "/" or path == "/ads-dashboard":
            self.serve_dashboard()
        elif path == "/api/google-ads/performance":
            self.serve_performance_data()
        elif path == "/api/google-ads/campaigns":
            self.serve_campaigns_data()
        elif path == "/api/health":
            self.serve_health_check()
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(DASHBOARD_HTML.encode())
    
    def serve_performance_data(self):
        """Serve the performance data from Google Ads API or mock data"""
        # Get parameters from query string
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # Extract start_date and end_date if present
        start_date = query_params.get('start_date', [None])[0]
        end_date = query_params.get('end_date', [None])[0]
        
        try:
            # Get data from Google Ads client
            data = ads_client.get_performance_data(start_date, end_date)
            logger.info(f"Retrieved performance data for period: {start_date} to {end_date}")
        except Exception as e:
            # Fallback to mock data
            logger.error(f"Error retrieving performance data: {str(e)}")
            data = PERFORMANCE_DATA
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_campaigns_data(self):
        """Serve the campaigns data from Google Ads API or mock data"""
        # Get parameters from query string
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # Extract start_date and end_date if present
        start_date = query_params.get('start_date', [None])[0]
        end_date = query_params.get('end_date', [None])[0]
        
        try:
            # Get data from Google Ads client
            campaigns = ads_client.get_campaigns_data(start_date, end_date)
            logger.info(f"Retrieved campaigns data for period: {start_date} to {end_date}")
            
            # Wrap in a structured response
            data = {
                "status": "success",
                "message": "Campaign data retrieved successfully",
                "data": campaigns
            }
        except Exception as e:
            # Fallback to mock data
            logger.error(f"Error retrieving campaigns data: {str(e)}")
            data = {
                "status": "error", 
                "message": f"Error retrieving campaign data: {str(e)}",
                "data": CAMPAIGNS_DATA
            }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_health_check(self):
        """Serve a health check response with Google Ads API status"""
        health_data = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'service': 'Allervie Analytics API',
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'version': '1.0.0',
            'has_google_ads_credentials': ads_client.has_credentials if hasattr(ads_client, 'has_credentials') else False,
            'google_ads_client_id': ads_client.client_id[:10] + '...' if hasattr(ads_client, 'client_id') and ads_client.client_id else None,
            'google_ads_customer_id': ads_client.login_customer_id if hasattr(ads_client, 'login_customer_id') else None
        }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(json.dumps(health_data).encode())

def run_server():
    """Start the HTTP server"""
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print("=" * 70)
    print(f"Starting Allervie Analytics Dashboard on port {port}")
    print(f"Dashboard URL: http://localhost:{port}/ads-dashboard")
    print(f"Google Ads API Credentials: {'FOUND' if hasattr(ads_client, 'has_credentials') and ads_client.has_credentials else 'NOT FOUND'}")
    print("=" * 70)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    run_server()