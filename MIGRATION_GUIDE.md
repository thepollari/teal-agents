# Teal Agents Framework - Migration and Upgrade Guide

## Overview

This guide provides comprehensive instructions for migrating between different versions of the Teal Agents Framework, upgrading dependencies, and handling breaking changes. It covers migration paths from legacy configurations to modern implementations and framework version upgrades.

## Framework Version Migration

### API Version Migration

The Teal Agents Framework supports multiple API versions with different capabilities:

- **`skagents/v1`** → Basic agents with custom types
- **`skagents/v2alpha1`** → Multi-modal agents with A2A capabilities  
- **`tealagents/v1alpha1`** → Stateful agents with authentication

#### Migration Path: v1 → v2alpha1

**Before (skagents/v1)**:
```yaml
apiVersion: skagents/v1
kind: Agent
name: MyAgent
service_name: MyAgent
version: 1.0
description: "Basic agent"
spec:
  model: gpt-4o
  system_prompt: "You are a helpful assistant"
  plugins:
    - WeatherPlugin
```

**After (skagents/v2alpha1)**:
```yaml
apiVersion: skagents/v2alpha1
kind: Agent
name: MyAgent
version: 1.0
metadata:
  description: "Enhanced agent with multi-modal support"
  skills:
    - id: "weather"
      name: "Weather Information"
      description: "Get weather information for locations"
      tags: ["weather", "location"]
      examples: ["What's the weather in New York?"]
      input_modes: ["text"]
      output_modes: ["text"]
spec:
  model: gpt-4o
  system_prompt: "You are a helpful assistant with weather capabilities"
  plugins:
    - WeatherPlugin
  max_tokens: 2000
  temperature: 0.7
```

**Migration Steps**:

1. **Update API Version**:
   ```bash
   # Find all v1 configurations
   find . -name "*.yaml" -exec grep -l "apiVersion: skagents/v1" {} \;
   
   # Update API version
   sed -i 's/apiVersion: skagents\/v1/apiVersion: skagents\/v2alpha1/g' config.yaml
   ```

2. **Add Metadata Section**:
   ```python
   # migration_script.py
   import yaml
   
   def migrate_v1_to_v2(config_file):
       with open(config_file, 'r') as f:
           config = yaml.safe_load(f)
       
       # Remove service_name (v1 only)
       if 'service_name' in config:
           del config['service_name']
       
       # Add metadata section
       config['metadata'] = {
           'description': config.get('description', ''),
           'skills': [{
               'id': 'default',
               'name': 'Default Skill',
               'description': 'Primary agent capability',
               'tags': [],
               'examples': [],
               'input_modes': ['text'],
               'output_modes': ['text']
           }]
       }
       
       # Enhanced spec section
       if 'spec' not in config:
           config['spec'] = {}
       
       config['spec'].update({
           'max_tokens': 2000,
           'temperature': 0.7
       })
       
       with open(config_file, 'w') as f:
           yaml.dump(config, f, default_flow_style=False)
   ```

3. **Update Input/Output Types**:
   ```python
   # For custom types, update to v2 format
   # v1: BaseInput
   # v2: BaseMultiModalInput (supports images)
   
   from sk_agents.ska_types import BaseMultiModalInput
   
   class CustomInput(BaseMultiModalInput):
       additional_field: str = ""
   ```

#### Migration Path: v2alpha1 → tealagents/v1alpha1

**Before (skagents/v2alpha1)**:
```yaml
apiVersion: skagents/v2alpha1
kind: Agent
name: ChatAgent
version: 1.0
spec:
  model: gpt-4o
  system_prompt: "You are a helpful assistant"
```

**After (tealagents/v1alpha1)**:
```yaml
apiVersion: tealagents/v1alpha1
kind: Agent
name: ChatAgent
version: 1.0
metadata:
  description: "Stateful chat agent with authentication"
  skills:
    - id: "chat"
      name: "Conversational AI"
      description: "Engage in natural conversations"
spec:
  model: gpt-4o
  system_prompt: "You are a helpful assistant"
  state_management:
    enabled: true
    backend: "redis"
    session_timeout: 3600
  authentication:
    required: true
    methods: ["jwt", "api_key"]
```

**Migration Steps**:

