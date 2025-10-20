package platforms.persistence.api

import platforms.persistence.repository.*
import kotlinx.coroutines.runBlocking
import java.time.Instant

/**
 * CockroachDB API Interface
 * ========================
 * 
 * Simple API layer for CRDB CRUD operations.
 * Provides clean interface for external consumers.
 */
class CrdbApi(private val crud: CockroachDbCrud) {
    
    /**
     * Create a new entity
     */
    fun createEntity(
        id: String,
        recordType: String,
        data: String,
        metadata: String? = null
    ): ApiResponse<String> = runBlocking {
        val entity = CrdbEntity(
            id = id,
            recordType = recordType,
            data = data,
            metadata = metadata,
            createdAt = Instant.now(),
            updatedAt = Instant.now(),
            version = "1.0"
        )
        
        when (val result = crud.create(entity)) {
            is CrdbResult.Success -> ApiResponse.Success(result.data)
            is CrdbResult.Error -> ApiResponse.Error(result.message, result.cause)
        }
    }
    
    /**
     * Get entity by ID
     */
    fun getEntity(id: String): ApiResponse<CrdbEntity?> = runBlocking {
        when (val result = crud.read(id)) {
            is CrdbResult.Success -> ApiResponse.Success(result.data)
            is CrdbResult.Error -> ApiResponse.Error(result.message, result.cause)
        }
    }
    
    /**
     * Update entity
     */
    fun updateEntity(
        id: String,
        data: String? = null,
        metadata: String? = null
    ): ApiResponse<CrdbEntity> = runBlocking {
        val updates = CrdbEntityUpdate(data = data, metadata = metadata)
        
        when (val result = crud.update(id, updates)) {
            is CrdbResult.Success -> ApiResponse.Success(result.data)
            is CrdbResult.Error -> ApiResponse.Error(result.message, result.cause)
        }
    }
    
    /**
     * Delete entity
     */
    fun deleteEntity(id: String): ApiResponse<Boolean> = runBlocking {
        when (val result = crud.delete(id)) {
            is CrdbResult.Success -> ApiResponse.Success(result.data)
            is CrdbResult.Error -> ApiResponse.Error(result.message, result.cause)
        }
    }
    
    /**
     * List entities with pagination
     */
    fun listEntities(limit: Int = 100, offset: Int = 0): ApiResponse<List<CrdbEntity>> = runBlocking {
        when (val result = crud.list(limit, offset)) {
            is CrdbResult.Success -> ApiResponse.Success(result.data)
            is CrdbResult.Error -> ApiResponse.Error(result.message, result.cause)
        }
    }
    
    /**
     * Count total entities
     */
    fun countEntities(): ApiResponse<Long> = runBlocking {
        when (val result = crud.count()) {
            is CrdbResult.Success -> ApiResponse.Success(result.data)
            is CrdbResult.Error -> ApiResponse.Error(result.message, result.cause)
        }
    }
}

/**
 * API Response wrapper
 */
sealed class ApiResponse<T> {
    data class Success<T>(val data: T) : ApiResponse<T>()
    data class Error<T>(val message: String, val cause: Throwable? = null) : ApiResponse<T>()
}

/**
 * API Factory for creating CRDB API instances
 */
object CrdbApiFactory {
    
    fun create(config: CrdbConfig = CrdbConfig()): CrdbApi {
        val crud = CockroachDbCrud(config)
        return CrdbApi(crud)
    }
    
    fun createWithCustomUrl(jdbcUrl: String): CrdbApi {
        val config = CrdbConfig(jdbcUrl = jdbcUrl)
        val crud = CockroachDbCrud(config)
        return CrdbApi(crud)
    }
}
