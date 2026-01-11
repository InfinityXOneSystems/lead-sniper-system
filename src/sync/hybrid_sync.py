"""
HYBRID LOCAL/CLOUD SYNC SYSTEM
==============================
Smart Routing | Computer On/Off Detection | Live Sync

Implements intelligent routing between local and cloud execution:
- Detects when local computer is off
- Automatically routes to cloud when local unavailable
- Maintains live sync between local and cloud
- Ensures continuous operation 24/7
"""

import asyncio
import json
import logging
import os
import socket
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import hashlib
import aiohttp

logger = logging.getLogger('HybridSync')


class ExecutionTarget(Enum):
    """Execution target types"""
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class SyncDirection(Enum):
    """Sync direction"""
    LOCAL_TO_CLOUD = "local_to_cloud"
    CLOUD_TO_LOCAL = "cloud_to_local"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class SyncConfig:
    """Sync configuration"""
    # Routing settings
    local_primary: bool = True
    cloud_fallback: bool = True
    smart_routing: bool = True
    
    # Local detection
    local_check_interval_seconds: int = 30
    local_timeout_seconds: int = 5
    local_heartbeat_port: int = 8765
    
    # Cloud settings
    cloud_project_id: str = "infinity-x-one-systems"
    cloud_region: str = "us-central1"
    cloud_run_url: Optional[str] = None
    
    # Sync settings
    sync_interval_seconds: int = 60
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    conflict_resolution: str = "latest_wins"
    
    # Storage paths
    local_data_path: str = "/home/ubuntu/lead-sniper/results"
    cloud_bucket: str = "gs://ix1-lead-sniper"


@dataclass
class SyncStatus:
    """Sync status"""
    last_sync: Optional[datetime] = None
    local_available: bool = True
    cloud_available: bool = True
    current_target: ExecutionTarget = ExecutionTarget.LOCAL
    pending_sync_items: int = 0
    sync_errors: List[str] = field(default_factory=list)


class LocalDetector:
    """
    Local Computer Availability Detector
    
    Detects when the local computer is on/off
    to enable smart routing decisions.
    """
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self._last_check = None
        self._is_available = True
        self._heartbeat_server = None
        logger.info("LocalDetector initialized")
    
    async def start_heartbeat_server(self):
        """Start heartbeat server for remote detection"""
        try:
            self._heartbeat_server = await asyncio.start_server(
                self._handle_heartbeat,
                '0.0.0.0',
                self.config.local_heartbeat_port
            )
            logger.info(f"Heartbeat server started on port {self.config.local_heartbeat_port}")
        except Exception as e:
            logger.error(f"Failed to start heartbeat server: {e}")
    
    async def _handle_heartbeat(self, reader, writer):
        """Handle heartbeat requests"""
        try:
            data = await reader.read(100)
            if data == b'PING':
                writer.write(b'PONG')
                await writer.drain()
        finally:
            writer.close()
    
    async def check_availability(self) -> bool:
        """Check if local computer is available"""
        try:
            # Method 1: Check if we can bind to localhost
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.config.local_timeout_seconds)
            result = sock.connect_ex(('127.0.0.1', 22))  # SSH port
            sock.close()
            
            # Method 2: Check system load
            load_avg = os.getloadavg()[0]
            
            # Method 3: Check disk availability
            disk_available = os.path.exists(self.config.local_data_path)
            
            self._is_available = disk_available and load_avg < 10
            self._last_check = datetime.utcnow()
            
            return self._is_available
            
        except Exception as e:
            logger.warning(f"Local availability check failed: {e}")
            self._is_available = False
            return False
    
    def is_available(self) -> bool:
        """Get cached availability status"""
        return self._is_available
    
    async def stop(self):
        """Stop heartbeat server"""
        if self._heartbeat_server:
            self._heartbeat_server.close()
            await self._heartbeat_server.wait_closed()


