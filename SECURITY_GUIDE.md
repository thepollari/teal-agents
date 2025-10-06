# Teal Agents Framework - Security Guide

## Overview

This guide covers security best practices, authentication patterns, deployment security, and threat mitigation strategies for the Teal Agents Framework. Security is implemented at multiple layers including network, application, data, and operational security.

## Security Architecture

### Defense in Depth

The framework implements multiple security layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    Network Security                         │
│  • TLS/SSL Encryption  • Firewall Rules  • VPN Access      │
├─────────────────────────────────────────────────────────────┤
│                  Application Security                       │
│  • Authentication  • Authorization  • Input Validation     │
├─────────────────────────────────────────────────────────────┤
│                     Data Security                           │
│  • Encryption at Rest  • Encryption in Transit  • Secrets  │
├─────────────────────────────────────────────────────────────┤
│                 Infrastructure Security                     │
│  • Container Security  • Access Controls  • Monitoring     │
└─────────────────────────────────────────────────────────────┘
```

### Security Principles

1. **Zero Trust Architecture** - Never trust, always verify
2. **Principle of Least Privilege** - Minimal necessary permissions
3. **Defense in Depth** - Multiple security layers
4. **Secure by Default** - Security-first configuration
5. **Continuous Monitoring** - Real-time threat detection

## Authentication and Authorization

### Authentication Methods

#### 1. API Key Authentication

**Implementation**:
```python
# Environment configuration
TA_API_KEY=your-secure-api-key-here
API_KEY_HEADER=X-API-Key  # or Authorization: Bearer
```

**Usage**:
```bash
curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [...]}'
```

**Best Practices**:
- Use cryptographically secure random keys (minimum 32 characters)
- Rotate keys regularly (recommended: every 90 days)
- Store keys in secure secret management systems
- Never log or expose keys in error messages

#### 2. JWT Authentication

**Configuration**:
```python
# Environment variables
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_ISSUER=teal-agents
```

**Token Structure**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "user123",
    "session_id": "session_abc123",
    "permissions": ["agent_execute", "workflow_create"],
    "iss": "teal-agents",
    "exp": 1642248000,
    "iat": 1642244400,
    "jti": "token_unique_id"
  }
}
```

**Implementation Example**:
```python
import jwt
from datetime import datetime, timedelta

def create_jwt_token(user_id: str, permissions: list) -> str:
    payload = {
        "user_id": user_id,
        "permissions": permissions,
        "iss": "teal-agents",
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
        "jti": generate_unique_id()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
```

#### 3. OAuth 2.0 Integration

**Supported Flows**:
- Authorization Code Flow (recommended for web applications)
- Client Credentials Flow (for service-to-service)
- Device Code Flow (for CLI/mobile applications)

**Configuration**:
```yaml
oauth:
  provider: "azure_ad"  # or "google", "okta", "custom"
  client_id: "${OAUTH_CLIENT_ID}"
  client_secret: "${OAUTH_CLIENT_SECRET}"
  redirect_uri: "https://your-app.com/callback"
  scopes: ["openid", "profile", "teal-agents.execute"]
  token_endpoint: "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"
  authorization_endpoint: "https://login.microsoftonline.com/tenant/oauth2/v2.0/authorize"
```

### Authorization Patterns

#### Role-Based Access Control (RBAC)

**Role Definitions**:
```yaml
roles:
  admin:
    permissions:
      - agent.create
      - agent.delete
      - agent.execute
      - workflow.create
      - workflow.delete
      - user.manage
  
  developer:
    permissions:
      - agent.execute
      - agent.test
      - workflow.create
      - workflow.execute
  
  user:
    permissions:
      - agent.execute
      - workflow.execute
```

**Implementation**:
```python
from functools import wraps

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_permissions = get_user_permissions(request.user)
            if permission not in user_permissions:
                raise HTTPException(403, "Insufficient permissions")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_permission("agent.execute")
async def execute_agent(agent_name: str, input_data: dict):
    # Agent execution logic
    pass
```

#### Attribute-Based Access Control (ABAC)

**Policy Example**:
```json
{
  "policy_id": "agent_execution_policy",
  "description": "Control agent execution based on user attributes",
  "rules": [
    {
      "effect": "allow",
      "condition": {
        "and": [
          {"user.department": "engineering"},
          {"agent.category": "development"},
          {"time.hour": {">=": 9, "<=": 17}}
        ]
      }
    },
    {
      "effect": "deny",
      "condition": {
        "user.risk_level": "high"
      }
    }
  ]
}
```