1. **Update Configuration**:
   ```python
   def migrate_v2_to_teal_v1(config_file):
       with open(config_file, 'r') as f:
           config = yaml.safe_load(f)
       
       # Update API version
       config['apiVersion'] = 'tealagents/v1alpha1'
       
       # Add state management
       config['spec']['state_management'] = {
           'enabled': True,
           'backend': 'redis',
           'session_timeout': 3600
       }
       
       # Add authentication
       config['spec']['authentication'] = {
           'required': True,
           'methods': ['jwt', 'api_key']
       }
       
       with open(config_file, 'w') as f:
           yaml.dump(config, f, default_flow_style=False)
   ```

2. **Set Up State Management**:
   ```bash
   # Environment variables for stateful agents
   export REDIS_URL=redis://localhost:6379
   export STATE_MANAGER_TYPE=redis
   export JWT_SECRET_KEY=your-secret-key
   ```

3. **Update Client Code**:
   ```python
   # Before (stateless)
   response = requests.post('/ChatAgent/1.0/', json={
       'chat_history': [{'role': 'user', 'content': 'Hello'}]
   })
   
   # After (stateful)
   response = requests.post('/ChatAgent/1.0/', 
       headers={'Authorization': 'Bearer jwt-token'},
       json={
           'chat_history': [{'role': 'user', 'content': 'Hello'}],
           'user_id': 'user123',
           'session_id': 'session_abc'
       }
   )
   ```

### Framework Version Upgrades

#### Upgrading from 1.x to 2.x

**Breaking Changes**:
- Plugin interface changes
- Configuration schema updates
- Dependency version bumps
- API endpoint modifications

**Migration Steps**:

1. **Update Dependencies**:
   ```bash
   # Update pyproject.toml
   uv add "sk-agents>=2.0.0,<3.0.0"
   uv add "semantic-kernel>=2.0.0"
   uv sync
   ```

2. **Update Plugin Interface**:
   ```python
   # Before (v1.x)
   from sk_agents.plugins import BasePlugin
   
   class WeatherPlugin(BasePlugin):
       def get_weather(self, location: str) -> str:
           return f"Weather in {location}"
   
   # After (v2.x)
   from sk_agents.ska_types import BasePlugin
   from semantic_kernel import kernel_function
   
   class WeatherPlugin(BasePlugin):
       @kernel_function(description="Get weather for location")
       async def get_weather(self, location: str) -> str:
           return f"Weather in {location}"
   ```

3. **Update Configuration Loading**:
   ```python
   # Before (v1.x)
   from sk_agents.config import load_config
   config = load_config('config.yaml')
   
   # After (v2.x)
   from ska_utils.app_config import AppConfig
   config = AppConfig.from_yaml('config.yaml')
   ```

#### Upgrading Dependencies

**Semantic Kernel Upgrades**:
```bash
# Check current version
uv run python -c "import semantic_kernel; print(semantic_kernel.__version__)"

# Update to latest compatible version
uv add "semantic-kernel>=1.5.0,<2.0.0"

# Handle breaking changes
# - Update import statements
# - Modify kernel initialization
# - Update plugin registration
```

**Python Version Upgrades**:
```bash
# Update Python version requirement
# pyproject.toml
requires-python = ">=3.12"

# Update Docker base image
FROM python:3.12-slim

# Update CI/CD configuration
# .github/workflows/test.yml
python-version: ["3.12", "3.13"]
```

## Configuration Migration

### Environment Variable Migration

#### Legacy to Modern Configuration

**Before**:
```bash
# Legacy environment variables
OPENAI_API_KEY=sk-...
AGENT_CONFIG_PATH=/path/to/config.yaml
DEBUG=true
LOG_LEVEL=INFO
```

**After**:
```bash
# Modern configuration
TA_OPENAI_API_KEY=sk-...
TA_SERVICE_CONFIG=/path/to/config.yaml
TA_DEBUG_MODE=true
TA_LOG_LEVEL=INFO
TA_REDIS_URL=redis://localhost:6379
TA_STATE_MANAGER_TYPE=redis
```

