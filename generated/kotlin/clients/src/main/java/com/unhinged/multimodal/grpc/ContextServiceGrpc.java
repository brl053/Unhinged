package com.unhinged.multimodal.grpc;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 * Context-Aware LLM Service - Pure LLM operations for prompt enhancement
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: context_service.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class ContextServiceGrpc {

  private ContextServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "multimodal.ContextService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.PromptGenerationRequest,
      com.unhinged.multimodal.grpc.PromptGenerationResponse> getGeneratePromptMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GeneratePrompt",
      requestType = com.unhinged.multimodal.grpc.PromptGenerationRequest.class,
      responseType = com.unhinged.multimodal.grpc.PromptGenerationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.PromptGenerationRequest,
      com.unhinged.multimodal.grpc.PromptGenerationResponse> getGeneratePromptMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.PromptGenerationRequest, com.unhinged.multimodal.grpc.PromptGenerationResponse> getGeneratePromptMethod;
    if ((getGeneratePromptMethod = ContextServiceGrpc.getGeneratePromptMethod) == null) {
      synchronized (ContextServiceGrpc.class) {
        if ((getGeneratePromptMethod = ContextServiceGrpc.getGeneratePromptMethod) == null) {
          ContextServiceGrpc.getGeneratePromptMethod = getGeneratePromptMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.PromptGenerationRequest, com.unhinged.multimodal.grpc.PromptGenerationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GeneratePrompt"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.PromptGenerationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.PromptGenerationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ContextServiceMethodDescriptorSupplier("GeneratePrompt"))
              .build();
        }
      }
    }
    return getGeneratePromptMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.ContextSearchRequest,
      com.unhinged.multimodal.grpc.ContextSearchResponse> getSearchContextMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "SearchContext",
      requestType = com.unhinged.multimodal.grpc.ContextSearchRequest.class,
      responseType = com.unhinged.multimodal.grpc.ContextSearchResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.ContextSearchRequest,
      com.unhinged.multimodal.grpc.ContextSearchResponse> getSearchContextMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.ContextSearchRequest, com.unhinged.multimodal.grpc.ContextSearchResponse> getSearchContextMethod;
    if ((getSearchContextMethod = ContextServiceGrpc.getSearchContextMethod) == null) {
      synchronized (ContextServiceGrpc.class) {
        if ((getSearchContextMethod = ContextServiceGrpc.getSearchContextMethod) == null) {
          ContextServiceGrpc.getSearchContextMethod = getSearchContextMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.ContextSearchRequest, com.unhinged.multimodal.grpc.ContextSearchResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "SearchContext"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.ContextSearchRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.ContextSearchResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ContextServiceMethodDescriptorSupplier("SearchContext"))
              .build();
        }
      }
    }
    return getSearchContextMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.TextGenerationRequest,
      com.unhinged.multimodal.grpc.TextGenerationResponse> getGenerateTextMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GenerateText",
      requestType = com.unhinged.multimodal.grpc.TextGenerationRequest.class,
      responseType = com.unhinged.multimodal.grpc.TextGenerationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.TextGenerationRequest,
      com.unhinged.multimodal.grpc.TextGenerationResponse> getGenerateTextMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.TextGenerationRequest, com.unhinged.multimodal.grpc.TextGenerationResponse> getGenerateTextMethod;
    if ((getGenerateTextMethod = ContextServiceGrpc.getGenerateTextMethod) == null) {
      synchronized (ContextServiceGrpc.class) {
        if ((getGenerateTextMethod = ContextServiceGrpc.getGenerateTextMethod) == null) {
          ContextServiceGrpc.getGenerateTextMethod = getGenerateTextMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.TextGenerationRequest, com.unhinged.multimodal.grpc.TextGenerationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GenerateText"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.TextGenerationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.TextGenerationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ContextServiceMethodDescriptorSupplier("GenerateText"))
              .build();
        }
      }
    }
    return getGenerateTextMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty,
      com.unhinged.multimodal.grpc.LLMModelsResponse> getGetAvailableModelsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetAvailableModels",
      requestType = com.unhinged.multimodal.grpc.Empty.class,
      responseType = com.unhinged.multimodal.grpc.LLMModelsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty,
      com.unhinged.multimodal.grpc.LLMModelsResponse> getGetAvailableModelsMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty, com.unhinged.multimodal.grpc.LLMModelsResponse> getGetAvailableModelsMethod;
    if ((getGetAvailableModelsMethod = ContextServiceGrpc.getGetAvailableModelsMethod) == null) {
      synchronized (ContextServiceGrpc.class) {
        if ((getGetAvailableModelsMethod = ContextServiceGrpc.getGetAvailableModelsMethod) == null) {
          ContextServiceGrpc.getGetAvailableModelsMethod = getGetAvailableModelsMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.Empty, com.unhinged.multimodal.grpc.LLMModelsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetAvailableModels"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.Empty.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.LLMModelsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ContextServiceMethodDescriptorSupplier("GetAvailableModels"))
              .build();
        }
      }
    }
    return getGetAvailableModelsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty,
      com.unhinged.multimodal.grpc.HealthResponse> getGetHealthMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetHealth",
      requestType = com.unhinged.multimodal.grpc.Empty.class,
      responseType = com.unhinged.multimodal.grpc.HealthResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty,
      com.unhinged.multimodal.grpc.HealthResponse> getGetHealthMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty, com.unhinged.multimodal.grpc.HealthResponse> getGetHealthMethod;
    if ((getGetHealthMethod = ContextServiceGrpc.getGetHealthMethod) == null) {
      synchronized (ContextServiceGrpc.class) {
        if ((getGetHealthMethod = ContextServiceGrpc.getGetHealthMethod) == null) {
          ContextServiceGrpc.getGetHealthMethod = getGetHealthMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.Empty, com.unhinged.multimodal.grpc.HealthResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetHealth"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.Empty.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.HealthResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ContextServiceMethodDescriptorSupplier("GetHealth"))
              .build();
        }
      }
    }
    return getGetHealthMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static ContextServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ContextServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ContextServiceStub>() {
        @java.lang.Override
        public ContextServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ContextServiceStub(channel, callOptions);
        }
      };
    return ContextServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static ContextServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ContextServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ContextServiceBlockingStub>() {
        @java.lang.Override
        public ContextServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ContextServiceBlockingStub(channel, callOptions);
        }
      };
    return ContextServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static ContextServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ContextServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ContextServiceFutureStub>() {
        @java.lang.Override
        public ContextServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ContextServiceFutureStub(channel, callOptions);
        }
      };
    return ContextServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * Context-Aware LLM Service - Pure LLM operations for prompt enhancement
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * Generate enhanced prompt with project context
     * </pre>
     */
    default void generatePrompt(com.unhinged.multimodal.grpc.PromptGenerationRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.PromptGenerationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGeneratePromptMethod(), responseObserver);
    }

    /**
     * <pre>
     * Search project context and documentation
     * </pre>
     */
    default void searchContext(com.unhinged.multimodal.grpc.ContextSearchRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ContextSearchResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSearchContextMethod(), responseObserver);
    }

    /**
     * <pre>
     * Generate text using LLM
     * </pre>
     */
    default void generateText(com.unhinged.multimodal.grpc.TextGenerationRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.TextGenerationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGenerateTextMethod(), responseObserver);
    }

    /**
     * <pre>
     * Get available LLM models
     * </pre>
     */
    default void getAvailableModels(com.unhinged.multimodal.grpc.Empty request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.LLMModelsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetAvailableModelsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Health check for service availability
     * </pre>
     */
    default void getHealth(com.unhinged.multimodal.grpc.Empty request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.HealthResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetHealthMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service ContextService.
   * <pre>
   * Context-Aware LLM Service - Pure LLM operations for prompt enhancement
   * </pre>
   */
  public static abstract class ContextServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return ContextServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service ContextService.
   * <pre>
   * Context-Aware LLM Service - Pure LLM operations for prompt enhancement
   * </pre>
   */
  public static final class ContextServiceStub
      extends io.grpc.stub.AbstractAsyncStub<ContextServiceStub> {
    private ContextServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ContextServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ContextServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Generate enhanced prompt with project context
     * </pre>
     */
    public void generatePrompt(com.unhinged.multimodal.grpc.PromptGenerationRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.PromptGenerationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGeneratePromptMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Search project context and documentation
     * </pre>
     */
    public void searchContext(com.unhinged.multimodal.grpc.ContextSearchRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ContextSearchResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getSearchContextMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Generate text using LLM
     * </pre>
     */
    public void generateText(com.unhinged.multimodal.grpc.TextGenerationRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.TextGenerationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGenerateTextMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Get available LLM models
     * </pre>
     */
    public void getAvailableModels(com.unhinged.multimodal.grpc.Empty request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.LLMModelsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetAvailableModelsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Health check for service availability
     * </pre>
     */
    public void getHealth(com.unhinged.multimodal.grpc.Empty request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.HealthResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetHealthMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service ContextService.
   * <pre>
   * Context-Aware LLM Service - Pure LLM operations for prompt enhancement
   * </pre>
   */
  public static final class ContextServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<ContextServiceBlockingStub> {
    private ContextServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ContextServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ContextServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Generate enhanced prompt with project context
     * </pre>
     */
    public com.unhinged.multimodal.grpc.PromptGenerationResponse generatePrompt(com.unhinged.multimodal.grpc.PromptGenerationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGeneratePromptMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Search project context and documentation
     * </pre>
     */
    public com.unhinged.multimodal.grpc.ContextSearchResponse searchContext(com.unhinged.multimodal.grpc.ContextSearchRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSearchContextMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Generate text using LLM
     * </pre>
     */
    public com.unhinged.multimodal.grpc.TextGenerationResponse generateText(com.unhinged.multimodal.grpc.TextGenerationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGenerateTextMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Get available LLM models
     * </pre>
     */
    public com.unhinged.multimodal.grpc.LLMModelsResponse getAvailableModels(com.unhinged.multimodal.grpc.Empty request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetAvailableModelsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Health check for service availability
     * </pre>
     */
    public com.unhinged.multimodal.grpc.HealthResponse getHealth(com.unhinged.multimodal.grpc.Empty request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetHealthMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service ContextService.
   * <pre>
   * Context-Aware LLM Service - Pure LLM operations for prompt enhancement
   * </pre>
   */
  public static final class ContextServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<ContextServiceFutureStub> {
    private ContextServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ContextServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ContextServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Generate enhanced prompt with project context
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.PromptGenerationResponse> generatePrompt(
        com.unhinged.multimodal.grpc.PromptGenerationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGeneratePromptMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Search project context and documentation
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.ContextSearchResponse> searchContext(
        com.unhinged.multimodal.grpc.ContextSearchRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getSearchContextMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Generate text using LLM
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.TextGenerationResponse> generateText(
        com.unhinged.multimodal.grpc.TextGenerationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGenerateTextMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Get available LLM models
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.LLMModelsResponse> getAvailableModels(
        com.unhinged.multimodal.grpc.Empty request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetAvailableModelsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Health check for service availability
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.HealthResponse> getHealth(
        com.unhinged.multimodal.grpc.Empty request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetHealthMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_GENERATE_PROMPT = 0;
  private static final int METHODID_SEARCH_CONTEXT = 1;
  private static final int METHODID_GENERATE_TEXT = 2;
  private static final int METHODID_GET_AVAILABLE_MODELS = 3;
  private static final int METHODID_GET_HEALTH = 4;

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
        case METHODID_GENERATE_PROMPT:
          serviceImpl.generatePrompt((com.unhinged.multimodal.grpc.PromptGenerationRequest) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.PromptGenerationResponse>) responseObserver);
          break;
        case METHODID_SEARCH_CONTEXT:
          serviceImpl.searchContext((com.unhinged.multimodal.grpc.ContextSearchRequest) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ContextSearchResponse>) responseObserver);
          break;
        case METHODID_GENERATE_TEXT:
          serviceImpl.generateText((com.unhinged.multimodal.grpc.TextGenerationRequest) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.TextGenerationResponse>) responseObserver);
          break;
        case METHODID_GET_AVAILABLE_MODELS:
          serviceImpl.getAvailableModels((com.unhinged.multimodal.grpc.Empty) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.LLMModelsResponse>) responseObserver);
          break;
        case METHODID_GET_HEALTH:
          serviceImpl.getHealth((com.unhinged.multimodal.grpc.Empty) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.HealthResponse>) responseObserver);
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
          getGeneratePromptMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.PromptGenerationRequest,
              com.unhinged.multimodal.grpc.PromptGenerationResponse>(
                service, METHODID_GENERATE_PROMPT)))
        .addMethod(
          getSearchContextMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.ContextSearchRequest,
              com.unhinged.multimodal.grpc.ContextSearchResponse>(
                service, METHODID_SEARCH_CONTEXT)))
        .addMethod(
          getGenerateTextMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.TextGenerationRequest,
              com.unhinged.multimodal.grpc.TextGenerationResponse>(
                service, METHODID_GENERATE_TEXT)))
        .addMethod(
          getGetAvailableModelsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.Empty,
              com.unhinged.multimodal.grpc.LLMModelsResponse>(
                service, METHODID_GET_AVAILABLE_MODELS)))
        .addMethod(
          getGetHealthMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.Empty,
              com.unhinged.multimodal.grpc.HealthResponse>(
                service, METHODID_GET_HEALTH)))
        .build();
  }

  private static abstract class ContextServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    ContextServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.unhinged.multimodal.grpc.ContextServiceProto.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("ContextService");
    }
  }

  private static final class ContextServiceFileDescriptorSupplier
      extends ContextServiceBaseDescriptorSupplier {
    ContextServiceFileDescriptorSupplier() {}
  }

  private static final class ContextServiceMethodDescriptorSupplier
      extends ContextServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    ContextServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (ContextServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new ContextServiceFileDescriptorSupplier())
              .addMethod(getGeneratePromptMethod())
              .addMethod(getSearchContextMethod())
              .addMethod(getGenerateTextMethod())
              .addMethod(getGetAvailableModelsMethod())
              .addMethod(getGetHealthMethod())
              .build();
        }
      }
    }
    return result;
  }
}
