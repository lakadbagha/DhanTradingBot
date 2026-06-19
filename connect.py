from dhanhq import dhanhq, DhanContext
from config import CLIENT_ID, ACCESS_TOKEN

dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
dhan = dhanhq(dhan_context)

funds = dhan.get_fund_limits()
print("Connected! Your funds:", funds)