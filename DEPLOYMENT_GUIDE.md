# 🚀 DEPLOYMENT GUIDE - Cloud Server Deployment

**Deploy Your Trading System to Run 24/7 on Cloud Server**

---

## 📋 TABLE OF CONTENTS

1. [Deployment Options](#deployment-options)
2. [Recommended Setup (AWS/Azure)](#recommended-setup)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Domain Setup (Optional)](#domain-setup)
5. [Security Best Practices](#security-best-practices)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Backup & Recovery](#backup--recovery)

---

## 🎯 DEPLOYMENT OPTIONS

### Option 1: Cloud VPS (Recommended) ⭐

**Best Providers:**
1. **AWS EC2** (Amazon Web Services)
   - Reliable, scalable
   - Free tier available (12 months)
   - Cost: ~$5-10/month (t3.micro)

2. **Microsoft Azure VM**
   - Windows/Linux support
   - Good for .NET developers
   - Cost: ~$5-15/month (B1s)

3. **DigitalOcean Droplet**
   - Simple, developer-friendly
   - Fixed pricing
   - Cost: $6/month (Basic Droplet)

4. **Linode**
   - Good performance
   - Easy setup
   - Cost: $5/month (Nanode)

**Pros:**
- ✅ Runs 24/7 (no power cuts)
- ✅ Fast internet connection
- ✅ Professional IP (less restrictions)
- ✅ Easy scaling
- ✅ Automatic backups available

**Cons:**
- ❌ Monthly cost ($5-15)
- ❌ Requires basic server knowledge

---

### Option 2: Keep on Your PC

**Current Setup (D:\dhan_algo)**

**Pros:**
- ✅ No extra cost
- ✅ Full control
- ✅ Easy to monitor

**Cons:**
- ❌ Must keep PC running 24/7
- ❌ Power cuts = trading stops
- ❌ Home internet reliability
- ❌ IP might get restricted

---

### Option 3: Raspberry Pi (Budget Option)

**Low-power dedicated device**

**Pros:**
- ✅ Low power consumption (~$3/year electricity)
- ✅ One-time cost (~$50-70)
- ✅ Runs 24/7

**Cons:**
- ❌ Less powerful
- ❌ Requires setup
- ❌ Still needs home internet

---

## ⭐ RECOMMENDED SETUP (AWS EC2)

### Why AWS?
- ✅ Free tier (1 year)
- ✅ Reliable (99.99% uptime)
- ✅ Fast deployment
- ✅ Professional infrastructure
- ✅ Easy to monitor

### Specifications Needed

**Minimum Requirements:**
```
CPU: 1 vCPU (t3.micro)
RAM: 1 GB
Storage: 8 GB SSD
OS: Ubuntu 22.04 LTS (Linux)
Network: Fixed IP address
```

**Monthly Cost:**
- Free tier: $0 (first 12 months)
- After free tier: ~$8-10/month
- With reserved instance: ~$5/month

---

## 📝 STEP-BY-STEP DEPLOYMENT

### Step 1: Create AWS Account

1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Enter email, password, account name
4. Add credit/debit card (for verification, won't charge during free tier)
5. Verify phone number
6. Select "Basic Support - Free"
7. Complete signup

---

### Step 2: Launch EC2 Instance

**In AWS Console:**

1. **Search for "EC2"** in search bar
2. Click **"Launch Instance"**

3. **Configure Instance:**
   ```
   Name: nifty-trading-bot
   
   Application and OS Images:
   - Ubuntu Server 22.04 LTS (Free tier eligible)
   
   Instance Type:
   - t3.micro (1 vCPU, 1 GB RAM) - Free tier
   
   Key Pair (login):
   - Create new key pair
   - Name: trading-bot-key
   - Type: RSA
   - Format: .pem (for Linux/Mac) or .ppk (for Windows/PuTTY)
   - Download and save securely!
   
   Network Settings:
   - Allow SSH (port 22) from "My IP"
   - Allow HTTP (port 80) - Optional for dashboard
   - Allow HTTPS (port 443) - Optional
   
   Storage:
   - 8 GB gp3 (Free tier eligible)
   ```

4. Click **"Launch Instance"**

5. Wait 2-3 minutes for instance to start

6. **Get Public IP:**
   - Click on your instance
   - Copy "Public IPv4 address" (e.g., 3.110.123.45)

---

### Step 3: Connect to Server

**For Windows (Using PowerShell):**

```powershell
# Navigate to key file location
cd C:\Users\YourName\Downloads

# Connect via SSH
ssh -i trading-bot-key.pem ubuntu@YOUR_SERVER_IP

# Example:
# ssh -i trading-bot-key.pem ubuntu@3.110.123.45
```

**First time you'll see:**
```
The authenticity of host '3.110.123.45' can't be established.
Are you sure you want to continue? (yes/no): yes
```

**You're now connected to your cloud server!** 🎉

---

### Step 4: Setup Python Environment

**On the server, run these commands:**

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Verify installation
python3.11 --version
# Should show: Python 3.11.x

# Install required packages
pip3 install dhanhq pandas numpy openpyxl requests

# Verify installations
python3.11 -c "import dhanhq; print('dhanhq OK')"
python3.11 -c "import pandas; print('pandas OK')"
```

---

### Step 5: Upload Your Trading System

**Method A: Using SCP (from your Windows PC):**

```powershell
# In PowerShell on your Windows PC
cd D:\dhan_algo

# Upload files to server
scp -i C:\Users\YourName\Downloads\trading-bot-key.pem -r * ubuntu@YOUR_SERVER_IP:/home/ubuntu/trading/

# This uploads all files from D:\dhan_algo to server
```

**Method B: Using Git (Recommended):**

```bash
# On server
cd /home/ubuntu
mkdir trading
cd trading

# If you use GitHub:
git clone YOUR_GITHUB_REPO_URL .

# Or manually upload essential files only
```

**Essential Files to Upload:**
```
✅ live_trading_engine_optimized.py
✅ strategy_config.py
✅ security_id_map.py
✅ position_manager.py
✅ creds.py
✅ get_all_security_ids.py
✅ create_security_map.py
```

---

### Step 6: Configure Auto-Start

**Create systemd service (runs automatically):**

```bash
# Create service file
sudo nano /etc/systemd/system/trading-bot.service
```

**Paste this configuration:**

```ini
[Unit]
Description=NIFTY Options Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/trading
ExecStart=/usr/bin/python3.11 /home/ubuntu/trading/live_trading_engine_optimized.py
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/trading/logs/bot.log
StandardError=append:/home/ubuntu/trading/logs/error.log

# Environment variables (optional)
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

**Save:** Ctrl+O, Enter, Ctrl+X

**Enable and start service:**

```bash
# Create logs directory
mkdir -p /home/ubuntu/trading/logs

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable trading-bot

# Start service
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot
```

**You should see:**
```
● trading-bot.service - NIFTY Options Trading Bot
   Active: active (running) since Sat 2026-04-05 09:15:00 UTC
```

---

### Step 7: Monitor Your Bot

**Check logs in real-time:**

```bash
# View live logs
tail -f /home/ubuntu/trading/logs/bot.log

# View last 50 lines
tail -n 50 /home/ubuntu/trading/logs/bot.log

# Check for errors
tail -f /home/ubuntu/trading/logs/error.log

# View trading CSV
cat /home/ubuntu/trading/livetrading_*.csv
```

**Useful commands:**

```bash
# Stop bot
sudo systemctl stop trading-bot

# Restart bot
sudo systemctl restart trading-bot

# Check if running
sudo systemctl is-active trading-bot

# View logs
journalctl -u trading-bot -f
```

---

## 🌐 DOMAIN SETUP (Optional)

### Why Use a Domain?

- ✅ Easy to remember (trading.yourdomain.com vs 3.110.123.45)
- ✅ Professional
- ✅ Can host dashboard/web interface
- ✅ Email alerts from custom domain

### Steps:

**1. Buy a Domain:**
- GoDaddy: ~$10/year
- Namecheap: ~$8/year
- Cloudflare: ~$8/year

**2. Point Domain to Server:**

In your domain registrar (e.g., GoDaddy):
```
Type: A Record
Name: trading (or @)
Value: YOUR_SERVER_IP (e.g., 3.110.123.45)
TTL: 1 hour
```

**3. Install Web Dashboard (Optional):**

```bash
# Install Flask (lightweight web framework)
pip3 install flask

# Create simple dashboard
nano /home/ubuntu/trading/dashboard.py
```

**Simple dashboard code:**

```python
from flask import Flask, jsonify
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>NIFTY Trading Bot Status</h1>
    <p><a href="/status">Check Status</a></p>
    <p><a href="/trades">Today's Trades</a></p>
    <p><a href="/logs">Recent Logs</a></p>
    """

@app.route('/status')
def status():
    # Check if bot is running
    status = os.popen('systemctl is-active trading-bot').read().strip()
    
    return jsonify({
        'bot_status': status,
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'market_status': 'Open' if is_market_hours() else 'Closed'
    })

@app.route('/trades')
def trades():
    # Read today's trades
    today = datetime.now().strftime('%d%m%y')
    csv_file = f'livetrading_{today}.csv'
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return df.to_html()
    else:
        return "No trades today"

@app.route('/logs')
def logs():
    # Read last 50 log lines
    logs = os.popen('tail -n 50 /home/ubuntu/trading/logs/bot.log').read()
    return f"<pre>{logs}</pre>"

def is_market_hours():
    now = datetime.now().time()
    from datetime import time
    return time(9, 15) <= now <= time(15, 30)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

**Run dashboard:**
```bash
sudo python3.11 /home/ubuntu/trading/dashboard.py
```

**Access at:** http://trading.yourdomain.com

---

## 🔒 SECURITY BEST PRACTICES

### 1. Secure API Credentials

**Encrypt creds.py:**

```bash
# Install cryptography
pip3 install cryptography

# Create encrypted credentials
python3.11 << EOF
from cryptography.fernet import Fernet

# Generate key (save this securely!)
key = Fernet.generate_key()
print(f"Encryption Key: {key.decode()}")

# Encrypt credentials
f = Fernet(key)

# Your credentials
client_id = "1104341808"
access_token = "YOUR_TOKEN"

# Encrypt
encrypted_id = f.encrypt(client_id.encode())
encrypted_token = f.encrypt(access_token.encode())

print(f"Encrypted ID: {encrypted_id.decode()}")
print(f"Encrypted Token: {encrypted_token.decode()}")
EOF
```

**Store encryption key separately** (not on server!)

### 2. IP Whitelist

In Dhan API settings:
- Add your server's public IP
- Remove "Allow all IPs"
- More secure

### 3. Firewall Setup

```bash
# Enable firewall
sudo ufw enable

# Allow SSH only from your IP
sudo ufw allow from YOUR_HOME_IP to any port 22

# Allow HTTP/HTTPS if using dashboard
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status
```

### 4. Automatic Updates

```bash
# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 5. SSH Key Only (Disable Password)

```bash
sudo nano /etc/ssh/sshd_config

# Change this line:
PasswordAuthentication no

# Restart SSH
sudo systemctl restart sshd
```

---

## 📊 MONITORING & ALERTS

### 1. Email Alerts (Free)

**Setup SendGrid or Gmail SMTP:**

```python
# Add to live_trading_engine_optimized.py

import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    """Send email alert"""
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'trading-bot@yourdomain.com'
    msg['To'] = 'your-email@gmail.com'
    
    # Gmail SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-app-password')
    server.send_message(msg)
    server.quit()

# Call when important events happen
send_alert('Trade Executed', f'CALL at strike 23000, Entry: Rs.105')
send_alert('Target Hit', f'Profit: Rs.1680')
send_alert('Bot Stopped', 'Emergency stop triggered')
```

### 2. Telegram Bot (Recommended)

**Setup Telegram notifications:**

```bash
pip3 install python-telegram-bot
```

```python
import telegram
from telegram import Bot

# Create bot at https://t.me/BotFather
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram(message):
    """Send Telegram notification"""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# Usage
send_telegram('🚀 Bot started successfully')
send_telegram('📊 Signal detected: Fibonacci CALL')
send_telegram('✅ Order placed: ID 12345')
send_telegram('🎯 Target hit: Rs.1680 profit')
```

### 3. CloudWatch (AWS Monitoring)

**Setup AWS CloudWatch alarms:**

1. Go to AWS CloudWatch
2. Create alarm for:
   - CPU usage > 80%
   - Disk usage > 90%
   - Network errors
3. Get SNS notifications via email/SMS

---

## 💾 BACKUP & RECOVERY

### Automatic Backups

**Daily backup script:**

```bash
# Create backup script
nano /home/ubuntu/backup.sh
```

```bash
#!/bin/bash

# Backup location
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup trading files
tar -czf $BACKUP_DIR/trading_backup_$DATE.tar.gz /home/ubuntu/trading

# Backup logs
cp /home/ubuntu/trading/logs/*.log $BACKUP_DIR/

# Backup CSV files
cp /home/ubuntu/trading/*.csv $BACKUP_DIR/

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Upload to cloud (optional)
# aws s3 cp $BACKUP_DIR/trading_backup_$DATE.tar.gz s3://your-bucket/backups/

echo "Backup completed: $DATE"
```

**Make executable and schedule:**

```bash
chmod +x /home/ubuntu/backup.sh

# Add to crontab (runs daily at 4 AM)
crontab -e

# Add this line:
0 4 * * * /home/ubuntu/backup.sh
```

### Recovery

**If bot crashes/server restarts:**

```bash
# Bot auto-restarts (systemd takes care of it)

# Manual restart if needed
sudo systemctl restart trading-bot

# Restore from backup
cd /home/ubuntu
tar -xzf backups/trading_backup_20260405.tar.gz

# Check what was running
cat logs/bot.log | grep "last entry"
```

---

## 📱 MOBILE ACCESS

### SSH from Phone

**For Android:**
- Install: **Termux** or **JuiceSSH**

**For iPhone:**
- Install: **Terminus** or **Shelly**

**Connect:**
```bash
ssh -i trading-bot-key.pem ubuntu@YOUR_SERVER_IP

# Check bot status
sudo systemctl status trading-bot

# View logs
tail -f logs/bot.log

# Stop/start
sudo systemctl stop trading-bot
sudo systemctl start trading-bot
```

---

## 💰 COST BREAKDOWN

### AWS Free Tier (First Year)
```
EC2 t3.micro: $0 (750 hours/month free)
Storage 8GB: $0 (30 GB free)
Data Transfer: $0 (1 GB/month outbound free)

Total Year 1: $0
```

### After Free Tier
```
EC2 t3.micro: $8.50/month
Storage 8GB: $0.80/month
Data Transfer: ~$1/month
Elastic IP: $0 (if instance running)

Total Monthly: ~$10/month
Total Yearly: ~$120/year
```

### With Reserved Instance (1-year commitment)
```
EC2 Reserved: $5/month
Storage: $0.80/month
Data Transfer: $1/month

Total Monthly: ~$7/month
Total Yearly: ~$84/year
```

### Alternative: DigitalOcean
```
Basic Droplet: $6/month
Storage included: 25 GB
Data Transfer: 1 TB

Total Monthly: $6/month (fixed)
Total Yearly: $72/year
```

---

## ✅ DEPLOYMENT CHECKLIST

### Before Deployment
- [ ] Test system locally (paper trading 3-5 days)
- [ ] Verify 58.2% win rate on backtests
- [ ] Confirm API credentials working
- [ ] Update security_id_map.py
- [ ] Test emergency stop

### Server Setup
- [ ] Create AWS/cloud account
- [ ] Launch EC2 instance (t3.micro)
- [ ] Configure security group (SSH only from your IP)
- [ ] Save SSH key securely
- [ ] Connect to server successfully

### Installation
- [ ] Install Python 3.11
- [ ] Install required packages (dhanhq, pandas, etc.)
- [ ] Upload trading files
- [ ] Test script manually first
- [ ] Configure systemd service
- [ ] Enable auto-start

### Security
- [ ] Encrypt creds.py
- [ ] Setup firewall (ufw)
- [ ] Add server IP to Dhan whitelist
- [ ] Disable password SSH
- [ ] Setup automatic updates

### Monitoring
- [ ] Configure email/Telegram alerts
- [ ] Setup log monitoring
- [ ] Test emergency notifications
- [ ] Setup CloudWatch alarms (AWS)

### Backup
- [ ] Create backup script
- [ ] Schedule daily backups (cron)
- [ ] Test recovery process
- [ ] Store backups off-server

### Go Live
- [ ] Start with paper trading on server
- [ ] Monitor for 2-3 days
- [ ] Enable live trading (PAPER_TRADING_MODE = False)
- [ ] Start with 1 lot
- [ ] Scale up gradually

---

## 🎯 QUICK START COMMANDS

**After server is setup, use these daily:**

```bash
# SSH into server
ssh -i trading-bot-key.pem ubuntu@YOUR_SERVER_IP

# Check bot status
sudo systemctl status trading-bot

# View live logs
tail -f /home/ubuntu/trading/logs/bot.log

# Check today's trades
cat /home/ubuntu/trading/livetrading_$(date +%d%m%y).csv

# Restart bot
sudo systemctl restart trading-bot

# Stop bot
sudo systemctl stop trading-bot

# Update security IDs (weekly)
cd /home/ubuntu/trading
python3.11 get_all_security_ids.py
python3.11 create_security_map.py
sudo systemctl restart trading-bot

# Check server resources
htop  # or: top

# Exit
exit
```

---

## 🚨 TROUBLESHOOTING

### Bot Not Starting
```bash
# Check service status
sudo systemctl status trading-bot

# View error logs
journalctl -u trading-bot -n 50

# Check Python errors
cat /home/ubuntu/trading/logs/error.log

# Test manually
cd /home/ubuntu/trading
python3.11 live_trading_engine_optimized.py
```

### Can't Connect via SSH
```bash
# Check security group (AWS Console)
# Ensure port 22 allowed from your IP

# Verify key file permissions
chmod 400 trading-bot-key.pem

# Try verbose mode
ssh -v -i trading-bot-key.pem ubuntu@YOUR_SERVER_IP
```

### High CPU/Memory Usage
```bash
# Check resource usage
htop

# Reduce monitoring frequency if needed
# Edit strategy_config.py
# Increase sleep time from 5 seconds to 10 seconds
```

---

## 📚 RESOURCES

**AWS Documentation:**
- EC2 Guide: https://docs.aws.amazon.com/ec2/
- Free Tier: https://aws.amazon.com/free/

**Tutorials:**
- Deploy Python on AWS: https://realpython.com/aws-ec2-python/
- Systemd Services: https://www.freedesktop.org/wiki/Software/systemd/

**Support:**
- AWS Support: https://console.aws.amazon.com/support/
- Dhan API: https://dhanhq.co/docs/

---

## 🎉 SUMMARY

**You Can Deploy in 3 Ways:**

1. **Cloud Server (Recommended)** ⭐
   - AWS/Azure/DigitalOcean
   - Runs 24/7 automatically
   - Cost: $6-10/month
   - Professional setup

2. **Your PC (Current)**
   - Keep D:\dhan_algo running
   - Must keep PC on 24/7
   - Cost: $0 (electricity)
   - Good for testing

3. **Raspberry Pi (Budget)**
   - Low power consumption
   - One-time cost ~$50
   - Runs 24/7
   - DIY option

**Recommended: Start with AWS Free Tier** (free for 1 year, then $10/month)

**Steps:**
1. Create AWS account → 10 mins
2. Launch EC2 instance → 5 mins
3. Connect via SSH → 2 mins
4. Install Python + packages → 10 mins
5. Upload trading files → 5 mins
6. Configure auto-start → 5 mins
7. Test and monitor → ongoing

**Total Setup Time: ~1 hour**

**Your bot will then run automatically:**
- ✅ Auto-starts when market opens
- ✅ Monitors positions continuously
- ✅ Sends alerts on trades
- ✅ Generates daily reports
- ✅ Restarts if crashes
- ✅ Runs 24/7 without you

---

**Ready to deploy?** Follow the step-by-step guide above! 🚀

**Questions?** Re-read the relevant section or test locally first!

---

**Created:** 05-Apr-2026  
**Status:** Complete Deployment Guide  
**Recommended:** AWS EC2 Free Tier
