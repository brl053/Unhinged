"use strict";(self.webpackChunkfrontend=self.webpackChunkfrontend||[]).push([[408],{408:(e,r,n)=>{n.r(r),n.d(r,{mount:()=>ye});var t,o=n(848),i=n(323),a=n(665),s=n(338),c=n(581);!function(e){e.BASIC="Basic Theme"}(t||(t={}));const d={name:t.BASIC,color:{palette:{white:"#ffffff"},text:{primary:"#ffffff",secondary:"#000000"},background:{primary:"#562b70",secondary:"#8550a6",hovered:"#f0f0f0"},border:{primary:"#301442",secondary:"#ffffff"}},fonts:{main:"Arial, sans-serif",heading:"Roboto, sans-serif"}};var l=n(600);const u=c.DU`
  body {
    margin: 0;
    padding: 0;
    /* font-family: 'Roboto', sans-serif; */
  }
`,p=({router:e})=>(0,o.jsxs)(c.NP,{theme:d,children:[(0,o.jsx)(u,{}),(0,o.jsx)(l.p,{router:e})]});var h=n(536),f=n(540),m=n(423);const g={maxDuration:3e5,sampleRate:16e3,channels:1,mimeType:"audio/webm;codecs=opus"},b=["audio/webm;codecs=opus","audio/webm","audio/mp4","audio/wav"];var y,v,x;!function(e){e.IDLE="idle",e.RECORDING="recording",e.PROCESSING="processing",e.COMPLETED="completed",e.ERROR="error"}(y||(y={})),(x=v||(v={})).PERMISSION_DENIED="permission_denied",x.DEVICE_NOT_FOUND="device_not_found",x.RECORDING_FAILED="recording_failed",x.TRANSCRIPTION_FAILED="transcription_failed",x.SYNTHESIS_FAILED="synthesis_failed",x.PLAYBACK_FAILED="playback_failed",x.NETWORK_ERROR="network_error",x.BROWSER_NOT_SUPPORTED="browser_not_supported";const w=()=>{return e=void 0,r=void 0,t=function*(){try{if("undefined"==typeof navigator||!navigator.mediaDevices||"function"!=typeof navigator.mediaDevices.getUserMedia||"undefined"==typeof window||!window.MediaRecorder)throw A(v.BROWSER_NOT_SUPPORTED,"Browser does not support audio recording");return yield navigator.mediaDevices.getUserMedia({audio:{sampleRate:g.sampleRate,channelCount:g.channels,echoCancellation:!0,noiseSuppression:!0,autoGainControl:!0}})}catch(e){if(e instanceof Error){if("NotAllowedError"===e.name||"PermissionDeniedError"===e.name)throw A(v.PERMISSION_DENIED,e.message,e);if("NotFoundError"===e.name||"DevicesNotFoundError"===e.name)throw A(v.DEVICE_NOT_FOUND,e.message,e)}throw A(v.RECORDING_FAILED,"Failed to access microphone",e)}},new((n=void 0)||(n=Promise))((function(o,i){function a(e){try{c(t.next(e))}catch(e){i(e)}}function s(e){try{c(t.throw(e))}catch(e){i(e)}}function c(e){var r;e.done?o(e.value):(r=e.value,r instanceof n?r:new n((function(e){e(r)}))).then(a,s)}c((t=t.apply(e,r||[])).next())}));var e,r,n,t},E=(e,r)=>{const n=r||`recording-${Date.now()}.webm`;return new File([e],n,{type:e.type})},R=e=>{const r=Math.floor(e/1e3);return`${Math.floor(r/60)}:${(r%60).toString().padStart(2,"0")}`},A=(e,r,n)=>({type:e,message:r,originalError:n});var S=function(e,r,n,t){return new(n||(n=Promise))((function(o,i){function a(e){try{c(t.next(e))}catch(e){i(e)}}function s(e){try{c(t.throw(e))}catch(e){i(e)}}function c(e){var r;e.done?o(e.value):(r=e.value,r instanceof n?r:new n((function(e){e(r)}))).then(a,s)}c((t=t.apply(e,r||[])).next())}))};const k=c.I4.div`
    display: grid;
    grid-template-rows: 65px 1fr;
    grid-template-columns: auto 1fr;
    grid-template-areas: 
        "header header"
        "sidenav main";
    height: 100vh;
    width: 100vw;
    background: ${({theme:e})=>e.color.background.primary};
    color: ${({theme:e})=>e.color.text.primary};
`,C=c.I4.header`
    grid-area: header;
    background: ${({theme:e})=>e.color.background.secondary};
    padding: 1em;
    border-bottom: 1px solid ${({theme:e})=>e.color.border.secondary};

`,j=c.I4.nav`
    grid-area: sidenav;
    background: ${({theme:e})=>e.color.background.secondary};
    padding: 0.5em;
    border-right: 1px solid ${({theme:e})=>e.color.border.secondary};

`,I=c.I4.main`
    grid-area: main;
    padding: 2em;
    overflow-y: auto;

`,O=c.I4.div`
    width: ${({size:e})=>e}px;
    height: ${({size:e})=>e}px;
    background-image: url('/assets/${({type:e})=>e}.svg');
    background-size: contain; // Ensure the SVG scales to fit the container
    background-repeat: no-repeat; // Prevent the SVG from repeating
    background-position: center; // Center the SVG within the container
`,D=({type:e,size:r})=>(0,o.jsx)(O,{type:e,size:r});var $,T;!function(e){e.DemonEmoji="demon_emoji",e.ChatBubbleFill="chat_bubble_fill",e.ChatBubbleLine="chat_bubble_line",e.Microphone="microphone",e.MicrophoneOff="microphone_off",e.Stop="stop"}($||($={})),function(e){e[e.Small=16]="Small",e[e.Medium=24]="Medium",e[e.Large=32]="Large"}(T||(T={}));const M=c.Ay.div`
    width: 100%;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    background: ${({theme:e})=>e.color.background.secondary};
`,N=c.Ay.div``,P=c.Ay.div``,_=c.Ay.div``,L=(c.Ay.div``,({routes:e})=>(0,o.jsxs)(M,{children:[(0,o.jsx)(N,{}),(0,o.jsx)(P,{children:e.map((e=>(0,o.jsx)(D,{size:T.Medium,type:e.icon})))}),(0,o.jsx)(_,{})]})),z=c.I4.div`
    display: flex;
    flex-direction: row;
    ${({size:e})=>void 0!==e&&`gap: ${e}px;`}
    ${({justification:e})=>e&&`justify-content: ${e};`}
    ${({alignment:e})=>e&&`align-items: ${e};`}
`,F=({size:e,justification:r,alignment:n,children:t})=>(0,o.jsx)(z,{size:e,justification:r,alignment:n,children:t});var G,H,B;!function(e){e.Start="start",e.Center="center",e.End="end",e.SpaceBetween="space-between",e.SpaceAround="space-around",e.SpaceEvenly="space-evenly"}(G||(G={})),function(e){e.Start="start",e.Center="center",e.End="end",e.Stretch="stretch",e.Baseline="baseline"}(H||(H={})),function(e){e[e.xSmall=12]="xSmall",e[e.Small=16]="Small",e[e.Medium=24]="Medium",e[e.Large=32]="Large"}(B||(B={}));const U=({title:e,subtitle:r,icon:n,children:t})=>(0,o.jsxs)(k,{children:[(0,o.jsx)(j,{children:(0,o.jsx)(L,{routes:be})}),(0,o.jsx)(C,{children:(0,o.jsxs)(F,{alignment:H.Center,size:B.xSmall,children:[(0,o.jsx)(D,{type:$.DemonEmoji,size:T.Large}),e,r]})}),(0,o.jsx)(I,{children:t})]}),Y=c.I4.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 20px;
  background: ${({theme:e})=>e.color.border.primary};
`,V=c.I4.div`
  flex: 1;
  overflow-y: auto; // Enable vertical scrolling if content overflows
  padding: 1em;
  word-wrap: break-word; // Ensure long words break and wrap to the next line
  overflow-wrap: break-word; // Ensure long words break and wrap to the next line
  white-space: pre-wrap; // Preserve whitespace and wrap text
`,W=c.I4.div``,q=c.I4.input`
  background-color: rgba(0, 0, 0, 0.8); // Transparent black background
  color: white; // White text color
  font-family: 'Courier New', Courier, monospace; // Terminal-esque font
  font-size: 16px; // Font size
  border: none; // Remove default border
  outline: none; // Remove default outline
  padding: 10px; // Padding inside the input
  width: 100%; // Full width
  box-sizing: border-box; // Include padding and border in element's total width and height
  /* caret-color: transparent; // Hide the default caret */
`,K=c.i7`
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
`,J=c.I4.div`
  display: inline-block;
  position: relative;
  width: 80px;
  height: 20px;

  div {
    position: absolute;
    top: 0;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: white;
    animation: ${K} 1s infinite ease-in-out both;
  }

  div:nth-child(1) {
    left: 4px;
    animation-delay: -0.32s;
  }

  div:nth-child(2) {
    left: 16px;
    animation-delay: -0.16s;
  }

  div:nth-child(3) {
    left: 28px;
  }
`;const Q=(e={})=>{const r=Object.assign(Object.assign({},g),e),[n,t]=(0,f.useState)(y.IDLE),[o,i]=(0,f.useState)(null),[a,s]=(0,f.useState)({level:0,peak:0,isActive:!1}),[c,d]=(0,f.useState)(0),[l,u]=(0,f.useState)(null),p=(0,f.useRef)(null),h=(0,f.useRef)(null),m=(0,f.useRef)(null),x=(0,f.useRef)(null),E=(0,f.useRef)(null),R=(0,f.useRef)(null),S=(0,f.useRef)(null),k=(0,f.useCallback)((()=>{p.current&&"inactive"!==p.current.state&&p.current.stop(),h.current&&(h.current.getTracks().forEach((e=>e.stop())),h.current=null),m.current&&(m.current.close(),m.current=null),E.current&&(cancelAnimationFrame(E.current),E.current=null),S.current&&(clearInterval(S.current),S.current=null),p.current=null,x.current=null,R.current=null}),[]),C=(0,f.useCallback)((()=>{if(!x.current)return;const e=new Float32Array(x.current.frequencyBinCount);x.current.getFloatTimeDomainData(e);const r=(e=>{let r=0;for(let n=0;n<e.length;n++)r+=Math.abs(e[n]);const n=r/e.length;return Math.min(100,Math.floor(200*n))})(e),t=r>10;s((e=>({level:r,peak:Math.max(e.peak,r),isActive:t}))),n===y.RECORDING&&(E.current=requestAnimationFrame(C))}),[n]),j=(0,f.useCallback)((e=>{try{const r=new AudioContext,n=r.createAnalyser(),t=r.createMediaStreamSource(e);n.fftSize=256,t.connect(n),m.current=r,x.current=n,C()}catch(e){console.warn("Audio analysis setup failed:",e)}}),[C]),I=(0,f.useCallback)((()=>{return e=void 0,o=void 0,s=function*(){try{u(null),t(y.RECORDING);const e=yield w();h.current=e,j(e);const o=(()=>{if("undefined"==typeof window||!window.MediaRecorder)return g.mimeType;for(const e of b)if(MediaRecorder.isTypeSupported(e))return e;return g.mimeType})(),a=new MediaRecorder(e,{mimeType:o}),s=[];a.ondataavailable=e=>{e.data.size>0&&s.push(e.data)},a.onstop=()=>{const e=new Blob(s,{type:o}),r=Date.now(),n={blob:e,duration:R.current?r-R.current:0,size:e.size,mimeType:o,timestamp:new Date};i(n),t(y.COMPLETED),k()},a.onerror=e=>{const r=A(v.RECORDING_FAILED,"Recording failed unexpectedly");u(r),t(y.ERROR),k()},p.current=a,R.current=Date.now(),a.start(),S.current=setInterval((()=>{R.current&&d(Date.now()-R.current)}),100),setTimeout((()=>{n===y.RECORDING&&O()}),r.maxDuration)}catch(e){u(e),t(y.ERROR),k()}},new((a=void 0)||(a=Promise))((function(r,n){function t(e){try{c(s.next(e))}catch(e){n(e)}}function i(e){try{c(s.throw(e))}catch(e){n(e)}}function c(e){var n;e.done?r(e.value):(n=e.value,n instanceof a?n:new a((function(e){e(n)}))).then(t,i)}c((s=s.apply(e,o||[])).next())}));var e,o,a,s}),[r.maxDuration,j,k,n]),O=(0,f.useCallback)((()=>{p.current&&"recording"===p.current.state&&(t(y.PROCESSING),p.current.stop())}),[]),D=(0,f.useCallback)((()=>{i(null),d(0),u(null),s({level:0,peak:0,isActive:!1}),t(y.IDLE),k()}),[k]);return(0,f.useEffect)((()=>k),[k]),{recordingState:n,recording:o,audioLevel:a,duration:c,error:l,startRecording:I,stopRecording:O,clearRecording:D,isRecording:n===y.RECORDING}};var X,Z;!function(e){e.PRIMARY="primary",e.SECONDARY="secondary",e.COMPACT="compact"}(X||(X={})),function(e){e.SMALL="small",e.MEDIUM="medium",e.LARGE="large"}(Z||(Z={}));const ee=c.i7`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`,re=c.i7`
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
`,ne=c.Ay.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  
  ${({disabled:e})=>e&&c.AH`
    opacity: 0.5;
    pointer-events: none;
  `}
`,te={[Z.SMALL]:c.AH`
    width: 32px;
    height: 32px;
    font-size: 14px;
  `,[Z.MEDIUM]:c.AH`
    width: 40px;
    height: 40px;
    font-size: 16px;
  `,[Z.LARGE]:c.AH`
    width: 48px;
    height: 48px;
    font-size: 18px;
  `},oe={[X.PRIMARY]:c.AH`
    background: ${({theme:e})=>e.color.background.secondary};
    color: ${({theme:e})=>e.color.text.primary};
    border: 2px solid ${({theme:e})=>e.color.border.primary};
    
    &:hover:not(:disabled) {
      background: ${({theme:e})=>e.color.background.hovered};
    }
  `,[X.SECONDARY]:c.AH`
    background: transparent;
    color: ${({theme:e})=>e.color.text.primary};
    border: 2px solid ${({theme:e})=>e.color.border.secondary};
    
    &:hover:not(:disabled) {
      background: ${({theme:e})=>e.color.background.secondary};
    }
  `,[X.COMPACT]:c.AH`
    background: ${({theme:e})=>e.color.background.primary};
    color: ${({theme:e})=>e.color.text.primary};
    border: 1px solid ${({theme:e})=>e.color.border.primary};
    
    &:hover:not(:disabled) {
      background: ${({theme:e})=>e.color.background.secondary};
    }
  `},ie=c.Ay.button`
  ${({size:e})=>te[e]}
  ${({variant:e})=>oe[e]}
  
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px ${({theme:e})=>e.color.border.secondary}40;
  }
  
  &:disabled {
    cursor: not-allowed;
  }
  
  ${({isRecording:e})=>e&&c.AH`
    animation: ${ee} 1.5s ease-in-out infinite;
    background: #ff4444 !important;
    color: white;
  `}
  
  ${({hasError:e})=>e&&c.AH`
    background: #ff6b6b !important;
    color: white;
  `}
`,ae=c.Ay.div`
  position: absolute;
  ${({size:e})=>te[e]}
  border-radius: 50%;
  pointer-events: none;
  z-index: -1;
`,se=c.Ay.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  border: 2px solid ${({theme:e})=>e.color.border.secondary};
  opacity: 0;
  
  ${({isActive:e,level:r})=>e&&c.AH`
    animation: ${re} 1s ease-out infinite;
    border-color: ${r>70?"#ff4444":r>40?"#ffaa00":"#44ff44"};
  `}
`,ce=c.Ay.span`
  font-family: ${({theme:e})=>e.fonts.main};
  font-size: 14px;
  color: ${({theme:e})=>e.color.text.primary};
  font-weight: 500;
  min-width: 40px;
  text-align: center;
  
  ${({variant:e})=>e===X.COMPACT&&c.AH`
    font-size: 12px;
    min-width: 35px;
  `}
`,de=c.Ay.span`
  font-family: ${({theme:e})=>e.fonts.main};
  font-size: 12px;
  color: ${({theme:e,isError:r})=>r?"#ff6b6b":e.color.text.primary};
  opacity: 0.8;
  
  ${({variant:e})=>e===X.COMPACT&&c.AH`
    font-size: 11px;
  `}
`,le=c.Ay.div`
  width: 16px;
  height: 16px;
  border: 2px solid ${({theme:e})=>e.color.border.primary};
  border-top: 2px solid ${({theme:e})=>e.color.text.primary};
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;var ue=function(e,r,n,t){return new(n||(n=Promise))((function(o,i){function a(e){try{c(t.next(e))}catch(e){i(e)}}function s(e){try{c(t.throw(e))}catch(e){i(e)}}function c(e){var r;e.done?o(e.value):(r=e.value,r instanceof n?r:new n((function(e){e(r)}))).then(a,s)}c((t=t.apply(e,r||[])).next())}))};const pe=e=>{switch(e){case Z.SMALL:return T.Small;case Z.MEDIUM:return T.Medium;case Z.LARGE:return T.Large;default:return T.Medium}},he=({onTranscription:e,onError:r,onRecordingStart:n,onRecordingStop:t,variant:i=X.PRIMARY,size:a=Z.MEDIUM,disabled:s=!1,placeholder:c="Click to record",showAudioLevel:d=!0,showDuration:l=!0,className:u,maxDuration:p})=>{const[h,g]=(0,f.useState)({isTranscribing:!1,lastTranscription:null,hasError:!1}),{recordingState:b,recording:x,audioLevel:w,duration:k,error:C,startRecording:j,stopRecording:I,clearRecording:O,isRecording:T}=Q({maxDuration:p}),M=(0,m.n)({mutationFn:e=>S(void 0,void 0,void 0,(function*(){try{const r=new FormData;r.append("audio",e);const n=yield fetch("http://localhost:8000/transcribe",{method:"POST",body:r});if(!n.ok){const e=yield n.text();throw A(v.TRANSCRIPTION_FAILED,`Transcription service error: ${n.status} - ${e}`)}const t=yield n.json();if(!t.text)throw A(v.TRANSCRIPTION_FAILED,"Invalid response from transcription service");return{text:t.text,language:t.language||"unknown",confidence:t.confidence}}catch(e){if(e instanceof TypeError&&e.message.includes("fetch"))throw A(v.NETWORK_ERROR,"Could not connect to transcription service");if(e&&"object"==typeof e&&"type"in e)throw e;throw A(v.TRANSCRIPTION_FAILED,e instanceof Error?e.message:"Unknown transcription error")}}))}),N=(0,f.useCallback)((r=>{g((e=>Object.assign(Object.assign({},e),{isTranscribing:!1,lastTranscription:r,hasError:!1}))),e(r),O()}),[e,O]),P=(0,f.useCallback)((e=>{g((e=>Object.assign(Object.assign({},e),{isTranscribing:!1,hasError:!0}))),null==r||r(e)}),[r]),_=(0,f.useCallback)((e=>ue(void 0,void 0,void 0,(function*(){try{g((e=>Object.assign(Object.assign({},e),{isTranscribing:!0,hasError:!1})));const r=yield M.mutateAsync(e);N(r)}catch(e){P({type:"transcription_failed",message:"Could not transcribe audio. Please try speaking more clearly.",originalError:e})}}))),[M,N,P]),L=(0,f.useCallback)((()=>ue(void 0,void 0,void 0,(function*(){if(!s)if(T)I(),null==t||t();else try{yield j(),null==n||n()}catch(e){const n=e;g((e=>Object.assign(Object.assign({},e),{hasError:!0}))),null==r||r(n)}}))),[s,T,j,I,n,t,r]);(0,f.useEffect)((()=>{if(b===y.COMPLETED&&x)try{(e=>{if(e.size>10485760)throw A(v.RECORDING_FAILED,"Audio file is too large. Please record a shorter message.");if(!e.type.startsWith("audio/"))throw A(v.RECORDING_FAILED,"Invalid file type. Please record audio only.")})(E(x.blob));const e=E(x.blob);_(e)}catch(e){P(e)}}),[b,x,_,P]),(0,f.useEffect)((()=>{C&&(g((e=>Object.assign(Object.assign({},e),{hasError:!0}))),null==r||r(C))}),[C,r]);const z=()=>h.hasError?"Error occurred":h.isTranscribing?"Transcribing...":b===y.PROCESSING?"Processing...":T?"Recording...":c,F=h.hasError||b===y.ERROR;return(0,o.jsxs)(ne,{variant:i,size:a,disabled:s,className:u,children:[(0,o.jsxs)(ie,{variant:i,size:a,isRecording:T,hasError:F,onClick:L,disabled:s||h.isTranscribing,title:z(),children:[h.isTranscribing?(0,o.jsx)(le,{}):(0,o.jsx)(D,{type:h.hasError?$.MicrophoneOff:T?$.Stop:$.Microphone,size:pe(a)}),d&&T&&(0,o.jsx)(ae,{size:a,children:(0,o.jsx)(se,{level:w.level,isActive:w.isActive})})]}),l&&T&&(0,o.jsx)(ce,{variant:i,children:R(k)}),i!==X.COMPACT&&(0,o.jsx)(de,{variant:i,isError:F,children:z()})]})};var fe;!function(e){e.Sent="sent",e.Received="received"}(fe||(fe={}));const me=c.Ay.div`
  background: ${({theme:e})=>e.color.background.secondary};
  padding: 1em;
  border-radius: 10px;
  margin-bottom: 1em;
  max-width: 80%;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  align-self: flex-end;
`,ge=({type:e,message:r})=>{const n=e===fe.Sent?G.End:G.Start;return(0,o.jsx)(F,{justification:n,alignment:H.Center,children:(0,o.jsx)(me,{type:e,message:r,children:r})})},be=[{path:"/",element:(0,o.jsx)((()=>{const[e,r]=(0,f.useState)(),[n,t]=(0,f.useState)([]),{mutate:i,isPending:a,isError:s,data:c,error:d}=(0,m.n)({mutationFn:e=>S(void 0,void 0,void 0,(function*(){const r=yield fetch("http://localhost:8080/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:e})});if(!r.ok)throw new Error("Failed to send message");return console.log("response",r),yield r.text()}))}),l=()=>{if(!e)return;const o={type:fe.Sent,message:e};t([...n,o]),i(e),r("")};return f.useEffect((()=>{if(!c)return;const e={type:fe.Received,message:c};t([...n,e])}),[c]),console.log(n),(0,o.jsx)(U,{title:"Ero-Ero Chatroom ~.~",children:(0,o.jsxs)(Y,{children:[(0,o.jsxs)(V,{children:[n.map(((e,r)=>(0,o.jsx)(ge,Object.assign({},e),r))),a&&(0,o.jsxs)(J,{children:[(0,o.jsx)("div",{}),(0,o.jsx)("div",{}),(0,o.jsx)("div",{})]})]}),(0,o.jsx)(W,{children:(0,o.jsxs)(F,{children:[(0,o.jsx)(q,{type:"text",value:e||"",onChange:e=>{r(e.target.value)},placeholder:"Enter your message or use voice input",onKeyPress:e=>{"Enter"!==e.key||a||l()}}),(0,o.jsx)(he,{onTranscription:e=>{const r=e.text.trim();if(r){const e={type:fe.Sent,message:r};t([...n,e]),i(r)}},onError:e=>{console.error("Voice input error:",e)},variant:X.PRIMARY,size:Z.MEDIUM,showAudioLevel:!0,showDuration:!0,disabled:a,placeholder:"Click to record"}),(0,o.jsx)("button",{onClick:l,disabled:a||!e,children:a?"Sending...":"Send Message"})]})}),s&&(0,o.jsxs)("p",{style:{color:"red"},children:["Error: ",d instanceof Error?d.message:"Unknown error"]})]})})}),{}),icon:$.ChatBubbleFill,showOnSideNav:!0}],ye=({mountPoint:e,mountOptions:r})=>{const n=null==r?void 0:r.basename,t=void 0===n?(0,h.Ys)(Object.values(be)):(0,h.Ys)(Object.values(be),{basename:n}),c=new i.E,d=s.createRoot(e);return d.render((0,o.jsx)(a.Ht,{client:c,children:(0,o.jsx)(p,{router:t})})),()=>queueMicrotask((()=>d.unmount()))}}}]);