package unhinged.llm;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 **
 * LLM service for completion and model management
 * 
 * Integrates with chat service for conversation context
 * and uses common patterns for consistency
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: llm.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class LLMServiceGrpc {

  private LLMServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "unhinged.llm.v1.LLMService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<unhinged.llm.CompletionRequest,
      unhinged.llm.CompletionResponse> getGenerateCompletionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GenerateCompletion",
      requestType = unhinged.llm.CompletionRequest.class,
      responseType = unhinged.llm.CompletionResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.llm.CompletionRequest,
      unhinged.llm.CompletionResponse> getGenerateCompletionMethod() {
    io.grpc.MethodDescriptor<unhinged.llm.CompletionRequest, unhinged.llm.CompletionResponse> getGenerateCompletionMethod;
    if ((getGenerateCompletionMethod = LLMServiceGrpc.getGenerateCompletionMethod) == null) {
      synchronized (LLMServiceGrpc.class) {
        if ((getGenerateCompletionMethod = LLMServiceGrpc.getGenerateCompletionMethod) == null) {
          LLMServiceGrpc.getGenerateCompletionMethod = getGenerateCompletionMethod =
              io.grpc.MethodDescriptor.<unhinged.llm.CompletionRequest, unhinged.llm.CompletionResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GenerateCompletion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.CompletionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.CompletionResponse.getDefaultInstance()))
              .setSchemaDescriptor(new LLMServiceMethodDescriptorSupplier("GenerateCompletion"))
              .build();
        }
      }
    }
    return getGenerateCompletionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.llm.CompletionRequest,
      unhinged.common.StreamChunk> getStreamCompletionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "StreamCompletion",
      requestType = unhinged.llm.CompletionRequest.class,
      responseType = unhinged.common.StreamChunk.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.llm.CompletionRequest,
      unhinged.common.StreamChunk> getStreamCompletionMethod() {
    io.grpc.MethodDescriptor<unhinged.llm.CompletionRequest, unhinged.common.StreamChunk> getStreamCompletionMethod;
    if ((getStreamCompletionMethod = LLMServiceGrpc.getStreamCompletionMethod) == null) {
      synchronized (LLMServiceGrpc.class) {
        if ((getStreamCompletionMethod = LLMServiceGrpc.getStreamCompletionMethod) == null) {
          LLMServiceGrpc.getStreamCompletionMethod = getStreamCompletionMethod =
              io.grpc.MethodDescriptor.<unhinged.llm.CompletionRequest, unhinged.common.StreamChunk>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "StreamCompletion"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.CompletionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.StreamChunk.getDefaultInstance()))
              .setSchemaDescriptor(new LLMServiceMethodDescriptorSupplier("StreamCompletion"))
              .build();
        }
      }
    }
    return getStreamCompletionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.llm.ListModelsRequest,
      unhinged.llm.ListModelsResponse> getListModelsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListModels",
      requestType = unhinged.llm.ListModelsRequest.class,
      responseType = unhinged.llm.ListModelsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.llm.ListModelsRequest,
      unhinged.llm.ListModelsResponse> getListModelsMethod() {
    io.grpc.MethodDescriptor<unhinged.llm.ListModelsRequest, unhinged.llm.ListModelsResponse> getListModelsMethod;
    if ((getListModelsMethod = LLMServiceGrpc.getListModelsMethod) == null) {
      synchronized (LLMServiceGrpc.class) {
        if ((getListModelsMethod = LLMServiceGrpc.getListModelsMethod) == null) {
          LLMServiceGrpc.getListModelsMethod = getListModelsMethod =
              io.grpc.MethodDescriptor.<unhinged.llm.ListModelsRequest, unhinged.llm.ListModelsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListModels"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.ListModelsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.ListModelsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new LLMServiceMethodDescriptorSupplier("ListModels"))
              .build();
        }
      }
    }
    return getListModelsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.llm.GetModelRequest,
      unhinged.llm.GetModelResponse> getGetModelMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetModel",
      requestType = unhinged.llm.GetModelRequest.class,
      responseType = unhinged.llm.GetModelResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.llm.GetModelRequest,
      unhinged.llm.GetModelResponse> getGetModelMethod() {
    io.grpc.MethodDescriptor<unhinged.llm.GetModelRequest, unhinged.llm.GetModelResponse> getGetModelMethod;
    if ((getGetModelMethod = LLMServiceGrpc.getGetModelMethod) == null) {
      synchronized (LLMServiceGrpc.class) {
        if ((getGetModelMethod = LLMServiceGrpc.getGetModelMethod) == null) {
          LLMServiceGrpc.getGetModelMethod = getGetModelMethod =
              io.grpc.MethodDescriptor.<unhinged.llm.GetModelRequest, unhinged.llm.GetModelResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetModel"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.GetModelRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.GetModelResponse.getDefaultInstance()))
              .setSchemaDescriptor(new LLMServiceMethodDescriptorSupplier("GetModel"))
              .build();
        }
      }
    }
    return getGetModelMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.llm.TokenEstimationRequest,
      unhinged.llm.TokenEstimationResponse> getEstimateTokensMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "EstimateTokens",
      requestType = unhinged.llm.TokenEstimationRequest.class,
      responseType = unhinged.llm.TokenEstimationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.llm.TokenEstimationRequest,
      unhinged.llm.TokenEstimationResponse> getEstimateTokensMethod() {
    io.grpc.MethodDescriptor<unhinged.llm.TokenEstimationRequest, unhinged.llm.TokenEstimationResponse> getEstimateTokensMethod;
    if ((getEstimateTokensMethod = LLMServiceGrpc.getEstimateTokensMethod) == null) {
      synchronized (LLMServiceGrpc.class) {
        if ((getEstimateTokensMethod = LLMServiceGrpc.getEstimateTokensMethod) == null) {
          LLMServiceGrpc.getEstimateTokensMethod = getEstimateTokensMethod =
              io.grpc.MethodDescriptor.<unhinged.llm.TokenEstimationRequest, unhinged.llm.TokenEstimationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "EstimateTokens"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.TokenEstimationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.TokenEstimationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new LLMServiceMethodDescriptorSupplier("EstimateTokens"))
              .build();
        }
      }
    }
    return getEstimateTokensMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.llm.TokenCountRequest,
      unhinged.llm.TokenCountResponse> getCountTokensMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "CountTokens",
      requestType = unhinged.llm.TokenCountRequest.class,
      responseType = unhinged.llm.TokenCountResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.llm.TokenCountRequest,
      unhinged.llm.TokenCountResponse> getCountTokensMethod() {
    io.grpc.MethodDescriptor<unhinged.llm.TokenCountRequest, unhinged.llm.TokenCountResponse> getCountTokensMethod;
    if ((getCountTokensMethod = LLMServiceGrpc.getCountTokensMethod) == null) {
      synchronized (LLMServiceGrpc.class) {
        if ((getCountTokensMethod = LLMServiceGrpc.getCountTokensMethod) == null) {
          LLMServiceGrpc.getCountTokensMethod = getCountTokensMethod =
              io.grpc.MethodDescriptor.<unhinged.llm.TokenCountRequest, unhinged.llm.TokenCountResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "CountTokens"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.TokenCountRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.llm.TokenCountResponse.getDefaultInstance()))
              .setSchemaDescriptor(new LLMServiceMethodDescriptorSupplier("CountTokens"))
              .build();
        }
      }
    }
    return getCountTokensMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.common.HealthCheckRequest,
      unhinged.common.HealthCheckResponse> getHealthCheckMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "HealthCheck",
      requestType = unhinged.common.HealthCheckRequest.class,
      responseType = unhinged.common.HealthCheckResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.common.HealthCheckRequest,
      unhinged.common.HealthCheckResponse> getHealthCheckMethod() {
    io.grpc.MethodDescriptor<unhinged.common.HealthCheckRequest, unhinged.common.HealthCheckResponse> getHealthCheckMethod;
    if ((getHealthCheckMethod = LLMServiceGrpc.getHealthCheckMethod) == null) {
      synchronized (LLMServiceGrpc.class) {
        if ((getHealthCheckMethod = LLMServiceGrpc.getHealthCheckMethod) == null) {
          LLMServiceGrpc.getHealthCheckMethod = getHealthCheckMethod =
              io.grpc.MethodDescriptor.<unhinged.common.HealthCheckRequest, unhinged.common.HealthCheckResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "HealthCheck"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.HealthCheckRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.HealthCheckResponse.getDefaultInstance()))
              .setSchemaDescriptor(new LLMServiceMethodDescriptorSupplier("HealthCheck"))
              .build();
        }
      }
    }
    return getHealthCheckMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static LLMServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<LLMServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<LLMServiceStub>() {
        @java.lang.Override
        public LLMServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new LLMServiceStub(channel, callOptions);
        }
      };
    return LLMServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static LLMServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<LLMServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<LLMServiceBlockingStub>() {
        @java.lang.Override
        public LLMServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new LLMServiceBlockingStub(channel, callOptions);
        }
      };
    return LLMServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static LLMServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<LLMServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<LLMServiceFutureStub>() {
        @java.lang.Override
        public LLMServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new LLMServiceFutureStub(channel, callOptions);
        }
      };
    return LLMServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   **
   * LLM service for completion and model management
   * 
   * Integrates with chat service for conversation context
   * and uses common patterns for consistency
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * Completion operations
     * </pre>
     */
    default void generateCompletion(unhinged.llm.CompletionRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.CompletionResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGenerateCompletionMethod(), responseObserver);
    }

    /**
     * <pre>
     * ← DRY!
     * </pre>
     */
    default void streamCompletion(unhinged.llm.CompletionRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getStreamCompletionMethod(), responseObserver);
    }

    /**
     * <pre>
     * Model management
     * </pre>
     */
    default void listModels(unhinged.llm.ListModelsRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.ListModelsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListModelsMethod(), responseObserver);
    }

    /**
     */
    default void getModel(unhinged.llm.GetModelRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.GetModelResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetModelMethod(), responseObserver);
    }

    /**
     * <pre>
     * Token operations
     * </pre>
     */
    default void estimateTokens(unhinged.llm.TokenEstimationRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.TokenEstimationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getEstimateTokensMethod(), responseObserver);
    }

    /**
     */
    default void countTokens(unhinged.llm.TokenCountRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.TokenCountResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getCountTokensMethod(), responseObserver);
    }

    /**
     * <pre>
     * Standard health check
     * </pre>
     */
    default void healthCheck(unhinged.common.HealthCheckRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.HealthCheckResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getHealthCheckMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service LLMService.
   * <pre>
   **
   * LLM service for completion and model management
   * 
   * Integrates with chat service for conversation context
   * and uses common patterns for consistency
   * </pre>
   */
  public static abstract class LLMServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return LLMServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service LLMService.
   * <pre>
   **
   * LLM service for completion and model management
   * 
   * Integrates with chat service for conversation context
   * and uses common patterns for consistency
   * </pre>
   */
  public static final class LLMServiceStub
      extends io.grpc.stub.AbstractAsyncStub<LLMServiceStub> {
    private LLMServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected LLMServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new LLMServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Completion operations
     * </pre>
     */
    public void generateCompletion(unhinged.llm.CompletionRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.CompletionResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGenerateCompletionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * ← DRY!
     * </pre>
     */
    public void streamCompletion(unhinged.llm.CompletionRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getStreamCompletionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Model management
     * </pre>
     */
    public void listModels(unhinged.llm.ListModelsRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.ListModelsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListModelsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getModel(unhinged.llm.GetModelRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.GetModelResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetModelMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Token operations
     * </pre>
     */
    public void estimateTokens(unhinged.llm.TokenEstimationRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.TokenEstimationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getEstimateTokensMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void countTokens(unhinged.llm.TokenCountRequest request,
        io.grpc.stub.StreamObserver<unhinged.llm.TokenCountResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getCountTokensMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Standard health check
     * </pre>
     */
    public void healthCheck(unhinged.common.HealthCheckRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.HealthCheckResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getHealthCheckMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service LLMService.
   * <pre>
   **
   * LLM service for completion and model management
   * 
   * Integrates with chat service for conversation context
   * and uses common patterns for consistency
   * </pre>
   */
  public static final class LLMServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<LLMServiceBlockingStub> {
    private LLMServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected LLMServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new LLMServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Completion operations
     * </pre>
     */
    public unhinged.llm.CompletionResponse generateCompletion(unhinged.llm.CompletionRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGenerateCompletionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * ← DRY!
     * </pre>
     */
    public java.util.Iterator<unhinged.common.StreamChunk> streamCompletion(
        unhinged.llm.CompletionRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getStreamCompletionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Model management
     * </pre>
     */
    public unhinged.llm.ListModelsResponse listModels(unhinged.llm.ListModelsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListModelsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.llm.GetModelResponse getModel(unhinged.llm.GetModelRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetModelMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Token operations
     * </pre>
     */
    public unhinged.llm.TokenEstimationResponse estimateTokens(unhinged.llm.TokenEstimationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getEstimateTokensMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.llm.TokenCountResponse countTokens(unhinged.llm.TokenCountRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getCountTokensMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Standard health check
     * </pre>
     */
    public unhinged.common.HealthCheckResponse healthCheck(unhinged.common.HealthCheckRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getHealthCheckMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service LLMService.
   * <pre>
   **
   * LLM service for completion and model management
   * 
   * Integrates with chat service for conversation context
   * and uses common patterns for consistency
   * </pre>
   */
  public static final class LLMServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<LLMServiceFutureStub> {
    private LLMServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected LLMServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new LLMServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Completion operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.llm.CompletionResponse> generateCompletion(
        unhinged.llm.CompletionRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGenerateCompletionMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Model management
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.llm.ListModelsResponse> listModels(
        unhinged.llm.ListModelsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListModelsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.llm.GetModelResponse> getModel(
        unhinged.llm.GetModelRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetModelMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Token operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.llm.TokenEstimationResponse> estimateTokens(
        unhinged.llm.TokenEstimationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getEstimateTokensMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.llm.TokenCountResponse> countTokens(
        unhinged.llm.TokenCountRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getCountTokensMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Standard health check
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.common.HealthCheckResponse> healthCheck(
        unhinged.common.HealthCheckRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getHealthCheckMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_GENERATE_COMPLETION = 0;
  private static final int METHODID_STREAM_COMPLETION = 1;
  private static final int METHODID_LIST_MODELS = 2;
  private static final int METHODID_GET_MODEL = 3;
  private static final int METHODID_ESTIMATE_TOKENS = 4;
  private static final int METHODID_COUNT_TOKENS = 5;
  private static final int METHODID_HEALTH_CHECK = 6;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final AsyncService serviceImpl;
    private final int methodId;

    MethodHandlers(AsyncService serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_GENERATE_COMPLETION:
          serviceImpl.generateCompletion((unhinged.llm.CompletionRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.llm.CompletionResponse>) responseObserver);
          break;
        case METHODID_STREAM_COMPLETION:
          serviceImpl.streamCompletion((unhinged.llm.CompletionRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.common.StreamChunk>) responseObserver);
          break;
        case METHODID_LIST_MODELS:
          serviceImpl.listModels((unhinged.llm.ListModelsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.llm.ListModelsResponse>) responseObserver);
          break;
        case METHODID_GET_MODEL:
          serviceImpl.getModel((unhinged.llm.GetModelRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.llm.GetModelResponse>) responseObserver);
          break;
        case METHODID_ESTIMATE_TOKENS:
          serviceImpl.estimateTokens((unhinged.llm.TokenEstimationRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.llm.TokenEstimationResponse>) responseObserver);
          break;
        case METHODID_COUNT_TOKENS:
          serviceImpl.countTokens((unhinged.llm.TokenCountRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.llm.TokenCountResponse>) responseObserver);
          break;
        case METHODID_HEALTH_CHECK:
          serviceImpl.healthCheck((unhinged.common.HealthCheckRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.common.HealthCheckResponse>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        default:
          throw new AssertionError();
      }
    }
  }

  public static final io.grpc.ServerServiceDefinition bindService(AsyncService service) {
    return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
        .addMethod(
          getGenerateCompletionMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.llm.CompletionRequest,
              unhinged.llm.CompletionResponse>(
                service, METHODID_GENERATE_COMPLETION)))
        .addMethod(
          getStreamCompletionMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              unhinged.llm.CompletionRequest,
              unhinged.common.StreamChunk>(
                service, METHODID_STREAM_COMPLETION)))
        .addMethod(
          getListModelsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.llm.ListModelsRequest,
              unhinged.llm.ListModelsResponse>(
                service, METHODID_LIST_MODELS)))
        .addMethod(
          getGetModelMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.llm.GetModelRequest,
              unhinged.llm.GetModelResponse>(
                service, METHODID_GET_MODEL)))
        .addMethod(
          getEstimateTokensMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.llm.TokenEstimationRequest,
              unhinged.llm.TokenEstimationResponse>(
                service, METHODID_ESTIMATE_TOKENS)))
        .addMethod(
          getCountTokensMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.llm.TokenCountRequest,
              unhinged.llm.TokenCountResponse>(
                service, METHODID_COUNT_TOKENS)))
        .addMethod(
          getHealthCheckMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.common.HealthCheckRequest,
              unhinged.common.HealthCheckResponse>(
                service, METHODID_HEALTH_CHECK)))
        .build();
  }

  private static abstract class LLMServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    LLMServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return unhinged.llm.LLMProto.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("LLMService");
    }
  }

  private static final class LLMServiceFileDescriptorSupplier
      extends LLMServiceBaseDescriptorSupplier {
    LLMServiceFileDescriptorSupplier() {}
  }

  private static final class LLMServiceMethodDescriptorSupplier
      extends LLMServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    LLMServiceMethodDescriptorSupplier(java.lang.String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (LLMServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new LLMServiceFileDescriptorSupplier())
              .addMethod(getGenerateCompletionMethod())
              .addMethod(getStreamCompletionMethod())
              .addMethod(getListModelsMethod())
              .addMethod(getGetModelMethod())
              .addMethod(getEstimateTokensMethod())
              .addMethod(getCountTokensMethod())
              .addMethod(getHealthCheckMethod())
              .build();
        }
      }
    }
    return result;
  }
}
