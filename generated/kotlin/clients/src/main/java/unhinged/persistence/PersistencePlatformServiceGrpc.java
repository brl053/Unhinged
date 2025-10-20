package unhinged.persistence;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: persistence_platform.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class PersistencePlatformServiceGrpc {

  private PersistencePlatformServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "unhinged.persistence.PersistencePlatformService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.InsertRequest,
      unhinged.persistence.PersistencePlatform.InsertResponse> getInsertMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Insert",
      requestType = unhinged.persistence.PersistencePlatform.InsertRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.InsertResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.InsertRequest,
      unhinged.persistence.PersistencePlatform.InsertResponse> getInsertMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.InsertRequest, unhinged.persistence.PersistencePlatform.InsertResponse> getInsertMethod;
    if ((getInsertMethod = PersistencePlatformServiceGrpc.getInsertMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getInsertMethod = PersistencePlatformServiceGrpc.getInsertMethod) == null) {
          PersistencePlatformServiceGrpc.getInsertMethod = getInsertMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.InsertRequest, unhinged.persistence.PersistencePlatform.InsertResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Insert"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.InsertRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.InsertResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("Insert"))
              .build();
        }
      }
    }
    return getInsertMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.InsertBatchRequest,
      unhinged.persistence.PersistencePlatform.InsertBatchResponse> getInsertBatchMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "InsertBatch",
      requestType = unhinged.persistence.PersistencePlatform.InsertBatchRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.InsertBatchResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.InsertBatchRequest,
      unhinged.persistence.PersistencePlatform.InsertBatchResponse> getInsertBatchMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.InsertBatchRequest, unhinged.persistence.PersistencePlatform.InsertBatchResponse> getInsertBatchMethod;
    if ((getInsertBatchMethod = PersistencePlatformServiceGrpc.getInsertBatchMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getInsertBatchMethod = PersistencePlatformServiceGrpc.getInsertBatchMethod) == null) {
          PersistencePlatformServiceGrpc.getInsertBatchMethod = getInsertBatchMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.InsertBatchRequest, unhinged.persistence.PersistencePlatform.InsertBatchResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "InsertBatch"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.InsertBatchRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.InsertBatchResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("InsertBatch"))
              .build();
        }
      }
    }
    return getInsertBatchMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.UpdateRequest,
      unhinged.persistence.PersistencePlatform.UpdateResponse> getUpdateMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Update",
      requestType = unhinged.persistence.PersistencePlatform.UpdateRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.UpdateResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.UpdateRequest,
      unhinged.persistence.PersistencePlatform.UpdateResponse> getUpdateMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.UpdateRequest, unhinged.persistence.PersistencePlatform.UpdateResponse> getUpdateMethod;
    if ((getUpdateMethod = PersistencePlatformServiceGrpc.getUpdateMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getUpdateMethod = PersistencePlatformServiceGrpc.getUpdateMethod) == null) {
          PersistencePlatformServiceGrpc.getUpdateMethod = getUpdateMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.UpdateRequest, unhinged.persistence.PersistencePlatform.UpdateResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Update"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.UpdateRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.UpdateResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("Update"))
              .build();
        }
      }
    }
    return getUpdateMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.DeleteRequest,
      unhinged.persistence.PersistencePlatform.DeleteResponse> getDeleteMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Delete",
      requestType = unhinged.persistence.PersistencePlatform.DeleteRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.DeleteResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.DeleteRequest,
      unhinged.persistence.PersistencePlatform.DeleteResponse> getDeleteMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.DeleteRequest, unhinged.persistence.PersistencePlatform.DeleteResponse> getDeleteMethod;
    if ((getDeleteMethod = PersistencePlatformServiceGrpc.getDeleteMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getDeleteMethod = PersistencePlatformServiceGrpc.getDeleteMethod) == null) {
          PersistencePlatformServiceGrpc.getDeleteMethod = getDeleteMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.DeleteRequest, unhinged.persistence.PersistencePlatform.DeleteResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Delete"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.DeleteRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.DeleteResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("Delete"))
              .build();
        }
      }
    }
    return getDeleteMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteQueryRequest,
      unhinged.persistence.PersistencePlatform.ExecuteQueryResponse> getExecuteQueryMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ExecuteQuery",
      requestType = unhinged.persistence.PersistencePlatform.ExecuteQueryRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.ExecuteQueryResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteQueryRequest,
      unhinged.persistence.PersistencePlatform.ExecuteQueryResponse> getExecuteQueryMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteQueryRequest, unhinged.persistence.PersistencePlatform.ExecuteQueryResponse> getExecuteQueryMethod;
    if ((getExecuteQueryMethod = PersistencePlatformServiceGrpc.getExecuteQueryMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getExecuteQueryMethod = PersistencePlatformServiceGrpc.getExecuteQueryMethod) == null) {
          PersistencePlatformServiceGrpc.getExecuteQueryMethod = getExecuteQueryMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.ExecuteQueryRequest, unhinged.persistence.PersistencePlatform.ExecuteQueryResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ExecuteQuery"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.ExecuteQueryRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.ExecuteQueryResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("ExecuteQuery"))
              .build();
        }
      }
    }
    return getExecuteQueryMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest,
      unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse> getExecuteRawQueryMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ExecuteRawQuery",
      requestType = unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest,
      unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse> getExecuteRawQueryMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest, unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse> getExecuteRawQueryMethod;
    if ((getExecuteRawQueryMethod = PersistencePlatformServiceGrpc.getExecuteRawQueryMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getExecuteRawQueryMethod = PersistencePlatformServiceGrpc.getExecuteRawQueryMethod) == null) {
          PersistencePlatformServiceGrpc.getExecuteRawQueryMethod = getExecuteRawQueryMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest, unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ExecuteRawQuery"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("ExecuteRawQuery"))
              .build();
        }
      }
    }
    return getExecuteRawQueryMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.VectorSearchRequest,
      unhinged.persistence.PersistencePlatform.VectorSearchResponse> getVectorSearchMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "VectorSearch",
      requestType = unhinged.persistence.PersistencePlatform.VectorSearchRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.VectorSearchResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.VectorSearchRequest,
      unhinged.persistence.PersistencePlatform.VectorSearchResponse> getVectorSearchMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.VectorSearchRequest, unhinged.persistence.PersistencePlatform.VectorSearchResponse> getVectorSearchMethod;
    if ((getVectorSearchMethod = PersistencePlatformServiceGrpc.getVectorSearchMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getVectorSearchMethod = PersistencePlatformServiceGrpc.getVectorSearchMethod) == null) {
          PersistencePlatformServiceGrpc.getVectorSearchMethod = getVectorSearchMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.VectorSearchRequest, unhinged.persistence.PersistencePlatform.VectorSearchResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "VectorSearch"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.VectorSearchRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.VectorSearchResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("VectorSearch"))
              .build();
        }
      }
    }
    return getVectorSearchMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GraphTraverseRequest,
      unhinged.persistence.PersistencePlatform.GraphTraverseResponse> getGraphTraverseMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GraphTraverse",
      requestType = unhinged.persistence.PersistencePlatform.GraphTraverseRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.GraphTraverseResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GraphTraverseRequest,
      unhinged.persistence.PersistencePlatform.GraphTraverseResponse> getGraphTraverseMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GraphTraverseRequest, unhinged.persistence.PersistencePlatform.GraphTraverseResponse> getGraphTraverseMethod;
    if ((getGraphTraverseMethod = PersistencePlatformServiceGrpc.getGraphTraverseMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getGraphTraverseMethod = PersistencePlatformServiceGrpc.getGraphTraverseMethod) == null) {
          PersistencePlatformServiceGrpc.getGraphTraverseMethod = getGraphTraverseMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.GraphTraverseRequest, unhinged.persistence.PersistencePlatform.GraphTraverseResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GraphTraverse"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.GraphTraverseRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.GraphTraverseResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("GraphTraverse"))
              .build();
        }
      }
    }
    return getGraphTraverseMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteOperationRequest,
      unhinged.persistence.PersistencePlatform.ExecuteOperationResponse> getExecuteOperationMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ExecuteOperation",
      requestType = unhinged.persistence.PersistencePlatform.ExecuteOperationRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.ExecuteOperationResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteOperationRequest,
      unhinged.persistence.PersistencePlatform.ExecuteOperationResponse> getExecuteOperationMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.ExecuteOperationRequest, unhinged.persistence.PersistencePlatform.ExecuteOperationResponse> getExecuteOperationMethod;
    if ((getExecuteOperationMethod = PersistencePlatformServiceGrpc.getExecuteOperationMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getExecuteOperationMethod = PersistencePlatformServiceGrpc.getExecuteOperationMethod) == null) {
          PersistencePlatformServiceGrpc.getExecuteOperationMethod = getExecuteOperationMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.ExecuteOperationRequest, unhinged.persistence.PersistencePlatform.ExecuteOperationResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ExecuteOperation"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.ExecuteOperationRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.ExecuteOperationResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("ExecuteOperation"))
              .build();
        }
      }
    }
    return getExecuteOperationMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.HealthCheckRequest,
      unhinged.persistence.PersistencePlatform.HealthCheckResponse> getHealthCheckMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "HealthCheck",
      requestType = unhinged.persistence.PersistencePlatform.HealthCheckRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.HealthCheckResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.HealthCheckRequest,
      unhinged.persistence.PersistencePlatform.HealthCheckResponse> getHealthCheckMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.HealthCheckRequest, unhinged.persistence.PersistencePlatform.HealthCheckResponse> getHealthCheckMethod;
    if ((getHealthCheckMethod = PersistencePlatformServiceGrpc.getHealthCheckMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getHealthCheckMethod = PersistencePlatformServiceGrpc.getHealthCheckMethod) == null) {
          PersistencePlatformServiceGrpc.getHealthCheckMethod = getHealthCheckMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.HealthCheckRequest, unhinged.persistence.PersistencePlatform.HealthCheckResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "HealthCheck"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.HealthCheckRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.HealthCheckResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("HealthCheck"))
              .build();
        }
      }
    }
    return getHealthCheckMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest,
      unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse> getGetPlatformInfoMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetPlatformInfo",
      requestType = unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest,
      unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse> getGetPlatformInfoMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest, unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse> getGetPlatformInfoMethod;
    if ((getGetPlatformInfoMethod = PersistencePlatformServiceGrpc.getGetPlatformInfoMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getGetPlatformInfoMethod = PersistencePlatformServiceGrpc.getGetPlatformInfoMethod) == null) {
          PersistencePlatformServiceGrpc.getGetPlatformInfoMethod = getGetPlatformInfoMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest, unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetPlatformInfo"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("GetPlatformInfo"))
              .build();
        }
      }
    }
    return getGetPlatformInfoMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GetMetricsRequest,
      unhinged.persistence.PersistencePlatform.GetMetricsResponse> getGetMetricsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetMetrics",
      requestType = unhinged.persistence.PersistencePlatform.GetMetricsRequest.class,
      responseType = unhinged.persistence.PersistencePlatform.GetMetricsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GetMetricsRequest,
      unhinged.persistence.PersistencePlatform.GetMetricsResponse> getGetMetricsMethod() {
    io.grpc.MethodDescriptor<unhinged.persistence.PersistencePlatform.GetMetricsRequest, unhinged.persistence.PersistencePlatform.GetMetricsResponse> getGetMetricsMethod;
    if ((getGetMetricsMethod = PersistencePlatformServiceGrpc.getGetMetricsMethod) == null) {
      synchronized (PersistencePlatformServiceGrpc.class) {
        if ((getGetMetricsMethod = PersistencePlatformServiceGrpc.getGetMetricsMethod) == null) {
          PersistencePlatformServiceGrpc.getGetMetricsMethod = getGetMetricsMethod =
              io.grpc.MethodDescriptor.<unhinged.persistence.PersistencePlatform.GetMetricsRequest, unhinged.persistence.PersistencePlatform.GetMetricsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetMetrics"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.GetMetricsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.persistence.PersistencePlatform.GetMetricsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new PersistencePlatformServiceMethodDescriptorSupplier("GetMetrics"))
              .build();
        }
      }
    }
    return getGetMetricsMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static PersistencePlatformServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<PersistencePlatformServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<PersistencePlatformServiceStub>() {
        @java.lang.Override
        public PersistencePlatformServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new PersistencePlatformServiceStub(channel, callOptions);
        }
      };
    return PersistencePlatformServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static PersistencePlatformServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<PersistencePlatformServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<PersistencePlatformServiceBlockingStub>() {
        @java.lang.Override
        public PersistencePlatformServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new PersistencePlatformServiceBlockingStub(channel, callOptions);
        }
      };
    return PersistencePlatformServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static PersistencePlatformServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<PersistencePlatformServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<PersistencePlatformServiceFutureStub>() {
        @java.lang.Override
        public PersistencePlatformServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new PersistencePlatformServiceFutureStub(channel, callOptions);
        }
      };
    return PersistencePlatformServiceFutureStub.newStub(factory, channel);
  }

  /**
   */
  public interface AsyncService {

    /**
     * <pre>
     * CRUD Operations
     * </pre>
     */
    default void insert(unhinged.persistence.PersistencePlatform.InsertRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.InsertResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getInsertMethod(), responseObserver);
    }

    /**
     */
    default void insertBatch(unhinged.persistence.PersistencePlatform.InsertBatchRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.InsertBatchResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getInsertBatchMethod(), responseObserver);
    }

    /**
     */
    default void update(unhinged.persistence.PersistencePlatform.UpdateRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.UpdateResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getUpdateMethod(), responseObserver);
    }

    /**
     */
    default void delete(unhinged.persistence.PersistencePlatform.DeleteRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.DeleteResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDeleteMethod(), responseObserver);
    }

    /**
     * <pre>
     * Query Operations
     * </pre>
     */
    default void executeQuery(unhinged.persistence.PersistencePlatform.ExecuteQueryRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteQueryResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getExecuteQueryMethod(), responseObserver);
    }

    /**
     */
    default void executeRawQuery(unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getExecuteRawQueryMethod(), responseObserver);
    }

    /**
     * <pre>
     * Vector Operations
     * </pre>
     */
    default void vectorSearch(unhinged.persistence.PersistencePlatform.VectorSearchRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.VectorSearchResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getVectorSearchMethod(), responseObserver);
    }

    /**
     * <pre>
     * Graph Operations
     * </pre>
     */
    default void graphTraverse(unhinged.persistence.PersistencePlatform.GraphTraverseRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GraphTraverseResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGraphTraverseMethod(), responseObserver);
    }

    /**
     * <pre>
     * Complex Operations
     * </pre>
     */
    default void executeOperation(unhinged.persistence.PersistencePlatform.ExecuteOperationRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteOperationResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getExecuteOperationMethod(), responseObserver);
    }

    /**
     * <pre>
     * Platform Management
     * </pre>
     */
    default void healthCheck(unhinged.persistence.PersistencePlatform.HealthCheckRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.HealthCheckResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getHealthCheckMethod(), responseObserver);
    }

    /**
     */
    default void getPlatformInfo(unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetPlatformInfoMethod(), responseObserver);
    }

    /**
     */
    default void getMetrics(unhinged.persistence.PersistencePlatform.GetMetricsRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GetMetricsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetMetricsMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service PersistencePlatformService.
   */
  public static abstract class PersistencePlatformServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return PersistencePlatformServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service PersistencePlatformService.
   */
  public static final class PersistencePlatformServiceStub
      extends io.grpc.stub.AbstractAsyncStub<PersistencePlatformServiceStub> {
    private PersistencePlatformServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected PersistencePlatformServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new PersistencePlatformServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * CRUD Operations
     * </pre>
     */
    public void insert(unhinged.persistence.PersistencePlatform.InsertRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.InsertResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getInsertMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void insertBatch(unhinged.persistence.PersistencePlatform.InsertBatchRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.InsertBatchResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getInsertBatchMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void update(unhinged.persistence.PersistencePlatform.UpdateRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.UpdateResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getUpdateMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void delete(unhinged.persistence.PersistencePlatform.DeleteRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.DeleteResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getDeleteMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Query Operations
     * </pre>
     */
    public void executeQuery(unhinged.persistence.PersistencePlatform.ExecuteQueryRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteQueryResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getExecuteQueryMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void executeRawQuery(unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getExecuteRawQueryMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Vector Operations
     * </pre>
     */
    public void vectorSearch(unhinged.persistence.PersistencePlatform.VectorSearchRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.VectorSearchResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getVectorSearchMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Graph Operations
     * </pre>
     */
    public void graphTraverse(unhinged.persistence.PersistencePlatform.GraphTraverseRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GraphTraverseResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGraphTraverseMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Complex Operations
     * </pre>
     */
    public void executeOperation(unhinged.persistence.PersistencePlatform.ExecuteOperationRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteOperationResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getExecuteOperationMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Platform Management
     * </pre>
     */
    public void healthCheck(unhinged.persistence.PersistencePlatform.HealthCheckRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.HealthCheckResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getHealthCheckMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getPlatformInfo(unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetPlatformInfoMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getMetrics(unhinged.persistence.PersistencePlatform.GetMetricsRequest request,
        io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GetMetricsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetMetricsMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service PersistencePlatformService.
   */
  public static final class PersistencePlatformServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<PersistencePlatformServiceBlockingStub> {
    private PersistencePlatformServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected PersistencePlatformServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new PersistencePlatformServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * CRUD Operations
     * </pre>
     */
    public unhinged.persistence.PersistencePlatform.InsertResponse insert(unhinged.persistence.PersistencePlatform.InsertRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getInsertMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.persistence.PersistencePlatform.InsertBatchResponse insertBatch(unhinged.persistence.PersistencePlatform.InsertBatchRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getInsertBatchMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.persistence.PersistencePlatform.UpdateResponse update(unhinged.persistence.PersistencePlatform.UpdateRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getUpdateMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.persistence.PersistencePlatform.DeleteResponse delete(unhinged.persistence.PersistencePlatform.DeleteRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getDeleteMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Query Operations
     * </pre>
     */
    public unhinged.persistence.PersistencePlatform.ExecuteQueryResponse executeQuery(unhinged.persistence.PersistencePlatform.ExecuteQueryRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getExecuteQueryMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse executeRawQuery(unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getExecuteRawQueryMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Vector Operations
     * </pre>
     */
    public unhinged.persistence.PersistencePlatform.VectorSearchResponse vectorSearch(unhinged.persistence.PersistencePlatform.VectorSearchRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getVectorSearchMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Graph Operations
     * </pre>
     */
    public unhinged.persistence.PersistencePlatform.GraphTraverseResponse graphTraverse(unhinged.persistence.PersistencePlatform.GraphTraverseRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGraphTraverseMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Complex Operations
     * </pre>
     */
    public unhinged.persistence.PersistencePlatform.ExecuteOperationResponse executeOperation(unhinged.persistence.PersistencePlatform.ExecuteOperationRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getExecuteOperationMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Platform Management
     * </pre>
     */
    public unhinged.persistence.PersistencePlatform.HealthCheckResponse healthCheck(unhinged.persistence.PersistencePlatform.HealthCheckRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getHealthCheckMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse getPlatformInfo(unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetPlatformInfoMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.persistence.PersistencePlatform.GetMetricsResponse getMetrics(unhinged.persistence.PersistencePlatform.GetMetricsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetMetricsMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service PersistencePlatformService.
   */
  public static final class PersistencePlatformServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<PersistencePlatformServiceFutureStub> {
    private PersistencePlatformServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected PersistencePlatformServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new PersistencePlatformServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * CRUD Operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.InsertResponse> insert(
        unhinged.persistence.PersistencePlatform.InsertRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getInsertMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.InsertBatchResponse> insertBatch(
        unhinged.persistence.PersistencePlatform.InsertBatchRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getInsertBatchMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.UpdateResponse> update(
        unhinged.persistence.PersistencePlatform.UpdateRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getUpdateMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.DeleteResponse> delete(
        unhinged.persistence.PersistencePlatform.DeleteRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getDeleteMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Query Operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.ExecuteQueryResponse> executeQuery(
        unhinged.persistence.PersistencePlatform.ExecuteQueryRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getExecuteQueryMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse> executeRawQuery(
        unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getExecuteRawQueryMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Vector Operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.VectorSearchResponse> vectorSearch(
        unhinged.persistence.PersistencePlatform.VectorSearchRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getVectorSearchMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Graph Operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.GraphTraverseResponse> graphTraverse(
        unhinged.persistence.PersistencePlatform.GraphTraverseRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGraphTraverseMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Complex Operations
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.ExecuteOperationResponse> executeOperation(
        unhinged.persistence.PersistencePlatform.ExecuteOperationRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getExecuteOperationMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Platform Management
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.HealthCheckResponse> healthCheck(
        unhinged.persistence.PersistencePlatform.HealthCheckRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getHealthCheckMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse> getPlatformInfo(
        unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetPlatformInfoMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.persistence.PersistencePlatform.GetMetricsResponse> getMetrics(
        unhinged.persistence.PersistencePlatform.GetMetricsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetMetricsMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_INSERT = 0;
  private static final int METHODID_INSERT_BATCH = 1;
  private static final int METHODID_UPDATE = 2;
  private static final int METHODID_DELETE = 3;
  private static final int METHODID_EXECUTE_QUERY = 4;
  private static final int METHODID_EXECUTE_RAW_QUERY = 5;
  private static final int METHODID_VECTOR_SEARCH = 6;
  private static final int METHODID_GRAPH_TRAVERSE = 7;
  private static final int METHODID_EXECUTE_OPERATION = 8;
  private static final int METHODID_HEALTH_CHECK = 9;
  private static final int METHODID_GET_PLATFORM_INFO = 10;
  private static final int METHODID_GET_METRICS = 11;

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
        case METHODID_INSERT:
          serviceImpl.insert((unhinged.persistence.PersistencePlatform.InsertRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.InsertResponse>) responseObserver);
          break;
        case METHODID_INSERT_BATCH:
          serviceImpl.insertBatch((unhinged.persistence.PersistencePlatform.InsertBatchRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.InsertBatchResponse>) responseObserver);
          break;
        case METHODID_UPDATE:
          serviceImpl.update((unhinged.persistence.PersistencePlatform.UpdateRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.UpdateResponse>) responseObserver);
          break;
        case METHODID_DELETE:
          serviceImpl.delete((unhinged.persistence.PersistencePlatform.DeleteRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.DeleteResponse>) responseObserver);
          break;
        case METHODID_EXECUTE_QUERY:
          serviceImpl.executeQuery((unhinged.persistence.PersistencePlatform.ExecuteQueryRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteQueryResponse>) responseObserver);
          break;
        case METHODID_EXECUTE_RAW_QUERY:
          serviceImpl.executeRawQuery((unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse>) responseObserver);
          break;
        case METHODID_VECTOR_SEARCH:
          serviceImpl.vectorSearch((unhinged.persistence.PersistencePlatform.VectorSearchRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.VectorSearchResponse>) responseObserver);
          break;
        case METHODID_GRAPH_TRAVERSE:
          serviceImpl.graphTraverse((unhinged.persistence.PersistencePlatform.GraphTraverseRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GraphTraverseResponse>) responseObserver);
          break;
        case METHODID_EXECUTE_OPERATION:
          serviceImpl.executeOperation((unhinged.persistence.PersistencePlatform.ExecuteOperationRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.ExecuteOperationResponse>) responseObserver);
          break;
        case METHODID_HEALTH_CHECK:
          serviceImpl.healthCheck((unhinged.persistence.PersistencePlatform.HealthCheckRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.HealthCheckResponse>) responseObserver);
          break;
        case METHODID_GET_PLATFORM_INFO:
          serviceImpl.getPlatformInfo((unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse>) responseObserver);
          break;
        case METHODID_GET_METRICS:
          serviceImpl.getMetrics((unhinged.persistence.PersistencePlatform.GetMetricsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.persistence.PersistencePlatform.GetMetricsResponse>) responseObserver);
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
          getInsertMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.InsertRequest,
              unhinged.persistence.PersistencePlatform.InsertResponse>(
                service, METHODID_INSERT)))
        .addMethod(
          getInsertBatchMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.InsertBatchRequest,
              unhinged.persistence.PersistencePlatform.InsertBatchResponse>(
                service, METHODID_INSERT_BATCH)))
        .addMethod(
          getUpdateMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.UpdateRequest,
              unhinged.persistence.PersistencePlatform.UpdateResponse>(
                service, METHODID_UPDATE)))
        .addMethod(
          getDeleteMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.DeleteRequest,
              unhinged.persistence.PersistencePlatform.DeleteResponse>(
                service, METHODID_DELETE)))
        .addMethod(
          getExecuteQueryMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.ExecuteQueryRequest,
              unhinged.persistence.PersistencePlatform.ExecuteQueryResponse>(
                service, METHODID_EXECUTE_QUERY)))
        .addMethod(
          getExecuteRawQueryMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.ExecuteRawQueryRequest,
              unhinged.persistence.PersistencePlatform.ExecuteRawQueryResponse>(
                service, METHODID_EXECUTE_RAW_QUERY)))
        .addMethod(
          getVectorSearchMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.VectorSearchRequest,
              unhinged.persistence.PersistencePlatform.VectorSearchResponse>(
                service, METHODID_VECTOR_SEARCH)))
        .addMethod(
          getGraphTraverseMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.GraphTraverseRequest,
              unhinged.persistence.PersistencePlatform.GraphTraverseResponse>(
                service, METHODID_GRAPH_TRAVERSE)))
        .addMethod(
          getExecuteOperationMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.ExecuteOperationRequest,
              unhinged.persistence.PersistencePlatform.ExecuteOperationResponse>(
                service, METHODID_EXECUTE_OPERATION)))
        .addMethod(
          getHealthCheckMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.HealthCheckRequest,
              unhinged.persistence.PersistencePlatform.HealthCheckResponse>(
                service, METHODID_HEALTH_CHECK)))
        .addMethod(
          getGetPlatformInfoMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.GetPlatformInfoRequest,
              unhinged.persistence.PersistencePlatform.GetPlatformInfoResponse>(
                service, METHODID_GET_PLATFORM_INFO)))
        .addMethod(
          getGetMetricsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.persistence.PersistencePlatform.GetMetricsRequest,
              unhinged.persistence.PersistencePlatform.GetMetricsResponse>(
                service, METHODID_GET_METRICS)))
        .build();
  }

  private static abstract class PersistencePlatformServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    PersistencePlatformServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return unhinged.persistence.PersistencePlatform.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("PersistencePlatformService");
    }
  }

  private static final class PersistencePlatformServiceFileDescriptorSupplier
      extends PersistencePlatformServiceBaseDescriptorSupplier {
    PersistencePlatformServiceFileDescriptorSupplier() {}
  }

  private static final class PersistencePlatformServiceMethodDescriptorSupplier
      extends PersistencePlatformServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    PersistencePlatformServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (PersistencePlatformServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new PersistencePlatformServiceFileDescriptorSupplier())
              .addMethod(getInsertMethod())
              .addMethod(getInsertBatchMethod())
              .addMethod(getUpdateMethod())
              .addMethod(getDeleteMethod())
              .addMethod(getExecuteQueryMethod())
              .addMethod(getExecuteRawQueryMethod())
              .addMethod(getVectorSearchMethod())
              .addMethod(getGraphTraverseMethod())
              .addMethod(getExecuteOperationMethod())
              .addMethod(getHealthCheckMethod())
              .addMethod(getGetPlatformInfoMethod())
              .addMethod(getGetMetricsMethod())
              .build();
        }
      }
    }
    return result;
  }
}
