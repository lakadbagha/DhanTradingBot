from dhanhq import dhanhq
from config import CLIENT_ID, ACCESS_TOKEN

dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)

funds = dhan.get_fund_limits()
print("Connected! Your funds:", funds)