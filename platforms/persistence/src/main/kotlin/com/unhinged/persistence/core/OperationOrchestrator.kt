// ============================================================================
// Persistence Platform - Operation Orchestrator Interface
// ============================================================================
//
// @file OperationOrchestrator.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Interface for orchestrating complex operations across multiple
//              database technologies including distributed transactions,
//              async pipelines, and ML workflows
//
// The OperationOrchestrator handles complex operations that span multiple
// database technologies, manages distributed transactions, coordinates
// async pipelines, and orchestrates ML workflows with proper error handling
// and rollback strategies.
//
// ============================================================================

package com.unhinged.persistence.core

import com.unhinged.persistence.model.*
import kotlinx.coroutines.flow.Flow

/*
 * @llm-type misc.interface
 * @llm-does operation orchestrator that manages complex multi-technol...
 * @llm-rule all complex operations must be orchestrated through this interface for consis...
 */
interface OperationOrchestrator {
    
    // ==========================================================================
    // Named Operation Execution
    // ==========================================================================
    
    /**
     * Execute a named operation defined in configuration
     * 
     * @param operationName Name of the operation from configuration
     * @param parameters Operation parameters
     * @param context Execution context
     * @return Operation result with status and data
     */
    suspend fun <T> executeNamedOperation(
        operationName: String,
        parameters: Map<String, Any>,
        context: ExecutionContext
    ): OperationResult<T>
    
    /**
     * Execute a custom operation specification
     * 
     * @param operationSpec Operation specification
     * @param context Execution context
     * @return Operation result
     */
    suspend fun <T> executeOperation(
        operationSpec: OperationSpec,
        context: ExecutionContext
    ): OperationResult<T>
    
    // ==========================================================================
    // Distributed Transactions
    // ==========================================================================
    
    /**
     * Execute a distributed transaction across multiple technologies
     * 
     * @param transactionSpec Transaction specification with steps
     * @param context Execution context
     * @return Transaction result with commit/rollback status
     */
    suspend fun <T> executeDistributedTransaction(
        transactionSpec: DistributedTransactionSpec,
        context: ExecutionContext
    ): TransactionResult<T>
    
    /**
     * Begin a distributed transaction
     * 
     * @param transactionSpec Transaction specification
     * @param context Execution context
     * @return Transaction handle for managing the transaction
     */
    suspend fun beginDistributedTransaction(
        transactionSpec: DistributedTransactionSpec,
        context: ExecutionContext
    ): DistributedTransactionHandle
    
    /**
     * Commit a distributed transaction
     * 
     * @param transactionHandle Transaction handle
     * @return Commit result
     */
    suspend fun commitDistributedTransaction(
        transactionHandle: DistributedTransactionHandle
    ): CommitResult
    
    /**
     * Rollback a distributed transaction
     * 
     * @param transactionHandle Transaction handle
     * @param reason Rollback reason
     * @return Rollback result
     */
    suspend fun rollbackDistributedTransaction(
        transactionHandle: DistributedTransactionHandle,
        reason: String
    ): RollbackResult
    
    // ==========================================================================
    // Async Pipeline Operations
    // ==========================================================================
    
    /**
     * Execute an async pipeline with multiple stages
     * 
     * @param pipelineSpec Pipeline specification
     * @param context Execution context
     * @return Pipeline execution handle for monitoring
     */
    suspend fun executeAsyncPipeline(
        pipelineSpec: AsyncPipelineSpec,
        context: ExecutionContext
    ): AsyncPipelineHandle
    
    /**
     * Monitor async pipeline execution
     * 
     * @param pipelineHandle Pipeline handle
     * @return Pipeline status and progress
     */
    suspend fun monitorPipeline(
        pipelineHandle: AsyncPipelineHandle
    ): PipelineStatus
    
    /**
     * Cancel an async pipeline
     * 
     * @param pipelineHandle Pipeline handle
     * @param reason Cancellation reason
     * @return Cancellation result
     */
    suspend fun cancelPipeline(
        pipelineHandle: AsyncPipelineHandle,
        reason: String
    ): CancellationResult
    
    /**
     * Get pipeline execution results
     * 
     * @param pipelineHandle Pipeline handle
     * @return Pipeline results as a flow
     */
    suspend fun <T> getPipelineResults(
        pipelineHandle: AsyncPipelineHandle
    ): Flow<T>
    
    // ==========================================================================
    // ML Workflow Operations
    // ==========================================================================
    
    /**
     * Execute an ML workflow with data processing and model operations
     * 
     * @param workflowSpec ML workflow specification
     * @param context Execution context
     * @return ML workflow result
     */
    suspend fun <T> executeMLWorkflow(
        workflowSpec: MLWorkflowSpec,
        context: ExecutionContext
    ): MLWorkflowResult<T>
    
    /**
     * Execute batch ML operations
     * 
     * @param batchSpec Batch ML specification
     * @param context Execution context
     * @return Batch execution handle
     */
    suspend fun executeBatchMLOperation(
        batchSpec: BatchMLSpec,
        context: ExecutionContext
    ): BatchMLHandle
    
    /**
     * Monitor batch ML operation progress
     * 
     * @param batchHandle Batch handle
     * @return Batch processing status
     */
    suspend fun monitorBatchML(
        batchHandle: BatchMLHandle
    ): BatchMLStatus
    
    // ==========================================================================
    // Saga Pattern Operations
    // ==========================================================================
    
