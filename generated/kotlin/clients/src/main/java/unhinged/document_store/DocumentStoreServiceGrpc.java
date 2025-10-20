package unhinged.document_store;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 * Service definition
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: document_store.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class DocumentStoreServiceGrpc {

  private DocumentStoreServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "unhinged.document_store.DocumentStoreService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.PutDocumentRequest,
      unhinged.document_store.DocumentStore.PutDocumentResponse> getPutDocumentMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "PutDocument",
      requestType = unhinged.document_store.DocumentStore.PutDocumentRequest.class,
      responseType = unhinged.document_store.DocumentStore.PutDocumentResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.PutDocumentRequest,
      unhinged.document_store.DocumentStore.PutDocumentResponse> getPutDocumentMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.PutDocumentRequest, unhinged.document_store.DocumentStore.PutDocumentResponse> getPutDocumentMethod;
    if ((getPutDocumentMethod = DocumentStoreServiceGrpc.getPutDocumentMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getPutDocumentMethod = DocumentStoreServiceGrpc.getPutDocumentMethod) == null) {
          DocumentStoreServiceGrpc.getPutDocumentMethod = getPutDocumentMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.PutDocumentRequest, unhinged.document_store.DocumentStore.PutDocumentResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "PutDocument"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.PutDocumentRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.PutDocumentResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("PutDocument"))
              .build();
        }
      }
    }
    return getPutDocumentMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.PutDocumentsRequest,
      unhinged.document_store.DocumentStore.PutDocumentsResponse> getPutDocumentsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "PutDocuments",
      requestType = unhinged.document_store.DocumentStore.PutDocumentsRequest.class,
      responseType = unhinged.document_store.DocumentStore.PutDocumentsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.PutDocumentsRequest,
      unhinged.document_store.DocumentStore.PutDocumentsResponse> getPutDocumentsMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.PutDocumentsRequest, unhinged.document_store.DocumentStore.PutDocumentsResponse> getPutDocumentsMethod;
    if ((getPutDocumentsMethod = DocumentStoreServiceGrpc.getPutDocumentsMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getPutDocumentsMethod = DocumentStoreServiceGrpc.getPutDocumentsMethod) == null) {
          DocumentStoreServiceGrpc.getPutDocumentsMethod = getPutDocumentsMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.PutDocumentsRequest, unhinged.document_store.DocumentStore.PutDocumentsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "PutDocuments"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.PutDocumentsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.PutDocumentsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("PutDocuments"))
              .build();
        }
      }
    }
    return getPutDocumentsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.GetDocumentRequest,
      unhinged.document_store.DocumentStore.GetDocumentResponse> getGetDocumentMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetDocument",
      requestType = unhinged.document_store.DocumentStore.GetDocumentRequest.class,
      responseType = unhinged.document_store.DocumentStore.GetDocumentResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.GetDocumentRequest,
      unhinged.document_store.DocumentStore.GetDocumentResponse> getGetDocumentMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.GetDocumentRequest, unhinged.document_store.DocumentStore.GetDocumentResponse> getGetDocumentMethod;
    if ((getGetDocumentMethod = DocumentStoreServiceGrpc.getGetDocumentMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getGetDocumentMethod = DocumentStoreServiceGrpc.getGetDocumentMethod) == null) {
          DocumentStoreServiceGrpc.getGetDocumentMethod = getGetDocumentMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.GetDocumentRequest, unhinged.document_store.DocumentStore.GetDocumentResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetDocument"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.GetDocumentRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.GetDocumentResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("GetDocument"))
              .build();
        }
      }
    }
    return getGetDocumentMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListDocumentsRequest,
      unhinged.document_store.DocumentStore.ListDocumentsResponse> getListDocumentsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListDocuments",
      requestType = unhinged.document_store.DocumentStore.ListDocumentsRequest.class,
      responseType = unhinged.document_store.DocumentStore.ListDocumentsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListDocumentsRequest,
      unhinged.document_store.DocumentStore.ListDocumentsResponse> getListDocumentsMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListDocumentsRequest, unhinged.document_store.DocumentStore.ListDocumentsResponse> getListDocumentsMethod;
    if ((getListDocumentsMethod = DocumentStoreServiceGrpc.getListDocumentsMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getListDocumentsMethod = DocumentStoreServiceGrpc.getListDocumentsMethod) == null) {
          DocumentStoreServiceGrpc.getListDocumentsMethod = getListDocumentsMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.ListDocumentsRequest, unhinged.document_store.DocumentStore.ListDocumentsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListDocuments"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListDocumentsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListDocumentsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("ListDocuments"))
              .build();
        }
      }
    }
    return getListDocumentsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListDocumentVersionsRequest,
      unhinged.document_store.DocumentStore.ListDocumentVersionsResponse> getListDocumentVersionsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListDocumentVersions",
      requestType = unhinged.document_store.DocumentStore.ListDocumentVersionsRequest.class,
      responseType = unhinged.document_store.DocumentStore.ListDocumentVersionsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListDocumentVersionsRequest,
      unhinged.document_store.DocumentStore.ListDocumentVersionsResponse> getListDocumentVersionsMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListDocumentVersionsRequest, unhinged.document_store.DocumentStore.ListDocumentVersionsResponse> getListDocumentVersionsMethod;
    if ((getListDocumentVersionsMethod = DocumentStoreServiceGrpc.getListDocumentVersionsMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getListDocumentVersionsMethod = DocumentStoreServiceGrpc.getListDocumentVersionsMethod) == null) {
          DocumentStoreServiceGrpc.getListDocumentVersionsMethod = getListDocumentVersionsMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.ListDocumentVersionsRequest, unhinged.document_store.DocumentStore.ListDocumentVersionsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListDocumentVersions"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListDocumentVersionsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListDocumentVersionsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("ListDocumentVersions"))
              .build();
        }
      }
    }
    return getListDocumentVersionsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.DeleteDocumentRequest,
      unhinged.document_store.DocumentStore.DeleteDocumentResponse> getDeleteDocumentMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "DeleteDocument",
      requestType = unhinged.document_store.DocumentStore.DeleteDocumentRequest.class,
      responseType = unhinged.document_store.DocumentStore.DeleteDocumentResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.DeleteDocumentRequest,
      unhinged.document_store.DocumentStore.DeleteDocumentResponse> getDeleteDocumentMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.DeleteDocumentRequest, unhinged.document_store.DocumentStore.DeleteDocumentResponse> getDeleteDocumentMethod;
    if ((getDeleteDocumentMethod = DocumentStoreServiceGrpc.getDeleteDocumentMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getDeleteDocumentMethod = DocumentStoreServiceGrpc.getDeleteDocumentMethod) == null) {
          DocumentStoreServiceGrpc.getDeleteDocumentMethod = getDeleteDocumentMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.DeleteDocumentRequest, unhinged.document_store.DocumentStore.DeleteDocumentResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "DeleteDocument"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.DeleteDocumentRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.DeleteDocumentResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("DeleteDocument"))
              .build();
        }
      }
    }
    return getDeleteDocumentMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.TagDocumentRequest,
      unhinged.document_store.DocumentStore.TagDocumentResponse> getTagDocumentMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "TagDocument",
      requestType = unhinged.document_store.DocumentStore.TagDocumentRequest.class,
      responseType = unhinged.document_store.DocumentStore.TagDocumentResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.TagDocumentRequest,
      unhinged.document_store.DocumentStore.TagDocumentResponse> getTagDocumentMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.TagDocumentRequest, unhinged.document_store.DocumentStore.TagDocumentResponse> getTagDocumentMethod;
    if ((getTagDocumentMethod = DocumentStoreServiceGrpc.getTagDocumentMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getTagDocumentMethod = DocumentStoreServiceGrpc.getTagDocumentMethod) == null) {
          DocumentStoreServiceGrpc.getTagDocumentMethod = getTagDocumentMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.TagDocumentRequest, unhinged.document_store.DocumentStore.TagDocumentResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "TagDocument"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.TagDocumentRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.TagDocumentResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("TagDocument"))
              .build();
        }
      }
    }
    return getTagDocumentMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListActiveTagsRequest,
      unhinged.document_store.DocumentStore.ListActiveTagsResponse> getListActiveTagsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListActiveTags",
      requestType = unhinged.document_store.DocumentStore.ListActiveTagsRequest.class,
      responseType = unhinged.document_store.DocumentStore.ListActiveTagsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListActiveTagsRequest,
      unhinged.document_store.DocumentStore.ListActiveTagsResponse> getListActiveTagsMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListActiveTagsRequest, unhinged.document_store.DocumentStore.ListActiveTagsResponse> getListActiveTagsMethod;
    if ((getListActiveTagsMethod = DocumentStoreServiceGrpc.getListActiveTagsMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getListActiveTagsMethod = DocumentStoreServiceGrpc.getListActiveTagsMethod) == null) {
          DocumentStoreServiceGrpc.getListActiveTagsMethod = getListActiveTagsMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.ListActiveTagsRequest, unhinged.document_store.DocumentStore.ListActiveTagsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListActiveTags"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListActiveTagsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListActiveTagsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("ListActiveTags"))
              .build();
        }
      }
    }
    return getListActiveTagsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListTagEventsRequest,
      unhinged.document_store.DocumentStore.ListTagEventsResponse> getListTagEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListTagEvents",
      requestType = unhinged.document_store.DocumentStore.ListTagEventsRequest.class,
      responseType = unhinged.document_store.DocumentStore.ListTagEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListTagEventsRequest,
      unhinged.document_store.DocumentStore.ListTagEventsResponse> getListTagEventsMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.ListTagEventsRequest, unhinged.document_store.DocumentStore.ListTagEventsResponse> getListTagEventsMethod;
    if ((getListTagEventsMethod = DocumentStoreServiceGrpc.getListTagEventsMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getListTagEventsMethod = DocumentStoreServiceGrpc.getListTagEventsMethod) == null) {
          DocumentStoreServiceGrpc.getListTagEventsMethod = getListTagEventsMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.ListTagEventsRequest, unhinged.document_store.DocumentStore.ListTagEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListTagEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListTagEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.ListTagEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("ListTagEvents"))
              .build();
        }
      }
    }
    return getListTagEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.GetSessionContextRequest,
      unhinged.document_store.DocumentStore.GetSessionContextResponse> getGetSessionContextMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetSessionContext",
      requestType = unhinged.document_store.DocumentStore.GetSessionContextRequest.class,
      responseType = unhinged.document_store.DocumentStore.GetSessionContextResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.GetSessionContextRequest,
      unhinged.document_store.DocumentStore.GetSessionContextResponse> getGetSessionContextMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.GetSessionContextRequest, unhinged.document_store.DocumentStore.GetSessionContextResponse> getGetSessionContextMethod;
    if ((getGetSessionContextMethod = DocumentStoreServiceGrpc.getGetSessionContextMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getGetSessionContextMethod = DocumentStoreServiceGrpc.getGetSessionContextMethod) == null) {
          DocumentStoreServiceGrpc.getGetSessionContextMethod = getGetSessionContextMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.GetSessionContextRequest, unhinged.document_store.DocumentStore.GetSessionContextResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetSessionContext"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.GetSessionContextRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.GetSessionContextResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("GetSessionContext"))
              .build();
        }
      }
    }
    return getGetSessionContextMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.HealthCheckRequest,
      unhinged.document_store.DocumentStore.HealthCheckResponse> getHealthCheckMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "HealthCheck",
      requestType = unhinged.document_store.DocumentStore.HealthCheckRequest.class,
      responseType = unhinged.document_store.DocumentStore.HealthCheckResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.HealthCheckRequest,
      unhinged.document_store.DocumentStore.HealthCheckResponse> getHealthCheckMethod() {
    io.grpc.MethodDescriptor<unhinged.document_store.DocumentStore.HealthCheckRequest, unhinged.document_store.DocumentStore.HealthCheckResponse> getHealthCheckMethod;
    if ((getHealthCheckMethod = DocumentStoreServiceGrpc.getHealthCheckMethod) == null) {
      synchronized (DocumentStoreServiceGrpc.class) {
        if ((getHealthCheckMethod = DocumentStoreServiceGrpc.getHealthCheckMethod) == null) {
          DocumentStoreServiceGrpc.getHealthCheckMethod = getHealthCheckMethod =
              io.grpc.MethodDescriptor.<unhinged.document_store.DocumentStore.HealthCheckRequest, unhinged.document_store.DocumentStore.HealthCheckResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "HealthCheck"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.HealthCheckRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.document_store.DocumentStore.HealthCheckResponse.getDefaultInstance()))
              .setSchemaDescriptor(new DocumentStoreServiceMethodDescriptorSupplier("HealthCheck"))
              .build();
        }
      }
    }
    return getHealthCheckMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static DocumentStoreServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<DocumentStoreServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<DocumentStoreServiceStub>() {
        @java.lang.Override
        public DocumentStoreServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new DocumentStoreServiceStub(channel, callOptions);
        }
      };
    return DocumentStoreServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static DocumentStoreServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<DocumentStoreServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<DocumentStoreServiceBlockingStub>() {
        @java.lang.Override
        public DocumentStoreServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new DocumentStoreServiceBlockingStub(channel, callOptions);
        }
      };
    return DocumentStoreServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static DocumentStoreServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<DocumentStoreServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<DocumentStoreServiceFutureStub>() {
        @java.lang.Override
        public DocumentStoreServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new DocumentStoreServiceFutureStub(channel, callOptions);
        }
      };
    return DocumentStoreServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * Service definition
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * Document CRUD operations
     * </pre>
     */
    default void putDocument(unhinged.document_store.DocumentStore.PutDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.PutDocumentResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getPutDocumentMethod(), responseObserver);
    }

    /**
     */
    default void putDocuments(unhinged.document_store.DocumentStore.PutDocumentsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.PutDocumentsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getPutDocumentsMethod(), responseObserver);
    }

    /**
     */
    default void getDocument(unhinged.document_store.DocumentStore.GetDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.GetDocumentResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetDocumentMethod(), responseObserver);
    }

    /**
     */
    default void listDocuments(unhinged.document_store.DocumentStore.ListDocumentsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListDocumentsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListDocumentsMethod(), responseObserver);
    }

    /**
     */
    default void listDocumentVersions(unhinged.document_store.DocumentStore.ListDocumentVersionsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListDocumentVersionsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListDocumentVersionsMethod(), responseObserver);
    }

    /**
     */
    default void deleteDocument(unhinged.document_store.DocumentStore.DeleteDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.DeleteDocumentResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDeleteDocumentMethod(), responseObserver);
    }

    /**
     * <pre>
     * Tag operations
     * </pre>
     */
    default void tagDocument(unhinged.document_store.DocumentStore.TagDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.TagDocumentResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getTagDocumentMethod(), responseObserver);
    }

    /**
     */
    default void listActiveTags(unhinged.document_store.DocumentStore.ListActiveTagsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListActiveTagsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListActiveTagsMethod(), responseObserver);
    }

    /**
     */
    default void listTagEvents(unhinged.document_store.DocumentStore.ListTagEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListTagEventsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListTagEventsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Session context
     * </pre>
     */
    default void getSessionContext(unhinged.document_store.DocumentStore.GetSessionContextRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.GetSessionContextResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetSessionContextMethod(), responseObserver);
    }

    /**
     * <pre>
     * Health check
     * </pre>
     */
    default void healthCheck(unhinged.document_store.DocumentStore.HealthCheckRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.HealthCheckResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getHealthCheckMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service DocumentStoreService.
   * <pre>
   * Service definition
   * </pre>
   */
  public static abstract class DocumentStoreServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return DocumentStoreServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service DocumentStoreService.
   * <pre>
   * Service definition
   * </pre>
   */
  public static final class DocumentStoreServiceStub
      extends io.grpc.stub.AbstractAsyncStub<DocumentStoreServiceStub> {
    private DocumentStoreServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected DocumentStoreServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new DocumentStoreServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Document CRUD operations
     * </pre>
     */
    public void putDocument(unhinged.document_store.DocumentStore.PutDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.PutDocumentResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getPutDocumentMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void putDocuments(unhinged.document_store.DocumentStore.PutDocumentsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.PutDocumentsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getPutDocumentsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getDocument(unhinged.document_store.DocumentStore.GetDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.GetDocumentResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetDocumentMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listDocuments(unhinged.document_store.DocumentStore.ListDocumentsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListDocumentsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListDocumentsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listDocumentVersions(unhinged.document_store.DocumentStore.ListDocumentVersionsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListDocumentVersionsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListDocumentVersionsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteDocument(unhinged.document_store.DocumentStore.DeleteDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.DeleteDocumentResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getDeleteDocumentMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Tag operations
     * </pre>
     */
    public void tagDocument(unhinged.document_store.DocumentStore.TagDocumentRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.TagDocumentResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getTagDocumentMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listActiveTags(unhinged.document_store.DocumentStore.ListActiveTagsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListActiveTagsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListActiveTagsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void listTagEvents(unhinged.document_store.DocumentStore.ListTagEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListTagEventsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListTagEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Session context
     * </pre>
     */
    public void getSessionContext(unhinged.document_store.DocumentStore.GetSessionContextRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.GetSessionContextResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetSessionContextMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Health check
     * </pre>
     */
    public void healthCheck(unhinged.document_store.DocumentStore.HealthCheckRequest request,
        io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.HealthCheckResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getHealthCheckMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service DocumentStoreService.
   * <pre>
   * Service definition
   * </pre>
   */
  public static final class DocumentStoreServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<DocumentStoreServiceBlockingStub> {
    private DocumentStoreServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected DocumentStoreServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new DocumentStoreServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Document CRUD operations
     * </pre>
     */
    public unhinged.document_store.DocumentStore.PutDocumentResponse putDocument(unhinged.document_store.DocumentStore.PutDocumentRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getPutDocumentMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.document_store.DocumentStore.PutDocumentsResponse putDocuments(unhinged.document_store.DocumentStore.PutDocumentsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getPutDocumentsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.document_store.DocumentStore.GetDocumentResponse getDocument(unhinged.document_store.DocumentStore.GetDocumentRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetDocumentMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.document_store.DocumentStore.ListDocumentsResponse listDocuments(unhinged.document_store.DocumentStore.ListDocumentsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListDocumentsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.document_store.DocumentStore.ListDocumentVersionsResponse listDocumentVersions(unhinged.document_store.DocumentStore.ListDocumentVersionsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListDocumentVersionsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.document_store.DocumentStore.DeleteDocumentResponse deleteDocument(unhinged.document_store.DocumentStore.DeleteDocumentRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getDeleteDocumentMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Tag operations
     * </pre>
     */
    public unhinged.document_store.DocumentStore.TagDocumentResponse tagDocument(unhinged.document_store.DocumentStore.TagDocumentRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getTagDocumentMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.document_store.DocumentStore.ListActiveTagsResponse listActiveTags(unhinged.document_store.DocumentStore.ListActiveTagsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListActiveTagsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.document_store.DocumentStore.ListTagEventsResponse listTagEvents(unhinged.document_store.DocumentStore.ListTagEventsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListTagEventsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Session context
     * </pre>
     */
    public unhinged.document_store.DocumentStore.GetSessionContextResponse getSessionContext(unhinged.document_store.DocumentStore.GetSessionContextRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetSessionContextMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Health check
     * </pre>
     */
    public unhinged.document_store.DocumentStore.HealthCheckResponse healthCheck(unhinged.document_store.DocumentStore.HealthCheckRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getHealthCheckMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service DocumentStoreService.
   * <pre>
   * Service definition
   * </pre>
   */
  public static final class DocumentStoreServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<DocumentStoreServiceFutureStub> {
    private DocumentStoreServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected DocumentStoreServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new DocumentStoreServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Document CRUD operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.PutDocumentResponse> putDocument(
        unhinged.document_store.DocumentStore.PutDocumentRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getPutDocumentMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.PutDocumentsResponse> putDocuments(
        unhinged.document_store.DocumentStore.PutDocumentsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getPutDocumentsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.GetDocumentResponse> getDocument(
        unhinged.document_store.DocumentStore.GetDocumentRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetDocumentMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.ListDocumentsResponse> listDocuments(
        unhinged.document_store.DocumentStore.ListDocumentsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListDocumentsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.ListDocumentVersionsResponse> listDocumentVersions(
        unhinged.document_store.DocumentStore.ListDocumentVersionsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListDocumentVersionsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.DeleteDocumentResponse> deleteDocument(
        unhinged.document_store.DocumentStore.DeleteDocumentRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getDeleteDocumentMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Tag operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.TagDocumentResponse> tagDocument(
        unhinged.document_store.DocumentStore.TagDocumentRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getTagDocumentMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.ListActiveTagsResponse> listActiveTags(
        unhinged.document_store.DocumentStore.ListActiveTagsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListActiveTagsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.ListTagEventsResponse> listTagEvents(
        unhinged.document_store.DocumentStore.ListTagEventsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListTagEventsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Session context
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.GetSessionContextResponse> getSessionContext(
        unhinged.document_store.DocumentStore.GetSessionContextRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetSessionContextMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Health check
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.document_store.DocumentStore.HealthCheckResponse> healthCheck(
        unhinged.document_store.DocumentStore.HealthCheckRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getHealthCheckMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_PUT_DOCUMENT = 0;
  private static final int METHODID_PUT_DOCUMENTS = 1;
  private static final int METHODID_GET_DOCUMENT = 2;
  private static final int METHODID_LIST_DOCUMENTS = 3;
  private static final int METHODID_LIST_DOCUMENT_VERSIONS = 4;
  private static final int METHODID_DELETE_DOCUMENT = 5;
  private static final int METHODID_TAG_DOCUMENT = 6;
  private static final int METHODID_LIST_ACTIVE_TAGS = 7;
  private static final int METHODID_LIST_TAG_EVENTS = 8;
  private static final int METHODID_GET_SESSION_CONTEXT = 9;
  private static final int METHODID_HEALTH_CHECK = 10;

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
        case METHODID_PUT_DOCUMENT:
          serviceImpl.putDocument((unhinged.document_store.DocumentStore.PutDocumentRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.PutDocumentResponse>) responseObserver);
          break;
        case METHODID_PUT_DOCUMENTS:
          serviceImpl.putDocuments((unhinged.document_store.DocumentStore.PutDocumentsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.PutDocumentsResponse>) responseObserver);
          break;
        case METHODID_GET_DOCUMENT:
          serviceImpl.getDocument((unhinged.document_store.DocumentStore.GetDocumentRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.GetDocumentResponse>) responseObserver);
          break;
        case METHODID_LIST_DOCUMENTS:
          serviceImpl.listDocuments((unhinged.document_store.DocumentStore.ListDocumentsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListDocumentsResponse>) responseObserver);
          break;
        case METHODID_LIST_DOCUMENT_VERSIONS:
          serviceImpl.listDocumentVersions((unhinged.document_store.DocumentStore.ListDocumentVersionsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListDocumentVersionsResponse>) responseObserver);
          break;
        case METHODID_DELETE_DOCUMENT:
          serviceImpl.deleteDocument((unhinged.document_store.DocumentStore.DeleteDocumentRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.DeleteDocumentResponse>) responseObserver);
          break;
        case METHODID_TAG_DOCUMENT:
          serviceImpl.tagDocument((unhinged.document_store.DocumentStore.TagDocumentRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.TagDocumentResponse>) responseObserver);
          break;
        case METHODID_LIST_ACTIVE_TAGS:
          serviceImpl.listActiveTags((unhinged.document_store.DocumentStore.ListActiveTagsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListActiveTagsResponse>) responseObserver);
          break;
        case METHODID_LIST_TAG_EVENTS:
          serviceImpl.listTagEvents((unhinged.document_store.DocumentStore.ListTagEventsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.ListTagEventsResponse>) responseObserver);
          break;
        case METHODID_GET_SESSION_CONTEXT:
          serviceImpl.getSessionContext((unhinged.document_store.DocumentStore.GetSessionContextRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.GetSessionContextResponse>) responseObserver);
          break;
        case METHODID_HEALTH_CHECK:
          serviceImpl.healthCheck((unhinged.document_store.DocumentStore.HealthCheckRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.document_store.DocumentStore.HealthCheckResponse>) responseObserver);
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
          getPutDocumentMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.PutDocumentRequest,
              unhinged.document_store.DocumentStore.PutDocumentResponse>(
                service, METHODID_PUT_DOCUMENT)))
        .addMethod(
          getPutDocumentsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.PutDocumentsRequest,
              unhinged.document_store.DocumentStore.PutDocumentsResponse>(
                service, METHODID_PUT_DOCUMENTS)))
        .addMethod(
          getGetDocumentMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.GetDocumentRequest,
              unhinged.document_store.DocumentStore.GetDocumentResponse>(
                service, METHODID_GET_DOCUMENT)))
        .addMethod(
          getListDocumentsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.ListDocumentsRequest,
              unhinged.document_store.DocumentStore.ListDocumentsResponse>(
                service, METHODID_LIST_DOCUMENTS)))
        .addMethod(
          getListDocumentVersionsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.ListDocumentVersionsRequest,
              unhinged.document_store.DocumentStore.ListDocumentVersionsResponse>(
                service, METHODID_LIST_DOCUMENT_VERSIONS)))
        .addMethod(
          getDeleteDocumentMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.DeleteDocumentRequest,
              unhinged.document_store.DocumentStore.DeleteDocumentResponse>(
                service, METHODID_DELETE_DOCUMENT)))
        .addMethod(
          getTagDocumentMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.TagDocumentRequest,
              unhinged.document_store.DocumentStore.TagDocumentResponse>(
                service, METHODID_TAG_DOCUMENT)))
        .addMethod(
          getListActiveTagsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.ListActiveTagsRequest,
              unhinged.document_store.DocumentStore.ListActiveTagsResponse>(
                service, METHODID_LIST_ACTIVE_TAGS)))
        .addMethod(
          getListTagEventsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.ListTagEventsRequest,
              unhinged.document_store.DocumentStore.ListTagEventsResponse>(
                service, METHODID_LIST_TAG_EVENTS)))
        .addMethod(
          getGetSessionContextMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.GetSessionContextRequest,
              unhinged.document_store.DocumentStore.GetSessionContextResponse>(
                service, METHODID_GET_SESSION_CONTEXT)))
        .addMethod(
          getHealthCheckMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.document_store.DocumentStore.HealthCheckRequest,
              unhinged.document_store.DocumentStore.HealthCheckResponse>(
                service, METHODID_HEALTH_CHECK)))
        .build();
  }

  private static abstract class DocumentStoreServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    DocumentStoreServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return unhinged.document_store.DocumentStore.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("DocumentStoreService");
    }
  }

  private static final class DocumentStoreServiceFileDescriptorSupplier
      extends DocumentStoreServiceBaseDescriptorSupplier {
    DocumentStoreServiceFileDescriptorSupplier() {}
  }

  private static final class DocumentStoreServiceMethodDescriptorSupplier
      extends DocumentStoreServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    DocumentStoreServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (DocumentStoreServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new DocumentStoreServiceFileDescriptorSupplier())
              .addMethod(getPutDocumentMethod())
              .addMethod(getPutDocumentsMethod())
              .addMethod(getGetDocumentMethod())
              .addMethod(getListDocumentsMethod())
              .addMethod(getListDocumentVersionsMethod())
              .addMethod(getDeleteDocumentMethod())
              .addMethod(getTagDocumentMethod())
              .addMethod(getListActiveTagsMethod())
              .addMethod(getListTagEventsMethod())
              .addMethod(getGetSessionContextMethod())
              .addMethod(getHealthCheckMethod())
              .build();
        }
      }
    }
    return result;
  }
}
