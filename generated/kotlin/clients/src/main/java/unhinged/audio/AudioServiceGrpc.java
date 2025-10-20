package unhinged.audio;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 **
 * Audio processing service for TTS and STT operations
 * 
 * Uses common streaming patterns for consistent behavior
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: audio.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class AudioServiceGrpc {

  private AudioServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "unhinged.audio.v1.AudioService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<unhinged.audio.TTSRequest,
      unhinged.common.StreamChunk> getTextToSpeechMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "TextToSpeech",
      requestType = unhinged.audio.TTSRequest.class,
      responseType = unhinged.common.StreamChunk.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.audio.TTSRequest,
      unhinged.common.StreamChunk> getTextToSpeechMethod() {
    io.grpc.MethodDescriptor<unhinged.audio.TTSRequest, unhinged.common.StreamChunk> getTextToSpeechMethod;
    if ((getTextToSpeechMethod = AudioServiceGrpc.getTextToSpeechMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getTextToSpeechMethod = AudioServiceGrpc.getTextToSpeechMethod) == null) {
          AudioServiceGrpc.getTextToSpeechMethod = getTextToSpeechMethod =
              io.grpc.MethodDescriptor.<unhinged.audio.TTSRequest, unhinged.common.StreamChunk>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "TextToSpeech"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.TTSRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.StreamChunk.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("TextToSpeech"))
              .build();
        }
      }
    }
    return getTextToSpeechMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.common.StreamChunk,
      unhinged.audio.STTResponse> getSpeechToTextMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "SpeechToText",
      requestType = unhinged.common.StreamChunk.class,
      responseType = unhinged.audio.STTResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.CLIENT_STREAMING)
  public static io.grpc.MethodDescriptor<unhinged.common.StreamChunk,
      unhinged.audio.STTResponse> getSpeechToTextMethod() {
    io.grpc.MethodDescriptor<unhinged.common.StreamChunk, unhinged.audio.STTResponse> getSpeechToTextMethod;
    if ((getSpeechToTextMethod = AudioServiceGrpc.getSpeechToTextMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getSpeechToTextMethod = AudioServiceGrpc.getSpeechToTextMethod) == null) {
          AudioServiceGrpc.getSpeechToTextMethod = getSpeechToTextMethod =
              io.grpc.MethodDescriptor.<unhinged.common.StreamChunk, unhinged.audio.STTResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.CLIENT_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "SpeechToText"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.StreamChunk.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.STTResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("SpeechToText"))
              .build();
        }
      }
    }
    return getSpeechToTextMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.audio.ProcessAudioRequest,
      unhinged.audio.ProcessAudioResponse> getProcessAudioFileMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ProcessAudioFile",
      requestType = unhinged.audio.ProcessAudioRequest.class,
      responseType = unhinged.audio.ProcessAudioResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.audio.ProcessAudioRequest,
      unhinged.audio.ProcessAudioResponse> getProcessAudioFileMethod() {
    io.grpc.MethodDescriptor<unhinged.audio.ProcessAudioRequest, unhinged.audio.ProcessAudioResponse> getProcessAudioFileMethod;
    if ((getProcessAudioFileMethod = AudioServiceGrpc.getProcessAudioFileMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getProcessAudioFileMethod = AudioServiceGrpc.getProcessAudioFileMethod) == null) {
          AudioServiceGrpc.getProcessAudioFileMethod = getProcessAudioFileMethod =
              io.grpc.MethodDescriptor.<unhinged.audio.ProcessAudioRequest, unhinged.audio.ProcessAudioResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ProcessAudioFile"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.ProcessAudioRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.ProcessAudioResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("ProcessAudioFile"))
              .build();
        }
      }
    }
    return getProcessAudioFileMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.audio.ListVoicesRequest,
      unhinged.audio.ListVoicesResponse> getListVoicesMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListVoices",
      requestType = unhinged.audio.ListVoicesRequest.class,
      responseType = unhinged.audio.ListVoicesResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.audio.ListVoicesRequest,
      unhinged.audio.ListVoicesResponse> getListVoicesMethod() {
    io.grpc.MethodDescriptor<unhinged.audio.ListVoicesRequest, unhinged.audio.ListVoicesResponse> getListVoicesMethod;
    if ((getListVoicesMethod = AudioServiceGrpc.getListVoicesMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getListVoicesMethod = AudioServiceGrpc.getListVoicesMethod) == null) {
          AudioServiceGrpc.getListVoicesMethod = getListVoicesMethod =
              io.grpc.MethodDescriptor.<unhinged.audio.ListVoicesRequest, unhinged.audio.ListVoicesResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListVoices"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.ListVoicesRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.ListVoicesResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("ListVoices"))
              .build();
        }
      }
    }
    return getListVoicesMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.audio.GetVoiceRequest,
      unhinged.audio.GetVoiceResponse> getGetVoiceMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetVoice",
      requestType = unhinged.audio.GetVoiceRequest.class,
      responseType = unhinged.audio.GetVoiceResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.audio.GetVoiceRequest,
      unhinged.audio.GetVoiceResponse> getGetVoiceMethod() {
    io.grpc.MethodDescriptor<unhinged.audio.GetVoiceRequest, unhinged.audio.GetVoiceResponse> getGetVoiceMethod;
    if ((getGetVoiceMethod = AudioServiceGrpc.getGetVoiceMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getGetVoiceMethod = AudioServiceGrpc.getGetVoiceMethod) == null) {
          AudioServiceGrpc.getGetVoiceMethod = getGetVoiceMethod =
              io.grpc.MethodDescriptor.<unhinged.audio.GetVoiceRequest, unhinged.audio.GetVoiceResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetVoice"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.GetVoiceRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.GetVoiceResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("GetVoice"))
              .build();
        }
      }
    }
    return getGetVoiceMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.audio.CreateCustomVoiceRequest,
      unhinged.audio.CreateCustomVoiceResponse> getCreateCustomVoiceMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "CreateCustomVoice",
      requestType = unhinged.audio.CreateCustomVoiceRequest.class,
      responseType = unhinged.audio.CreateCustomVoiceResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.audio.CreateCustomVoiceRequest,
      unhinged.audio.CreateCustomVoiceResponse> getCreateCustomVoiceMethod() {
    io.grpc.MethodDescriptor<unhinged.audio.CreateCustomVoiceRequest, unhinged.audio.CreateCustomVoiceResponse> getCreateCustomVoiceMethod;
    if ((getCreateCustomVoiceMethod = AudioServiceGrpc.getCreateCustomVoiceMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getCreateCustomVoiceMethod = AudioServiceGrpc.getCreateCustomVoiceMethod) == null) {
          AudioServiceGrpc.getCreateCustomVoiceMethod = getCreateCustomVoiceMethod =
              io.grpc.MethodDescriptor.<unhinged.audio.CreateCustomVoiceRequest, unhinged.audio.CreateCustomVoiceResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "CreateCustomVoice"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.CreateCustomVoiceRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.CreateCustomVoiceResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("CreateCustomVoice"))
              .build();
        }
      }
    }
    return getCreateCustomVoiceMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.audio.ConvertAudioRequest,
      unhinged.audio.ConvertAudioResponse> getConvertAudioFormatMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ConvertAudioFormat",
      requestType = unhinged.audio.ConvertAudioRequest.class,
      responseType = unhinged.audio.ConvertAudioResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.audio.ConvertAudioRequest,
      unhinged.audio.ConvertAudioResponse> getConvertAudioFormatMethod() {
    io.grpc.MethodDescriptor<unhinged.audio.ConvertAudioRequest, unhinged.audio.ConvertAudioResponse> getConvertAudioFormatMethod;
    if ((getConvertAudioFormatMethod = AudioServiceGrpc.getConvertAudioFormatMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getConvertAudioFormatMethod = AudioServiceGrpc.getConvertAudioFormatMethod) == null) {
          AudioServiceGrpc.getConvertAudioFormatMethod = getConvertAudioFormatMethod =
              io.grpc.MethodDescriptor.<unhinged.audio.ConvertAudioRequest, unhinged.audio.ConvertAudioResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ConvertAudioFormat"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.ConvertAudioRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.ConvertAudioResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("ConvertAudioFormat"))
              .build();
        }
      }
    }
    return getConvertAudioFormatMethod;
  }

  private static volatile io.grpc.MethodDescriptor<unhinged.audio.AnalyzeAudioRequest,
      unhinged.audio.AnalyzeAudioResponse> getAnalyzeAudioMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "AnalyzeAudio",
      requestType = unhinged.audio.AnalyzeAudioRequest.class,
      responseType = unhinged.audio.AnalyzeAudioResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<unhinged.audio.AnalyzeAudioRequest,
      unhinged.audio.AnalyzeAudioResponse> getAnalyzeAudioMethod() {
    io.grpc.MethodDescriptor<unhinged.audio.AnalyzeAudioRequest, unhinged.audio.AnalyzeAudioResponse> getAnalyzeAudioMethod;
    if ((getAnalyzeAudioMethod = AudioServiceGrpc.getAnalyzeAudioMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getAnalyzeAudioMethod = AudioServiceGrpc.getAnalyzeAudioMethod) == null) {
          AudioServiceGrpc.getAnalyzeAudioMethod = getAnalyzeAudioMethod =
              io.grpc.MethodDescriptor.<unhinged.audio.AnalyzeAudioRequest, unhinged.audio.AnalyzeAudioResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "AnalyzeAudio"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.AnalyzeAudioRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.audio.AnalyzeAudioResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("AnalyzeAudio"))
              .build();
        }
      }
    }
    return getAnalyzeAudioMethod;
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
    if ((getHealthCheckMethod = AudioServiceGrpc.getHealthCheckMethod) == null) {
      synchronized (AudioServiceGrpc.class) {
        if ((getHealthCheckMethod = AudioServiceGrpc.getHealthCheckMethod) == null) {
          AudioServiceGrpc.getHealthCheckMethod = getHealthCheckMethod =
              io.grpc.MethodDescriptor.<unhinged.common.HealthCheckRequest, unhinged.common.HealthCheckResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "HealthCheck"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.HealthCheckRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  unhinged.common.HealthCheckResponse.getDefaultInstance()))
              .setSchemaDescriptor(new AudioServiceMethodDescriptorSupplier("HealthCheck"))
              .build();
        }
      }
    }
    return getHealthCheckMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static AudioServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<AudioServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<AudioServiceStub>() {
        @java.lang.Override
        public AudioServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new AudioServiceStub(channel, callOptions);
        }
      };
    return AudioServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static AudioServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<AudioServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<AudioServiceBlockingStub>() {
        @java.lang.Override
        public AudioServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new AudioServiceBlockingStub(channel, callOptions);
        }
      };
    return AudioServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static AudioServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<AudioServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<AudioServiceFutureStub>() {
        @java.lang.Override
        public AudioServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new AudioServiceFutureStub(channel, callOptions);
        }
      };
    return AudioServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   **
   * Audio processing service for TTS and STT operations
   * 
   * Uses common streaming patterns for consistent behavior
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * Text-to-Speech (streaming audio output)
     * </pre>
     */
    default void textToSpeech(unhinged.audio.TTSRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getTextToSpeechMethod(), responseObserver);
    }

    /**
     * <pre>
     * Speech-to-Text (streaming audio input)
     * </pre>
     */
    default io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> speechToText(
        io.grpc.stub.StreamObserver<unhinged.audio.STTResponse> responseObserver) {
      return io.grpc.stub.ServerCalls.asyncUnimplementedStreamingCall(getSpeechToTextMethod(), responseObserver);
    }

    /**
     * <pre>
     * Batch processing
     * </pre>
     */
    default void processAudioFile(unhinged.audio.ProcessAudioRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.ProcessAudioResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getProcessAudioFileMethod(), responseObserver);
    }

    /**
     * <pre>
     * Voice management
     * </pre>
     */
    default void listVoices(unhinged.audio.ListVoicesRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.ListVoicesResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListVoicesMethod(), responseObserver);
    }

    /**
     */
    default void getVoice(unhinged.audio.GetVoiceRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.GetVoiceResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetVoiceMethod(), responseObserver);
    }

    /**
     */
    default void createCustomVoice(unhinged.audio.CreateCustomVoiceRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.CreateCustomVoiceResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getCreateCustomVoiceMethod(), responseObserver);
    }

    /**
     * <pre>
     * Audio utilities
     * </pre>
     */
    default void convertAudioFormat(unhinged.audio.ConvertAudioRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.ConvertAudioResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getConvertAudioFormatMethod(), responseObserver);
    }

    /**
     */
    default void analyzeAudio(unhinged.audio.AnalyzeAudioRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.AnalyzeAudioResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getAnalyzeAudioMethod(), responseObserver);
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
   * Base class for the server implementation of the service AudioService.
   * <pre>
   **
   * Audio processing service for TTS and STT operations
   * 
   * Uses common streaming patterns for consistent behavior
   * </pre>
   */
  public static abstract class AudioServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return AudioServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service AudioService.
   * <pre>
   **
   * Audio processing service for TTS and STT operations
   * 
   * Uses common streaming patterns for consistent behavior
   * </pre>
   */
  public static final class AudioServiceStub
      extends io.grpc.stub.AbstractAsyncStub<AudioServiceStub> {
    private AudioServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected AudioServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new AudioServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Text-to-Speech (streaming audio output)
     * </pre>
     */
    public void textToSpeech(unhinged.audio.TTSRequest request,
        io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getTextToSpeechMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Speech-to-Text (streaming audio input)
     * </pre>
     */
    public io.grpc.stub.StreamObserver<unhinged.common.StreamChunk> speechToText(
        io.grpc.stub.StreamObserver<unhinged.audio.STTResponse> responseObserver) {
      return io.grpc.stub.ClientCalls.asyncClientStreamingCall(
          getChannel().newCall(getSpeechToTextMethod(), getCallOptions()), responseObserver);
    }

    /**
     * <pre>
     * Batch processing
     * </pre>
     */
    public void processAudioFile(unhinged.audio.ProcessAudioRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.ProcessAudioResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getProcessAudioFileMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Voice management
     * </pre>
     */
    public void listVoices(unhinged.audio.ListVoicesRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.ListVoicesResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListVoicesMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getVoice(unhinged.audio.GetVoiceRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.GetVoiceResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetVoiceMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void createCustomVoice(unhinged.audio.CreateCustomVoiceRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.CreateCustomVoiceResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getCreateCustomVoiceMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Audio utilities
     * </pre>
     */
    public void convertAudioFormat(unhinged.audio.ConvertAudioRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.ConvertAudioResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getConvertAudioFormatMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void analyzeAudio(unhinged.audio.AnalyzeAudioRequest request,
        io.grpc.stub.StreamObserver<unhinged.audio.AnalyzeAudioResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getAnalyzeAudioMethod(), getCallOptions()), request, responseObserver);
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
   * A stub to allow clients to do synchronous rpc calls to service AudioService.
   * <pre>
   **
   * Audio processing service for TTS and STT operations
   * 
   * Uses common streaming patterns for consistent behavior
   * </pre>
   */
  public static final class AudioServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<AudioServiceBlockingStub> {
    private AudioServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected AudioServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new AudioServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Text-to-Speech (streaming audio output)
     * </pre>
     */
    public java.util.Iterator<unhinged.common.StreamChunk> textToSpeech(
        unhinged.audio.TTSRequest request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getTextToSpeechMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Batch processing
     * </pre>
     */
    public unhinged.audio.ProcessAudioResponse processAudioFile(unhinged.audio.ProcessAudioRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getProcessAudioFileMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Voice management
     * </pre>
     */
    public unhinged.audio.ListVoicesResponse listVoices(unhinged.audio.ListVoicesRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListVoicesMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.audio.GetVoiceResponse getVoice(unhinged.audio.GetVoiceRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetVoiceMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.audio.CreateCustomVoiceResponse createCustomVoice(unhinged.audio.CreateCustomVoiceRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getCreateCustomVoiceMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Audio utilities
     * </pre>
     */
    public unhinged.audio.ConvertAudioResponse convertAudioFormat(unhinged.audio.ConvertAudioRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getConvertAudioFormatMethod(), getCallOptions(), request);
    }

    /**
     */
    public unhinged.audio.AnalyzeAudioResponse analyzeAudio(unhinged.audio.AnalyzeAudioRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getAnalyzeAudioMethod(), getCallOptions(), request);
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
   * A stub to allow clients to do ListenableFuture-style rpc calls to service AudioService.
   * <pre>
   **
   * Audio processing service for TTS and STT operations
   * 
   * Uses common streaming patterns for consistent behavior
   * </pre>
   */
  public static final class AudioServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<AudioServiceFutureStub> {
    private AudioServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected AudioServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new AudioServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Batch processing
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.audio.ProcessAudioResponse> processAudioFile(
        unhinged.audio.ProcessAudioRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getProcessAudioFileMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Voice management
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.audio.ListVoicesResponse> listVoices(
        unhinged.audio.ListVoicesRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListVoicesMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.audio.GetVoiceResponse> getVoice(
        unhinged.audio.GetVoiceRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetVoiceMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.audio.CreateCustomVoiceResponse> createCustomVoice(
        unhinged.audio.CreateCustomVoiceRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getCreateCustomVoiceMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Audio utilities
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.audio.ConvertAudioResponse> convertAudioFormat(
        unhinged.audio.ConvertAudioRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getConvertAudioFormatMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<unhinged.audio.AnalyzeAudioResponse> analyzeAudio(
        unhinged.audio.AnalyzeAudioRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getAnalyzeAudioMethod(), getCallOptions()), request);
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

  private static final int METHODID_TEXT_TO_SPEECH = 0;
  private static final int METHODID_PROCESS_AUDIO_FILE = 1;
  private static final int METHODID_LIST_VOICES = 2;
  private static final int METHODID_GET_VOICE = 3;
  private static final int METHODID_CREATE_CUSTOM_VOICE = 4;
  private static final int METHODID_CONVERT_AUDIO_FORMAT = 5;
  private static final int METHODID_ANALYZE_AUDIO = 6;
  private static final int METHODID_HEALTH_CHECK = 7;
  private static final int METHODID_SPEECH_TO_TEXT = 8;

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
        case METHODID_TEXT_TO_SPEECH:
          serviceImpl.textToSpeech((unhinged.audio.TTSRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.common.StreamChunk>) responseObserver);
          break;
        case METHODID_PROCESS_AUDIO_FILE:
          serviceImpl.processAudioFile((unhinged.audio.ProcessAudioRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.audio.ProcessAudioResponse>) responseObserver);
          break;
        case METHODID_LIST_VOICES:
          serviceImpl.listVoices((unhinged.audio.ListVoicesRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.audio.ListVoicesResponse>) responseObserver);
          break;
        case METHODID_GET_VOICE:
          serviceImpl.getVoice((unhinged.audio.GetVoiceRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.audio.GetVoiceResponse>) responseObserver);
          break;
        case METHODID_CREATE_CUSTOM_VOICE:
          serviceImpl.createCustomVoice((unhinged.audio.CreateCustomVoiceRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.audio.CreateCustomVoiceResponse>) responseObserver);
          break;
        case METHODID_CONVERT_AUDIO_FORMAT:
          serviceImpl.convertAudioFormat((unhinged.audio.ConvertAudioRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.audio.ConvertAudioResponse>) responseObserver);
          break;
        case METHODID_ANALYZE_AUDIO:
          serviceImpl.analyzeAudio((unhinged.audio.AnalyzeAudioRequest) request,
              (io.grpc.stub.StreamObserver<unhinged.audio.AnalyzeAudioResponse>) responseObserver);
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
        case METHODID_SPEECH_TO_TEXT:
          return (io.grpc.stub.StreamObserver<Req>) serviceImpl.speechToText(
              (io.grpc.stub.StreamObserver<unhinged.audio.STTResponse>) responseObserver);
        default:
          throw new AssertionError();
      }
    }
  }

  public static final io.grpc.ServerServiceDefinition bindService(AsyncService service) {
    return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
        .addMethod(
          getTextToSpeechMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              unhinged.audio.TTSRequest,
              unhinged.common.StreamChunk>(
                service, METHODID_TEXT_TO_SPEECH)))
        .addMethod(
          getSpeechToTextMethod(),
          io.grpc.stub.ServerCalls.asyncClientStreamingCall(
            new MethodHandlers<
              unhinged.common.StreamChunk,
              unhinged.audio.STTResponse>(
                service, METHODID_SPEECH_TO_TEXT)))
        .addMethod(
          getProcessAudioFileMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.audio.ProcessAudioRequest,
              unhinged.audio.ProcessAudioResponse>(
                service, METHODID_PROCESS_AUDIO_FILE)))
        .addMethod(
          getListVoicesMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.audio.ListVoicesRequest,
              unhinged.audio.ListVoicesResponse>(
                service, METHODID_LIST_VOICES)))
        .addMethod(
          getGetVoiceMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.audio.GetVoiceRequest,
              unhinged.audio.GetVoiceResponse>(
                service, METHODID_GET_VOICE)))
        .addMethod(
          getCreateCustomVoiceMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.audio.CreateCustomVoiceRequest,
              unhinged.audio.CreateCustomVoiceResponse>(
                service, METHODID_CREATE_CUSTOM_VOICE)))
        .addMethod(
          getConvertAudioFormatMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.audio.ConvertAudioRequest,
              unhinged.audio.ConvertAudioResponse>(
                service, METHODID_CONVERT_AUDIO_FORMAT)))
        .addMethod(
          getAnalyzeAudioMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.audio.AnalyzeAudioRequest,
              unhinged.audio.AnalyzeAudioResponse>(
                service, METHODID_ANALYZE_AUDIO)))
        .addMethod(
          getHealthCheckMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              unhinged.common.HealthCheckRequest,
              unhinged.common.HealthCheckResponse>(
                service, METHODID_HEALTH_CHECK)))
        .build();
  }

  private static abstract class AudioServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    AudioServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return unhinged.audio.AudioProto.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("AudioService");
    }
  }

  private static final class AudioServiceFileDescriptorSupplier
      extends AudioServiceBaseDescriptorSupplier {
    AudioServiceFileDescriptorSupplier() {}
  }

  private static final class AudioServiceMethodDescriptorSupplier
      extends AudioServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    AudioServiceMethodDescriptorSupplier(java.lang.String methodName) {
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
      synchronized (AudioServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new AudioServiceFileDescriptorSupplier())
              .addMethod(getTextToSpeechMethod())
              .addMethod(getSpeechToTextMethod())
              .addMethod(getProcessAudioFileMethod())
              .addMethod(getListVoicesMethod())
              .addMethod(getGetVoiceMethod())
              .addMethod(getCreateCustomVoiceMethod())
              .addMethod(getConvertAudioFormatMethod())
              .addMethod(getAnalyzeAudioMethod())
              .addMethod(getHealthCheckMethod())
              .build();
        }
      }
    }
    return result;
  }
}