    /**
     * Execute a saga with compensating transactions
     * 
     * @param sagaSpec Saga specification
     * @param context Execution context
     * @return Saga execution result
     */
    suspend fun <T> executeSaga(
        sagaSpec: SagaSpec,
        context: ExecutionContext
    ): SagaResult<T>
    
    /**
     * Execute compensating actions for failed saga
     * 
     * @param sagaHandle Saga handle
     * @param failurePoint Point where saga failed
     * @return Compensation result
     */
    suspend fun executeCompensation(
        sagaHandle: SagaHandle,
        failurePoint: SagaStep
    ): CompensationResult
    
    // ==========================================================================
    // Bulk Operations
    // ==========================================================================
    
    /**
     * Execute bulk data operations across multiple technologies
     * 
     * @param bulkSpec Bulk operation specification
     * @param context Execution context
     * @return Bulk operation result
     */
    suspend fun <T> executeBulkOperation(
        bulkSpec: BulkOperationSpec,
        context: ExecutionContext
    ): BulkOperationResult<T>
    
    /**
     * Execute data migration between technologies
     * 
     * @param migrationSpec Migration specification
     * @param context Execution context
     * @return Migration result
     */
    suspend fun executeMigration(
        migrationSpec: DataMigrationSpec,
        context: ExecutionContext
    ): MigrationResult
    
    /**
     * Execute data synchronization between technologies
     * 
     * @param syncSpec Synchronization specification
     * @param context Execution context
     * @return Synchronization result
     */
    suspend fun executeDataSync(
        syncSpec: DataSyncSpec,
        context: ExecutionContext
    ): SyncResult
    
    // ==========================================================================
    // Event-Driven Operations
    // ==========================================================================
    
    /**
     * Execute operation triggered by event
     * 
     * @param event Triggering event
     * @param operationSpec Operation to execute
     * @param context Execution context
     * @return Event-driven operation result
     */
    suspend fun <T> executeEventDrivenOperation(
        event: PlatformEvent,
        operationSpec: OperationSpec,
        context: ExecutionContext
    ): OperationResult<T>
    
    /**
     * Register event handler for automatic operation execution
     * 
     * @param eventPattern Event pattern to match
     * @param operationName Operation to execute
     * @param config Handler configuration
     */
    suspend fun registerEventHandler(
        eventPattern: EventPattern,
        operationName: String,
        config: EventHandlerConfig
    )
    
    /**
     * Unregister event handler
     * 
     * @param handlerId Handler ID to remove
     */
    suspend fun unregisterEventHandler(handlerId: String)
    
    // ==========================================================================
    // Operation Monitoring and Management
    // ==========================================================================
    
    /**
     * Get active operations status
     * 
     * @return List of currently active operations
     */
    suspend fun getActiveOperations(): List<ActiveOperation>
    
    /**
     * Get operation execution history
     * 
     * @param timeRange Time range for history
     * @param filters Optional filters
     * @return Operation execution history
     */
    suspend fun getOperationHistory(
        timeRange: TimeRange,
        filters: OperationFilters? = null
    ): List<OperationExecutionRecord>
    
    /**
     * Get operation performance metrics
     * 
     * @return Current operation performance metrics
     */
    suspend fun getOperationMetrics(): OperationMetrics
    
    /**
     * Cancel a running operation
     * 
     * @param operationId Operation ID to cancel
     * @param reason Cancellation reason
     * @return Cancellation result
     */
    suspend fun cancelOperation(
        operationId: String,
        reason: String
    ): CancellationResult
    
    /**
     * Retry a failed operation
     * 
     * @param operationId Failed operation ID
     * @param retryConfig Retry configuration
     * @return Retry result
     */
    suspend fun <T> retryOperation(
        operationId: String,
        retryConfig: RetryConfig
    ): OperationResult<T>
    
    // ==========================================================================
    // Configuration and Validation
    // ==========================================================================
    
    /**
     * Validate an operation specification
     * 
     * @param operationSpec Operation to validate
     * @return Validation result
     */
    suspend fun validateOperation(
        operationSpec: OperationSpec
    ): OperationValidationResult
    
    /**
     * Get supported operation types
     * 
     * @return Set of supported operation types
     */
    fun getSupportedOperationTypes(): Set<OperationType>
    
    /**
     * Update orchestrator configuration
     * 
     * @param config New configuration
     */
    suspend fun updateConfiguration(config: OrchestratorConfig)
    
    /**
     * Get current configuration
     * 
     * @return Current orchestrator configuration
     */
    fun getConfiguration(): OrchestratorConfig
}

/**
 * Operation types supported by the orchestrator
 */
enum class OperationType {
    SIMPLE_CRUD,
    DISTRIBUTED_TRANSACTION,
    ASYNC_PIPELINE,
    ML_WORKFLOW,
    SAGA,
    BULK_OPERATION,
    DATA_MIGRATION,
    DATA_SYNC,
    EVENT_DRIVEN
}

/**
 * Operation execution status
 */
enum class OperationStatus {
    PENDING,
    RUNNING,
    COMPLETED,
    FAILED,
    CANCELLED,
    COMPENSATING,
    COMPENSATED
}

/**
 * Transaction isolation levels
 */
enum class IsolationLevel {
    READ_UNCOMMITTED,
    READ_COMMITTED,
    REPEATABLE_READ,
    SERIALIZABLE
}