**Migration Script**:
```bash
#!/bin/bash
# migrate_env.sh

# Create backup
cp .env .env.backup

# Migrate variables
sed -i 's/^OPENAI_API_KEY=/TA_OPENAI_API_KEY=/' .env
sed -i 's/^AGENT_CONFIG_PATH=/TA_SERVICE_CONFIG=/' .env
sed -i 's/^DEBUG=/TA_DEBUG_MODE=/' .env
sed -i 's/^LOG_LEVEL=/TA_LOG_LEVEL=/' .env

# Add new variables
echo "TA_REDIS_URL=redis://localhost:6379" >> .env
echo "TA_STATE_MANAGER_TYPE=memory" >> .env

echo "Environment migration completed"
```

### Docker Configuration Migration

#### Docker Compose v1 to v2

**Before (docker-compose v1)**:
```yaml
version: '2'
services:
  teal-agents:
    image: teal-agents:1.0
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    links:
      - redis
  
  redis:
    image: redis:6
```

**After (docker-compose v2)**:
```yaml
version: '3.8'
services:
  teal-agents:
    image: ghcr.io/teal-agents/teal-agents:2.0
    ports:
      - "8000:8000"
    environment:
      - TA_OPENAI_API_KEY=${OPENAI_API_KEY}
      - TA_REDIS_URL=redis://redis:6379
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Database Migration

### State Storage Migration

#### From Memory to Redis

**Migration Steps**:

1. **Install Redis**:
   ```bash
   # Docker
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   
   # Or using docker-compose
   docker-compose up -d redis
   ```

2. **Update Configuration**:
   ```python
   # config.py
   STATE_MANAGER_CONFIG = {
       'type': 'redis',
       'url': 'redis://localhost:6379',
       'db': 0,
       'key_prefix': 'teal_agents:',
       'ttl': 3600
   }
   ```

3. **Migrate Existing Sessions**:
   ```python
   # migrate_sessions.py
   import json
   import redis
   from datetime import datetime, timedelta
   
   def migrate_memory_to_redis():
       redis_client = redis.from_url('redis://localhost:6379')
       
       # Load existing session data (if any)
       try:
           with open('sessions.json', 'r') as f:
               sessions = json.load(f)
           
           for session_id, session_data in sessions.items():
               key = f"teal_agents:session:{session_id}"
               redis_client.setex(
                   key, 
                   3600,  # 1 hour TTL
                   json.dumps(session_data)
               )
           
           print(f"Migrated {len(sessions)} sessions to Redis")
       except FileNotFoundError:
           print("No existing sessions to migrate")
   
   if __name__ == "__main__":
       migrate_memory_to_redis()
   ```

## Plugin Migration

### Plugin Interface Updates

#### Legacy Plugin to Modern Plugin

**Before (Legacy)**:
```python
class WeatherPlugin:
    def __init__(self):
        self.name = "WeatherPlugin"
    
    def get_weather(self, location: str) -> str:
        # Implementation
        return f"Weather in {location}"
    
    def get_forecast(self, location: str, days: int) -> str:
        # Implementation
        return f"Forecast for {location}"
```

**After (Modern)**:
```python
from sk_agents.ska_types import BasePlugin
from semantic_kernel import kernel_function
from pydantic import BaseModel
from typing import Optional

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    condition: str
    humidity: Optional[int] = None

class WeatherPlugin(BasePlugin):
    """Weather information plugin"""
    
    @kernel_function(
        description="Get current weather for a location",
        name="get_weather"
    )
    async def get_weather(self, location: str) -> WeatherResponse:
        """Get current weather information"""
        # Implementation with proper error handling
        try:
            weather_data = await self._fetch_weather(location)
            return WeatherResponse(
                location=location,
                temperature=weather_data['temp'],
                condition=weather_data['condition'],
                humidity=weather_data.get('humidity')
            )
        except Exception as e:
            raise ValueError(f"Failed to get weather for {location}: {e}")
    
    @kernel_function(
        description="Get weather forecast for multiple days",
        name="get_forecast"
    )
    async def get_forecast(self, location: str, days: int = 3) -> list[WeatherResponse]:
        """Get weather forecast"""
        # Implementation
        pass
    
    async def _fetch_weather(self, location: str) -> dict:
        """Private method to fetch weather data"""
        # Implementation
        pass
```

## Testing Migration

### Test Framework Updates

#### Pytest Configuration Migration

**Before**:
```python
# test_agents.py
import unittest
from sk_agents import Agent

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Agent('config.yaml')
    
    def test_agent_response(self):
        response = self.agent.execute({'message': 'Hello'})
        self.assertIsNotNone(response)
