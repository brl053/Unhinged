package unhinged.cdc;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: cdc_service.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class CDCServiceGrpc {

  private CDCServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "unhinged.cdc.CDCService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.PublishEventRequest,
      unhinged.cdc.CdcService.PublishEventResponse> getPublishEventMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "PublishEvent",
      requestType = unhinged.cdc.CdcService.PublishEventRequest.class,
      responseType = unhinged.cdc.CdcService.PublishEventResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.PublishEventRequest,
      unhinged.cdc.CdcService.PublishEventResponse> getPublishEventMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.PublishEventRequest, unhinged.cdc.CdcService.PublishEventResponse> getPublishEventMethod;
    if ((getPublishEventMethod = CDCServiceGrpc.getPublishEventMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getPublishEventMethod = CDCServiceGrpc.getPublishEventMethod) == null) {
          CDCServiceGrpc.getPublishEventMethod = getPublishEventMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.PublishEventRequest, unhinged.cdc.CdcService.PublishEventResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "PublishEvent"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.PublishEventRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.PublishEventResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("PublishEvent"))
              .build();
        }
      }
    }
    return getPublishEventMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.PublishEventsRequest,
      unhinged.cdc.CdcService.PublishEventsResponse> getPublishEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "PublishEvents",
      requestType = unhinged.cdc.CdcService.PublishEventsRequest.class,
      responseType = unhinged.cdc.CdcService.PublishEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.PublishEventsRequest,
      unhinged.cdc.CdcService.PublishEventsResponse> getPublishEventsMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.PublishEventsRequest, unhinged.cdc.CdcService.PublishEventsResponse> getPublishEventsMethod;
    if ((getPublishEventsMethod = CDCServiceGrpc.getPublishEventsMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getPublishEventsMethod = CDCServiceGrpc.getPublishEventsMethod) == null) {
          CDCServiceGrpc.getPublishEventsMethod = getPublishEventsMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.PublishEventsRequest, unhinged.cdc.CdcService.PublishEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "PublishEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.PublishEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.PublishEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("PublishEvents"))
              .build();
        }
      }
    }
    return getPublishEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.SubscribeRequest,
      unhinged.cdc.CdcService.EventStreamResponse> getSubscribeMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "Subscribe",
      requestType = unhinged.cdc.CdcService.SubscribeRequest.class,
      responseType = unhinged.cdc.CdcService.EventStreamResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.SubscribeRequest,
      unhinged.cdc.CdcService.EventStreamResponse> getSubscribeMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.SubscribeRequest, unhinged.cdc.CdcService.EventStreamResponse> getSubscribeMethod;
    if ((getSubscribeMethod = CDCServiceGrpc.getSubscribeMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getSubscribeMethod = CDCServiceGrpc.getSubscribeMethod) == null) {
          CDCServiceGrpc.getSubscribeMethod = getSubscribeMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.SubscribeRequest, unhinged.cdc.CdcService.EventStreamResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "Subscribe"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.SubscribeRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.EventStreamResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("Subscribe"))
              .build();
        }
      }
    }
    return getSubscribeMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.AcknowledgeEventsRequest,
      unhinged.cdc.CdcService.AcknowledgeEventsResponse> getAcknowledgeEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "AcknowledgeEvents",
      requestType = unhinged.cdc.CdcService.AcknowledgeEventsRequest.class,
      responseType = unhinged.cdc.CdcService.AcknowledgeEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.AcknowledgeEventsRequest,
      unhinged.cdc.CdcService.AcknowledgeEventsResponse> getAcknowledgeEventsMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.AcknowledgeEventsRequest, unhinged.cdc.CdcService.AcknowledgeEventsResponse> getAcknowledgeEventsMethod;
    if ((getAcknowledgeEventsMethod = CDCServiceGrpc.getAcknowledgeEventsMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getAcknowledgeEventsMethod = CDCServiceGrpc.getAcknowledgeEventsMethod) == null) {
          CDCServiceGrpc.getAcknowledgeEventsMethod = getAcknowledgeEventsMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.AcknowledgeEventsRequest, unhinged.cdc.CdcService.AcknowledgeEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "AcknowledgeEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.AcknowledgeEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.AcknowledgeEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("AcknowledgeEvents"))
              .build();
        }
      }
    }
    return getAcknowledgeEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ReplayEventsRequest,
      unhinged.cdc.CdcService.EventStreamResponse> getReplayEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ReplayEvents",
      requestType = unhinged.cdc.CdcService.ReplayEventsRequest.class,
      responseType = unhinged.cdc.CdcService.EventStreamResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ReplayEventsRequest,
      unhinged.cdc.CdcService.EventStreamResponse> getReplayEventsMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ReplayEventsRequest, unhinged.cdc.CdcService.EventStreamResponse> getReplayEventsMethod;
    if ((getReplayEventsMethod = CDCServiceGrpc.getReplayEventsMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getReplayEventsMethod = CDCServiceGrpc.getReplayEventsMethod) == null) {
          CDCServiceGrpc.getReplayEventsMethod = getReplayEventsMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.ReplayEventsRequest, unhinged.cdc.CdcService.EventStreamResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ReplayEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.ReplayEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.EventStreamResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("ReplayEvents"))
              .build();
        }
      }
    }
    return getReplayEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ListDeadLetterEventsRequest,
      unhinged.cdc.CdcService.ListDeadLetterEventsResponse> getListDeadLetterEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListDeadLetterEvents",
      requestType = unhinged.cdc.CdcService.ListDeadLetterEventsRequest.class,
      responseType = unhinged.cdc.CdcService.ListDeadLetterEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ListDeadLetterEventsRequest,
      unhinged.cdc.CdcService.ListDeadLetterEventsResponse> getListDeadLetterEventsMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ListDeadLetterEventsRequest, unhinged.cdc.CdcService.ListDeadLetterEventsResponse> getListDeadLetterEventsMethod;
    if ((getListDeadLetterEventsMethod = CDCServiceGrpc.getListDeadLetterEventsMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getListDeadLetterEventsMethod = CDCServiceGrpc.getListDeadLetterEventsMethod) == null) {
          CDCServiceGrpc.getListDeadLetterEventsMethod = getListDeadLetterEventsMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.ListDeadLetterEventsRequest, unhinged.cdc.CdcService.ListDeadLetterEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListDeadLetterEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.ListDeadLetterEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.ListDeadLetterEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("ListDeadLetterEvents"))
              .build();
        }
      }
    }
    return getListDeadLetterEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest,
      unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse> getReprocessDeadLetterEventsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ReprocessDeadLetterEvents",
      requestType = unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest.class,
      responseType = unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest,
      unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse> getReprocessDeadLetterEventsMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest, unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse> getReprocessDeadLetterEventsMethod;
    if ((getReprocessDeadLetterEventsMethod = CDCServiceGrpc.getReprocessDeadLetterEventsMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getReprocessDeadLetterEventsMethod = CDCServiceGrpc.getReprocessDeadLetterEventsMethod) == null) {
          CDCServiceGrpc.getReprocessDeadLetterEventsMethod = getReprocessDeadLetterEventsMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest, unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ReprocessDeadLetterEvents"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("ReprocessDeadLetterEvents"))
              .build();
        }
      }
    }
    return getReprocessDeadLetterEventsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.GetEventStatsRequest,
      unhinged.cdc.CdcService.GetEventStatsResponse> getGetEventStatsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetEventStats",
      requestType = unhinged.cdc.CdcService.GetEventStatsRequest.class,
      responseType = unhinged.cdc.CdcService.GetEventStatsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.GetEventStatsRequest,
      unhinged.cdc.CdcService.GetEventStatsResponse> getGetEventStatsMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.GetEventStatsRequest, unhinged.cdc.CdcService.GetEventStatsResponse> getGetEventStatsMethod;
    if ((getGetEventStatsMethod = CDCServiceGrpc.getGetEventStatsMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getGetEventStatsMethod = CDCServiceGrpc.getGetEventStatsMethod) == null) {
          CDCServiceGrpc.getGetEventStatsMethod = getGetEventStatsMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.GetEventStatsRequest, unhinged.cdc.CdcService.GetEventStatsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetEventStats"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.GetEventStatsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.GetEventStatsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("GetEventStats"))
              .build();
        }
      }
    }
    return getGetEventStatsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ListSubscriptionsRequest,
      unhinged.cdc.CdcService.ListSubscriptionsResponse> getListSubscriptionsMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListSubscriptions",
      requestType = unhinged.cdc.CdcService.ListSubscriptionsRequest.class,
      responseType = unhinged.cdc.CdcService.ListSubscriptionsResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ListSubscriptionsRequest,
      unhinged.cdc.CdcService.ListSubscriptionsResponse> getListSubscriptionsMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.ListSubscriptionsRequest, unhinged.cdc.CdcService.ListSubscriptionsResponse> getListSubscriptionsMethod;
    if ((getListSubscriptionsMethod = CDCServiceGrpc.getListSubscriptionsMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getListSubscriptionsMethod = CDCServiceGrpc.getListSubscriptionsMethod) == null) {
          CDCServiceGrpc.getListSubscriptionsMethod = getListSubscriptionsMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.ListSubscriptionsRequest, unhinged.cdc.CdcService.ListSubscriptionsResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListSubscriptions"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.ListSubscriptionsRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.ListSubscriptionsResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("ListSubscriptions"))
              .build();
        }
      }
    }
    return getListSubscriptionsMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.UpdateSubscriptionRequest,
      unhinged.cdc.CdcService.UpdateSubscriptionResponse> getUpdateSubscriptionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "UpdateSubscription",
      requestType = unhinged.cdc.CdcService.UpdateSubscriptionRequest.class,
      responseType = unhinged.cdc.CdcService.UpdateSubscriptionResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.UpdateSubscriptionRequest,
      unhinged.cdc.CdcService.UpdateSubscriptionResponse> getUpdateSubscriptionMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.UpdateSubscriptionRequest, unhinged.cdc.CdcService.UpdateSubscriptionResponse> getUpdateSubscriptionMethod;
    if ((getUpdateSubscriptionMethod = CDCServiceGrpc.getUpdateSubscriptionMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getUpdateSubscriptionMethod = CDCServiceGrpc.getUpdateSubscriptionMethod) == null) {
          CDCServiceGrpc.getUpdateSubscriptionMethod = getUpdateSubscriptionMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.UpdateSubscriptionRequest, unhinged.cdc.CdcService.UpdateSubscriptionResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "UpdateSubscription"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.UpdateSubscriptionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.UpdateSubscriptionResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("UpdateSubscription"))
              .build();
        }
      }
    }
    return getUpdateSubscriptionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.DeleteSubscriptionRequest,
      unhinged.cdc.CdcService.DeleteSubscriptionResponse> getDeleteSubscriptionMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "DeleteSubscription",
      requestType = unhinged.cdc.CdcService.DeleteSubscriptionRequest.class,
      responseType = unhinged.cdc.CdcService.DeleteSubscriptionResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.DeleteSubscriptionRequest,
      unhinged.cdc.CdcService.DeleteSubscriptionResponse> getDeleteSubscriptionMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.DeleteSubscriptionRequest, unhinged.cdc.CdcService.DeleteSubscriptionResponse> getDeleteSubscriptionMethod;
    if ((getDeleteSubscriptionMethod = CDCServiceGrpc.getDeleteSubscriptionMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getDeleteSubscriptionMethod = CDCServiceGrpc.getDeleteSubscriptionMethod) == null) {
          CDCServiceGrpc.getDeleteSubscriptionMethod = getDeleteSubscriptionMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.DeleteSubscriptionRequest, unhinged.cdc.CdcService.DeleteSubscriptionResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "DeleteSubscription"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.DeleteSubscriptionRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.DeleteSubscriptionResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("DeleteSubscription"))
              .build();
        }
      }
    }
    return getDeleteSubscriptionMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.cdc.CdcService.GetServiceStatusRequest,
      unhinged.cdc.CdcService.GetServiceStatusResponse> getGetServiceStatusMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetServiceStatus",
      requestType = unhinged.cdc.CdcService.GetServiceStatusRequest.class,
      responseType = unhinged.cdc.CdcService.GetServiceStatusResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.cdc.CdcService.GetServiceStatusRequest,
      unhinged.cdc.CdcService.GetServiceStatusResponse> getGetServiceStatusMethod() {
    io.grpc.MethodDescriptor<unhinged.cdc.CdcService.GetServiceStatusRequest, unhinged.cdc.CdcService.GetServiceStatusResponse> getGetServiceStatusMethod;
    if ((getGetServiceStatusMethod = CDCServiceGrpc.getGetServiceStatusMethod) == null) {
      synchronized (CDCServiceGrpc.class) {
        if ((getGetServiceStatusMethod = CDCServiceGrpc.getGetServiceStatusMethod) == null) {
          CDCServiceGrpc.getGetServiceStatusMethod = getGetServiceStatusMethod =
              io.grpc.MethodDescriptor.<unhinged.cdc.CdcService.GetServiceStatusRequest, unhinged.cdc.CdcService.GetServiceStatusResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetServiceStatus"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.GetServiceStatusRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.cdc.CdcService.GetServiceStatusResponse.getDefaultInstance()))
              .setSchemaDescriptor(new CDCServiceMethodDescriptorSupplier("GetServiceStatus"))
              .build();
        }
      }
    }
    return getGetServiceStatusMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static CDCServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CDCServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CDCServiceStub>() {
        @java.lang.Override
        public CDCServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CDCServiceStub(channel, callOptions);
        }
      };
    return CDCServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static CDCServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CDCServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CDCServiceBlockingStub>() {
        @java.lang.Override
        public CDCServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CDCServiceBlockingStub(channel, callOptions);
        }
      };
    return CDCServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static CDCServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CDCServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CDCServiceFutureStub>() {
        @java.lang.Override
        public CDCServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CDCServiceFutureStub(channel, callOptions);
        }
      };
    return CDCServiceFutureStub.newStub(factory, channel);
  }

  /**
   */
  public interface AsyncService {

    /**
     * <pre>
     * Event publishing
     * </pre>
     */
    default void publishEvent(unhinged.cdc.CdcService.PublishEventRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.PublishEventResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getPublishEventMethod(), responseObserver);
    }

    /**
     */
    default void publishEvents(unhinged.cdc.CdcService.PublishEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.PublishEventsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getPublishEventsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Event subscription (streaming)
     * </pre>
     */
    default void subscribe(unhinged.cdc.CdcService.SubscribeRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.EventStreamResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getSubscribeMethod(), responseObserver);
    }

    /**
     */
    default void acknowledgeEvents(unhinged.cdc.CdcService.AcknowledgeEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.AcknowledgeEventsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getAcknowledgeEventsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Event replay
     * </pre>
     */
    default void replayEvents(unhinged.cdc.CdcService.ReplayEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.EventStreamResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getReplayEventsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Dead letter queue
     * </pre>
     */
    default void listDeadLetterEvents(unhinged.cdc.CdcService.ListDeadLetterEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ListDeadLetterEventsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListDeadLetterEventsMethod(), responseObserver);
    }

    /**
     */
    default void reprocessDeadLetterEvents(unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getReprocessDeadLetterEventsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Analytics
     * </pre>
     */
    default void getEventStats(unhinged.cdc.CdcService.GetEventStatsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.GetEventStatsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetEventStatsMethod(), responseObserver);
    }

    /**
     * <pre>
     * Subscription management
     * </pre>
     */
    default void listSubscriptions(unhinged.cdc.CdcService.ListSubscriptionsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ListSubscriptionsResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListSubscriptionsMethod(), responseObserver);
    }

    /**
     */
    default void updateSubscription(unhinged.cdc.CdcService.UpdateSubscriptionRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.UpdateSubscriptionResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getUpdateSubscriptionMethod(), responseObserver);
    }

    /**
     */
    default void deleteSubscription(unhinged.cdc.CdcService.DeleteSubscriptionRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.DeleteSubscriptionResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDeleteSubscriptionMethod(), responseObserver);
    }

    /**
     * <pre>
     * Health and status
     * </pre>
     */
    default void getServiceStatus(unhinged.cdc.CdcService.GetServiceStatusRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.GetServiceStatusResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetServiceStatusMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service CDCService.
   */
  public static abstract class CDCServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return CDCServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service CDCService.
   */
  public static final class CDCServiceStub
      extends io.grpc.stub.AbstractAsyncStub<CDCServiceStub> {
    private CDCServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CDCServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CDCServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Event publishing
     * </pre>
     */
    public void publishEvent(unhinged.cdc.CdcService.PublishEventRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.PublishEventResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getPublishEventMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void publishEvents(unhinged.cdc.CdcService.PublishEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.PublishEventsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getPublishEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Event subscription (streaming)
     * </pre>
     */
    public void subscribe(unhinged.cdc.CdcService.SubscribeRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.EventStreamResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getSubscribeMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void acknowledgeEvents(unhinged.cdc.CdcService.AcknowledgeEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.AcknowledgeEventsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getAcknowledgeEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Event replay
     * </pre>
     */
    public void replayEvents(unhinged.cdc.CdcService.ReplayEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.EventStreamResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getReplayEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Dead letter queue
     * </pre>
     */
    public void listDeadLetterEvents(unhinged.cdc.CdcService.ListDeadLetterEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ListDeadLetterEventsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListDeadLetterEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void reprocessDeadLetterEvents(unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getReprocessDeadLetterEventsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Analytics
     * </pre>
     */
    public void getEventStats(unhinged.cdc.CdcService.GetEventStatsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.GetEventStatsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetEventStatsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Subscription management
     * </pre>
     */
    public void listSubscriptions(unhinged.cdc.CdcService.ListSubscriptionsRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ListSubscriptionsResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListSubscriptionsMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void updateSubscription(unhinged.cdc.CdcService.UpdateSubscriptionRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.UpdateSubscriptionResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getUpdateSubscriptionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void deleteSubscription(unhinged.cdc.CdcService.DeleteSubscriptionRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.DeleteSubscriptionResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getDeleteSubscriptionMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Health and status
     * </pre>
     */
    public void getServiceStatus(unhinged.cdc.CdcService.GetServiceStatusRequest request,
        io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.GetServiceStatusResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetServiceStatusMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service CDCService.
   */
  public static final class CDCServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<CDCServiceBlockingStub> {
    private CDCServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CDCServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CDCServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Event publishing
     * </pre>
     */
    public unhinged.cdc.CdcService.PublishEventResponse publishEvent(unhinged.cdc.CdcService.PublishEventRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getPublishEventMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.cdc.CdcService.PublishEventsResponse publishEvents(unhinged.cdc.CdcService.PublishEventsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getPublishEventsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Event subscription (streaming)
     * </pre>
     */
    public java.util.Iterator<unhinged.cdc.CdcService.EventStreamResponse> subscribe(
        unhinged.cdc.CdcService.SubscribeRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getSubscribeMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.cdc.CdcService.AcknowledgeEventsResponse acknowledgeEvents(unhinged.cdc.CdcService.AcknowledgeEventsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getAcknowledgeEventsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Event replay
     * </pre>
     */
    public java.util.Iterator<unhinged.cdc.CdcService.EventStreamResponse> replayEvents(
        unhinged.cdc.CdcService.ReplayEventsRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getReplayEventsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Dead letter queue
     * </pre>
     */
    public unhinged.cdc.CdcService.ListDeadLetterEventsResponse listDeadLetterEvents(unhinged.cdc.CdcService.ListDeadLetterEventsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListDeadLetterEventsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse reprocessDeadLetterEvents(unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getReprocessDeadLetterEventsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Analytics
     * </pre>
     */
    public unhinged.cdc.CdcService.GetEventStatsResponse getEventStats(unhinged.cdc.CdcService.GetEventStatsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetEventStatsMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Subscription management
     * </pre>
     */
    public unhinged.cdc.CdcService.ListSubscriptionsResponse listSubscriptions(unhinged.cdc.CdcService.ListSubscriptionsRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListSubscriptionsMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.cdc.CdcService.UpdateSubscriptionResponse updateSubscription(unhinged.cdc.CdcService.UpdateSubscriptionRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getUpdateSubscriptionMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.cdc.CdcService.DeleteSubscriptionResponse deleteSubscription(unhinged.cdc.CdcService.DeleteSubscriptionRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getDeleteSubscriptionMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Health and status
     * </pre>
     */
    public unhinged.cdc.CdcService.GetServiceStatusResponse getServiceStatus(unhinged.cdc.CdcService.GetServiceStatusRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetServiceStatusMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service CDCService.
   */
  public static final class CDCServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<CDCServiceFutureStub> {
    private CDCServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CDCServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CDCServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Event publishing
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.PublishEventResponse> publishEvent(
        unhinged.cdc.CdcService.PublishEventRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getPublishEventMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.PublishEventsResponse> publishEvents(
        unhinged.cdc.CdcService.PublishEventsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getPublishEventsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.AcknowledgeEventsResponse> acknowledgeEvents(
        unhinged.cdc.CdcService.AcknowledgeEventsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getAcknowledgeEventsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Dead letter queue
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.ListDeadLetterEventsResponse> listDeadLetterEvents(
        unhinged.cdc.CdcService.ListDeadLetterEventsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListDeadLetterEventsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse> reprocessDeadLetterEvents(
        unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getReprocessDeadLetterEventsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Analytics
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.GetEventStatsResponse> getEventStats(
        unhinged.cdc.CdcService.GetEventStatsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetEventStatsMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Subscription management
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.ListSubscriptionsResponse> listSubscriptions(
        unhinged.cdc.CdcService.ListSubscriptionsRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListSubscriptionsMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.UpdateSubscriptionResponse> updateSubscription(
        unhinged.cdc.CdcService.UpdateSubscriptionRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getUpdateSubscriptionMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.DeleteSubscriptionResponse> deleteSubscription(
        unhinged.cdc.CdcService.DeleteSubscriptionRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getDeleteSubscriptionMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Health and status
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.cdc.CdcService.GetServiceStatusResponse> getServiceStatus(
        unhinged.cdc.CdcService.GetServiceStatusRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetServiceStatusMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_PUBLISH_EVENT = 0;
  private static final int METHODID_PUBLISH_EVENTS = 1;
  private static final int METHODID_SUBSCRIBE = 2;
  private static final int METHODID_ACKNOWLEDGE_EVENTS = 3;
  private static final int METHODID_REPLAY_EVENTS = 4;
  private static final int METHODID_LIST_DEAD_LETTER_EVENTS = 5;
  private static final int METHODID_REPROCESS_DEAD_LETTER_EVENTS = 6;
  private static final int METHODID_GET_EVENT_STATS = 7;
  private static final int METHODID_LIST_SUBSCRIPTIONS = 8;
  private static final int METHODID_UPDATE_SUBSCRIPTION = 9;
  private static final int METHODID_DELETE_SUBSCRIPTION = 10;
  private static final int METHODID_GET_SERVICE_STATUS = 11;

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
        case METHODID_PUBLISH_EVENT:
          serviceImpl.publishEvent((unhinged.cdc.CdcService.PublishEventRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.PublishEventResponse>) responseObserver);
          break;
        case METHODID_PUBLISH_EVENTS:
          serviceImpl.publishEvents((unhinged.cdc.CdcService.PublishEventsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.PublishEventsResponse>) responseObserver);
          break;
        case METHODID_SUBSCRIBE:
          serviceImpl.subscribe((unhinged.cdc.CdcService.SubscribeRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.EventStreamResponse>) responseObserver);
          break;
        case METHODID_ACKNOWLEDGE_EVENTS:
          serviceImpl.acknowledgeEvents((unhinged.cdc.CdcService.AcknowledgeEventsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.AcknowledgeEventsResponse>) responseObserver);
          break;
        case METHODID_REPLAY_EVENTS:
          serviceImpl.replayEvents((unhinged.cdc.CdcService.ReplayEventsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.EventStreamResponse>) responseObserver);
          break;
        case METHODID_LIST_DEAD_LETTER_EVENTS:
          serviceImpl.listDeadLetterEvents((unhinged.cdc.CdcService.ListDeadLetterEventsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ListDeadLetterEventsResponse>) responseObserver);
          break;
        case METHODID_REPROCESS_DEAD_LETTER_EVENTS:
          serviceImpl.reprocessDeadLetterEvents((unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse>) responseObserver);
          break;
        case METHODID_GET_EVENT_STATS:
          serviceImpl.getEventStats((unhinged.cdc.CdcService.GetEventStatsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.GetEventStatsResponse>) responseObserver);
          break;
        case METHODID_LIST_SUBSCRIPTIONS:
          serviceImpl.listSubscriptions((unhinged.cdc.CdcService.ListSubscriptionsRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.ListSubscriptionsResponse>) responseObserver);
          break;
        case METHODID_UPDATE_SUBSCRIPTION:
          serviceImpl.updateSubscription((unhinged.cdc.CdcService.UpdateSubscriptionRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.UpdateSubscriptionResponse>) responseObserver);
          break;
        case METHODID_DELETE_SUBSCRIPTION:
          serviceImpl.deleteSubscription((unhinged.cdc.CdcService.DeleteSubscriptionRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.DeleteSubscriptionResponse>) responseObserver);
          break;
        case METHODID_GET_SERVICE_STATUS:
          serviceImpl.getServiceStatus((unhinged.cdc.CdcService.GetServiceStatusRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.cdc.CdcService.GetServiceStatusResponse>) responseObserver);
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
          getPublishEventMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.PublishEventRequest,
              unhinged.cdc.CdcService.PublishEventResponse>(
                service, METHODID_PUBLISH_EVENT)))
        .addMethod(
          getPublishEventsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.PublishEventsRequest,
              unhinged.cdc.CdcService.PublishEventsResponse>(
                service, METHODID_PUBLISH_EVENTS)))
        .addMethod(
          getSubscribeMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.SubscribeRequest,
              unhinged.cdc.CdcService.EventStreamResponse>(
                service, METHODID_SUBSCRIBE)))
        .addMethod(
          getAcknowledgeEventsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.AcknowledgeEventsRequest,
              unhinged.cdc.CdcService.AcknowledgeEventsResponse>(
                service, METHODID_ACKNOWLEDGE_EVENTS)))
        .addMethod(
          getReplayEventsMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.ReplayEventsRequest,
              unhinged.cdc.CdcService.EventStreamResponse>(
                service, METHODID_REPLAY_EVENTS)))
        .addMethod(
          getListDeadLetterEventsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.ListDeadLetterEventsRequest,
              unhinged.cdc.CdcService.ListDeadLetterEventsResponse>(
                service, METHODID_LIST_DEAD_LETTER_EVENTS)))
        .addMethod(
          getReprocessDeadLetterEventsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.ReprocessDeadLetterEventsRequest,
              unhinged.cdc.CdcService.ReprocessDeadLetterEventsResponse>(
                service, METHODID_REPROCESS_DEAD_LETTER_EVENTS)))
        .addMethod(
          getGetEventStatsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.GetEventStatsRequest,
              unhinged.cdc.CdcService.GetEventStatsResponse>(
                service, METHODID_GET_EVENT_STATS)))
        .addMethod(
          getListSubscriptionsMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.ListSubscriptionsRequest,
              unhinged.cdc.CdcService.ListSubscriptionsResponse>(
                service, METHODID_LIST_SUBSCRIPTIONS)))
        .addMethod(
          getUpdateSubscriptionMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.UpdateSubscriptionRequest,
              unhinged.cdc.CdcService.UpdateSubscriptionResponse>(
                service, METHODID_UPDATE_SUBSCRIPTION)))
        .addMethod(
          getDeleteSubscriptionMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.DeleteSubscriptionRequest,
              unhinged.cdc.CdcService.DeleteSubscriptionResponse>(
                service, METHODID_DELETE_SUBSCRIPTION)))
        .addMethod(
          getGetServiceStatusMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.cdc.CdcService.GetServiceStatusRequest,
              unhinged.cdc.CdcService.GetServiceStatusResponse>(
                service, METHODID_GET_SERVICE_STATUS)))
        .build();
  }

  private static abstract class CDCServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    CDCServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return unhinged.cdc.CdcService.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("CDCService");
    }
  }

  private static final class CDCServiceFileDescriptorSupplier
      extends CDCServiceBaseDescriptorSupplier {
    CDCServiceFileDescriptorSupplier() {}
  }

  private static final class CDCServiceMethodDescriptorSupplier
      extends CDCServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    CDCServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (CDCServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new CDCServiceFileDescriptorSupplier())
              .addMethod(getPublishEventMethod())
              .addMethod(getPublishEventsMethod())
              .addMethod(getSubscribeMethod())
              .addMethod(getAcknowledgeEventsMethod())
              .addMethod(getReplayEventsMethod())
              .addMethod(getListDeadLetterEventsMethod())
              .addMethod(getReprocessDeadLetterEventsMethod())
              .addMethod(getGetEventStatsMethod())
              .addMethod(getListSubscriptionsMethod())
              .addMethod(getUpdateSubscriptionMethod())
              .addMethod(getDeleteSubscriptionMethod())
              .addMethod(getGetServiceStatusMethod())
              .build();
        }
      }
    }
    return result;
  }
}
