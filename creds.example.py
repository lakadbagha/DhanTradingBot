# ============================================================================
# DHAN API CREDENTIALS - EXAMPLE TEMPLATE
# ============================================================================
# INSTRUCTIONS:
# 1. Copy this file to 'creds.py'
# 2. Fill in your actual Dhan API credentials
# 3. NEVER commit creds.py to Git (it's in .gitignore)
# ============================================================================

# Your Dhan Client ID (e.g., "1234567890")
client_id = "YOUR_CLIENT_ID_HERE"

# Your Dhan Access Token (get from Dhan Developer Portal)
access_token = "YOUR_ACCESS_TOKEN_HERE"

# ============================================================================
# HOW TO GET CREDENTIALS:
# ============================================================================
# 1. Login to Dhan: https://www.dhan.co/
# 2. Go to: Developer API → API Keys
# 3. Generate Access Token
# 4. Copy Client ID and Access Token here
# ============================================================================

# Optional: Paper Trading Mode (set to True for testing)
PAPER_TRADING = False

# Optional: Risk Limits
MAX_LOSS_PER_DAY = 5000  # Rs. 5,000 max loss per day
MAX_TRADES_PER_DAY = 2
