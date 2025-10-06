# Teal Agents Framework - Performance and Monitoring Guide

## Overview

This guide covers performance optimization strategies, monitoring implementation, telemetry configuration, and troubleshooting techniques for the Teal Agents Framework. It provides comprehensive guidance for achieving optimal performance in development, staging, and production environments.

## Performance Architecture

### System Performance Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Performance Layers                       │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                          │
│  • Agent Execution Optimization  • Caching Strategies      │
│  • Connection Pooling  • Async Processing                  │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  • Resource Allocation  • Load Balancing  • Auto-scaling   │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  • Database Optimization  • State Management  • Caching    │
├─────────────────────────────────────────────────────────────┤
│  Network Layer                                              │
│  • CDN  • Connection Optimization  • Compression           │
└─────────────────────────────────────────────────────────────┘
```

### Key Performance Metrics

| Metric Category | Key Indicators | Target Values |
|----------------|----------------|---------------|
| **Response Time** | Agent execution latency | < 2s (95th percentile) |
| **Throughput** | Requests per second | > 100 RPS per instance |
| **Availability** | Uptime percentage | > 99.9% |
| **Resource Usage** | CPU/Memory utilization | < 70% average |
| **Error Rate** | Failed requests | < 0.1% |

## Application Performance Optimization

### Agent Execution Optimization

#### Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

class OptimizedAgentExecutor:
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def execute_agent_batch(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple agent requests concurrently"""
        tasks = []
        for request in requests:
            task = self.execute_single_agent(request)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
    
    async def execute_single_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor, 
                self._sync_execute_agent, 
                request
            )
    
    def _sync_execute_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Synchronous agent execution logic
        return {"response": "Agent response", "metadata": {}}
```

#### Connection Pooling

```python
import aiohttp
import asyncio
from typing import Optional

class HTTPClientPool:
    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 30):
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=max_connections_per_host,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=timeout
            )
        return self.session
    
    async def make_request(self, method: str, url: str, **kwargs) -> dict:
        session = await self.get_session()
        async with session.request(method, url, **kwargs) as response:
            return await response.json()
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Global client pool instance
http_client_pool = HTTPClientPool()
```

#### Caching Strategies

```python
import redis
import json
import hashlib
from typing import Any, Optional
from functools import wraps

class AgentResponseCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    def cache_key(self, agent_name: str, agent_version: str, input_data: dict) -> str:
        """Generate cache key from agent and input data"""
        input_hash = hashlib.md5(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()
        return f"agent:{agent_name}:{agent_version}:{input_hash}"
    
    async def get_cached_response(self, cache_key: str) -> Optional[dict]:
        """Retrieve cached response"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Cache retrieval error: {e}")
        return None
    
    async def cache_response(self, cache_key: str, response: dict, ttl: int = None):
        """Cache agent response"""
        try:
            self.redis_client.setex(
                cache_key, 
                ttl or self.default_ttl, 
                json.dumps(response)
            )
        except Exception as e:
            print(f"Cache storage error: {e}")

def cache_agent_response(ttl: int = 3600):
    """Decorator to cache agent responses"""
    def decorator(func):
        @wraps(func)
        async def wrapper(agent_name: str, agent_version: str, input_data: dict, *args, **kwargs):
            cache = AgentResponseCache()
            cache_key = cache.cache_key(agent_name, agent_version, input_data)
            
            # Try to get cached response
            cached_response = await cache.get_cached_response(cache_key)
            if cached_response:
                cached_response['metadata']['cached'] = True
                return cached_response
            
            # Execute agent and cache response
            response = await func(agent_name, agent_version, input_data, *args, **kwargs)
            await cache.cache_response(cache_key, response, ttl)
            response['metadata']['cached'] = False
            
            return response
        return wrapper
    return decorator
```

### Memory Management

#### Memory Pool Configuration

