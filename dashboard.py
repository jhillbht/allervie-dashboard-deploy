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
                    <div class="d-flex justify-content-end">
                        <div class="d-flex me-3">
                            <div class="me-2">
                                <label for="start-date" class="form-label">Start Date</label>
                                <input type="date" id="start-date" class="form-control date-picker">
                            </div>
                            <div>
                                <label for="end-date" class="form-label">End Date</label>
                                <input type="date" id="end-date" class="form-control date-picker">
                            </div>
                        </div>
                        <div>
                            <label class="form-label">&nbsp;</label>
                            <button id="refresh-btn" class="btn btn-primary d-block">Refresh Data</button>
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
                                        <th>Impressions</th>
                                        <th>Clicks</th>
                                        <th>CTR</th>
                                        <th>Cost</th>
                                    </tr>
                                </thead>
                                <tbody id="campaigns-tbody">
                                    <!-- Campaign data will be loaded here -->
                                    <tr>
                                        <td colspan="6" class="text-center">
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
                    <div class="card-header">
                        <h5>Google Ads API Connection Status</h5>
                    </div>
                    <div class="card-body">
                        <div id="api-status">Checking API connection status...</div>
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

        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            loadPerformanceData();
            loadCampaigns();
            checkApiStatus();
        });

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

        // Check API status
        async function checkApiStatus() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/health?cache_buster=${Date.now()}`);
                const data = await response.json();
                
                if (data.has_google_ads_credentials) {
                    apiStatus.innerHTML = `
                        <div class="alert alert-success">
                            <strong>Connected to Google Ads API</strong>
                            <p>Using client ID: ${data.google_ads_client_id || 'Unknown'}</p>
                            <p>Customer ID: ${data.google_ads_customer_id || 'Unknown'}</p>
                        </div>
                    `;
                } else {
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
                    return;
                }
                
                displayMetrics(data);
                updatePerformanceChart(data);
                
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
                } else if (result && Array.isArray(result)) {
                    // Direct array response
                    campaignsData = result;
                    console.log('Received campaign data as direct array:', campaignsData);
                } else if (result && result.status === 'error') {
                    // Handle error response
                    console.error('Error response from API:', result.message);
                    campaignsBody.innerHTML = `<tr><td colspan="6" class="text-center">Error retrieving campaign data: ${result.message}</td></tr>`;
                    campaignsNote.textContent = "";
                    return;
                } else if (result && result.data && Array.isArray(result.data) && result.data.length === 0) {
                    // Empty data array
                    console.warn('API returned empty data array');
                    campaignsData = [];
                    campaignsBody.innerHTML = '<tr><td colspan="6" class="text-center">No campaign data available from API.</td></tr>';
                    campaignsNote.textContent = "";
                    return;
                } else {
                    // Handle unexpected response format
                    console.error('Unexpected response format:', result);
                    campaignsData = [];
                    campaignsBody.innerHTML = '<tr><td colspan="6" class="text-center">Unexpected data format received from API.</td></tr>';
                    campaignsNote.textContent = "";
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
                campaignsBody.innerHTML = '<tr><td colspan="6" class="text-center">Failed to load campaign data.</td></tr>';
                campaignsNote.textContent = "";
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
                campaignsBody.innerHTML = '<tr><td colspan="6" class="text-center">No campaigns match the selected filters.</td></tr>';
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
                    <td>${formatNumber(campaign.impressions || 0)}</td>
                    <td>${formatNumber(campaign.clicks || 0)}</td>
                    <td>${(campaign.ctr || 0).toFixed(2)}%</td>
                    <td>${formatCurrency(campaign.cost || 0)}</td>
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