## Network Security

### TLS/SSL Configuration

#### Certificate Management

**Production Certificate Setup**:
```yaml
# docker-compose.yml
services:
  teal-agents:
    image: ghcr.io/teal-agents/teal-agents:latest
    ports:
      - "443:8000"
    volumes:
      - ./certs/cert.pem:/app/certs/cert.pem:ro
      - ./certs/key.pem:/app/certs/key.pem:ro
    environment:
      - TLS_CERT_FILE=/app/certs/cert.pem
      - TLS_KEY_FILE=/app/certs/key.pem
      - TLS_ENABLED=true
```

**Let's Encrypt Integration**:
```bash
# Automated certificate renewal
#!/bin/bash
certbot renew --quiet --deploy-hook "docker-compose restart teal-agents"
```

#### TLS Configuration

**Minimum TLS Version**: TLS 1.2 (recommended: TLS 1.3)

**Cipher Suites** (recommended):
```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-RSA-AES128-GCM-SHA256
```

**NGINX Configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name teal-agents.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/teal-agents.crt;
    ssl_certificate_key /etc/ssl/private/teal-agents.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    location / {
        proxy_pass http://teal-agents-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Configuration

#### Network Segmentation

```bash
# iptables rules for production deployment
#!/bin/bash

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow HTTPS traffic
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow SSH (restrict to management network)
iptables -A INPUT -p tcp --dport 22 -s 10.0.1.0/24 -j ACCEPT

# Allow internal service communication
iptables -A INPUT -p tcp --dport 6379 -s 10.0.2.0/24 -j ACCEPT  # Redis
iptables -A INPUT -p tcp --dport 8000 -s 10.0.2.0/24 -j ACCEPT  # DynamoDB

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: "
```

#### Kubernetes Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: teal-agents-netpol
  namespace: teal-agents
spec:
  podSelector:
    matchLabels:
      app: teal-agents
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: load-balancer
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - podSelector:
        matchLabels:
          app: dynamodb
    ports:
    - protocol: TCP
      port: 8000
  - to: []  # Allow external API calls
    ports:
    - protocol: TCP
      port: 443
```

## Data Security

### Encryption at Rest

#### Database Encryption

**Redis Configuration**:
```bash
# redis.conf
requirepass your-strong-redis-password
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""
```

**DynamoDB Encryption**:
```yaml
# CloudFormation template
Resources:
  TealAgentsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: teal-agents-sessions
      SSESpecification:
        SSEEnabled: true
        KMSMasterKeyId: alias/teal-agents-key
      PointInTimeRecoveryEnabled: true
```

#### File System Encryption

**Docker Volume Encryption**:
```bash
# Create encrypted volume
docker volume create --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=1g,uid=1000,gid=1000,mode=0700 \
  encrypted-data
```

**Kubernetes Encrypted Storage**:
```yaml
apiVersion: v1
kind: StorageClass
metadata:
  name: encrypted-ssd
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  encrypted: "true"
  kms-key: projects/PROJECT_ID/locations/LOCATION/keyRings/RING_NAME/cryptoKeys/KEY_NAME
```

### Encryption in Transit

#### Internal Service Communication

**mTLS Configuration**:
```yaml
# istio-config.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: teal-agents
spec:
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: teal-agents-mtls
  namespace: teal-agents
spec:
  host: "*.teal-agents.svc.cluster.local"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
```

#### API Communication

**Client Certificate Authentication**:
```python
import ssl
import requests

# Configure client certificate
session = requests.Session()
session.cert = ('/path/to/client.crt', '/path/to/client.key')
session.verify = '/path/to/ca.crt'

response = session.post(
    'https://teal-agents.yourdomain.com/SimpleAgent/1.0/',
    json={'chat_history': [...]}
)
```

### Secret Management

#### Kubernetes Secrets

```yaml
# Create secret from command line
apiVersion: v1
kind: Secret
metadata:
  name: teal-agents-secrets
  namespace: teal-agents
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  jwt-secret: <base64-encoded-secret>
  redis-password: <base64-encoded-password>
```

**Secret Rotation**:
```bash
#!/bin/bash
# Automated secret rotation script

# Generate new API key
NEW_KEY=$(openssl rand -hex 32)

# Update Kubernetes secret
kubectl patch secret teal-agents-secrets -n teal-agents \
  -p='{"data":{"openai-api-key":"'$(echo -n $NEW_KEY | base64)'"}}'

# Restart deployments to pick up new secret
kubectl rollout restart deployment/teal-agents -n teal-agents
```

#### HashiCorp Vault Integration

```python
import hvac

# Vault client configuration
client = hvac.Client(
    url='https://vault.yourdomain.com',
    token=os.environ['VAULT_TOKEN']
)

# Read secret
secret = client.secrets.kv.v2.read_secret_version(
    path='teal-agents/api-keys'
)

openai_key = secret['data']['data']['openai_api_key']
```

#### AWS Secrets Manager

```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('teal-agents/api-keys')
openai_key = secrets['openai_api_key']
```

## Container Security

### Image Security

#### Base Image Hardening

```dockerfile
# Use minimal base images
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r tealagents && useradd -r -g tealagents tealagents

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=tealagents:tealagents . /app/

# Switch to non-root user
USER tealagents

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "sk_agents.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Image Scanning

**Trivy Integration**:
```bash
# Scan for vulnerabilities
trivy image ghcr.io/teal-agents/teal-agents:latest

# Fail build on high/critical vulnerabilities
trivy image --exit-code 1 --severity HIGH,CRITICAL \
  ghcr.io/teal-agents/teal-agents:latest
```

**GitHub Actions Security Scanning**:
```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build image
      run: docker build -t teal-agents:test .
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'teal-agents:test'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

### Runtime Security

#### Security Contexts

```yaml
# Kubernetes security context
apiVersion: apps/v1
kind: Deployment
metadata:
  name: teal-agents
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: teal-agents
        image: ghcr.io/teal-agents/teal-agents:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: var-tmp
          mountPath: /var/tmp
      volumes:
      - name: tmp
        emptyDir: {}
      - name: var-tmp
        emptyDir: {}
```

#### Pod Security Standards

```yaml
# Pod Security Policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: teal-agents-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Input Validation and Sanitization

### Request Validation

```python
from pydantic import BaseModel, validator
from typing import List, Optional
import re

class ChatMessage(BaseModel):
    role: str
    content: str
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant', 'system']:
            raise ValueError('Invalid role')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        # Sanitize content
        if len(v) > 10000:
            raise ValueError('Content too long')
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Potentially dangerous content detected')
        
        return v

class AgentRequest(BaseModel):
    chat_history: List[ChatMessage]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    @validator('chat_history')
    def validate_chat_history(cls, v):
        if len(v) > 100:
            raise ValueError('Chat history too long')
        return v
```

### SQL Injection Prevention

```python
# Use parameterized queries
async def get_user_sessions(user_id: str):
    query = """
    SELECT session_id, created_at, last_activity 
    FROM user_sessions 
    WHERE user_id = $1 AND active = true
    """
    return await database.fetch_all(query, user_id)

# Avoid string concatenation
# BAD: f"SELECT * FROM users WHERE id = {user_id}"
# GOOD: Use parameterized queries as above
```

### XSS Prevention

```python
import html
from markupsafe import escape

def sanitize_output(content: str) -> str:
    """Sanitize content for safe display"""
    # HTML escape
    content = html.escape(content)
    
    # Additional sanitization for markdown
    content = content.replace('[', '\\[').replace(']', '\\]')
    
    return content

# Usage in response
response_content = sanitize_output(agent_response)
```

## Monitoring and Incident Response

### Security Monitoring

#### Log Analysis

```python
import logging
from datetime import datetime

# Security event logging
security_logger = logging.getLogger('security')

def log_security_event(event_type: str, user_id: str, details: dict):
    security_logger.warning({
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent'),
        'details': details
    })

# Usage
log_security_event('authentication_failure', user_id, {
    'reason': 'invalid_api_key',
    'endpoint': '/SimpleAgent/1.0/'
})
```

#### Anomaly Detection

```python
from collections import defaultdict
from datetime import datetime, timedelta

class AnomalyDetector:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.failed_attempts = defaultdict(int)
    
    def check_rate_limit(self, user_id: str, limit: int = 100) -> bool:
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Clean old requests
        self.request_counts[user_id] = [
            req_time for req_time in self.request_counts[user_id]
            if req_time > hour_ago
        ]
        
        # Check current count
        current_count = len(self.request_counts[user_id])
        if current_count >= limit:
            log_security_event('rate_limit_exceeded', user_id, {
                'requests_per_hour': current_count,
                'limit': limit
            })
            return False
        
        self.request_counts[user_id].append(now)
        return True
    
    def check_failed_attempts(self, user_id: str, threshold: int = 5) -> bool:
        if self.failed_attempts[user_id] >= threshold:
            log_security_event('brute_force_detected', user_id, {
                'failed_attempts': self.failed_attempts[user_id],
                'threshold': threshold
            })
            return False
        return True
```

### Incident Response

#### Automated Response

```python
class SecurityIncidentHandler:
    def __init__(self):
        self.blocked_ips = set()
        self.blocked_users = set()
    
    def handle_security_incident(self, incident_type: str, details: dict):
        if incident_type == 'brute_force_detected':
            self.block_user(details['user_id'])
            self.notify_security_team(incident_type, details)
        
        elif incident_type == 'rate_limit_exceeded':
            self.temporary_block_ip(details['ip_address'])
        
        elif incident_type == 'suspicious_payload':
            self.quarantine_request(details)
            self.notify_security_team(incident_type, details)
    
    def block_user(self, user_id: str):
        self.blocked_users.add(user_id)
        # Update database/cache
        redis_client.sadd('blocked_users', user_id)
    
    def notify_security_team(self, incident_type: str, details: dict):
        # Send alert to security team
        alert_payload = {
            'incident_type': incident_type,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details,
            'severity': self.get_severity(incident_type)
        }
        
        # Send to SIEM/alerting system
        send_security_alert(alert_payload)
```

## Compliance and Auditing

### Audit Logging

```python
class AuditLogger:
    def __init__(self):
        self.audit_logger = logging.getLogger('audit')
    
    def log_agent_execution(self, user_id: str, agent_name: str, 
                          input_data: dict, output_data: dict):
        audit_event = {
            'event_type': 'agent_execution',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'agent_name': agent_name,
            'input_hash': self.hash_sensitive_data(input_data),
            'output_hash': self.hash_sensitive_data(output_data),
            'execution_time': time.time() - start_time,
            'success': True
        }
        self.audit_logger.info(audit_event)
    
    def hash_sensitive_data(self, data: dict) -> str:
        """Create hash of data for audit trail without storing sensitive content"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
```

### GDPR Compliance

```python
class GDPRCompliance:
    def __init__(self):
        self.data_retention_days = 365
    
    def handle_data_deletion_request(self, user_id: str):
        """Handle GDPR Article 17 - Right to erasure"""
        # Delete user data from all systems
        self.delete_user_sessions(user_id)
        self.delete_user_chat_history(user_id)
        self.anonymize_audit_logs(user_id)
        
        # Log the deletion
        self.log_data_deletion(user_id)
    
    def export_user_data(self, user_id: str) -> dict:
        """Handle GDPR Article 20 - Right to data portability"""
        user_data = {
            'user_id': user_id,
            'sessions': self.get_user_sessions(user_id),
            'chat_history': self.get_user_chat_history(user_id),
            'preferences': self.get_user_preferences(user_id),
            'export_timestamp': datetime.utcnow().isoformat()
        }
        
        self.log_data_export(user_id)
        return user_data
```

## Security Testing

### Penetration Testing

```bash
#!/bin/bash
# Automated security testing script

# Test for common vulnerabilities
echo "Running security tests..."

# Test SQL injection
curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "'; DROP TABLE users; --"}]}'

# Test XSS
curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
  -H "Content-Type: application/json" \
  -d '{"chat_history": [{"role": "user", "content": "<script>alert(\"XSS\")</script>"}]}'

# Test authentication bypass
curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid-token" \
  -d '{"chat_history": [{"role": "user", "content": "test"}]}'

# Test rate limiting
for i in {1..150}; do
  curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
    -H "Content-Type: application/json" \
    -H "X-API-Key: test-key" \
    -d '{"chat_history": [{"role": "user", "content": "test"}]}' &
done
wait

echo "Security tests completed"
```

### Vulnerability Scanning

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  push:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: SAST Scan
      uses: github/super-linter@v4
      env:
        DEFAULT_BRANCH: main
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        VALIDATE_PYTHON_BANDIT: true
    
    - name: Dependency Scan
      run: |
        pip install safety
        safety check --json --output safety-report.json
    
    - name: Container Scan
      run: |
        docker build -t teal-agents:test .
        trivy image --format json --output trivy-report.json teal-agents:test
    
    - name: Upload Results
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          safety-report.json
          trivy-report.json
```

This comprehensive security guide provides the foundation for deploying and maintaining secure Teal Agents Framework installations across various environments and threat models.