```python
import gc
import psutil
from typing import Dict, Any

class MemoryManager:
    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        memory_info = self.process.memory_info()
        system_memory = psutil.virtual_memory()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': self.process.memory_percent(),
            'system_available_mb': system_memory.available / 1024 / 1024,
            'system_percent': system_memory.percent
        }
    
    def should_trigger_gc(self) -> bool:
        """Check if garbage collection should be triggered"""
        memory_usage = self.get_memory_usage()
        return memory_usage['percent'] > self.max_memory_percent
    
    def optimize_memory(self):
        """Perform memory optimization"""
        if self.should_trigger_gc():
            # Force garbage collection
            collected = gc.collect()
            
            # Log memory optimization
            memory_after = self.get_memory_usage()
            print(f"Memory optimization: collected {collected} objects, "
                  f"memory usage: {memory_after['percent']:.1f}%")

# Global memory manager
memory_manager = MemoryManager()
```

## Infrastructure Performance

### Resource Allocation

#### Container Resource Limits

```yaml
# Kubernetes deployment with optimized resources
apiVersion: apps/v1
kind: Deployment
metadata:
  name: teal-agents
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: teal-agents
        image: ghcr.io/teal-agents/teal-agents:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: UVICORN_WORKERS
          value: "4"
        - name: UVICORN_WORKER_CLASS
          value: "uvicorn.workers.UvicornWorker"
        - name: MAX_CONCURRENT_REQUESTS
          value: "100"
        - name: KEEPALIVE_TIMEOUT
          value: "65"
```

#### Auto-scaling Configuration

```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: teal-agents-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: teal-agents
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "50"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

## Database and State Management Performance

### Redis Optimization

#### Redis Configuration

```bash
# redis.conf - Production optimized
# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes

# Network
tcp-keepalive 300
timeout 0
tcp-backlog 511

# Performance
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Logging
loglevel notice
syslog-enabled yes
syslog-ident redis
```

## Monitoring and Telemetry

### Application Metrics

#### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

# Define metrics
REQUEST_COUNT = Counter(
    'teal_agents_requests_total',
    'Total number of requests',
    ['agent_name', 'status', 'endpoint']
)

REQUEST_DURATION = Histogram(
    'teal_agents_request_duration_seconds',
    'Request duration in seconds',
    ['agent_name', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf')]
)

ACTIVE_CONNECTIONS = Gauge(
    'teal_agents_active_connections',
    'Number of active connections'
)

MEMORY_USAGE = Gauge(
    'teal_agents_memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'teal_agents_cpu_usage_percent',
    'CPU usage percentage'
)

def track_performance(agent_name: str = None, endpoint: str = None):
    """Decorator to track request performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_COUNT.labels(
                    agent_name=agent_name or 'unknown',
                    status=status,
                    endpoint=endpoint or 'unknown'
                ).inc()
                REQUEST_DURATION.labels(
                    agent_name=agent_name or 'unknown',
                    endpoint=endpoint or 'unknown'
                ).observe(duration)
        
        return wrapper
    return decorator

# Start metrics server
def start_metrics_server(port: int = 8080):
    start_http_server(port)
    print(f"Metrics server started on port {port}")
```

### Health Checks and Monitoring

#### Comprehensive Health Check

```python
from typing import Dict, Any
import asyncio
import aiohttp
import redis

class HealthChecker:
    def __init__(self):
        self.checks = {
            'database': self.check_database,
            'redis': self.check_redis,
            'external_apis': self.check_external_apis,
            'memory': self.check_memory,
            'disk': self.check_disk_space
        }
    
    async def check_health(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True
        
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                if not result.get('healthy', False):
                    overall_healthy = False
            except Exception as e:
                results[check_name] = {
                    'healthy': False,
                    'error': str(e)
                }
                overall_healthy = False
        
        return {
            'healthy': overall_healthy,
            'timestamp': time.time(),
            'checks': results
        }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            start_time = time.time()
            redis_client.ping()
            response_time = time.time() - start_time
            
            return {
                'healthy': True,
                'response_time': response_time,
                'memory_usage': redis_client.info()['used_memory']
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

# Global health checker
health_checker = HealthChecker()
```

