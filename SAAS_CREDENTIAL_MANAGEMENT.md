# 🔐 SAAS CREDENTIAL MANAGEMENT - TECHNICAL GUIDE

**How to Handle User Credentials in Multi-Tenant Trading Bot SaaS**

---

## 📋 **TABLE OF CONTENTS**

1. [Current vs SaaS Architecture](#architecture)
2. [Database Schema for Credentials](#database)
3. [Encryption Strategy](#encryption)
4. [Backend API Implementation](#backend)
5. [Bot Instance Credential Injection](#injection)
6. [Security Best Practices](#security)
7. [Code Examples](#code-examples)
8. [Kubernetes Secrets Management](#kubernetes)

---

## 🏗️ **1. CURRENT vs SaaS ARCHITECTURE** {#architecture}

### **Current (Single User):**

```
Your PC
└── trading_bot/
    ├── creds.py  ← YOUR credentials (hardcoded)
    │   ├── client_id = "1234567890"
    │   └── access_token = "eyJhbGc..."
    │
    └── live_trading_engine.py
        └── from creds import client_id, access_token
```

**Works for:** 1 user (you)

---

### **SaaS (Multi-User):**

```
Cloud Infrastructure
│
├── PostgreSQL Database (Encrypted)
│   ├── User 1: client_id (encrypted), access_token (encrypted)
│   ├── User 2: client_id (encrypted), access_token (encrypted)
│   └── User 3: client_id (encrypted), access_token (encrypted)
│
├── Backend API (Node.js/FastAPI)
│   └── Handles credential storage & retrieval
│
└── Bot Instances (Docker/Kubernetes)
    ├── User 1 Bot ← Gets User 1 credentials at runtime
    ├── User 2 Bot ← Gets User 2 credentials at runtime
    └── User 3 Bot ← Gets User 3 credentials at runtime
```

**Key Difference:** Credentials are stored **per-user** in database, retrieved **dynamically** at runtime.

---

## 💾 **2. DATABASE SCHEMA FOR CREDENTIALS** {#database}

### **Users Table:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    
    -- Dhan Credentials (ENCRYPTED!)
    dhan_client_id_encrypted TEXT,
    dhan_access_token_encrypted TEXT,
    encryption_key_id INTEGER,  -- Reference to which key was used
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active'
);
```

### **Encryption Keys Table:**

```sql
CREATE TABLE encryption_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) NOT NULL,  -- Hashed version (for lookup)
    created_at TIMESTAMP DEFAULT NOW(),
    rotated_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'  -- 'active', 'rotated', 'deprecated'
);
```

**Why separate table?** For key rotation (change encryption keys every 90 days for security).

---

## 🔒 **3. ENCRYPTION STRATEGY** {#encryption}

### **3.1 Two-Layer Encryption (Recommended):**

```
User's Dhan Token
    ↓
Layer 1: AES-256 encryption (user-specific key)
    ↓
Layer 2: Store in encrypted database column
    ↓
Stored in PostgreSQL
```

### **3.2 Encryption Implementation (Python):**

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class CredentialEncryption:
    """Handle encryption/decryption of user credentials"""
    
    def __init__(self, master_key: str):
        """
        master_key: Stored in AWS KMS / Azure Key Vault / Environment Variable
        """
        self.master_key = master_key.encode()
    
    def generate_user_key(self, user_id: int) -> bytes:
        """
        Generate unique encryption key for each user
        This way, even if one user's key is compromised, others are safe
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=f"user_{user_id}_salt".encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return key
    
    def encrypt_credential(self, user_id: int, plaintext: str) -> str:
        """
        Encrypt user's Dhan credential
        
        Example:
        >>> encryptor = CredentialEncryption(master_key="YOUR_MASTER_KEY")
        >>> encrypted = encryptor.encrypt_credential(
        ...     user_id=123,
        ...     plaintext="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        ... )
        >>> print(encrypted)
        'gAAAAABh3K...'  # Encrypted token
        """
        user_key = self.generate_user_key(user_id)
        fernet = Fernet(user_key)
        encrypted = fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt_credential(self, user_id: int, encrypted_text: str) -> str:
        """
        Decrypt user's Dhan credential when bot starts
        
        Example:
        >>> encryptor = CredentialEncryption(master_key="YOUR_MASTER_KEY")
        >>> plaintext = encryptor.decrypt_credential(
        ...     user_id=123,
        ...     encrypted_text="gAAAAABh3K..."
        ... )
        >>> print(plaintext)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'  # Original token
        """
        user_key = self.generate_user_key(user_id)
        fernet = Fernet(user_key)
        decrypted = fernet.decrypt(encrypted_text.encode())
        return decrypted.decode()


# Usage Example:
# ================

# When user registers and enters Dhan credentials:
encryptor = CredentialEncryption(master_key=os.getenv("MASTER_ENCRYPTION_KEY"))

user_id = 123
client_id = "1234567890"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Encrypt before storing in database
encrypted_client_id = encryptor.encrypt_credential(user_id, client_id)
encrypted_token = encryptor.encrypt_credential(user_id, access_token)

# Store in database
cursor.execute("""
    UPDATE users 
    SET dhan_client_id_encrypted = %s,
        dhan_access_token_encrypted = %s
    WHERE id = %s
""", (encrypted_client_id, encrypted_token, user_id))


# When bot starts, retrieve and decrypt:
row = cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
user = row.fetchone()

client_id = encryptor.decrypt_credential(user_id, user['dhan_client_id_encrypted'])
access_token = encryptor.decrypt_credential(user_id, user['dhan_access_token_encrypted'])

# Now use for Dhan API
from dhanhq import dhanhq
dhan = dhanhq(client_id, access_token)
```

### **3.3 Master Key Storage:**

**Options:**

| Method | Security | Cost | Complexity |
|--------|----------|------|------------|
| **AWS KMS** | ⭐⭐⭐⭐⭐ | Rs. 100/month | Medium |
| **Azure Key Vault** | ⭐⭐⭐⭐⭐ | Rs. 150/month | Medium |
| **HashiCorp Vault** | ⭐⭐⭐⭐⭐ | Free (self-hosted) | High |
| **Environment Variable** | ⭐⭐⭐ | Free | Low |

**Recommended:** Start with **Environment Variable**, move to **AWS KMS** when you have 100+ users.

---

## 🔧 **4. BACKEND API IMPLEMENTATION** {#backend}

### **4.1 User Registration (Store Credentials):**

**API Endpoint:** `POST /api/auth/register`

```python
# backend/api/auth.py (FastAPI example)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    dhan_client_id: str
    dhan_access_token: str

@router.post("/register")
async def register_user(req: RegisterRequest):
    """
    User registration - store credentials securely
    """
    # 1. Hash password (for login)
    password_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt())
    
    # 2. Create user in database
    cursor.execute("""
        INSERT INTO users (email, password_hash, full_name)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (req.email, password_hash, req.full_name))
    
    user_id = cursor.fetchone()['id']
    
    # 3. Encrypt Dhan credentials
    encryptor = CredentialEncryption(master_key=os.getenv("MASTER_KEY"))
    encrypted_client_id = encryptor.encrypt_credential(
        user_id, 
        req.dhan_client_id
    )
    encrypted_token = encryptor.encrypt_credential(
        user_id, 
        req.dhan_access_token
    )
    
    # 4. Store encrypted credentials
    cursor.execute("""
        UPDATE users 
        SET dhan_client_id_encrypted = %s,
            dhan_access_token_encrypted = %s
        WHERE id = %s
    """, (encrypted_client_id, encrypted_token, user_id))
    
    # 5. Provision bot instance (Kubernetes)
    provision_bot_instance(user_id)
    
    return {
        "success": True,
        "user_id": user_id,
        "message": "Registration successful! Your bot is being provisioned."
    }
```

### **4.2 Retrieve Credentials (For Bot Start):**

**API Endpoint:** `GET /api/users/{user_id}/credentials`

```python
# backend/api/users.py

@router.get("/{user_id}/credentials")
async def get_user_credentials(user_id: int):
    """
    Retrieve decrypted credentials for bot instance
    
    ⚠️ IMPORTANT: This endpoint should ONLY be accessible from:
    - Backend services (not exposed to public)
    - Bot instances (with service-to-service authentication)
    """
    # 1. Fetch encrypted credentials from database
    cursor.execute("""
        SELECT dhan_client_id_encrypted, dhan_access_token_encrypted
        FROM users
        WHERE id = %s AND status = 'active'
    """, (user_id,))
    
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Decrypt credentials
    encryptor = CredentialEncryption(master_key=os.getenv("MASTER_KEY"))
    
    client_id = encryptor.decrypt_credential(
        user_id, 
        user['dhan_client_id_encrypted']
    )
    access_token = encryptor.decrypt_credential(
        user_id, 
        user['dhan_access_token_encrypted']
    )
    
    # 3. Return (over secure internal network only!)
    return {
        "user_id": user_id,
        "dhan_client_id": client_id,
        "dhan_access_token": access_token
    }
```

**⚠️ CRITICAL:** This endpoint must be:
- Internal-only (not accessible from internet)
- Service-to-service authenticated
- Logged for auditing

---

## 🐳 **5. BOT INSTANCE CREDENTIAL INJECTION** {#injection}

### **5.1 How Bot Gets Credentials at Startup:**

**Option A: Environment Variables (Recommended)**

```python
# Modified live_trading_engine_with_trailing.py

import os
from dhanhq import dhanhq

# REMOVED: from creds import client_id, access_token

# NEW: Get credentials from environment variables
# These are injected by Kubernetes when pod starts
client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")
user_id = os.getenv("USER_ID")

if not client_id or not access_token:
    raise ValueError("Dhan credentials not provided! Check environment variables.")

# Now use credentials as before
dhan = dhanhq(client_id, access_token)

# Rest of your bot code...
```

**Option B: Fetch from Backend API**

```python
# Modified live_trading_engine_with_trailing.py

import os
import requests
from dhanhq import dhanhq

user_id = os.getenv("USER_ID")
backend_url = os.getenv("BACKEND_API_URL", "http://backend-service:8000")

# Fetch credentials from backend
response = requests.get(
    f"{backend_url}/api/users/{user_id}/credentials",
    headers={"X-Service-Token": os.getenv("SERVICE_TOKEN")}  # Service auth
)

if response.status_code != 200:
    raise ValueError(f"Failed to fetch credentials: {response.text}")

credentials = response.json()
client_id = credentials['dhan_client_id']
access_token = credentials['dhan_access_token']

# Use credentials
dhan = dhanhq(client_id, access_token)
```

---

## ☸️ **6. KUBERNETES SECRETS MANAGEMENT** {#kubernetes}

### **6.1 Create Kubernetes Secret per User:**

When user registers, create a Kubernetes Secret:

```python
# backend/bot_provisioning.py

from kubernetes import client, config
import base64

def provision_bot_instance(user_id: int, client_id: str, access_token: str):
    """
    Provision isolated bot instance with user's credentials
    """
    # Load Kubernetes config
    config.load_incluster_config()  # When running in K8s
    v1 = client.CoreV1Api()
    
    # 1. Create namespace for user (isolation)
    namespace = f"user-{user_id}"
    try:
        v1.create_namespace(
            body=client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
        )
    except client.exceptions.ApiException:
        pass  # Namespace already exists
    
    # 2. Create Secret with encrypted credentials
    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name=f"dhan-credentials",
            namespace=namespace
        ),
        type="Opaque",
        data={
            "DHAN_CLIENT_ID": base64.b64encode(client_id.encode()).decode(),
            "DHAN_ACCESS_TOKEN": base64.b64encode(access_token.encode()).decode(),
            "USER_ID": base64.b64encode(str(user_id).encode()).decode()
        }
    )
    
    v1.create_namespaced_secret(namespace=namespace, body=secret)
    
    # 3. Create bot deployment
    create_bot_deployment(user_id, namespace)


def create_bot_deployment(user_id: int, namespace: str):
    """
    Create bot deployment that uses the Secret
    """
    apps_v1 = client.AppsV1Api()
    
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(
            name=f"trading-bot",
            namespace=namespace
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": "trading-bot", "user": str(user_id)}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": "trading-bot", "user": str(user_id)}
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="trading-bot",
                            image="nifty-trading-bot:latest",
                            
                            # ⭐ INJECT CREDENTIALS FROM SECRET
                            env_from=[
                                client.V1EnvFromSource(
                                    secret_ref=client.V1SecretEnvSource(
                                        name="dhan-credentials"
                                    )
                                )
                            ],
                            
                            # Resource limits
                            resources=client.V1ResourceRequirements(
                                limits={"cpu": "500m", "memory": "512Mi"},
                                requests={"cpu": "250m", "memory": "256Mi"}
                            )
                        )
                    ]
                )
            )
        )
    )
    
    apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)
```

### **6.2 Kubernetes Manifest (YAML):**

```yaml
# bot-deployment.yaml (template)

apiVersion: v1
kind: Secret
metadata:
  name: dhan-credentials
  namespace: user-{{ USER_ID }}
type: Opaque
data:
  DHAN_CLIENT_ID: {{ BASE64_CLIENT_ID }}
  DHAN_ACCESS_TOKEN: {{ BASE64_ACCESS_TOKEN }}
  USER_ID: {{ BASE64_USER_ID }}

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-bot
  namespace: user-{{ USER_ID }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: trading-bot
  template:
    metadata:
      labels:
        app: trading-bot
        user: "{{ USER_ID }}"
    spec:
      containers:
      - name: trading-bot
        image: nifty-trading-bot:latest
        
        # ⭐ CREDENTIALS INJECTED AS ENV VARS
        envFrom:
        - secretRef:
            name: dhan-credentials
        
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "250m"
            memory: "256Mi"
```

---

## 🔐 **7. SECURITY BEST PRACTICES** {#security}

### **7.1 Credential Storage Checklist:**

✅ **DO:**
- ✅ Encrypt credentials before storing in database
- ✅ Use unique encryption key per user
- ✅ Store master key in AWS KMS / Azure Key Vault
- ✅ Rotate encryption keys every 90 days
- ✅ Use Kubernetes Secrets for runtime credentials
- ✅ Enable database column-level encryption
- ✅ Log all credential access (audit trail)
- ✅ Use HTTPS for all API calls
- ✅ Implement service-to-service authentication

❌ **DON'T:**
- ❌ Store plaintext credentials in database
- ❌ Hardcode credentials in code
- ❌ Expose credentials in API responses
- ❌ Log credentials (even encrypted)
- ❌ Share credentials between users
- ❌ Use same encryption key for all users
- ❌ Store credentials in Git repository

### **7.2 Credential Access Logging:**

```python
# backend/audit_log.py

import logging
from datetime import datetime

class CredentialAccessLogger:
    """Log every credential access for security audit"""
    
    def __init__(self):
        self.logger = logging.getLogger("credential_access")
    
    def log_access(self, user_id: int, action: str, ip_address: str):
        """
        Log credential access
        
        Actions: 'retrieve', 'update', 'delete'
        """
        self.logger.info(
            f"[CREDENTIAL_ACCESS] "
            f"UserID={user_id} "
            f"Action={action} "
            f"IP={ip_address} "
            f"Timestamp={datetime.utcnow().isoformat()}"
        )
        
        # Also store in database for compliance
        cursor.execute("""
            INSERT INTO credential_access_log 
            (user_id, action, ip_address, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, action, ip_address))


# Usage:
logger = CredentialAccessLogger()
logger.log_access(
    user_id=123,
    action='retrieve',
    ip_address='103.x.x.x'
)
```

---

## 📊 **8. COMPLETE FLOW DIAGRAM**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REGISTRATION                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────┐
      │ User enters:                         │
      │ - Email/Password                     │
      │ - Dhan Client ID: "1234567890"       │
      │ - Dhan Access Token: "eyJhbGc..."    │
      └──────────────────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────┐
      │ Backend API:                         │
      │ 1. Create user (user_id = 123)       │
      │ 2. Encrypt credentials:              │
      │    - client_id → "gAAAAABh3..."     │
      │    - token → "gAAAAABh4..."         │
      │ 3. Store in database (encrypted)     │
      └──────────────────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────┐
      │ PostgreSQL Database:                 │
      │ ┌──────────────────────────────────┐ │
      │ │ users table:                     │ │
      │ │ - id: 123                        │ │
      │ │ - email: user@example.com        │ │
      │ │ - dhan_client_id_encrypted:      │ │
      │ │   "gAAAAABh3..."                 │ │
      │ │ - dhan_access_token_encrypted:   │ │
      │ │   "gAAAAABh4..."                 │ │
      │ └──────────────────────────────────┘ │
      └──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOT PROVISIONING                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────┐
      │ Kubernetes:                          │
      │ 1. Create namespace: "user-123"      │
      │ 2. Create Secret:                    │
      │    - DHAN_CLIENT_ID (encrypted)      │
      │    - DHAN_ACCESS_TOKEN (encrypted)   │
      │ 3. Deploy bot pod                    │
      └──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOT STARTUP                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────┐
      │ Bot Container:                       │
      │ 1. Read env vars:                    │
      │    - DHAN_CLIENT_ID (from Secret)    │
      │    - DHAN_ACCESS_TOKEN (from Secret) │
      │ 2. Initialize Dhan API:              │
      │    dhan = dhanhq(client_id, token)   │
      │ 3. Start trading                     │
      └──────────────────────────────────────┘
                            │
                            ▼
      ┌──────────────────────────────────────┐
      │ Dhan API:                            │
      │ - Authenticate with user's           │
      │   credentials                        │
      │ - Place trades on user's account     │
      └──────────────────────────────────────┘
```

---

## 💡 **9. SUMMARY: KEY CHANGES NEEDED**

### **9.1 Current Bot Code (Single User):**

```python
# ❌ OLD WAY (current):
from creds import client_id, access_token
dhan = dhanhq(client_id, access_token)
```

### **9.2 SaaS Bot Code (Multi-User):**

```python
# ✅ NEW WAY (SaaS):
import os
from dhanhq import dhanhq

# Get credentials from environment (injected by Kubernetes)
client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")
user_id = os.getenv("USER_ID")

if not client_id or not access_token:
    raise ValueError("Credentials not found!")

dhan = dhanhq(client_id, access_token)

# Rest of your trading logic stays the same!
```

**That's it!** Only 5 lines of code change in your bot.

---

## 🎯 **10. FINAL ANSWER TO YOUR QUESTION**

### **Q: "When we move to SaaS, how do we manage client_id and access_token?"**

**A: Three-Step System:**

1. **Storage (Registration):**
   - User enters their Dhan credentials on your website
   - Backend encrypts them (AES-256, user-specific key)
   - Stores in PostgreSQL database

2. **Retrieval (Bot Start):**
   - When bot starts, Kubernetes injects credentials as environment variables
   - Bot reads from env vars instead of `creds.py`

3. **Security:**
   - Master encryption key in AWS KMS
   - Credentials never in plaintext
   - Each user isolated (namespace + secrets)
   - Full audit logging

### **Code Changes Needed:**

**In your bot (5 lines):**
```python
# Remove:
from creds import client_id, access_token

# Add:
import os
client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")
```

**Everything else stays the same!** Your trading logic doesn't change.

---

## 📚 **11. IMPLEMENTATION PRIORITY**

**Phase 1 (MVP):**
1. ✅ Database schema with encrypted columns
2. ✅ Encryption/decryption functions
3. ✅ Backend API for credential storage
4. ✅ Modified bot to read from env vars
5. ✅ Basic Kubernetes deployment

**Phase 2 (Production):**
1. ✅ Move master key to AWS KMS
2. ✅ Implement key rotation
3. ✅ Add audit logging
4. ✅ Service-to-service authentication
5. ✅ Penetration testing

---

**Document Version:** 1.0  
**Last Updated:** 05-04-2026  
**Author:** SaaS Technical Architecture Team

**Next Steps:**
1. Test encryption/decryption locally
2. Set up PostgreSQL with encrypted columns
3. Modify bot to use environment variables
4. Deploy test instance on Kubernetes
5. Validate end-to-end flow
