"""
Async metrics collector with batch writing for efficiency
"""
import asyncio
import json
from pathlib import Path
from collections import deque
from datetime import datetime


class MetricsCollector:
    """Collects and persists game metrics with batched async writes"""
    
    def __init__(self, storage_path="data/metrics", batch_size=10):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.batch_size = batch_size
        self.pending_writes = deque()
        self.write_task = None
        
    async def save_game_metrics_async(self, metrics_dict):
        """Non-blocking save - queues for batch write"""
        self.pending_writes.append(metrics_dict)
        
        # Start batch writer if not running
        if self.write_task is None or self.write_task.done():
            self.write_task = asyncio.create_task(self._batch_writer())
    
    async def _batch_writer(self):
        """Write metrics in batches to reduce I/O"""
        while self.pending_writes:
            # Wait to accumulate more writes
            await asyncio.sleep(1)
            
            if not self.pending_writes:
                break
            
            # Group by date
            by_date = {}
            batch_count = min(self.batch_size, len(self.pending_writes))
            
            for _ in range(batch_count):
                if not self.pending_writes:
                    break
                metrics = self.pending_writes.popleft()
                date_str = datetime.fromtimestamp(metrics['started_at']).strftime('%Y-%m-%d')
                
                if date_str not in by_date:
                    by_date[date_str] = []
                by_date[date_str].append(metrics)
            
            # Write each date's batch
            for date_str, metrics_list in by_date.items():
                await self._append_to_file(date_str, metrics_list)
    
    async def _append_to_file(self, date_str, metrics_list):
        """Append metrics to daily file"""
        file_path = self.storage_path / f"games_{date_str}.json"
        
        # Read existing (only once per batch)
        existing = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing = json.load(f)
        
        # Append new metrics
        existing.extend(metrics_list)
        
        # Write back (single write operation)
        with open(file_path, 'w') as f:
            json.dump(existing, f)
    
    def get_pending_count(self):
        """Get number of pending writes (for monitoring)"""
        return len(self.pending_writes)