### Logging and Observability

#### Structured Logging

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create structured formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self.StructuredFormatter())
        self.logger.addHandler(handler)
    
    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add extra fields if present
            if hasattr(record, 'user_id'):
                log_entry['user_id'] = record.user_id
            if hasattr(record, 'agent_name'):
                log_entry['agent_name'] = record.agent_name
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'execution_time'):
                log_entry['execution_time'] = record.execution_time
            
            return json.dumps(log_entry)

# Usage example
performance_logger = StructuredLogger('performance')

def log_agent_execution(agent_name: str, execution_time: float, user_id: str = None):
    performance_logger.logger.info(
        f"Agent {agent_name} executed",
        extra={
            'agent_name': agent_name,
            'execution_time': execution_time,
            'user_id': user_id
        }
    )
```

## Performance Testing

### Load Testing

#### Locust Configuration

```python
# locustfile.py
from locust import HttpUser, task, between
import json
import random

class TealAgentsUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup for each user"""
        self.api_key = "test-api-key"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    @task(3)
    def execute_simple_agent(self):
        """Test simple agent execution"""
        payload = {
            "chat_history": [
                {
                    "role": "user",
                    "content": f"Hello! This is test message {random.randint(1, 1000)}"
                }
            ]
        }
        
        with self.client.post(
            "/SimpleAgent/1.0/",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def execute_plugin_agent(self):
        """Test agent with plugins"""
        payload = {
            "chat_history": [
                {
                    "role": "user",
                    "content": "What's the weather like today?"
                }
            ]
        }
        
        self.client.post(
            "/WeatherAgent/1.0/",
            json=payload,
            headers=self.headers
        )

# Run load test
# locust -f locustfile.py --host=http://localhost:8000
```

## Troubleshooting Performance Issues

### Common Performance Problems

#### High Response Times

**Diagnosis Steps:**
```bash
# Check system resources
top -p $(pgrep -f "uvicorn")
htop

# Check memory usage
free -h
cat /proc/meminfo

# Check disk I/O
iostat -x 1

# Check network connections
netstat -an | grep :8000
ss -tuln | grep :8000
```

**Solutions:**
1. **Increase worker processes**:
   ```bash
   uvicorn sk_agents.app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

2. **Optimize database connections**:
   ```python
   # Increase connection pool size
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=30
   ```

3. **Enable caching**:
   ```python
   REDIS_CACHE_ENABLED=true
   CACHE_TTL=3600
   ```

#### Memory Leaks

**Detection:**
```python
import tracemalloc
import gc

def detect_memory_leaks():
    tracemalloc.start()
    
    # Run your application code
    # ...
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    # Get top memory consumers
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()

# Force garbage collection
def force_gc():
    collected = gc.collect()
    print(f"Garbage collected {collected} objects")
```

## Best Practices Summary

### Development Best Practices

1. **Use Async/Await**: Leverage Python's async capabilities for I/O operations
2. **Connection Pooling**: Reuse connections for external services
3. **Caching Strategy**: Implement multi-level caching (memory, Redis, CDN)
4. **Resource Limits**: Set appropriate CPU and memory limits
5. **Monitoring**: Implement comprehensive monitoring from day one

### Production Best Practices

1. **Auto-scaling**: Configure HPA based on CPU, memory, and custom metrics
2. **Load Balancing**: Use proper load balancing strategies
3. **Health Checks**: Implement comprehensive health checks
4. **Circuit Breakers**: Protect against cascading failures
5. **Performance Testing**: Regular load testing and benchmarking

### Monitoring Best Practices

1. **Structured Logging**: Use structured, searchable logs
2. **Distributed Tracing**: Implement tracing for complex workflows
3. **Custom Metrics**: Track business-specific metrics
4. **Alerting**: Set up proactive alerting on key metrics
5. **Dashboard**: Create comprehensive performance dashboards

This comprehensive performance guide provides the foundation for optimizing, monitoring, and troubleshooting the Teal Agents Framework across all deployment scenarios and scale requirements.
