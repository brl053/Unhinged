#!/usr/bin/env python3

"""
Standalone CDC Service

A lightweight Python service that handles:
1. Event production to Kafka
2. Event consumption from Kafka to PostgreSQL  
3. Session-based event API
4. WebSocket real-time streaming

This runs alongside the existing Kotlin backend until we can integrate properly.
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import asyncpg
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092')
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql://postgres:postgres@localhost:5432/unhinged_db')
TOPIC_NAME = 'llm-events'

app = FastAPI(title="CDC Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
websocket_connections: Dict[str, WebSocket] = {}

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# Kafka producer
kafka_producer: Optional[KafkaProducer] = None

class LLMInferenceEvent(BaseModel):
    prompt: str
    response: str
    model: str
    prompt_tokens: int
    response_tokens: int
    latency_ms: int
    success: bool
    error_message: str = ""
    intent: str
    confidence: float
    user_id: str
    session_id: str

class UniversalEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp_ms: int
    user_id: str
    session_id: str
    payload: dict

@app.on_event("startup")
async def startup():
    global db_pool, kafka_producer
    
    # Initialize database pool
    try:
        db_pool = await asyncpg.create_pool(POSTGRES_URL, min_size=2, max_size=10)
        logger.info("✅ Connected to PostgreSQL")
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        raise
    
    # Initialize Kafka producer
    try:
        kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKERS.split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3
        )
        logger.info("✅ Connected to Kafka")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Kafka: {e}")
        raise
    
    # Start Kafka consumer in background
    asyncio.create_task(kafka_consumer_task())
    logger.info("🚀 CDC Service started")

@app.on_event("shutdown")
async def shutdown():
    global db_pool, kafka_producer
    
    if db_pool:
        await db_pool.close()
    
    if kafka_producer:
        kafka_producer.close()
    
    logger.info("✅ CDC Service shutdown")

@app.get("/ping")
async def ping():
    return {"message": "pong", "timestamp": int(datetime.now().timestamp() * 1000)}

@app.get("/health")
async def health():
    # Check database
    db_status = "healthy"
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
    except Exception as e:
        db_status = f"unhealthy: {e}"
    
    # Check Kafka (simple check)
    kafka_status = "healthy" if kafka_producer else "unhealthy: not connected"
    
    return {
        "status": "healthy",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "services": {
            "database": db_status,
            "kafka": kafka_status
        }
    }

@app.post("/api/events/llm-inference")
async def produce_llm_inference_event(event: LLMInferenceEvent):
    """Produce LLM inference event to Kafka"""
    try:
        universal_event = UniversalEvent(
            event_id=str(uuid.uuid4()),
            event_type="llm.inference.completed",
            timestamp_ms=int(datetime.now().timestamp() * 1000),
            user_id=event.user_id,
            session_id=event.session_id,
            payload=event.dict()
        )
        
        # Send to Kafka
        kafka_producer.send(
            TOPIC_NAME,
            key=universal_event.session_id,
            value=universal_event.dict()
        )
        kafka_producer.flush()
        
        logger.info(f"📤 Event produced: {universal_event.event_id}")
        return {"event_id": universal_event.event_id, "status": "produced"}
        
    except Exception as e:
        logger.error(f"❌ Failed to produce event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/events")
async def get_session_events(session_id: str, limit: int = 100):
    """Get all events for a session"""
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT event_id, event_type, timestamp_ms, user_id, session_id, payload, created_at
                FROM events 
                WHERE session_id = $1 
                ORDER BY timestamp_ms DESC 
                LIMIT $2
            """, session_id, limit)
            
            events = []
            for row in rows:
                events.append({
                    "event_id": row["event_id"],
                    "event_type": row["event_type"],
                    "timestamp_ms": row["timestamp_ms"],
                    "user_id": row["user_id"],
                    "session_id": row["session_id"],
                    "payload": row["payload"],
                    "created_at": row["created_at"].isoformat()
                })
            
            return {"session_id": session_id, "events": events, "count": len(events)}
            
    except Exception as e:
        logger.error(f"❌ Failed to get session events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events")
async def get_recent_events(limit: int = 50):
    """Get recent events across all sessions"""
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT event_id, event_type, timestamp_ms, user_id, session_id, payload, created_at
                FROM events 
                ORDER BY timestamp_ms DESC 
                LIMIT $1
            """, limit)
            
            events = []
            for row in rows:
                events.append({
                    "event_id": row["event_id"],
                    "event_type": row["event_type"],
                    "timestamp_ms": row["timestamp_ms"],
                    "user_id": row["user_id"],
                    "session_id": row["session_id"],
                    "payload": row["payload"],
                    "created_at": row["created_at"].isoformat()
                })
            
            return events
            
    except Exception as e:
        logger.error(f"❌ Failed to get recent events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/api/events/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    websocket_connections[connection_id] = websocket
    
    logger.info(f"🔌 WebSocket connected: {connection_id}")
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected: {connection_id}")
    finally:
        websocket_connections.pop(connection_id, None)

async def kafka_consumer_task():
    """Background task to consume Kafka events and store in PostgreSQL"""
    logger.info("📥 Starting Kafka consumer...")
    
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKERS.split(','),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
        group_id='cdc-consumer',
        auto_offset_reset='latest'
    )
    
    for message in consumer:
        try:
            event_data = message.value
            
            # Store in PostgreSQL
            async with db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO events (event_id, event_type, timestamp_ms, user_id, session_id, payload)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                    event_data['event_id'],
                    event_data['event_type'],
                    event_data['timestamp_ms'],
                    event_data['user_id'],
                    event_data['session_id'],
                    json.dumps(event_data['payload'])
                )
            
            # Broadcast to WebSocket clients
            event_json = json.dumps(event_data)
            disconnected = []
            
            for conn_id, ws in websocket_connections.items():
                try:
                    await ws.send_text(event_json)
                except Exception:
                    disconnected.append(conn_id)
            
            # Clean up disconnected clients
            for conn_id in disconnected:
                websocket_connections.pop(conn_id, None)
            
            logger.info(f"✅ Processed event: {event_data['event_id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process Kafka message: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
