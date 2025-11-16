#!/usr/bin/env python3
"""
Session Store Tests - Comprehensive Concurrent Access Testing

Tests for write-through session storage with focus on concurrent access
and failure modes as specified by consultant.

@llm-type test.session
@llm-does comprehensive session store testing with concurrent access validation
"""

import unittest
import threading
import time
import json
import random
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from session_store import SessionStore, SessionStoreConfig, SessionStoreError

class TestSessionStore(unittest.TestCase):
    """Comprehensive session store tests"""
    
    def setUp(self):
        """Set up test session store"""
        self.config = SessionStoreConfig(
            redis_db=1  # Use test database
        )
        self.store = SessionStore(self.config)
        
        # Clean up any existing test data
        self._cleanup_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        self._cleanup_test_data()
        self.store.close()
    
    def _cleanup_test_data(self):
        """Remove all test session data"""
        test_keys = self.store.list_keys("test:*")
        for key in test_keys:
            self.store.delete(key)
    
    def test_basic_operations(self):
        """Test basic CRUD operations"""
        key = "test:basic"
        value = {"user_id": "test123", "data": "basic_test"}
        
        # Test write
        self.assertTrue(self.store.write(key, value))
        
        # Test read
        result = self.store.read(key)
        self.assertEqual(result, value)
        
        # Test exists
        self.assertTrue(self.store.exists(key))
        
        # Test delete
        self.assertTrue(self.store.delete(key))
        self.assertFalse(self.store.exists(key))
        self.assertIsNone(self.store.read(key))
    
    def test_write_through_consistency(self):
        """Test that writes appear in both Redis and CRDB"""
        key = "test:consistency"
        value = {"test": "write_through", "timestamp": time.time()}
        
        # Write data
        self.assertTrue(self.store.write(key, value))
        
        # Verify in Redis
        redis_value = self.store.redis_client.get(key)
        self.assertIsNotNone(redis_value)
        self.assertEqual(json.loads(redis_value), value)
        
        # Clear Redis cache
        self.store.redis_client.delete(key)
        
        # Should still be readable from CRDB
        result = self.store.read(key)
        self.assertEqual(result, value)
        
        # Should repopulate Redis cache
        redis_value = self.store.redis_client.get(key)
        self.assertIsNotNone(redis_value)
    
    def test_concurrent_writes_same_key(self):
        """Test concurrent writes to the same session key - Critical Test #1"""
        key = "test:concurrent_same"
        num_threads = 10
        writes_per_thread = 5
        
        def write_worker(thread_id: int):
            """Worker function for concurrent writes"""
            results = []
            for i in range(writes_per_thread):
                value = {
                    "thread_id": thread_id,
                    "write_number": i,
                    "timestamp": time.time(),
                    "data": f"thread_{thread_id}_write_{i}"
                }
                success = self.store.write(key, value)
                results.append((success, value))
                time.sleep(0.001)  # Small delay to increase contention
            return results
        
        # Execute concurrent writes
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(write_worker, i) for i in range(num_threads)]
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # Verify all writes succeeded
        successful_writes = [r for r in all_results if r[0]]
        self.assertEqual(len(successful_writes), num_threads * writes_per_thread)
        
        # Verify final state is consistent
        final_value = self.store.read(key)
        self.assertIsNotNone(final_value)
        
        # Verify Redis and CRDB have same value
        redis_value = json.loads(self.store.redis_client.get(key))
        self.assertEqual(redis_value, final_value)
    
    def test_redis_restart_simulation(self):
        """Test CRDB repopulation after Redis restart - Critical Test #2"""
        key = "test:redis_restart"
        value = {"test": "redis_restart", "important_data": "must_survive"}
        
        # Write data
        self.assertTrue(self.store.write(key, value))
        
        # Verify it's in both stores
        self.assertEqual(self.store.read(key), value)
        
        # Simulate Redis restart by flushing Redis
        self.store.redis_client.flushdb()
        
        # Data should still be readable (from CRDB)
        result = self.store.read(key)
        self.assertEqual(result, value)
        
        # Redis should be repopulated
        redis_value = self.store.redis_client.get(key)
        self.assertIsNotNone(redis_value)
        self.assertEqual(json.loads(redis_value), value)
    
    def test_crdb_slowness_simulation(self):
        """Test Redis masking CRDB latency - Critical Test #3"""
        key = "test:crdb_slow"
        value = {"test": "crdb_slowness", "data": "latency_test"}
        
        # Write data normally
        self.assertTrue(self.store.write(key, value))
        
        # Multiple rapid reads should be fast (Redis cache)
        start_time = time.time()
        for _ in range(100):
            result = self.store.read(key)
            self.assertEqual(result, value)
        read_time = time.time() - start_time
        
        # Should be very fast (under 10ms for 100 reads)
        self.assertLess(read_time, 0.01)
    
    def test_concurrent_read_write_mixed(self):
        """Test mixed concurrent read/write operations"""
        base_key = "test:mixed"
        num_threads = 8
        operations_per_thread = 10
        
        def mixed_worker(thread_id: int):
            """Worker with mixed read/write operations"""
            results = {"reads": 0, "writes": 0, "errors": 0}
            
            for i in range(operations_per_thread):
                key = f"{base_key}:{thread_id}:{i}"
                
                try:
                    if random.choice([True, False]):
                        # Write operation
                        value = {"thread": thread_id, "op": i, "type": "write"}
                        if self.store.write(key, value):
                            results["writes"] += 1
                    else:
                        # Read operation (might not exist)
                        result = self.store.read(key)
                        results["reads"] += 1
                        
                except Exception:
                    results["errors"] += 1
                    
                time.sleep(0.001)
            
            return results
        
        # Execute mixed operations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(mixed_worker, i) for i in range(num_threads)]
            all_results = [future.result() for future in as_completed(futures)]
        
        # Verify no errors occurred
        total_errors = sum(r["errors"] for r in all_results)
        self.assertEqual(total_errors, 0)
        
        # Verify operations completed
        total_ops = sum(r["reads"] + r["writes"] for r in all_results)
        self.assertEqual(total_ops, num_threads * operations_per_thread)
    
    def test_large_value_handling(self):
        """Test handling of large JSON values (under 10MB limit)"""
        key = "test:large_value"
        
        # Create ~1MB value
        large_data = {
            "type": "large_test",
            "data": "x" * (1024 * 1024),  # 1MB string
            "metadata": {"size": "1MB", "test": True}
        }
        
        # Should write successfully
        self.assertTrue(self.store.write(key, large_data))
        
        # Should read back correctly
        result = self.store.read(key)
        self.assertEqual(result, large_data)
        
        # Should exist in both stores
        self.assertTrue(self.store.exists(key))
    
    def test_session_key_patterns(self):
        """Test session key patterns and listing"""
        # Create various session keys
        session_keys = [
            "session:user123:metadata",
            "session:user123:state", 
            "session:user123:artifacts",
            "session:user456:metadata",
            "session:user456:context"
        ]
        
        for key in session_keys:
            value = {"key": key, "test": True}
            self.assertTrue(self.store.write(key, value))
        
        # Test pattern matching
        all_sessions = self.store.list_keys("session:*")
        self.assertGreaterEqual(len(all_sessions), len(session_keys))
        
        user123_sessions = self.store.list_keys("session:user123:*")
        self.assertEqual(len(user123_sessions), 3)
    
    def test_health_check(self):
        """Test health check functionality"""
        health = self.store.health_check()
        
        # Should have both Redis and CRDB status
        self.assertIn("redis", health)
        self.assertIn("crdb", health)
        
        # Both should be healthy
        self.assertEqual(health["redis"]["status"], "healthy")
        self.assertEqual(health["crdb"]["status"], "healthy")
        
        # Should have latency measurements
        self.assertIsNotNone(health["redis"]["latency_ms"])
        self.assertIsNotNone(health["crdb"]["latency_ms"])
        
        # Latency should be reasonable (under 10ms for local)
        self.assertLess(health["redis"]["latency_ms"], 10)
        self.assertLess(health["crdb"]["latency_ms"], 10)
    
    def test_stress_rapid_operations(self):
        """Stress test with rapid session creation/deletion cycles"""
        num_sessions = 100
        
        # Rapid creation
        start_time = time.time()
        for i in range(num_sessions):
            key = f"test:stress:{i}"
            value = {"session_id": i, "created": time.time()}
            self.assertTrue(self.store.write(key, value))
        creation_time = time.time() - start_time
        
        # Rapid reading
        start_time = time.time()
        for i in range(num_sessions):
            key = f"test:stress:{i}"
            result = self.store.read(key)
            self.assertIsNotNone(result)
            self.assertEqual(result["session_id"], i)
        read_time = time.time() - start_time
        
        # Rapid deletion
        start_time = time.time()
        for i in range(num_sessions):
            key = f"test:stress:{i}"
            self.assertTrue(self.store.delete(key))
        deletion_time = time.time() - start_time
        
        # Performance should be reasonable
        print(f"Stress test results:")
        print(f"  Creation: {creation_time:.3f}s ({num_sessions/creation_time:.1f} ops/sec)")
        print(f"  Reading: {read_time:.3f}s ({num_sessions/read_time:.1f} ops/sec)")
        print(f"  Deletion: {deletion_time:.3f}s ({num_sessions/deletion_time:.1f} ops/sec)")
        
        # Should handle at least 100 ops/sec
        self.assertGreater(num_sessions/creation_time, 100)
        self.assertGreater(num_sessions/read_time, 100)
        self.assertGreater(num_sessions/deletion_time, 100)

