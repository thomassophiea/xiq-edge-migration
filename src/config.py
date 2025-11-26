"""
Configuration constants for XIQ to Edge Services Migration Tool
Centralized configuration to avoid hardcoded values throughout the codebase
"""

# API Configuration
MAX_PAGINATION_PAGES = 100  # Maximum pages to fetch in paginated requests
DEFAULT_API_TIMEOUT = 30  # Default timeout for API requests in seconds
DEFAULT_PAGE_LIMIT = 100  # Default items per page for paginated requests

# Edge Services Configuration
EDGE_SERVICES_DEFAULT_PORT = 5825
EDGE_SERVICES_BASE_PATH = '/management'

# Session Configuration
SESSION_COOKIE_SECURE_PRODUCTION = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# State Management
MAX_LOG_ENTRIES = 1000  # Maximum number of log entries to keep in memory
PROFILE_CACHE_TTL = 300  # Profile cache time-to-live in seconds (5 minutes)

# Frontend Configuration
LOG_POLLING_INTERVAL_MS = 3000  # Log polling interval in milliseconds (3 seconds)
DEFAULT_PROGRESS_UPDATE_INTERVAL_MS = 500  # Progress update interval

# XIQ Region URLs
XIQ_REGION_URLS = {
    'Global': 'https://api.extremecloudiq.com',
    'EU': 'https://api-eu.extremecloudiq.com',
    'APAC': 'https://api-apac.extremecloudiq.com',
    'California': 'https://api-ca.extremecloudiq.com'
}

# Security Configuration
REQUIRE_SECRET_KEY_IN_PRODUCTION = True
MIN_PASSWORD_LENGTH = 8

# Performance Configuration
ENABLE_CONNECTION_POOLING = True
ENABLE_RESPONSE_CACHING = True

# Default Role IDs (Edge Services)
DEFAULT_AUTHENTICATED_ROLE_ID = "4459ee6c-2f76-11e7-93ae-92361f002671"

# Logging Configuration
DEFAULT_LOG_LEVEL = 'INFO'
VERBOSE_LOG_LEVEL = 'DEBUG'

# File Upload Configuration
MAX_UPLOAD_SIZE_MB = 10

# Rate Limiting Configuration (for future implementation)
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_LOGIN_ATTEMPTS = 5
RATE_LIMIT_LOGIN_WINDOW_SECONDS = 300  # 5 minutes

# CORS Configuration
CORS_ORIGINS = ['*']  # Configure appropriately for production

# Database Configuration (for future use)
DATABASE_URL = None  # Will use environment variable if set
REDIS_URL = None  # Will use environment variable if set
