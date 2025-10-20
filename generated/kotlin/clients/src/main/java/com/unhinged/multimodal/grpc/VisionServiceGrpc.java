package com.unhinged.multimodal.grpc;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 * Vision AI Service - Pure model inference operations
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: vision_service.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class VisionServiceGrpc {

  private VisionServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "multimodal.VisionService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.VisionInferenceRequest,
      com.unhinged.multimodal.grpc.VisionInferenceResponse> getInferMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Infer",
      requestType = com.unhinged.multimodal.grpc.VisionInferenceRequest.class,
      responseType = com.unhinged.multimodal.grpc.VisionInferenceResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.VisionInferenceRequest,
      com.unhinged.multimodal.grpc.VisionInferenceResponse> getInferMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.VisionInferenceRequest, com.unhinged.multimodal.grpc.VisionInferenceResponse> getInferMethod;
    if ((getInferMethod = VisionServiceGrpc.getInferMethod) == null) {
      synchronized (VisionServiceGrpc.class) {
        if ((getInferMethod = VisionServiceGrpc.getInferMethod) == null) {
          VisionServiceGrpc.getInferMethod = getInferMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.VisionInferenceRequest, com.unhinged.multimodal.grpc.VisionInferenceResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Infer"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.VisionInferenceRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.VisionInferenceResponse.getDefaultInstance()))
              .setSchemaDescriptor(new VisionServiceMethodDescriptorSupplier("Infer"))
              .build();
        }
      }
    }
    return getInferMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty,
      com.unhinged.multimodal.grpc.ModelsResponse> getGetAvailableModelsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetAvailableModels",
      requestType = com.unhinged.multimodal.grpc.Empty.class,
      responseType = com.unhinged.multimodal.grpc.ModelsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty,
      com.unhinged.multimodal.grpc.ModelsResponse> getGetAvailableModelsMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.Empty, com.unhinged.multimodal.grpc.ModelsResponse> getGetAvailableModelsMethod;
    if ((getGetAvailableModelsMethod = VisionServiceGrpc.getGetAvailableModelsMethod) == null) {
      synchronized (VisionServiceGrpc.class) {
        if ((getGetAvailableModelsMethod = VisionServiceGrpc.getGetAvailableModelsMethod) == null) {
          VisionServiceGrpc.getGetAvailableModelsMethod = getGetAvailableModelsMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.Empty, com.unhinged.multimodal.grpc.ModelsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetAvailableModels"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.Empty.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.ModelsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new VisionServiceMethodDescriptorSupplier("GetAvailableModels"))
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
    if ((getGetHealthMethod = VisionServiceGrpc.getGetHealthMethod) == null) {
      synchronized (VisionServiceGrpc.class) {
        if ((getGetHealthMethod = VisionServiceGrpc.getGetHealthMethod) == null) {
          VisionServiceGrpc.getGetHealthMethod = getGetHealthMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.Empty, com.unhinged.multimodal.grpc.HealthResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetHealth"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.Empty.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.HealthResponse.getDefaultInstance()))
              .setSchemaDescriptor(new VisionServiceMethodDescriptorSupplier("GetHealth"))
              .build();
        }
      }
    }
    return getGetHealthMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.ModelMetricsRequest,
      com.unhinged.multimodal.grpc.ModelMetricsResponse> getGetModelMetricsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetModelMetrics",
      requestType = com.unhinged.multimodal.grpc.ModelMetricsRequest.class,
      responseType = com.unhinged.multimodal.grpc.ModelMetricsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.ModelMetricsRequest,
      com.unhinged.multimodal.grpc.ModelMetricsResponse> getGetModelMetricsMethod() {
    io.grpc.MethodDescriptor<com.unhinged.multimodal.grpc.ModelMetricsRequest, com.unhinged.multimodal.grpc.ModelMetricsResponse> getGetModelMetricsMethod;
    if ((getGetModelMetricsMethod = VisionServiceGrpc.getGetModelMetricsMethod) == null) {
      synchronized (VisionServiceGrpc.class) {
        if ((getGetModelMetricsMethod = VisionServiceGrpc.getGetModelMetricsMethod) == null) {
          VisionServiceGrpc.getGetModelMetricsMethod = getGetModelMetricsMethod =
              io.grpc.MethodDescriptor.<com.unhinged.multimodal.grpc.ModelMetricsRequest, com.unhinged.multimodal.grpc.ModelMetricsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetModelMetrics"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.ModelMetricsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.unhinged.multimodal.grpc.ModelMetricsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new VisionServiceMethodDescriptorSupplier("GetModelMetrics"))
              .build();
        }
      }
    }
    return getGetModelMetricsMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static VisionServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<VisionServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<VisionServiceStub>() {
        @java.lang.Override
        public VisionServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new VisionServiceStub(channel, callOptions);
        }
      };
    return VisionServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static VisionServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<VisionServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<VisionServiceBlockingStub>() {
        @java.lang.Override
        public VisionServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new VisionServiceBlockingStub(channel, callOptions);
        }
      };
    return VisionServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static VisionServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<VisionServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<VisionServiceFutureStub>() {
        @java.lang.Override
        public VisionServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new VisionServiceFutureStub(channel, callOptions);
        }
      };
    return VisionServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * Vision AI Service - Pure model inference operations
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * Perform image inference using specified model
     * </pre>
     */
    default void infer(com.unhinged.multimodal.grpc.VisionInferenceRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.VisionInferenceResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getInferMethod(), responseObserver);
    }

    /**
     * <pre>
     * Get list of available vision models
     * </pre>
     */
    default void getAvailableModels(com.unhinged.multimodal.grpc.Empty request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ModelsResponse> responseObserver) {
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

    /**
     * <pre>
     * Get model performance metrics
     * </pre>
     */
    default void getModelMetrics(com.unhinged.multimodal.grpc.ModelMetricsRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ModelMetricsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetModelMetricsMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service VisionService.
   * <pre>
   * Vision AI Service - Pure model inference operations
   * </pre>
   */
  public static abstract class VisionServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return VisionServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service VisionService.
   * <pre>
   * Vision AI Service - Pure model inference operations
   * </pre>
   */
  public static final class VisionServiceStub
      extends io.grpc.stub.AbstractAsyncStub<VisionServiceStub> {
    private VisionServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected VisionServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new VisionServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Perform image inference using specified model
     * </pre>
     */
    public void infer(com.unhinged.multimodal.grpc.VisionInferenceRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.VisionInferenceResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getInferMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Get list of available vision models
     * </pre>
     */
    public void getAvailableModels(com.unhinged.multimodal.grpc.Empty request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ModelsResponse> responseObserver) {
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

    /**
     * <pre>
     * Get model performance metrics
     * </pre>
     */
    public void getModelMetrics(com.unhinged.multimodal.grpc.ModelMetricsRequest request,
        io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ModelMetricsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetModelMetricsMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service VisionService.
   * <pre>
   * Vision AI Service - Pure model inference operations
   * </pre>
   */
  public static final class VisionServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<VisionServiceBlockingStub> {
    private VisionServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected VisionServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new VisionServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Perform image inference using specified model
     * </pre>
     */
    public com.unhinged.multimodal.grpc.VisionInferenceResponse infer(com.unhinged.multimodal.grpc.VisionInferenceRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getInferMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Get list of available vision models
     * </pre>
     */
    public com.unhinged.multimodal.grpc.ModelsResponse getAvailableModels(com.unhinged.multimodal.grpc.Empty request) {
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

    /**
     * <pre>
     * Get model performance metrics
     * </pre>
     */
    public com.unhinged.multimodal.grpc.ModelMetricsResponse getModelMetrics(com.unhinged.multimodal.grpc.ModelMetricsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetModelMetricsMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service VisionService.
   * <pre>
   * Vision AI Service - Pure model inference operations
   * </pre>
   */
  public static final class VisionServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<VisionServiceFutureStub> {
    private VisionServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected VisionServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new VisionServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Perform image inference using specified model
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.VisionInferenceResponse> infer(
        com.unhinged.multimodal.grpc.VisionInferenceRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getInferMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Get list of available vision models
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.ModelsResponse> getAvailableModels(
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

    /**
     * <pre>
     * Get model performance metrics
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<com.unhinged.multimodal.grpc.ModelMetricsResponse> getModelMetrics(
        com.unhinged.multimodal.grpc.ModelMetricsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetModelMetricsMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_INFER = 0;
  private static final int METHODID_GET_AVAILABLE_MODELS = 1;
  private static final int METHODID_GET_HEALTH = 2;
  private static final int METHODID_GET_MODEL_METRICS = 3;

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
        case METHODID_INFER:
          serviceImpl.infer((com.unhinged.multimodal.grpc.VisionInferenceRequest) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.VisionInferenceResponse>) responseObserver);
          break;
        case METHODID_GET_AVAILABLE_MODELS:
          serviceImpl.getAvailableModels((com.unhinged.multimodal.grpc.Empty) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ModelsResponse>) responseObserver);
          break;
        case METHODID_GET_HEALTH:
          serviceImpl.getHealth((com.unhinged.multimodal.grpc.Empty) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.HealthResponse>) responseObserver);
          break;
        case METHODID_GET_MODEL_METRICS:
          serviceImpl.getModelMetrics((com.unhinged.multimodal.grpc.ModelMetricsRequest) request,
              (io.grpc.stub.StreamObserver<com.unhinged.multimodal.grpc.ModelMetricsResponse>) responseObserver);
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
          getInferMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.VisionInferenceRequest,
              com.unhinged.multimodal.grpc.VisionInferenceResponse>(
                service, METHODID_INFER)))
        .addMethod(
          getGetAvailableModelsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.Empty,
              com.unhinged.multimodal.grpc.ModelsResponse>(
                service, METHODID_GET_AVAILABLE_MODELS)))
        .addMethod(
          getGetHealthMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.Empty,
              com.unhinged.multimodal.grpc.HealthResponse>(
                service, METHODID_GET_HEALTH)))
        .addMethod(
          getGetModelMetricsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.unhinged.multimodal.grpc.ModelMetricsRequest,
              com.unhinged.multimodal.grpc.ModelMetricsResponse>(
                service, METHODID_GET_MODEL_METRICS)))
        .build();
  }

  private static abstract class VisionServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    VisionServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.unhinged.multimodal.grpc.VisionServiceProto.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("VisionService");
    }
  }

  private static final class VisionServiceFileDescriptorSupplier
      extends VisionServiceBaseDescriptorSupplier {
    VisionServiceFileDescriptorSupplier() {}
  }

  private static final class VisionServiceMethodDescriptorSupplier
      extends VisionServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    VisionServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (VisionServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new VisionServiceFileDescriptorSupplier())
              .addMethod(getInferMethod())
              .addMethod(getGetAvailableModelsMethod())
              .addMethod(getGetHealthMethod())
              .addMethod(getGetModelMetricsMethod())
              .build();
        }
      }
    }
    return result;
  }
}
