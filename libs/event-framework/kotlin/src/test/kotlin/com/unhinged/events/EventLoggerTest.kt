package com.unhinged.events

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Assertions.*
import java.io.ByteArrayOutputStream
import java.io.PrintStream

class EventLoggerTest {
    
    private lateinit var originalOut: PrintStream
    private lateinit var outputStream: ByteArrayOutputStream
    
    @BeforeEach
    fun setUp() {
        originalOut = System.out
        outputStream = ByteArrayOutputStream()
        System.setOut(PrintStream(outputStream))
    }
    
    @Test
    fun `should create logger with factory`() {
        val logger = EventLoggerFactory.createLogger("test-service")
        assertNotNull(logger)
    }
    
    @Test
    fun `should log info message with YAML format`() {
        val config = EventLoggerConfig(
            serviceId = "test-service",
            minLogLevel = LogLevel.INFO,
            outputFormat = OutputFormat.YAML
        )
        
        val logger = EventLoggerFactory.createLogger(config)
        logger.info("Test message", mapOf("key" to "value"))
        
        val output = outputStream.toString()
        assertTrue(output.contains("level: INFO"))
        assertTrue(output.contains("message: Test message"))
        assertTrue(output.contains("service_id: test-service"))
        assertTrue(output.contains("key: value"))
    }
    
    @Test
    fun `should respect log level filtering`() {
        val config = EventLoggerConfig(
            serviceId = "test-service",
            minLogLevel = LogLevel.WARN
        )
        
        val logger = EventLoggerFactory.createLogger(config)
        
        assertFalse(logger.isEnabled(LogLevel.DEBUG))
        assertFalse(logger.isEnabled(LogLevel.INFO))
        assertTrue(logger.isEnabled(LogLevel.WARN))
        assertTrue(logger.isEnabled(LogLevel.ERROR))
    }
    
    @Test
    fun `should add context to child logger`() {
        val logger = EventLoggerFactory.createLogger("test-service")
        val childLogger = logger.withContext(mapOf("request_id" to "123"))
        
        childLogger.info("Test message")
        
        val output = outputStream.toString()
        assertTrue(output.contains("request_id: '123'"))
    }
    
    @Test
    fun `should add trace context`() {
        val logger = EventLoggerFactory.createLogger("test-service")
        val tracedLogger = logger.withTrace("trace123", "span456")
        
        tracedLogger.info("Test message")
        
        val output = outputStream.toString()
        assertTrue(output.contains("trace_id: trace123"))
        assertTrue(output.contains("span_id: span456"))
    }
    
    @Test
    fun `should log error with exception`() {
        val logger = EventLoggerFactory.createLogger("test-service")
        val exception = RuntimeException("Test exception")
        
        logger.error("Error occurred", exception)
        
        val output = outputStream.toString()
        assertTrue(output.contains("level: ERROR"))
        assertTrue(output.contains("message: Error occurred"))
        assertTrue(output.contains("exception:"))
        assertTrue(output.contains("type: RuntimeException"))
        assertTrue(output.contains("message: Test exception"))
    }
    
    @Test
    fun `should create service event logger`() {
        val serviceLogger = createServiceEventLogger("test-service", "1.0.0")
        assertNotNull(serviceLogger)
        
        serviceLogger.logServiceStartup(8080)
        
        val output = outputStream.toString()
        assertTrue(output.contains("Service starting"))
        assertTrue(output.contains("port: 8080"))
        assertTrue(output.contains("event_type: service.startup"))
    }
    
    @Test
    fun `log levels should have correct numeric values`() {
        assertEquals(0, LogLevel.DEBUG.value)
        assertEquals(1, LogLevel.INFO.value)
        assertEquals(2, LogLevel.WARN.value)
        assertEquals(3, LogLevel.ERROR.value)
    }
    
    @Test
    fun `should parse log levels from values and names`() {
        assertEquals(LogLevel.DEBUG, LogLevel.fromValue(0))
        assertEquals(LogLevel.INFO, LogLevel.fromValue(1))
        assertEquals(LogLevel.WARN, LogLevel.fromValue(2))
        assertEquals(LogLevel.ERROR, LogLevel.fromValue(3))
        
        assertEquals(LogLevel.DEBUG, LogLevel.fromName("DEBUG"))
        assertEquals(LogLevel.INFO, LogLevel.fromName("info"))
        assertEquals(LogLevel.WARN, LogLevel.fromName("Warn"))
        assertEquals(LogLevel.ERROR, LogLevel.fromName("ERROR"))
    }
    
    fun tearDown() {
        System.setOut(originalOut)
    }
}