```

**After**:
```python
# test_agents.py
import pytest
import asyncio
from sk_agents import Agent
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def agent():
    """Create test agent instance"""
    agent = Agent('test_config.yaml')
    await agent.initialize()
    yield agent
    await agent.cleanup()

@pytest.mark.asyncio
async def test_agent_response(agent):
    """Test agent response generation"""
    with patch('sk_agents.completion_factory.create_completion') as mock_completion:
        mock_completion.return_value = "Test response"
        
        response = await agent.execute({
            'chat_history': [{'role': 'user', 'content': 'Hello'}]
        })
        
        assert response is not None
        assert 'response' in response
        assert response['response'] == "Test response"

@pytest.mark.integration
async def test_agent_with_real_api(agent):
    """Integration test with real API"""
    response = await agent.execute({
        'chat_history': [{'role': 'user', 'content': 'Hello'}]
    })
    
    assert response is not None
    assert len(response['response']) > 0
```

## Deployment Migration

### Kubernetes Migration

#### From Docker Compose to Kubernetes

**Migration Steps**:

1. **Convert Services**:
   ```bash
   # Use kompose to convert docker-compose.yml
   kompose convert -f docker-compose.yml
   
   # Or create manually
   kubectl create deployment teal-agents --image=ghcr.io/teal-agents/teal-agents:latest
   kubectl expose deployment teal-agents --port=80 --target-port=8000
   ```

2. **Create ConfigMaps**:
   ```yaml
   # configmap.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: teal-agents-config
   data:
     TA_LOG_LEVEL: "INFO"
     TA_REDIS_URL: "redis://redis-service:6379"
   ```

3. **Create Secrets**:
   ```bash
   kubectl create secret generic teal-agents-secrets \
     --from-literal=TA_OPENAI_API_KEY=sk-... \
     --from-literal=TA_JWT_SECRET=secret-key
   ```

## Rollback Procedures

### Configuration Rollback

```bash
#!/bin/bash
# rollback.sh

# Backup current configuration
cp config.yaml config.yaml.backup

# Restore previous configuration
if [ -f "config.yaml.v1" ]; then
    cp config.yaml.v1 config.yaml
    echo "Rolled back to v1 configuration"
else
    echo "No v1 configuration found"
    exit 1
fi

# Restart services
docker-compose restart teal-agents
```

### Database Rollback

```python
# rollback_db.py
import redis
import json
from datetime import datetime

def rollback_redis_migration():
    """Rollback Redis migration"""
    redis_client = redis.from_url('redis://localhost:6379')
    
    # Export current data
    backup_data = {}
    keys = redis_client.keys('teal_agents:*')
    
    for key in keys:
        backup_data[key.decode()] = redis_client.get(key).decode()
    
    # Save backup
    with open(f'redis_backup_{datetime.now().isoformat()}.json', 'w') as f:
        json.dump(backup_data, f)
    
    # Clear migrated data
    if keys:
        redis_client.delete(*keys)
    
    print(f"Rolled back {len(keys)} Redis keys")
```

## Validation and Testing

### Migration Validation

```python
# validate_migration.py
import yaml
import requests
import asyncio

async def validate_migration():
    """Validate successful migration"""
    
    # Test configuration loading
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        assert config['apiVersion'] in ['skagents/v2alpha1', 'tealagents/v1alpha1']
        print("✓ Configuration format valid")
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return False
    
    # Test API endpoints
    try:
        response = requests.get('http://localhost:8000/health')
        assert response.status_code == 200
        print("✓ Health endpoint accessible")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test agent execution
    try:
        response = requests.post(
            f'http://localhost:8000/{config["name"]}/{config["version"]}/',
            json={'chat_history': [{'role': 'user', 'content': 'test'}]}
        )
        assert response.status_code == 200
        print("✓ Agent execution successful")
    except Exception as e:
        print(f"✗ Agent execution failed: {e}")
        return False
    
    print("Migration validation completed successfully")
    return True

if __name__ == "__main__":
    asyncio.run(validate_migration())
```

This comprehensive migration guide ensures smooth transitions between framework versions while maintaining data integrity and minimizing downtime during upgrades.
