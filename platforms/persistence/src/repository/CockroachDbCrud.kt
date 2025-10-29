//
// @llm-type service.api
// @llm-does cockroachdb crud operations for persistence platform
//
package platforms.persistence.repository

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.slf4j.LoggerFactory
import java.sql.Connection
import java.sql.DriverManager
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.util.*

/**
 * CockroachDB Single Entity CRUD Operations
 * ========================================
 * 
 * Direct implementation for CRDB using JDBC.
 * Each operation isolated, no abstractions yet.
 * Focus on CRDB-specific configurations and idiosyncrasies.
 */
class CockroachDbCrud(private val config: CrdbConfig) {
    
    companion object {
        private val logger = LoggerFactory.getLogger(CockroachDbCrud::class.java)
        private const val DRIVER_CLASS = "org.postgresql.Driver"
    }
    
    init {
        Class.forName(DRIVER_CLASS)
        initializeDatabase()
    }
    
    /**
     * CREATE - Insert single entity
     */
    suspend fun create(entity: CrdbEntity): CrdbResult<String> = withContext(Dispatchers.IO) {
        var connection: Connection? = null
        var statement: PreparedStatement? = null
        
        try {
            connection = getConnection()
            
            val sql = """
                INSERT INTO entities (
                    id, record_type, data, metadata, 
                    created_at, updated_at, version
                ) VALUES (?, ?, ?::JSONB, ?::JSONB, ?, ?, ?)
                RETURNING id
            """.trimIndent()
            
            statement = connection.prepareStatement(sql)
            statement.setString(1, entity.id)
            statement.setString(2, entity.recordType)
            statement.setString(3, entity.data)
            statement.setString(4, entity.metadata)
            statement.setTimestamp(5, Timestamp.from(entity.createdAt))
            statement.setTimestamp(6, Timestamp.from(entity.updatedAt))
            statement.setString(7, entity.version)
            
            val resultSet = statement.executeQuery()
            
            if (resultSet.next()) {
                val insertedId = resultSet.getString("id")
                logger.info("Created entity with ID: $insertedId")
                CrdbResult.Success(insertedId)
            } else {
                CrdbResult.Error("Failed to create entity - no ID returned")
            }
            
        } catch (e: SQLException) {
            logger.error("Failed to create entity: ${entity.id}", e)
            CrdbResult.Error("Create failed: ${e.message}", e)
        } finally {
            statement?.close()
            connection?.close()
        }
    }
    
    /**
     * READ - Get single entity by ID
     */
    suspend fun read(id: String): CrdbResult<CrdbEntity?> = withContext(Dispatchers.IO) {
        var connection: Connection? = null
        var statement: PreparedStatement? = null
        
        try {
            connection = getConnection()
            
            val sql = """
                SELECT id, record_type, data, metadata, 
                       created_at, updated_at, version
                FROM entities 
                WHERE id = ?
            """.trimIndent()
            
            statement = connection.prepareStatement(sql)
            statement.setString(1, id)
            
            val resultSet = statement.executeQuery()
            
            if (resultSet.next()) {
                val entity = mapResultSetToEntity(resultSet)
                logger.debug("Found entity: $id")
                CrdbResult.Success(entity)
            } else {
                logger.debug("Entity not found: $id")
                CrdbResult.Success(null)
            }
            
        } catch (e: SQLException) {
            logger.error("Failed to read entity: $id", e)
            CrdbResult.Error("Read failed: ${e.message}", e)
        } finally {
            statement?.close()
            connection?.close()
        }
    }
    
    /**
     * UPDATE - Update single entity
     */
    suspend fun update(id: String, updates: CrdbEntityUpdate): CrdbResult<CrdbEntity> = withContext(Dispatchers.IO) {
        var connection: Connection? = null
        var statement: PreparedStatement? = null
        
        try {
            connection = getConnection()
            
            // CRDB-specific: Use UPSERT for better performance
            val sql = """
                UPDATE entities 
                SET data = COALESCE(?::JSONB, data),
                    metadata = COALESCE(?::JSONB, metadata),
                    updated_at = ?,
                    version = ?
                WHERE id = ?
                RETURNING id, record_type, data, metadata, 
                         created_at, updated_at, version
            """.trimIndent()
            
            statement = connection.prepareStatement(sql)
            statement.setString(1, updates.data)
            statement.setString(2, updates.metadata)
            statement.setTimestamp(3, Timestamp.from(Instant.now()))
            statement.setString(4, generateNewVersion())
            statement.setString(5, id)
            
            val resultSet = statement.executeQuery()
            
            if (resultSet.next()) {
                val updatedEntity = mapResultSetToEntity(resultSet)
                logger.info("Updated entity: $id")
                CrdbResult.Success(updatedEntity)
            } else {
                CrdbResult.Error("Entity not found for update: $id")
            }
            
        } catch (e: SQLException) {
            logger.error("Failed to update entity: $id", e)
            CrdbResult.Error("Update failed: ${e.message}", e)
        } finally {
            statement?.close()
            connection?.close()
        }
    }
    
