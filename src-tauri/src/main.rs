// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, Window, WindowEvent};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::collections::HashMap;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::sync::Mutex;
use tokio::net::TcpStream;
use tokio::time::timeout;
use tonic::transport::Channel;
use tonic_reflection::pb::v1::server_reflection_client::ServerReflectionClient;
use tonic_reflection::pb::v1::{ServerReflectionRequest, ServerReflectionResponse};
use tonic_reflection::pb::v1::server_reflection_request::MessageRequest;
use tonic_reflection::pb::v1::server_reflection_response::MessageResponse;
use tracing::{info, warn, error, debug};
use anyhow::Result;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum GrpcToolError {
    #[error("Connection failed: {0}")]
    ConnectionError(String),
    #[error("Discovery failed: {0}")]
    DiscoveryError(String),
    #[error("Reflection failed: {0}")]
    ReflectionError(String),
}

#[derive(Debug, Serialize, Deserialize)]
struct GrpcResponse {
    success: bool,
    message: String,
    data: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct GrpcService {
    name: String,
    methods: Vec<GrpcMethod>,
    metadata: ServiceMetadata,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct GrpcMethod {
    name: String,
    input_type: String,
    output_type: String,
    client_streaming: bool,
    server_streaming: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ServiceMetadata {
    host: String,
    port: u16,
    discovered_at: u64,
    last_health_check: u64,
    health_status: HealthStatus,
    response_time_ms: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
enum HealthStatus {
    Healthy,
    Unhealthy,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct LocalhostService {
    host: String,
    port: u16,
    is_grpc: bool,
    services: Vec<GrpcService>,
    metadata: ServiceMetadata,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct GrpcConnection {
    host: String,
    port: u16,
    use_tls: bool,
    connected: bool,
}

impl Default for GrpcConnection {
    fn default() -> Self {
        Self {
            host: "localhost".to_string(),
            port: 9090,
            use_tls: false,
            connected: false,
        }
    }
}

// Enhanced application state for localhost service discovery
struct GrpcToolState {
    connection: Arc<Mutex<GrpcConnection>>,
    services: Arc<Mutex<Vec<GrpcService>>>,
    client: Arc<Mutex<Option<ServerReflectionClient<Channel>>>>,
    localhost_services: Arc<Mutex<HashMap<String, LocalhostService>>>,
    connection_pool: Arc<Mutex<HashMap<String, Channel>>>,
}

// Common gRPC ports to scan on localhost
const COMMON_GRPC_PORTS: &[u16] = &[
    9090, 8080, 50051, 50052, 50053, 8081, 8082, 8083, 8084, 8085,
    9091, 9092, 9093, 9094, 9095, 3000, 3001, 3002, 4000, 4001,
    5000, 5001, 5002, 6000, 6001, 7000, 7001, 8000, 8001, 8002,
];

#[tauri::command]
async fn scan_localhost_services(
    state: tauri::State<'_, GrpcToolState>,
) -> Result<GrpcResponse, String> {
    info!("🔍 Starting localhost gRPC service discovery...");
    
    let mut discovered_services = HashMap::new();
    let mut scan_results = Vec::new();
    
    for &port in COMMON_GRPC_PORTS {
        let host = "localhost".to_string();
        let endpoint = format!("{}:{}", host, port);
        
        debug!("Scanning port {}", port);
        
        match scan_port(&host, port).await {
            Ok(is_grpc) => {
                if is_grpc {
                    info!("✅ Found gRPC service at {}", endpoint);
                    
                    let metadata = ServiceMetadata {
                        host: host.clone(),
                        port,
                        discovered_at: current_timestamp(),
                        last_health_check: current_timestamp(),
                        health_status: HealthStatus::Healthy,
                        response_time_ms: None,
                    };
                    
                    let localhost_service = LocalhostService {
                        host: host.clone(),
                        port,
                        is_grpc: true,
                        services: Vec::new(), // Will be populated by reflection
                        metadata,
                    };
                    
                    discovered_services.insert(endpoint.clone(), localhost_service);
                    scan_results.push(serde_json::json!({
                        "endpoint": endpoint,
                        "status": "grpc_detected",
                        "port": port
                    }));
                } else {
                    debug!("Port {} is open but not gRPC", port);
                }
            }
            Err(e) => {
                debug!("Port {} scan failed: {}", port, e);
            }
        }
    }
    
    // Update state
    *state.localhost_services.lock().await = discovered_services.clone();
    
    info!("🎯 Discovery complete: found {} gRPC services", discovered_services.len());
    
    Ok(GrpcResponse {
        success: true,
        message: format!("Discovered {} gRPC services on localhost", discovered_services.len()),
        data: Some(serde_json::json!({
            "services": discovered_services,
            "scan_results": scan_results,
            "ports_scanned": COMMON_GRPC_PORTS.len(),
            "grpc_services_found": discovered_services.len()
        })),
    })
}

async fn scan_port(host: &str, port: u16) -> Result<bool> {
    // First, check if port is open
    let addr = format!("{}:{}", host, port);
    
    match timeout(Duration::from_millis(100), TcpStream::connect(&addr)).await {
        Ok(Ok(_stream)) => {
            debug!("Port {} is open, checking if it's gRPC", port);
            
            // Try to establish a gRPC connection
            match is_grpc_service(host, port).await {
                Ok(is_grpc) => Ok(is_grpc),
                Err(_) => Ok(false), // Port is open but not gRPC
            }
        }
        Ok(Err(_)) | Err(_) => Ok(false), // Port is closed or timeout
    }
}

async fn is_grpc_service(host: &str, port: u16) -> Result<bool> {
    let endpoint = format!("http://{}:{}", host, port);
    
    match Channel::from_shared(endpoint) {
        Ok(channel) => {
            match timeout(Duration::from_millis(500), channel.connect()).await {
                Ok(Ok(conn)) => {
                    // Try to create a reflection client
                    let mut client = ServerReflectionClient::new(conn);
                    
                    // Try a simple reflection request
                    let (tx, rx) = tokio::sync::mpsc::channel(1);
                    let request = ServerReflectionRequest {
                        host: "".to_string(),
                        message_request: Some(MessageRequest::ListServices("".to_string())),
                    };
                    
                    if tx.send(request).await.is_err() {
                        return Ok(false);
                    }
                    drop(tx);
                    
                    let request_stream = tokio_stream::wrappers::ReceiverStream::new(rx);
                    
                    match timeout(Duration::from_millis(1000), client.server_reflection_info(request_stream)).await {
                        Ok(Ok(_)) => Ok(true), // Successfully got reflection response
                        Ok(Err(_)) | Err(_) => Ok(false), // Not a gRPC service or no reflection
                    }
                }
                Ok(Err(_)) | Err(_) => Ok(false), // Connection failed
            }
        }
        Err(_) => Ok(false), // Invalid endpoint
    }
}

fn current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

#[tauri::command]
async fn get_localhost_services(
    state: tauri::State<'_, GrpcToolState>,
) -> Result<Vec<LocalhostService>, String> {
    let services = state.localhost_services.lock().await;
    Ok(services.values().cloned().collect())
}

#[tauri::command]
async fn connect_grpc(
    host: String,
    port: u16,
    use_tls: bool,
    state: tauri::State<'_, GrpcToolState>,
) -> Result<GrpcResponse, String> {
    let endpoint = if use_tls {
        format!("https://{}:{}", host, port)
    } else {
        format!("http://{}:{}", host, port)
    };

    info!("🔗 Connecting to gRPC server at {}", endpoint);

    match Channel::from_shared(endpoint.clone()) {
        Ok(channel) => {
            match channel.connect().await {
                Ok(conn) => {
                    let client = ServerReflectionClient::new(conn.clone());
                    *state.client.lock().await = Some(client);
                    
                    // Store connection in pool
                    let pool_key = format!("{}:{}", host, port);
                    state.connection_pool.lock().await.insert(pool_key, conn);
                    
                    let mut connection = state.connection.lock().await;
                    connection.host = host;
                    connection.port = port;
                    connection.use_tls = use_tls;
                    connection.connected = true;

                    info!("✅ Connected to gRPC server at {}", endpoint);

                    Ok(GrpcResponse {
                        success: true,
                        message: format!("Connected to gRPC server at {}", endpoint),
                        data: Some(serde_json::json!({
                            "endpoint": endpoint,
                            "tls": use_tls
                        })),
                    })
                }
                Err(e) => {
                    error!("❌ Failed to connect to {}: {}", endpoint, e);
                    Ok(GrpcResponse {
                        success: false,
                        message: format!("Failed to connect to gRPC server: {}", e),
                        data: None,
                    })
                }
            }
        }
        Err(e) => Ok(GrpcResponse {
            success: false,
            message: format!("Invalid endpoint: {}", e),
            data: None,
        }),
    }
}

#[tauri::command]
async fn discover_services(state: tauri::State<'_, GrpcToolState>) -> Result<GrpcResponse, String> {
    let client_guard = state.client.lock().await;
    if let Some(client) = client_guard.as_ref() {
        let mut client = client.clone();
        drop(client_guard);

        info!("🔍 Discovering services via reflection...");

        // Create a stream of requests
        let (tx, rx) = tokio::sync::mpsc::channel(1);

        // Send the list services request
        let request = ServerReflectionRequest {
            host: "".to_string(),
            message_request: Some(MessageRequest::ListServices("".to_string())),
        };

        if tx.send(request).await.is_err() {
            return Ok(GrpcResponse {
                success: false,
                message: "Failed to send reflection request".to_string(),
                data: None,
            });
        }

        // Close the sender to indicate end of stream
        drop(tx);

        let request_stream = tokio_stream::wrappers::ReceiverStream::new(rx);

        match client.server_reflection_info(request_stream).await {
            Ok(response) => {
                let mut services = Vec::new();
                let mut stream = response.into_inner();

                while let Ok(Some(msg)) = stream.message().await {
                    if let Some(MessageResponse::ListServicesResponse(list_response)) = msg.message_response {
                        for service in list_response.service {
                            let connection = state.connection.lock().await;
                            let metadata = ServiceMetadata {
                                host: connection.host.clone(),
                                port: connection.port,
                                discovered_at: current_timestamp(),
                                last_health_check: current_timestamp(),
                                health_status: HealthStatus::Healthy,
                                response_time_ms: None,
                            };

                            services.push(GrpcService {
                                name: service.name,
                                methods: Vec::new(), // TODO: Implement method discovery
                                metadata,
                            });
                        }
                        break;
                    }
                }

                *state.services.lock().await = services.clone();

                info!("✅ Discovered {} services", services.len());

                Ok(GrpcResponse {
                    success: true,
                    message: format!("Discovered {} services", services.len()),
                    data: Some(serde_json::to_value(services).unwrap()),
                })
            }
            Err(e) => {
                error!("❌ Service discovery failed: {}", e);
                Ok(GrpcResponse {
                    success: false,
                    message: format!("Failed to discover services: {}", e),
                    data: None,
                })
            }
        }
    } else {
        Ok(GrpcResponse {
            success: false,
            message: "Not connected to gRPC server".to_string(),
            data: None,
        })
    }
}

#[tauri::command]
async fn get_connection_status(state: tauri::State<'_, GrpcToolState>) -> Result<GrpcConnection, String> {
    let connection = state.connection.lock().await;
    Ok(connection.clone())
}

#[tauri::command]
async fn get_services(state: tauri::State<'_, GrpcToolState>) -> Result<Vec<GrpcService>, String> {
    let services = state.services.lock().await;
    Ok(services.clone())
}

#[tauri::command]
async fn disconnect_grpc(state: tauri::State<'_, GrpcToolState>) -> Result<GrpcResponse, String> {
    info!("🔌 Disconnecting from gRPC server...");

    *state.client.lock().await = None;
    let mut connection = state.connection.lock().await;
    connection.connected = false;
    *state.services.lock().await = Vec::new();

    // Clear connection pool
    state.connection_pool.lock().await.clear();

    info!("✅ Disconnected from gRPC server");

    Ok(GrpcResponse {
        success: true,
        message: "Disconnected from gRPC server".to_string(),
        data: None,
    })
}

#[tauri::command]
async fn health_check_service(
    host: String,
    port: u16,
    state: tauri::State<'_, GrpcToolState>,
) -> Result<GrpcResponse, String> {
    let start_time = std::time::Instant::now();

    match scan_port(&host, port).await {
        Ok(is_healthy) => {
            let response_time = start_time.elapsed().as_millis() as u64;

            // Update localhost services health status
            let endpoint = format!("{}:{}", host, port);
            let mut services = state.localhost_services.lock().await;

            if let Some(service) = services.get_mut(&endpoint) {
                service.metadata.last_health_check = current_timestamp();
                service.metadata.health_status = if is_healthy {
                    HealthStatus::Healthy
                } else {
                    HealthStatus::Unhealthy
                };
                service.metadata.response_time_ms = Some(response_time);
            }

            Ok(GrpcResponse {
                success: is_healthy,
                message: if is_healthy {
                    format!("Service at {}:{} is healthy ({}ms)", host, port, response_time)
                } else {
                    format!("Service at {}:{} is unhealthy", host, port)
                },
                data: Some(serde_json::json!({
                    "host": host,
                    "port": port,
                    "healthy": is_healthy,
                    "response_time_ms": response_time
                })),
            })
        }
        Err(e) => Ok(GrpcResponse {
            success: false,
            message: format!("Health check failed: {}", e),
            data: None,
        }),
    }
}

// Window management commands
#[tauri::command]
async fn minimize_window(window: Window) -> Result<(), String> {
    window.minimize().map_err(|e| e.to_string())
}

#[tauri::command]
async fn maximize_window(window: Window) -> Result<(), String> {
    window.maximize().map_err(|e| e.to_string())
}

#[tauri::command]
async fn close_window(window: Window) -> Result<(), String> {
    window.close().map_err(|e| e.to_string())
}

#[tauri::command]
async fn set_window_title(window: Window, title: String) -> Result<(), String> {
    window.set_title(&title).map_err(|e| e.to_string())
}

fn main() {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Initialize gRPC tool state
    let grpc_state = GrpcToolState {
        connection: Arc::new(Mutex::new(GrpcConnection::default())),
        services: Arc::new(Mutex::new(Vec::new())),
        client: Arc::new(Mutex::new(None)),
        localhost_services: Arc::new(Mutex::new(HashMap::new())),
        connection_pool: Arc::new(Mutex::new(HashMap::new())),
    };

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(grpc_state)
        .invoke_handler(tauri::generate_handler![
            scan_localhost_services,
            get_localhost_services,
            connect_grpc,
            disconnect_grpc,
            discover_services,
            get_connection_status,
            get_services,
            health_check_service,
            minimize_window,
            maximize_window,
            close_window,
            set_window_title
        ])
        .setup(|app| {
            info!("🚀 gRPC Tool with Localhost Discovery is starting...");

            // Get the main window
            let window = app.get_webview_window("main").unwrap();

            // Set up window event handlers
            window.on_window_event(move |event| {
                match event {
                    WindowEvent::CloseRequested { .. } => {
                        info!("🛑 Window close requested");
                    }
                    WindowEvent::Resized(size) => {
                        debug!("📏 Window resized to: {}x{}", size.width, size.height);
                    }
                    WindowEvent::Focused(focused) => {
                        debug!("🎯 Window focus changed: {}", focused);
                    }
                    _ => {}
                }
            });

            info!("✅ gRPC Tool setup complete!");
            info!("🔍 Ready for localhost service discovery");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running gRPC tool");
}
