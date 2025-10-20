package unhinged.chat;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 **
 * Chat service for conversation and message management
 * 
 * Uses common patterns for consistent API behavior across services
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: chat.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class ChatServiceGrpc {

  private ChatServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "unhinged.chat.v1.ChatService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<unhinged.chat.CreateConversationRequest,
      unhinged.chat.CreateConversationResponse> getCreateConversationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "CreateConversation",
      requestType = unhinged.chat.CreateConversationRequest.class,
      responseType = unhinged.chat.CreateConversationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.CreateConversationRequest,
      unhinged.chat.CreateConversationResponse> getCreateConversationMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.CreateConversationRequest, unhinged.chat.CreateConversationResponse> getCreateConversationMethod;
    if ((getCreateConversationMethod = ChatServiceGrpc.getCreateConversationMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getCreateConversationMethod = ChatServiceGrpc.getCreateConversationMethod) == null) {
          ChatServiceGrpc.getCreateConversationMethod = getCreateConversationMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.CreateConversationRequest, unhinged.chat.CreateConversationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "CreateConversation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.CreateConversationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.CreateConversationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("CreateConversation"))
              .build();
        }
      }
    }
    return getCreateConversationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.GetConversationRequest,
      unhinged.chat.GetConversationResponse> getGetConversationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetConversation",
      requestType = unhinged.chat.GetConversationRequest.class,
      responseType = unhinged.chat.GetConversationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.GetConversationRequest,
      unhinged.chat.GetConversationResponse> getGetConversationMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.GetConversationRequest, unhinged.chat.GetConversationResponse> getGetConversationMethod;
    if ((getGetConversationMethod = ChatServiceGrpc.getGetConversationMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getGetConversationMethod = ChatServiceGrpc.getGetConversationMethod) == null) {
          ChatServiceGrpc.getGetConversationMethod = getGetConversationMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.GetConversationRequest, unhinged.chat.GetConversationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetConversation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.GetConversationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.GetConversationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("GetConversation"))
              .build();
        }
      }
    }
    return getGetConversationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.ListConversationsRequest,
      unhinged.chat.ListConversationsResponse> getListConversationsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListConversations",
      requestType = unhinged.chat.ListConversationsRequest.class,
      responseType = unhinged.chat.ListConversationsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.ListConversationsRequest,
      unhinged.chat.ListConversationsResponse> getListConversationsMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.ListConversationsRequest, unhinged.chat.ListConversationsResponse> getListConversationsMethod;
    if ((getListConversationsMethod = ChatServiceGrpc.getListConversationsMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getListConversationsMethod = ChatServiceGrpc.getListConversationsMethod) == null) {
          ChatServiceGrpc.getListConversationsMethod = getListConversationsMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.ListConversationsRequest, unhinged.chat.ListConversationsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListConversations"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.ListConversationsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.ListConversationsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("ListConversations"))
              .build();
        }
      }
    }
    return getListConversationsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.UpdateConversationRequest,
      unhinged.chat.UpdateConversationResponse> getUpdateConversationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "UpdateConversation",
      requestType = unhinged.chat.UpdateConversationRequest.class,
      responseType = unhinged.chat.UpdateConversationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.UpdateConversationRequest,
      unhinged.chat.UpdateConversationResponse> getUpdateConversationMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.UpdateConversationRequest, unhinged.chat.UpdateConversationResponse> getUpdateConversationMethod;
    if ((getUpdateConversationMethod = ChatServiceGrpc.getUpdateConversationMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getUpdateConversationMethod = ChatServiceGrpc.getUpdateConversationMethod) == null) {
          ChatServiceGrpc.getUpdateConversationMethod = getUpdateConversationMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.UpdateConversationRequest, unhinged.chat.UpdateConversationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "UpdateConversation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.UpdateConversationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.UpdateConversationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("UpdateConversation"))
              .build();
        }
      }
    }
    return getUpdateConversationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.DeleteConversationRequest,
      unhinged.chat.DeleteConversationResponse> getDeleteConversationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "DeleteConversation",
      requestType = unhinged.chat.DeleteConversationRequest.class,
      responseType = unhinged.chat.DeleteConversationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.DeleteConversationRequest,
      unhinged.chat.DeleteConversationResponse> getDeleteConversationMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.DeleteConversationRequest, unhinged.chat.DeleteConversationResponse> getDeleteConversationMethod;
    if ((getDeleteConversationMethod = ChatServiceGrpc.getDeleteConversationMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getDeleteConversationMethod = ChatServiceGrpc.getDeleteConversationMethod) == null) {
          ChatServiceGrpc.getDeleteConversationMethod = getDeleteConversationMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.DeleteConversationRequest, unhinged.chat.DeleteConversationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "DeleteConversation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.DeleteConversationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.DeleteConversationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("DeleteConversation"))
              .build();
        }
      }
    }
    return getDeleteConversationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.SendMessageRequest,
      unhinged.chat.SendMessageResponse> getSendMessageMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "SendMessage",
      requestType = unhinged.chat.SendMessageRequest.class,
      responseType = unhinged.chat.SendMessageResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.SendMessageRequest,
      unhinged.chat.SendMessageResponse> getSendMessageMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.SendMessageRequest, unhinged.chat.SendMessageResponse> getSendMessageMethod;
    if ((getSendMessageMethod = ChatServiceGrpc.getSendMessageMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getSendMessageMethod = ChatServiceGrpc.getSendMessageMethod) == null) {
          ChatServiceGrpc.getSendMessageMethod = getSendMessageMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.SendMessageRequest, unhinged.chat.SendMessageResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "SendMessage"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.SendMessageRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.SendMessageResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("SendMessage"))
              .build();
        }
      }
    }
    return getSendMessageMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.GetMessagesRequest,
      unhinged.chat.GetMessagesResponse> getGetMessagesMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetMessages",
      requestType = unhinged.chat.GetMessagesRequest.class,
      responseType = unhinged.chat.GetMessagesResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.GetMessagesRequest,
      unhinged.chat.GetMessagesResponse> getGetMessagesMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.GetMessagesRequest, unhinged.chat.GetMessagesResponse> getGetMessagesMethod;
    if ((getGetMessagesMethod = ChatServiceGrpc.getGetMessagesMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getGetMessagesMethod = ChatServiceGrpc.getGetMessagesMethod) == null) {
          ChatServiceGrpc.getGetMessagesMethod = getGetMessagesMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.GetMessagesRequest, unhinged.chat.GetMessagesResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetMessages"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.GetMessagesRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.GetMessagesResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("GetMessages"))
              .build();
        }
      }
    }
    return getGetMessagesMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.UpdateMessageRequest,
      unhinged.chat.UpdateMessageResponse> getUpdateMessageMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "UpdateMessage",
      requestType = unhinged.chat.UpdateMessageRequest.class,
      responseType = unhinged.chat.UpdateMessageResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.UpdateMessageRequest,
      unhinged.chat.UpdateMessageResponse> getUpdateMessageMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.UpdateMessageRequest, unhinged.chat.UpdateMessageResponse> getUpdateMessageMethod;
    if ((getUpdateMessageMethod = ChatServiceGrpc.getUpdateMessageMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getUpdateMessageMethod = ChatServiceGrpc.getUpdateMessageMethod) == null) {
          ChatServiceGrpc.getUpdateMessageMethod = getUpdateMessageMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.UpdateMessageRequest, unhinged.chat.UpdateMessageResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "UpdateMessage"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.UpdateMessageRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.UpdateMessageResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("UpdateMessage"))
              .build();
        }
      }
    }
    return getUpdateMessageMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.DeleteMessageRequest,
      unhinged.chat.DeleteMessageResponse> getDeleteMessageMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "DeleteMessage",
      requestType = unhinged.chat.DeleteMessageRequest.class,
      responseType = unhinged.chat.DeleteMessageResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.chat.DeleteMessageRequest,
      unhinged.chat.DeleteMessageResponse> getDeleteMessageMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.DeleteMessageRequest, unhinged.chat.DeleteMessageResponse> getDeleteMessageMethod;
    if ((getDeleteMessageMethod = ChatServiceGrpc.getDeleteMessageMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getDeleteMessageMethod = ChatServiceGrpc.getDeleteMessageMethod) == null) {
          ChatServiceGrpc.getDeleteMessageMethod = getDeleteMessageMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.DeleteMessageRequest, unhinged.chat.DeleteMessageResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "DeleteMessage"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.DeleteMessageRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.DeleteMessageResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("DeleteMessage"))
              .build();
        }
      }
    }
    return getDeleteMessageMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.StreamChatRequest,
      unhinged.common.StreamChunk> getStreamChatMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "StreamChat",
      requestType = unhinged.chat.StreamChatRequest.class,
      responseType = unhinged.common.StreamChunk.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.chat.StreamChatRequest,
      unhinged.common.StreamChunk> getStreamChatMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.StreamChatRequest, unhinged.common.StreamChunk> getStreamChatMethod;
    if ((getStreamChatMethod = ChatServiceGrpc.getStreamChatMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getStreamChatMethod = ChatServiceGrpc.getStreamChatMethod) == null) {
          ChatServiceGrpc.getStreamChatMethod = getStreamChatMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.StreamChatRequest, unhinged.common.StreamChunk>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "StreamChat"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.StreamChatRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.StreamChunk.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("StreamChat"))
              .build();
        }
      }
    }
    return getStreamChatMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.chat.SubscribeRequest,
      unhinged.common.StreamChunk> getSubscribeToConversationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "SubscribeToConversation",
      requestType = unhinged.chat.SubscribeRequest.class,
      responseType = unhinged.common.StreamChunk.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.chat.SubscribeRequest,
      unhinged.common.StreamChunk> getSubscribeToConversationMethod() {
    io.grpc.MethodDescriptor<unhinged.chat.SubscribeRequest, unhinged.common.StreamChunk> getSubscribeToConversationMethod;
    if ((getSubscribeToConversationMethod = ChatServiceGrpc.getSubscribeToConversationMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getSubscribeToConversationMethod = ChatServiceGrpc.getSubscribeToConversationMethod) == null) {
          ChatServiceGrpc.getSubscribeToConversationMethod = getSubscribeToConversationMethod =
              io.grpc.MethodDescriptor.<unhinged.chat.SubscribeRequest, unhinged.common.StreamChunk>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "SubscribeToConversation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.chat.SubscribeRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.StreamChunk.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("SubscribeToConversation"))
              .build();
        }
      }
    }
    return getSubscribeToConversationMethod;
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
    if ((getHealthCheckMethod = ChatServiceGrpc.getHealthCheckMethod) == null) {
      synchronized (ChatServiceGrpc.class) {
        if ((getHealthCheckMethod = ChatServiceGrpc.getHealthCheckMethod) == null) {
          ChatServiceGrpc.getHealthCheckMethod = getHealthCheckMethod =
              io.grpc.MethodDescriptor.<unhinged.common.HealthCheckRequest, unhinged.common.HealthCheckResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "HealthCheck"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.HealthCheckRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.HealthCheckResponse.getDefaultInstance()))
              .setSchemaDescriptor(new ChatServiceMethodDescriptorSupplier("HealthCheck"))
              .build();
        }
      }
    }
    return getHealthCheckMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static ChatServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ChatServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ChatServiceStub>() {
        @java.lang.Override
        public ChatServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ChatServiceStub(channel, callOptions);
        }
      };
    return ChatServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static ChatServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ChatServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ChatServiceBlockingStub>() {
        @java.lang.Override
        public ChatServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ChatServiceBlockingStub(channel, callOptions);
        }
      };
    return ChatServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static ChatServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<ChatServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<ChatServiceFutureStub>() {
        @java.lang.Override
        public ChatServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new ChatServiceFutureStub(channel, callOptions);
        }
      };
    return ChatServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   **
   * Chat service for conversation and message management
   * 
   * Uses common patterns for consistent API behavior across services
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * Conversation management
     * </pre>
     */
    default void createConversation(unhinged.chat.CreateConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.CreateConversationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getCreateConversationMethod(), responseObserver);
    }

    /**
     */
    default void getConversation(unhinged.chat.GetConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.GetConversationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetConversationMethod(), responseObserver);
    }

    /**
     */
    default void listConversations(unhinged.chat.ListConversationsRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.ListConversationsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListConversationsMethod(), responseObserver);
    }

    /**
     */
    default void updateConversation(unhinged.chat.UpdateConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.UpdateConversationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getUpdateConversationMethod(), responseObserver);
    }

    /**
     */
    default void deleteConversation(unhinged.chat.DeleteConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.DeleteConversationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDeleteConversationMethod(), responseObserver);
    }

    /**
     * <pre>
     * Message management
     * </pre>
     */
    default void sendMessage(unhinged.chat.SendMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.SendMessageResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSendMessageMethod(), responseObserver);
    }

    /**
     */
    default void getMessages(unhinged.chat.GetMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.GetMessagesResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetMessagesMethod(), responseObserver);
    }

    /**
     */
    default void updateMessage(unhinged.chat.UpdateMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.UpdateMessageResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getUpdateMessageMethod(), responseObserver);
    }

    /**
     */
    default void deleteMessage(unhinged.chat.DeleteMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.DeleteMessageResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDeleteMessageMethod(), responseObserver);
    }

    /**
     * <pre>
     * Real-time streaming (uses common StreamChunk pattern)
     * </pre>
     */
    default void streamChat(unhinged.chat.StreamChatRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getStreamChatMethod(), responseObserver);
    }

    /**
     */
    default void subscribeToConversation(unhinged.chat.SubscribeRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSubscribeToConversationMethod(), responseObserver);
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
   * Base class for the server implementation of the service ChatService.
   * <pre>
   **
   * Chat service for conversation and message management
   * 
   * Uses common patterns for consistent API behavior across services
   * </pre>
   */
  public static abstract class ChatServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return ChatServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service ChatService.
   * <pre>
   **
   * Chat service for conversation and message management
   * 
   * Uses common patterns for consistent API behavior across services
   * </pre>
   */
  public static final class ChatServiceStub
      extends io.grpc.stub.AbstractAsyncStub<ChatServiceStub> {
    private ChatServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ChatServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ChatServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Conversation management
     * </pre>
     */
    public void createConversation(unhinged.chat.CreateConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.CreateConversationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getCreateConversationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getConversation(unhinged.chat.GetConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.GetConversationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetConversationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listConversations(unhinged.chat.ListConversationsRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.ListConversationsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListConversationsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateConversation(unhinged.chat.UpdateConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.UpdateConversationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getUpdateConversationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteConversation(unhinged.chat.DeleteConversationRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.DeleteConversationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getDeleteConversationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Message management
     * </pre>
     */
    public void sendMessage(unhinged.chat.SendMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.SendMessageResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getSendMessageMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getMessages(unhinged.chat.GetMessagesRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.GetMessagesResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetMessagesMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateMessage(unhinged.chat.UpdateMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.UpdateMessageResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getUpdateMessageMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteMessage(unhinged.chat.DeleteMessageRequest request,
        io.grpc.stub.StreamObserver<unhinged.chat.DeleteMessageResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getDeleteMessageMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Real-time streaming (uses common StreamChunk pattern)
     * </pre>
     */
    public void streamChat(unhinged.chat.StreamChatRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getStreamChatMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void subscribeToConversation(unhinged.chat.SubscribeRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getSubscribeToConversationMethod(), getCallOptions()), request, responseObserver);
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
   * A stub to allow clients to do synchronous rpc calls to service ChatService.
   * <pre>
   **
   * Chat service for conversation and message management
   * 
   * Uses common patterns for consistent API behavior across services
   * </pre>
   */
  public static final class ChatServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<ChatServiceBlockingStub> {
    private ChatServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ChatServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ChatServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Conversation management
     * </pre>
     */
    public unhinged.chat.CreateConversationResponse createConversation(unhinged.chat.CreateConversationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getCreateConversationMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.chat.GetConversationResponse getConversation(unhinged.chat.GetConversationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetConversationMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.chat.ListConversationsResponse listConversations(unhinged.chat.ListConversationsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListConversationsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.chat.UpdateConversationResponse updateConversation(unhinged.chat.UpdateConversationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getUpdateConversationMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.chat.DeleteConversationResponse deleteConversation(unhinged.chat.DeleteConversationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getDeleteConversationMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Message management
     * </pre>
     */
    public unhinged.chat.SendMessageResponse sendMessage(unhinged.chat.SendMessageRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getSendMessageMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.chat.GetMessagesResponse getMessages(unhinged.chat.GetMessagesRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetMessagesMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.chat.UpdateMessageResponse updateMessage(unhinged.chat.UpdateMessageRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getUpdateMessageMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.chat.DeleteMessageResponse deleteMessage(unhinged.chat.DeleteMessageRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getDeleteMessageMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Real-time streaming (uses common StreamChunk pattern)
     * </pre>
     */
    public java.util.Iterator<unhinged.common.StreamChunk> streamChat(
        unhinged.chat.StreamChatRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getStreamChatMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<unhinged.common.StreamChunk> subscribeToConversation(
        unhinged.chat.SubscribeRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getSubscribeToConversationMethod(), getCallOptions(), request);
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
   * A stub to allow clients to do ListenableFuture-style rpc calls to service ChatService.
   * <pre>
   **
   * Chat service for conversation and message management
   * 
   * Uses common patterns for consistent API behavior across services
   * </pre>
   */
  public static final class ChatServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<ChatServiceFutureStub> {
    private ChatServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected ChatServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new ChatServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Conversation management
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.CreateConversationResponse> createConversation(
        unhinged.chat.CreateConversationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getCreateConversationMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.GetConversationResponse> getConversation(
        unhinged.chat.GetConversationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetConversationMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.ListConversationsResponse> listConversations(
        unhinged.chat.ListConversationsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListConversationsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.UpdateConversationResponse> updateConversation(
        unhinged.chat.UpdateConversationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getUpdateConversationMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.DeleteConversationResponse> deleteConversation(
        unhinged.chat.DeleteConversationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getDeleteConversationMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Message management
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.SendMessageResponse> sendMessage(
        unhinged.chat.SendMessageRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getSendMessageMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.GetMessagesResponse> getMessages(
        unhinged.chat.GetMessagesRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetMessagesMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.UpdateMessageResponse> updateMessage(
        unhinged.chat.UpdateMessageRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getUpdateMessageMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.chat.DeleteMessageResponse> deleteMessage(
        unhinged.chat.DeleteMessageRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getDeleteMessageMethod(), getCallOptions()), request);
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

  private static final int METHODID_CREATE_CONVERSATION = 0;
  private static final int METHODID_GET_CONVERSATION = 1;
  private static final int METHODID_LIST_CONVERSATIONS = 2;
  private static final int METHODID_UPDATE_CONVERSATION = 3;
  private static final int METHODID_DELETE_CONVERSATION = 4;
  private static final int METHODID_SEND_MESSAGE = 5;
  private static final int METHODID_GET_MESSAGES = 6;
  private static final int METHODID_UPDATE_MESSAGE = 7;
  private static final int METHODID_DELETE_MESSAGE = 8;
  private static final int METHODID_STREAM_CHAT = 9;
  private static final int METHODID_SUBSCRIBE_TO_CONVERSATION = 10;
  private static final int METHODID_HEALTH_CHECK = 11;

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
        case METHODID_CREATE_CONVERSATION:
          serviceImpl.createConversation((unhinged.chat.CreateConversationRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.CreateConversationResponse>) responseObserver);
          break;
        case METHODID_GET_CONVERSATION:
          serviceImpl.getConversation((unhinged.chat.GetConversationRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.GetConversationResponse>) responseObserver);
          break;
        case METHODID_LIST_CONVERSATIONS:
          serviceImpl.listConversations((unhinged.chat.ListConversationsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.ListConversationsResponse>) responseObserver);
          break;
        case METHODID_UPDATE_CONVERSATION:
          serviceImpl.updateConversation((unhinged.chat.UpdateConversationRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.UpdateConversationResponse>) responseObserver);
          break;
        case METHODID_DELETE_CONVERSATION:
          serviceImpl.deleteConversation((unhinged.chat.DeleteConversationRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.DeleteConversationResponse>) responseObserver);
          break;
        case METHODID_SEND_MESSAGE:
          serviceImpl.sendMessage((unhinged.chat.SendMessageRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.SendMessageResponse>) responseObserver);
          break;
        case METHODID_GET_MESSAGES:
          serviceImpl.getMessages((unhinged.chat.GetMessagesRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.GetMessagesResponse>) responseObserver);
          break;
        case METHODID_UPDATE_MESSAGE:
          serviceImpl.updateMessage((unhinged.chat.UpdateMessageRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.UpdateMessageResponse>) responseObserver);
          break;
        case METHODID_DELETE_MESSAGE:
          serviceImpl.deleteMessage((unhinged.chat.DeleteMessageRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.chat.DeleteMessageResponse>) responseObserver);
          break;
        case METHODID_STREAM_CHAT:
          serviceImpl.streamChat((unhinged.chat.StreamChatRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.common.StreamChunk>) responseObserver);
          break;
        case METHODID_SUBSCRIBE_TO_CONVERSATION:
          serviceImpl.subscribeToConversation((unhinged.chat.SubscribeRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.common.StreamChunk>) responseObserver);
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
          getCreateConversationMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.CreateConversationRequest,
              unhinged.chat.CreateConversationResponse>(
                service, METHODID_CREATE_CONVERSATION)))
        .addMethod(
          getGetConversationMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.GetConversationRequest,
              unhinged.chat.GetConversationResponse>(
                service, METHODID_GET_CONVERSATION)))
        .addMethod(
          getListConversationsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.ListConversationsRequest,
              unhinged.chat.ListConversationsResponse>(
                service, METHODID_LIST_CONVERSATIONS)))
        .addMethod(
          getUpdateConversationMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.UpdateConversationRequest,
              unhinged.chat.UpdateConversationResponse>(
                service, METHODID_UPDATE_CONVERSATION)))
        .addMethod(
          getDeleteConversationMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.DeleteConversationRequest,
              unhinged.chat.DeleteConversationResponse>(
                service, METHODID_DELETE_CONVERSATION)))
        .addMethod(
          getSendMessageMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.SendMessageRequest,
              unhinged.chat.SendMessageResponse>(
                service, METHODID_SEND_MESSAGE)))
        .addMethod(
          getGetMessagesMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.GetMessagesRequest,
              unhinged.chat.GetMessagesResponse>(
                service, METHODID_GET_MESSAGES)))
        .addMethod(
          getUpdateMessageMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.UpdateMessageRequest,
              unhinged.chat.UpdateMessageResponse>(
                service, METHODID_UPDATE_MESSAGE)))
        .addMethod(
          getDeleteMessageMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.chat.DeleteMessageRequest,
              unhinged.chat.DeleteMessageResponse>(
                service, METHODID_DELETE_MESSAGE)))
        .addMethod(
          getStreamChatMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              unhinged.chat.StreamChatRequest,
              unhinged.common.StreamChunk>(
                service, METHODID_STREAM_CHAT)))
        .addMethod(
          getSubscribeToConversationMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              unhinged.chat.SubscribeRequest,
              unhinged.common.StreamChunk>(
                service, METHODID_SUBSCRIBE_TO_CONVERSATION)))
        .addMethod(
          getHealthCheckMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.common.HealthCheckRequest,
              unhinged.common.HealthCheckResponse>(
                service, METHODID_HEALTH_CHECK)))
        .build();
  }

  private static abstract class ChatServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    ChatServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return unhinged.chat.ChatProto.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("ChatService");
    }
  }

  private static final class ChatServiceFileDescriptorSupplier
      extends ChatServiceBaseDescriptorSupplier {
    ChatServiceFileDescriptorSupplier() {}
  }

  private static final class ChatServiceMethodDescriptorSupplier
      extends ChatServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    ChatServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (ChatServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new ChatServiceFileDescriptorSupplier())
              .addMethod(getCreateConversationMethod())
              .addMethod(getGetConversationMethod())
              .addMethod(getListConversationsMethod())
              .addMethod(getUpdateConversationMethod())
              .addMethod(getDeleteConversationMethod())
              .addMethod(getSendMessageMethod())
              .addMethod(getGetMessagesMethod())
              .addMethod(getUpdateMessageMethod())
              .addMethod(getDeleteMessageMethod())
              .addMethod(getStreamChatMethod())
              .addMethod(getSubscribeToConversationMethod())
              .addMethod(getHealthCheckMethod())
              .build();
        }
      }
    }
    return result;
  }
}
