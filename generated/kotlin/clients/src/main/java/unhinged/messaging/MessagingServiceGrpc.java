package unhinged.messaging;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: messaging.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class MessagingServiceGrpc {

  private MessagingServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "unhinged.messaging.MessagingService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SendMessageRequest,
      unhinged.messaging.Messaging.SendMessageResponse> getSendMessageMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "SendMessage",
      requestType = unhinged.messaging.Messaging.SendMessageRequest.class,
      responseType = unhinged.messaging.Messaging.SendMessageResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SendMessageRequest,
      unhinged.messaging.Messaging.SendMessageResponse> getSendMessageMethod() {
    io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SendMessageRequest, unhinged.messaging.Messaging.SendMessageResponse> getSendMessageMethod;
    if ((getSendMessageMethod = MessagingServiceGrpc.getSendMessageMethod) == null) {
      synchronized (MessagingServiceGrpc.class) {
        if ((getSendMessageMethod = MessagingServiceGrpc.getSendMessageMethod) == null) {
          MessagingServiceGrpc.getSendMessageMethod = getSendMessageMethod =
              io.grpc.MethodDescriptor.<unhinged.messaging.Messaging.SendMessageRequest, unhinged.messaging.Messaging.SendMessageResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "SendMessage"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.SendMessageRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.SendMessageResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MessagingServiceMethodDescriptorSupplier("SendMessage"))
              .build();
        }
      }
    }
    return getSendMessageMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SendMessagesRequest,
      unhinged.messaging.Messaging.SendMessagesResponse> getSendMessagesMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "SendMessages",
      requestType = unhinged.messaging.Messaging.SendMessagesRequest.class,
      responseType = unhinged.messaging.Messaging.SendMessagesResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SendMessagesRequest,
      unhinged.messaging.Messaging.SendMessagesResponse> getSendMessagesMethod() {
    io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SendMessagesRequest, unhinged.messaging.Messaging.SendMessagesResponse> getSendMessagesMethod;
    if ((getSendMessagesMethod = MessagingServiceGrpc.getSendMessagesMethod) == null) {
      synchronized (MessagingServiceGrpc.class) {
        if ((getSendMessagesMethod = MessagingServiceGrpc.getSendMessagesMethod) == null) {
          MessagingServiceGrpc.getSendMessagesMethod = getSendMessagesMethod =
              io.grpc.MethodDescriptor.<unhinged.messaging.Messaging.SendMessagesRequest, unhinged.messaging.Messaging.SendMessagesResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "SendMessages"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.SendMessagesRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.SendMessagesResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MessagingServiceMethodDescriptorSupplier("SendMessages"))
              .build();
        }
      }
    }
    return getSendMessagesMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.messaging.Messaging.ReceiveMessagesRequest,
      unhinged.messaging.Messaging.ReceiveMessagesResponse> getReceiveMessagesMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ReceiveMessages",
      requestType = unhinged.messaging.Messaging.ReceiveMessagesRequest.class,
      responseType = unhinged.messaging.Messaging.ReceiveMessagesResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.messaging.Messaging.ReceiveMessagesRequest,
      unhinged.messaging.Messaging.ReceiveMessagesResponse> getReceiveMessagesMethod() {
    io.grpc.MethodDescriptor<unhinged.messaging.Messaging.ReceiveMessagesRequest, unhinged.messaging.Messaging.ReceiveMessagesResponse> getReceiveMessagesMethod;
    if ((getReceiveMessagesMethod = MessagingServiceGrpc.getReceiveMessagesMethod) == null) {
      synchronized (MessagingServiceGrpc.class) {
        if ((getReceiveMessagesMethod = MessagingServiceGrpc.getReceiveMessagesMethod) == null) {
          MessagingServiceGrpc.getReceiveMessagesMethod = getReceiveMessagesMethod =
              io.grpc.MethodDescriptor.<unhinged.messaging.Messaging.ReceiveMessagesRequest, unhinged.messaging.Messaging.ReceiveMessagesResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ReceiveMessages"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.ReceiveMessagesRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.ReceiveMessagesResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MessagingServiceMethodDescriptorSupplier("ReceiveMessages"))
              .build();
        }
      }
    }
    return getReceiveMessagesMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.messaging.Messaging.AcknowledgeMessageRequest,
      unhinged.messaging.Messaging.AcknowledgeMessageResponse> getAcknowledgeMessageMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "AcknowledgeMessage",
      requestType = unhinged.messaging.Messaging.AcknowledgeMessageRequest.class,
      responseType = unhinged.messaging.Messaging.AcknowledgeMessageResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.messaging.Messaging.AcknowledgeMessageRequest,
      unhinged.messaging.Messaging.AcknowledgeMessageResponse> getAcknowledgeMessageMethod() {
    io.grpc.MethodDescriptor<unhinged.messaging.Messaging.AcknowledgeMessageRequest, unhinged.messaging.Messaging.AcknowledgeMessageResponse> getAcknowledgeMessageMethod;
    if ((getAcknowledgeMessageMethod = MessagingServiceGrpc.getAcknowledgeMessageMethod) == null) {
      synchronized (MessagingServiceGrpc.class) {
        if ((getAcknowledgeMessageMethod = MessagingServiceGrpc.getAcknowledgeMessageMethod) == null) {
          MessagingServiceGrpc.getAcknowledgeMessageMethod = getAcknowledgeMessageMethod =
              io.grpc.MethodDescriptor.<unhinged.messaging.Messaging.AcknowledgeMessageRequest, unhinged.messaging.Messaging.AcknowledgeMessageResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "AcknowledgeMessage"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.AcknowledgeMessageRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.AcknowledgeMessageResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MessagingServiceMethodDescriptorSupplier("AcknowledgeMessage"))
              .build();
        }
      }
    }
    return getAcknowledgeMessageMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SubscribeToMessagesRequest,
      unhinged.messaging.Messaging.MessageStreamResponse> getSubscribeToMessagesMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "SubscribeToMessages",
      requestType = unhinged.messaging.Messaging.SubscribeToMessagesRequest.class,
      responseType = unhinged.messaging.Messaging.MessageStreamResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SubscribeToMessagesRequest,
      unhinged.messaging.Messaging.MessageStreamResponse> getSubscribeToMessagesMethod() {
    io.grpc.MethodDescriptor<unhinged.messaging.Messaging.SubscribeToMessagesRequest, unhinged.messaging.Messaging.MessageStreamResponse> getSubscribeToMessagesMethod;
    if ((getSubscribeToMessagesMethod = MessagingServiceGrpc.getSubscribeToMessagesMethod) == null) {
      synchronized (MessagingServiceGrpc.class) {
        if ((getSubscribeToMessagesMethod = MessagingServiceGrpc.getSubscribeToMessagesMethod) == null) {
          MessagingServiceGrpc.getSubscribeToMessagesMethod = getSubscribeToMessagesMethod =
              io.grpc.MethodDescriptor.<unhinged.messaging.Messaging.SubscribeToMessagesRequest, unhinged.messaging.Messaging.MessageStreamResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "SubscribeToMessages"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.SubscribeToMessagesRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.messaging.Messaging.MessageStreamResponse.getDefaultInstance()))
              .setSchemaDescriptor(new MessagingServiceMethodDescriptorSupplier("SubscribeToMessages"))
              .build();
        }
      }
    }
    return getSubscribeToMessagesMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static MessagingServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MessagingServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MessagingServiceStub>() {
        @java.lang.Override
        public MessagingServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MessagingServiceStub(channel, callOptions);
        }
      };
    return MessagingServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static MessagingServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MessagingServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MessagingServiceBlockingStub>() {
        @java.lang.Override
        public MessagingServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MessagingServiceBlockingStub(channel, callOptions);
        }
      };
    return MessagingServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static MessagingServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<MessagingServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<MessagingServiceFutureStub>() {
        @java.lang.Override
        public MessagingServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new MessagingServiceFutureStub(channel, callOptions);
        }
      };
    return MessagingServiceFutureStub.newStub(factory, channel);
  }

  /**
   */
  public interface AsyncService {

    /**
     * <pre>
     * Message sending
     * </pre>
     */
    default void sendMessage(unhinged.messaging.Messaging.SendMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.SendMessageResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSendMessageMethod(), responseObserver);
    }

    /**
     */
    default void sendMessages(unhinged.messaging.Messaging.SendMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.SendMessagesResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSendMessagesMethod(), responseObserver);
    }

    /**
     * <pre>
     * Message receiving (polling)
     * </pre>
     */
    default void receiveMessages(unhinged.messaging.Messaging.ReceiveMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.ReceiveMessagesResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getReceiveMessagesMethod(), responseObserver);
    }

    /**
     */
    default void acknowledgeMessage(unhinged.messaging.Messaging.AcknowledgeMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.AcknowledgeMessageResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getAcknowledgeMessageMethod(), responseObserver);
    }

    /**
     * <pre>
     * Message streaming
     * </pre>
     */
    default void subscribeToMessages(unhinged.messaging.Messaging.SubscribeToMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.MessageStreamResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSubscribeToMessagesMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service MessagingService.
   */
  public static abstract class MessagingServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return MessagingServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service MessagingService.
   */
  public static final class MessagingServiceStub
      extends io.grpc.stub.AbstractAsyncStub<MessagingServiceStub> {
    private MessagingServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MessagingServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MessagingServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Message sending
     * </pre>
     */
    public void sendMessage(unhinged.messaging.Messaging.SendMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.SendMessageResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getSendMessageMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void sendMessages(unhinged.messaging.Messaging.SendMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.SendMessagesResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getSendMessagesMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Message receiving (polling)
     * </pre>
     */
    public void receiveMessages(unhinged.messaging.Messaging.ReceiveMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.ReceiveMessagesResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getReceiveMessagesMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void acknowledgeMessage(unhinged.messaging.Messaging.AcknowledgeMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.AcknowledgeMessageResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getAcknowledgeMessageMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Message streaming
     * </pre>
     */
    public void subscribeToMessages(unhinged.messaging.Messaging.SubscribeToMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.MessageStreamResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getSubscribeToMessagesMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service MessagingService.
   */
  public static final class MessagingServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<MessagingServiceBlockingStub> {
    private MessagingServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MessagingServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MessagingServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Message sending
     * </pre>
     */
    public unhinged.messaging.Messaging.SendMessageResponse sendMessage(unhinged.messaging.Messaging.SendMessageRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSendMessageMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.messaging.Messaging.SendMessagesResponse sendMessages(unhinged.messaging.Messaging.SendMessagesRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSendMessagesMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Message receiving (polling)
     * </pre>
     */
    public unhinged.messaging.Messaging.ReceiveMessagesResponse receiveMessages(unhinged.messaging.Messaging.ReceiveMessagesRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getReceiveMessagesMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.messaging.Messaging.AcknowledgeMessageResponse acknowledgeMessage(unhinged.messaging.Messaging.AcknowledgeMessageRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getAcknowledgeMessageMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Message streaming
     * </pre>
     */
    public java.util.Iterator<unhinged.messaging.Messaging.MessageStreamResponse> subscribeToMessages(
        unhinged.messaging.Messaging.SubscribeToMessagesRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getSubscribeToMessagesMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service MessagingService.
   */
  public static final class MessagingServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<MessagingServiceFutureStub> {
    private MessagingServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected MessagingServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new MessagingServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Message sending
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.messaging.Messaging.SendMessageResponse> sendMessage(
        unhinged.messaging.Messaging.SendMessageRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getSendMessageMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.messaging.Messaging.SendMessagesResponse> sendMessages(
        unhinged.messaging.Messaging.SendMessagesRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getSendMessagesMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Message receiving (polling)
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.messaging.Messaging.ReceiveMessagesResponse> receiveMessages(
        unhinged.messaging.Messaging.ReceiveMessagesRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getReceiveMessagesMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.messaging.Messaging.AcknowledgeMessageResponse> acknowledgeMessage(
        unhinged.messaging.Messaging.AcknowledgeMessageRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getAcknowledgeMessageMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_SEND_MESSAGE = 0;
  private static final int METHODID_SEND_MESSAGES = 1;
  private static final int METHODID_RECEIVE_MESSAGES = 2;
  private static final int METHODID_ACKNOWLEDGE_MESSAGE = 3;
  private static final int METHODID_SUBSCRIBE_TO_MESSAGES = 4;

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
        case METHODID_SEND_MESSAGE:
          serviceImpl.sendMessage((unhinged.messaging.Messaging.SendMessageRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.SendMessageResponse>) responseObserver);
          break;
        case METHODID_SEND_MESSAGES:
          serviceImpl.sendMessages((unhinged.messaging.Messaging.SendMessagesRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.SendMessagesResponse>) responseObserver);
          break;
        case METHODID_RECEIVE_MESSAGES:
          serviceImpl.receiveMessages((unhinged.messaging.Messaging.ReceiveMessagesRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.ReceiveMessagesResponse>) responseObserver);
          break;
        case METHODID_ACKNOWLEDGE_MESSAGE:
          serviceImpl.acknowledgeMessage((unhinged.messaging.Messaging.AcknowledgeMessageRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.AcknowledgeMessageResponse>) responseObserver);
          break;
        case METHODID_SUBSCRIBE_TO_MESSAGES:
          serviceImpl.subscribeToMessages((unhinged.messaging.Messaging.SubscribeToMessagesRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.messaging.Messaging.MessageStreamResponse>) responseObserver);
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
          getSendMessageMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.messaging.Messaging.SendMessageRequest,
              unhinged.messaging.Messaging.SendMessageResponse>(
                service, METHODID_SEND_MESSAGE)))
        .addMethod(
          getSendMessagesMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.messaging.Messaging.SendMessagesRequest,
              unhinged.messaging.Messaging.SendMessagesResponse>(
                service, METHODID_SEND_MESSAGES)))
        .addMethod(
          getReceiveMessagesMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.messaging.Messaging.ReceiveMessagesRequest,
              unhinged.messaging.Messaging.ReceiveMessagesResponse>(
                service, METHODID_RECEIVE_MESSAGES)))
        .addMethod(
          getAcknowledgeMessageMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.messaging.Messaging.AcknowledgeMessageRequest,
              unhinged.messaging.Messaging.AcknowledgeMessageResponse>(
                service, METHODID_ACKNOWLEDGE_MESSAGE)))
        .addMethod(
          getSubscribeToMessagesMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              unhinged.messaging.Messaging.SubscribeToMessagesRequest,
              unhinged.messaging.Messaging.MessageStreamResponse>(
                service, METHODID_SUBSCRIBE_TO_MESSAGES)))
        .build();
  }

  private static abstract class MessagingServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    MessagingServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return unhinged.messaging.Messaging.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("MessagingService");
    }
  }

  private static final class MessagingServiceFileDescriptorSupplier
      extends MessagingServiceBaseDescriptorSupplier {
    MessagingServiceFileDescriptorSupplier() {}
  }

  private static final class MessagingServiceMethodDescriptorSupplier
      extends MessagingServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    MessagingServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (MessagingServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new MessagingServiceFileDescriptorSupplier())
              .addMethod(getSendMessageMethod())
              .addMethod(getSendMessagesMethod())
              .addMethod(getReceiveMessagesMethod())
              .addMethod(getAcknowledgeMessageMethod())
              .addMethod(getSubscribeToMessagesMethod())
              .build();
        }
      }
    }
    return result;
  }
}