    /**
     * DELETE - Delete single entity
     */
    suspend fun delete(id: String): CrdbResult<Boolean> = withContext(Dispatchers.IO) {
        var connection: Connection? = null
        var statement: PreparedStatement? = null
        
        try {
            connection = getConnection()
            
            val sql = "DELETE FROM entities WHERE id = ?"
            
            statement = connection.prepareStatement(sql)
            statement.setString(1, id)
            
            val rowsAffected = statement.executeUpdate()
            
            if (rowsAffected > 0) {
                logger.info("Deleted entity: $id")
                CrdbResult.Success(true)
            } else {
                logger.debug("Entity not found for deletion: $id")
                CrdbResult.Success(false)
            }
            
        } catch (e: SQLException) {
            logger.error("Failed to delete entity: $id", e)
            CrdbResult.Error("Delete failed: ${e.message}", e)
        } finally {
            statement?.close()
            connection?.close()
        }
    }
    
    /**
     * LIST - Get entities with pagination
     */
    suspend fun list(limit: Int = 100, offset: Int = 0): CrdbResult<List<CrdbEntity>> = withContext(Dispatchers.IO) {
        var connection: Connection? = null
        var statement: PreparedStatement? = null
        
        try {
            connection = getConnection()
            
            val sql = """
                SELECT id, record_type, data, metadata, 
                       created_at, updated_at, version
                FROM entities 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """.trimIndent()
            
            statement = connection.prepareStatement(sql)
            statement.setInt(1, limit)
            statement.setInt(2, offset)
            
            val resultSet = statement.executeQuery()
            val entities = mutableListOf<CrdbEntity>()
            
            while (resultSet.next()) {
                entities.add(mapResultSetToEntity(resultSet))
            }
            
            logger.debug("Listed ${entities.size} entities")
            CrdbResult.Success(entities)
            
        } catch (e: SQLException) {
            logger.error("Failed to list entities", e)
            CrdbResult.Error("List failed: ${e.message}", e)
        } finally {
            statement?.close()
            connection?.close()
        }
    }
    
    /**
     * COUNT - Get total entity count
     */
    suspend fun count(): CrdbResult<Long> = withContext(Dispatchers.IO) {
        var connection: Connection? = null
        var statement: PreparedStatement? = null
        
        try {
            connection = getConnection()
            
            val sql = "SELECT COUNT(*) as total FROM entities"
            statement = connection.prepareStatement(sql)
            
            val resultSet = statement.executeQuery()
            
            if (resultSet.next()) {
                val total = resultSet.getLong("total")
                CrdbResult.Success(total)
            } else {
                CrdbResult.Success(0L)
            }
            
        } catch (e: SQLException) {
            logger.error("Failed to count entities", e)
            CrdbResult.Error("Count failed: ${e.message}", e)
        } finally {
            statement?.close()
            connection?.close()
        }
    }
    
    // Private helper methods
    private fun getConnection(): Connection {
        return DriverManager.getConnection(
            config.jdbcUrl,
            config.username,
            config.password
        ).apply {
            autoCommit = true // CRDB handles transactions automatically
        }
    }
    
    private fun initializeDatabase() {
        try {
            val connection = getConnection()
            
            val createTableSql = """
                CREATE TABLE IF NOT EXISTS entities (
                    id STRING PRIMARY KEY,
                    record_type STRING NOT NULL,
                    data JSONB NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    version STRING NOT NULL,
                    INDEX idx_record_type (record_type),
                    INDEX idx_created_at (created_at),
                    INVERTED INDEX idx_data (data),
                    INVERTED INDEX idx_metadata (metadata)
                )
            """.trimIndent()
            
            connection.createStatement().execute(createTableSql)
            connection.close()
            
            logger.info("CockroachDB entities table initialized")
            
        } catch (e: SQLException) {
            logger.error("Failed to initialize database", e)
            throw RuntimeException("Database initialization failed", e)
        }
    }
    
    private fun mapResultSetToEntity(resultSet: ResultSet): CrdbEntity {
        return CrdbEntity(
            id = resultSet.getString("id"),
            recordType = resultSet.getString("record_type"),
            data = resultSet.getString("data"),
            metadata = resultSet.getString("metadata"),
            createdAt = resultSet.getTimestamp("created_at").toInstant(),
            updatedAt = resultSet.getTimestamp("updated_at").toInstant(),
            version = resultSet.getString("version")
        )
    }
    
    private fun generateNewVersion(): String {
        return UUID.randomUUID().toString()
    }
}

/**
 * CockroachDB Entity Model
 */
data class CrdbEntity(
    val id: String,
    val recordType: String,
    val data: String, // JSON string
    val metadata: String?, // JSON string
    val createdAt: Instant,
    val updatedAt: Instant,
    val version: String
)

/**
 * Update model for partial updates
 */
data class CrdbEntityUpdate(
    val data: String? = null,
    val metadata: String? = null
)

/**
 * Result wrapper for CRDB operations
 */
sealed class CrdbResult<T> {
    data class Success<T>(val data: T) : CrdbResult<T>()
    data class Error<T>(val message: String, val cause: Throwable? = null) : CrdbResult<T>()
}

/**
 * CockroachDB Configuration
 */
data class CrdbConfig(
    val jdbcUrl: String = "jdbc:postgresql://localhost:26257/defaultdb?sslmode=disable",
    val username: String = "root",
    val password: String = "",
    val maxPoolSize: Int = 10,
    val connectionTimeout: Long = 5000
)