def run_stability_test(duration_hours: float = 24.0):
    """Run 24-hour stability test as specified by consultant"""
    print(f"Starting {duration_hours}-hour stability test...")
    
    config = SessionStoreConfig(redis_db=2, crdb_database="unhinged_stability")
    store = SessionStore(config)
    
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    
    operations = {"writes": 0, "reads": 0, "deletes": 0, "errors": 0}
    
    try:
        while time.time() < end_time:
            try:
                # Random operations
                session_id = str(uuid.uuid4())
                key = f"stability:session:{session_id}"
                
                # Write
                value = {
                    "session_id": session_id,
                    "timestamp": time.time(),
                    "data": f"stability_test_{operations['writes']}"
                }
                if store.write(key, value):
                    operations["writes"] += 1
                
                # Read
                result = store.read(key)
                if result:
                    operations["reads"] += 1
                
                # Delete (50% chance)
                if random.choice([True, False]):
                    if store.delete(key):
                        operations["deletes"] += 1
                
                # Health check every 1000 operations
                if (operations["writes"] + operations["reads"]) % 1000 == 0:
                    health = store.health_check()
                    if health["redis"]["status"] != "healthy" or health["crdb"]["status"] != "healthy":
                        print(f"Health check failed: {health}")
                        operations["errors"] += 1
                
                time.sleep(0.1)  # 10 ops/sec
                
            except Exception as e:
                operations["errors"] += 1
                print(f"Operation error: {e}")
        
        print(f"Stability test completed:")
        print(f"  Duration: {duration_hours} hours")
        print(f"  Operations: {operations}")
        print(f"  Error rate: {operations['errors']/(sum(operations.values())):.4f}")
        
    finally:
        store.close()

if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run stability test if requested
    import sys
    if "--stability" in sys.argv:
        run_stability_test(24.0)