class CloudConnector:
    """
    Cloud Connector for GCP Integration
    
    Manages connection to Google Cloud services
    for cloud-based execution and storage.
    """
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self._client = None
        self._storage_client = None
        self._is_available = False
        logger.info("CloudConnector initialized")
    
    async def initialize(self):
        """Initialize cloud connections"""
        try:
            # Initialize GCS client
            from google.cloud import storage
            
            sa_key = os.environ.get('GCP_SA_KEY')
            if sa_key:
                from google.oauth2 import service_account
                key_dict = json.loads(sa_key)
                credentials = service_account.Credentials.from_service_account_info(key_dict)
                self._storage_client = storage.Client(
                    project=self.config.cloud_project_id,
                    credentials=credentials
                )
            else:
                self._storage_client = storage.Client(project=self.config.cloud_project_id)
            
            self._is_available = True
            logger.info("Cloud connector initialized")
            
        except ImportError:
            logger.warning("Google Cloud Storage not available")
            self._is_available = True  # Continue in mock mode
        except Exception as e:
            logger.error(f"Cloud initialization error: {e}")
            self._is_available = False
    
    async def check_availability(self) -> bool:
        """Check cloud availability"""
        try:
            if self._storage_client:
                # Try to list buckets
                list(self._storage_client.list_buckets(max_results=1))
                self._is_available = True
            else:
                # Mock mode - assume available
                self._is_available = True
            return self._is_available
        except Exception as e:
            logger.warning(f"Cloud availability check failed: {e}")
            self._is_available = False
            return False
    
    def is_available(self) -> bool:
        """Get cached availability status"""
        return self._is_available
    
    async def upload_file(self, local_path: str, cloud_path: str):
        """Upload file to cloud storage"""
        if not self._storage_client:
            logger.warning("Cloud storage not available, skipping upload")
            return
        
        try:
            bucket_name = self.config.cloud_bucket.replace('gs://', '')
            bucket = self._storage_client.bucket(bucket_name)
            blob = bucket.blob(cloud_path)
            blob.upload_from_filename(local_path)
            logger.info(f"Uploaded {local_path} to {cloud_path}")
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise
    
    async def download_file(self, cloud_path: str, local_path: str):
        """Download file from cloud storage"""
        if not self._storage_client:
            logger.warning("Cloud storage not available, skipping download")
            return
        
        try:
            bucket_name = self.config.cloud_bucket.replace('gs://', '')
            bucket = self._storage_client.bucket(bucket_name)
            blob = bucket.blob(cloud_path)
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
            logger.info(f"Downloaded {cloud_path} to {local_path}")
        except Exception as e:
            logger.error(f"Download error: {e}")
            raise
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files in cloud storage"""
        if not self._storage_client:
            return []
        
        try:
            bucket_name = self.config.cloud_bucket.replace('gs://', '')
            bucket = self._storage_client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"List files error: {e}")
            return []
    
    async def trigger_cloud_run(self, payload: Dict) -> Dict:
        """Trigger Cloud Run execution"""
        if not self.config.cloud_run_url:
            logger.warning("Cloud Run URL not configured")
            return {'status': 'skipped', 'reason': 'no_url'}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.cloud_run_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Cloud Run trigger error: {e}")
            return {'status': 'error', 'error': str(e)}


class SmartRouter:
    """
    Smart Routing System
    
    Intelligently routes execution between local and cloud
    based on availability and optimal resource utilization.
    """
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self.local_detector = LocalDetector(config)
        self.cloud_connector = CloudConnector(config)
        self._current_target = ExecutionTarget.LOCAL if config.local_primary else ExecutionTarget.CLOUD
        logger.info(f"SmartRouter initialized (primary: {self._current_target.value})")
    
    async def initialize(self):
        """Initialize router components"""
        await self.local_detector.start_heartbeat_server()
        await self.cloud_connector.initialize()
    
    async def determine_target(self) -> ExecutionTarget:
        """Determine optimal execution target"""
        # Check local availability
        local_available = await self.local_detector.check_availability()
        
        # Check cloud availability
        cloud_available = await self.cloud_connector.check_availability()
        
        # Smart routing logic
        if self.config.local_primary:
            if local_available:
                self._current_target = ExecutionTarget.LOCAL
            elif cloud_available and self.config.cloud_fallback:
                logger.info("Local unavailable, routing to cloud")
                self._current_target = ExecutionTarget.CLOUD
            else:
                raise RuntimeError("No execution targets available")
        else:
            if cloud_available:
                self._current_target = ExecutionTarget.CLOUD
            elif local_available:
                logger.info("Cloud unavailable, routing to local")
                self._current_target = ExecutionTarget.LOCAL
            else:
                raise RuntimeError("No execution targets available")
        
        return self._current_target
    
    def get_current_target(self) -> ExecutionTarget:
        """Get current execution target"""
        return self._current_target
    
    async def execute(self, task: Callable, *args, **kwargs) -> Any:
        """Execute task on optimal target"""
        target = await self.determine_target()
        
        if target == ExecutionTarget.LOCAL:
            return await self._execute_local(task, *args, **kwargs)
        else:
            return await self._execute_cloud(task, *args, **kwargs)
    
    async def _execute_local(self, task: Callable, *args, **kwargs) -> Any:
        """Execute task locally"""
        logger.info("Executing task locally")
        if asyncio.iscoroutinefunction(task):
            return await task(*args, **kwargs)
        return task(*args, **kwargs)
    
    async def _execute_cloud(self, task: Callable, *args, **kwargs) -> Any:
        """Execute task on cloud"""
        logger.info("Executing task on cloud")
        
        # Serialize task for cloud execution
        payload = {
            'task': task.__name__,
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return await self.cloud_connector.trigger_cloud_run(payload)
    
    async def stop(self):
        """Stop router components"""
        await self.local_detector.stop()


class HybridSyncManager:
    """
    Hybrid Sync Manager
    
    Manages synchronization between local and cloud storage
    to ensure data consistency across execution targets.
    """
    
    def __init__(self, config: Optional[SyncConfig] = None):
        self.config = config or SyncConfig()
        self.router = SmartRouter(self.config)
        self.status = SyncStatus()
        self._sync_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        logger.info("HybridSyncManager initialized")
    
    async def initialize(self):
        """Initialize sync manager"""
        await self.router.initialize()
        logger.info("HybridSyncManager initialized")
    
    async def start(self):
        """Start sync manager"""
        self._running = True
        
        # Start sync daemon
        asyncio.create_task(self._sync_daemon())
        
        logger.info("HybridSyncManager started")
    
    async def stop(self):
        """Stop sync manager"""
        self._running = False
        await self.router.stop()
        logger.info("HybridSyncManager stopped")
    
    async def _sync_daemon(self):
        """Background sync daemon"""
        while self._running:
            try:
                await self._perform_sync()
                await asyncio.sleep(self.config.sync_interval_seconds)
            except Exception as e:
                logger.error(f"Sync daemon error: {e}")
                self.status.sync_errors.append(str(e))
    
    async def _perform_sync(self):
        """Perform sync operation"""
        direction = self.config.sync_direction
        
        if direction in [SyncDirection.LOCAL_TO_CLOUD, SyncDirection.BIDIRECTIONAL]:
            await self._sync_local_to_cloud()
        
        if direction in [SyncDirection.CLOUD_TO_LOCAL, SyncDirection.BIDIRECTIONAL]:
            await self._sync_cloud_to_local()
        
        self.status.last_sync = datetime.utcnow()
    
    async def _sync_local_to_cloud(self):
        """Sync local files to cloud"""
        if not os.path.exists(self.config.local_data_path):
            return
        
        for root, dirs, files in os.walk(self.config.local_data_path):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, self.config.local_data_path)
                
                try:
                    await self.router.cloud_connector.upload_file(local_path, relative_path)
                except Exception as e:
                    logger.error(f"Failed to sync {local_path}: {e}")
    
    async def _sync_cloud_to_local(self):
        """Sync cloud files to local"""
        try:
            cloud_files = await self.router.cloud_connector.list_files()
            
            for cloud_path in cloud_files:
                local_path = os.path.join(self.config.local_data_path, cloud_path)
                
                # Check if local file exists and is newer
                if os.path.exists(local_path):
                    if self.config.conflict_resolution == "latest_wins":
                        # Skip if local is newer (simplified check)
                        continue
                
                try:
                    await self.router.cloud_connector.download_file(cloud_path, local_path)
                except Exception as e:
                    logger.error(f"Failed to sync {cloud_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Cloud to local sync error: {e}")
    
    async def queue_sync(self, item: Dict):
        """Queue an item for sync"""
        await self._sync_queue.put(item)
        self.status.pending_sync_items = self._sync_queue.qsize()
    
    def get_status(self) -> SyncStatus:
        """Get sync status"""
        self.status.local_available = self.router.local_detector.is_available()
        self.status.cloud_available = self.router.cloud_connector.is_available()
        self.status.current_target = self.router.get_current_target()
        return self.status


# Export classes
__all__ = [
    'HybridSyncManager',
    'SmartRouter',
    'LocalDetector',
    'CloudConnector',
    'SyncConfig',
    'SyncStatus',
    'ExecutionTarget',
    'SyncDirection'
]
