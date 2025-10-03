"use strict";(self.webpackChunkfrontend=self.webpackChunkfrontend||[]).push([[408],{408:(e,r,n)=>{n.r(r),n.d(r,{mount:()=>xe});var t,o=n(848),i=n(323),a=n(665),s=n(338),c=n(581);!function(e){e.BASIC="Basic Theme"}(t||(t={}));const d={name:t.BASIC,color:{palette:{white:"#ffffff"},text:{primary:"#ffffff",secondary:"#000000"},background:{primary:"#562b70",secondary:"#8550a6",hovered:"#f0f0f0"},border:{primary:"#301442",secondary:"#ffffff"}},fonts:{main:"Arial, sans-serif",heading:"Roboto, sans-serif"}};var l=n(600);const u=c.DU`
  body {
    margin: 0;
    padding: 0;
    /* font-family: 'Roboto', sans-serif; */
  }
`,p=({router:e})=>(0,o.jsxs)(c.NP,{theme:d,children:[(0,o.jsx)(u,{}),(0,o.jsx)(l.p,{router:e})]});var h=n(536),f=n(540),m=n(423);const b={maxDuration:3e5,sampleRate:16e3,channels:1,mimeType:"audio/webm;codecs=opus"},y=["audio/webm;codecs=opus","audio/webm","audio/mp4","audio/wav"];var g,v;!function(e){e.IDLE="idle",e.RECORDING="recording",e.PROCESSING="processing",e.COMPLETED="completed",e.ERROR="error"}(g||(g={})),function(e){e.PERMISSION_DENIED="permission_denied",e.DEVICE_NOT_FOUND="device_not_found",e.RECORDING_FAILED="recording_failed",e.TRANSCRIPTION_FAILED="transcription_failed",e.SYNTHESIS_FAILED="synthesis_failed",e.PLAYBACK_FAILED="playback_failed",e.NETWORK_ERROR="network_error",e.BROWSER_NOT_SUPPORTED="browser_not_supported"}(v||(v={}));var x=function(e,r,n,t){return new(n||(n=Promise))((function(o,i){function a(e){try{c(t.next(e))}catch(e){i(e)}}function s(e){try{c(t.throw(e))}catch(e){i(e)}}function c(e){var r;e.done?o(e.value):(r=e.value,r instanceof n?r:new n((function(e){e(r)}))).then(a,s)}c((t=t.apply(e,r||[])).next())}))};const w=(e,r)=>{const n=r||`recording-${Date.now()}.webm`;return new File([e],n,{type:e.type})},E=e=>{const r=Math.floor(e/1e3);return`${Math.floor(r/60)}:${(r%60).toString().padStart(2,"0")}`},R=(e,r,n)=>({type:e,message:r,originalError:n}),A=e=>{try{e.pause(),e.currentTime=0,e.src&&e.src.startsWith("blob:")&&URL.revokeObjectURL(e.src)}catch(e){console.warn("Failed to stop audio:",e)}};var S=function(e,r,n,t){return new(n||(n=Promise))((function(o,i){function a(e){try{c(t.next(e))}catch(e){i(e)}}function s(e){try{c(t.throw(e))}catch(e){i(e)}}function c(e){var r;e.done?o(e.value):(r=e.value,r instanceof n?r:new n((function(e){e(r)}))).then(a,s)}c((t=t.apply(e,r||[])).next())}))};const k="http://localhost:8000",I=c.I4.div`
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

`,O=c.I4.nav`
    grid-area: sidenav;
    background: ${({theme:e})=>e.color.background.secondary};
    padding: 0.5em;
    border-right: 1px solid ${({theme:e})=>e.color.border.secondary};

`,j=c.I4.main`
    grid-area: main;
    padding: 2em;
    overflow-y: auto;

`,D=c.I4.div`
    width: ${({size:e})=>e}px;
    height: ${({size:e})=>e}px;
    background-image: url('/assets/${({type:e})=>e}.svg');
    background-size: contain; // Ensure the SVG scales to fit the container
    background-repeat: no-repeat; // Prevent the SVG from repeating
    background-position: center; // Center the SVG within the container
`,T=({type:e,size:r})=>(0,o.jsx)(D,{type:e,size:r});var $,L;!function(e){e.DemonEmoji="demon_emoji",e.ChatBubbleFill="chat_bubble_fill",e.ChatBubbleLine="chat_bubble_line",e.Microphone="microphone",e.MicrophoneOff="microphone_off",e.Stop="stop"}($||($={})),function(e){e[e.Small=16]="Small",e[e.Medium=24]="Medium",e[e.Large=32]="Large"}(L||(L={}));const P=c.Ay.div`
    width: 100%;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    background: ${({theme:e})=>e.color.background.secondary};
`,M=c.Ay.div``,N=c.Ay.div``,_=c.Ay.div``,F=(c.Ay.div``,({routes:e})=>(0,o.jsxs)(P,{children:[(0,o.jsx)(M,{}),(0,o.jsx)(N,{children:e.map((e=>(0,o.jsx)(T,{size:L.Medium,type:e.icon})))}),(0,o.jsx)(_,{})]})),z=c.I4.div`
    display: flex;
    flex-direction: row;
    ${({size:e})=>void 0!==e&&`gap: ${e}px;`}
    ${({justification:e})=>e&&`justify-content: ${e};`}
    ${({alignment:e})=>e&&`align-items: ${e};`}
`,U=({size:e,justification:r,alignment:n,children:t})=>(0,o.jsx)(z,{size:e,justification:r,alignment:n,children:t});var B,G,Y;!function(e){e.Start="start",e.Center="center",e.End="end",e.SpaceBetween="space-between",e.SpaceAround="space-around",e.SpaceEvenly="space-evenly"}(B||(B={})),function(e){e.Start="start",e.Center="center",e.End="end",e.Stretch="stretch",e.Baseline="baseline"}(G||(G={})),function(e){e[e.xSmall=12]="xSmall",e[e.Small=16]="Small",e[e.Medium=24]="Medium",e[e.Large=32]="Large"}(Y||(Y={}));const H=({title:e,subtitle:r,icon:n,children:t})=>(0,o.jsxs)(I,{children:[(0,o.jsx)(O,{children:(0,o.jsx)(F,{routes:ve})}),(0,o.jsx)(C,{children:(0,o.jsxs)(U,{alignment:G.Center,size:Y.xSmall,children:[(0,o.jsx)(T,{type:$.DemonEmoji,size:L.Large}),e,r]})}),(0,o.jsx)(j,{children:t})]}),K=c.I4.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 20px;
  background: ${({theme:e})=>e.color.border.primary};
`,W=c.I4.div`
  flex: 1;
  overflow-y: auto; // Enable vertical scrolling if content overflows
  padding: 1em;
  word-wrap: break-word; // Ensure long words break and wrap to the next line
  overflow-wrap: break-word; // Ensure long words break and wrap to the next line
  white-space: pre-wrap; // Preserve whitespace and wrap text
`,V=c.I4.div``,q=c.I4.input`
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
`,J=c.i7`
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
`,Q=c.I4.div`
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
    animation: ${J} 1s infinite ease-in-out both;
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
`;const X=(e={})=>{const r=Object.assign(Object.assign({},b),e),[n,t]=(0,f.useState)(g.IDLE),[o,i]=(0,f.useState)(null),[a,s]=(0,f.useState)({level:0,peak:0,isActive:!1}),[c,d]=(0,f.useState)(0),[l,u]=(0,f.useState)(null),p=(0,f.useRef)(null),h=(0,f.useRef)(null),m=(0,f.useRef)(null),w=(0,f.useRef)(null),E=(0,f.useRef)(null),A=(0,f.useRef)(null),S=(0,f.useRef)(null),k=(0,f.useCallback)((()=>{p.current&&"inactive"!==p.current.state&&p.current.stop(),h.current&&(h.current.getTracks().forEach((e=>e.stop())),h.current=null),m.current&&(m.current.close(),m.current=null),E.current&&(cancelAnimationFrame(E.current),E.current=null),S.current&&(clearInterval(S.current),S.current=null),p.current=null,w.current=null,A.current=null}),[]),I=(0,f.useCallback)((()=>{if(!w.current)return;const e=new Float32Array(w.current.frequencyBinCount);w.current.getFloatTimeDomainData(e);const r=(e=>{let r=0;for(let n=0;n<e.length;n++)r+=Math.abs(e[n]);const n=r/e.length;return Math.min(100,Math.floor(200*n))})(e),t=r>10;s((e=>({level:r,peak:Math.max(e.peak,r),isActive:t}))),n===g.RECORDING&&(E.current=requestAnimationFrame(I))}),[n]),C=(0,f.useCallback)((e=>{try{const r=new AudioContext,n=r.createAnalyser(),t=r.createMediaStreamSource(e);n.fftSize=256,t.connect(n),m.current=r,w.current=n,I()}catch(e){console.warn("Audio analysis setup failed:",e)}}),[I]),O=(0,f.useCallback)((()=>{return e=void 0,o=void 0,s=function*(){try{u(null),t(g.RECORDING);const e=yield x(void 0,void 0,void 0,(function*(){try{if("undefined"==typeof navigator||!navigator.mediaDevices||"function"!=typeof navigator.mediaDevices.getUserMedia||"undefined"==typeof window||!window.MediaRecorder)throw R(v.BROWSER_NOT_SUPPORTED,"Browser does not support audio recording");return yield navigator.mediaDevices.getUserMedia({audio:{sampleRate:b.sampleRate,channelCount:b.channels,echoCancellation:!0,noiseSuppression:!0,autoGainControl:!0}})}catch(e){if(e instanceof Error){if("NotAllowedError"===e.name||"PermissionDeniedError"===e.name)throw R(v.PERMISSION_DENIED,e.message,e);if("NotFoundError"===e.name||"DevicesNotFoundError"===e.name)throw R(v.DEVICE_NOT_FOUND,e.message,e)}throw R(v.RECORDING_FAILED,"Failed to access microphone",e)}}));h.current=e,C(e);const o=(()=>{if("undefined"==typeof window||!window.MediaRecorder)return b.mimeType;for(const e of y)if(MediaRecorder.isTypeSupported(e))return e;return b.mimeType})(),a=new MediaRecorder(e,{mimeType:o}),s=[];a.ondataavailable=e=>{e.data.size>0&&s.push(e.data)},a.onstop=()=>{const e=new Blob(s,{type:o}),r=Date.now(),n={blob:e,duration:A.current?r-A.current:0,size:e.size,mimeType:o,timestamp:new Date};i(n),t(g.COMPLETED),k()},a.onerror=e=>{const r=R(v.RECORDING_FAILED,"Recording failed unexpectedly");u(r),t(g.ERROR),k()},p.current=a,A.current=Date.now(),a.start(),S.current=setInterval((()=>{A.current&&d(Date.now()-A.current)}),100),setTimeout((()=>{n===g.RECORDING&&j()}),r.maxDuration)}catch(e){u(e),t(g.ERROR),k()}},new((a=void 0)||(a=Promise))((function(r,n){function t(e){try{c(s.next(e))}catch(e){n(e)}}function i(e){try{c(s.throw(e))}catch(e){n(e)}}function c(e){var n;e.done?r(e.value):(n=e.value,n instanceof a?n:new a((function(e){e(n)}))).then(t,i)}c((s=s.apply(e,o||[])).next())}));var e,o,a,s}),[r.maxDuration,C,k,n]),j=(0,f.useCallback)((()=>{p.current&&"recording"===p.current.state&&(t(g.PROCESSING),p.current.stop())}),[]),D=(0,f.useCallback)((()=>{i(null),d(0),u(null),s({level:0,peak:0,isActive:!1}),t(g.IDLE),k()}),[k]);return(0,f.useEffect)((()=>k),[k]),{recordingState:n,recording:o,audioLevel:a,duration:c,error:l,startRecording:O,stopRecording:j,clearRecording:D,isRecording:n===g.RECORDING}};var Z,ee;!function(e){e.PRIMARY="primary",e.SECONDARY="secondary",e.COMPACT="compact"}(Z||(Z={})),function(e){e.SMALL="small",e.MEDIUM="medium",e.LARGE="large"}(ee||(ee={}));const re=c.i7`
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
`,ne=c.i7`
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
`,te=c.Ay.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  
  ${({disabled:e})=>e&&c.AH`
    opacity: 0.5;
    pointer-events: none;
  `}
`,oe={[ee.SMALL]:c.AH`
    width: 32px;
    height: 32px;
    font-size: 14px;
  `,[ee.MEDIUM]:c.AH`
    width: 40px;
    height: 40px;
    font-size: 16px;
  `,[ee.LARGE]:c.AH`
    width: 48px;
    height: 48px;
    font-size: 18px;
  `},ie={[Z.PRIMARY]:c.AH`
    background: ${({theme:e})=>e.color.background.secondary};
    color: ${({theme:e})=>e.color.text.primary};
    border: 2px solid ${({theme:e})=>e.color.border.primary};
    
    &:hover:not(:disabled) {
      background: ${({theme:e})=>e.color.background.hovered};
    }
  `,[Z.SECONDARY]:c.AH`
    background: transparent;
    color: ${({theme:e})=>e.color.text.primary};
    border: 2px solid ${({theme:e})=>e.color.border.secondary};
    
    &:hover:not(:disabled) {
      background: ${({theme:e})=>e.color.background.secondary};
    }
  `,[Z.COMPACT]:c.AH`
    background: ${({theme:e})=>e.color.background.primary};
    color: ${({theme:e})=>e.color.text.primary};
    border: 1px solid ${({theme:e})=>e.color.border.primary};
    
    &:hover:not(:disabled) {
      background: ${({theme:e})=>e.color.background.secondary};
    }
  `},ae=c.Ay.button`
  ${({size:e})=>oe[e]}
  ${({variant:e})=>ie[e]}
  
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
    animation: ${re} 1.5s ease-in-out infinite;
    background: #ff4444 !important;
    color: white;
  `}
  
  ${({hasError:e})=>e&&c.AH`
    background: #ff6b6b !important;
    color: white;
  `}
`,se=c.Ay.div`
  position: absolute;
  ${({size:e})=>oe[e]}
  border-radius: 50%;
  pointer-events: none;
  z-index: -1;
`,ce=c.Ay.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  border: 2px solid ${({theme:e})=>e.color.border.secondary};
  opacity: 0;
  
  ${({isActive:e,level:r})=>e&&c.AH`
    animation: ${ne} 1s ease-out infinite;
    border-color: ${r>70?"#ff4444":r>40?"#ffaa00":"#44ff44"};
  `}
`,de=c.Ay.span`
  font-family: ${({theme:e})=>e.fonts.main};
  font-size: 14px;
  color: ${({theme:e})=>e.color.text.primary};
  font-weight: 500;
  min-width: 40px;
  text-align: center;
  
  ${({variant:e})=>e===Z.COMPACT&&c.AH`
    font-size: 12px;
    min-width: 35px;
  `}
`,le=c.Ay.span`
  font-family: ${({theme:e})=>e.fonts.main};
  font-size: 12px;
  color: ${({theme:e,isError:r})=>r?"#ff6b6b":e.color.text.primary};
  opacity: 0.8;
  
  ${({variant:e})=>e===Z.COMPACT&&c.AH`
    font-size: 11px;
  `}
`,ue=c.Ay.div`
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
`;var pe=function(e,r,n,t){return new(n||(n=Promise))((function(o,i){function a(e){try{c(t.next(e))}catch(e){i(e)}}function s(e){try{c(t.throw(e))}catch(e){i(e)}}function c(e){var r;e.done?o(e.value):(r=e.value,r instanceof n?r:new n((function(e){e(r)}))).then(a,s)}c((t=t.apply(e,r||[])).next())}))};const he=e=>{switch(e){case ee.SMALL:return L.Small;case ee.MEDIUM:return L.Medium;case ee.LARGE:return L.Large;default:return L.Medium}},fe=({onTranscription:e,onError:r,onRecordingStart:n,onRecordingStop:t,variant:i=Z.PRIMARY,size:a=ee.MEDIUM,disabled:s=!1,placeholder:c="Click to record",showAudioLevel:d=!0,showDuration:l=!0,className:u,maxDuration:p})=>{const[h,b]=(0,f.useState)({isTranscribing:!1,lastTranscription:null,hasError:!1}),{recordingState:y,recording:x,audioLevel:A,duration:I,error:C,startRecording:O,stopRecording:j,clearRecording:D,isRecording:L}=X({maxDuration:p}),P=(0,m.n)({mutationFn:e=>S(void 0,void 0,void 0,(function*(){try{const r=new FormData;r.append("audio",e);const n=yield fetch(`${k}/transcribe`,{method:"POST",body:r});if(!n.ok){const e=yield n.text();throw R(v.TRANSCRIPTION_FAILED,`Transcription service error: ${n.status} - ${e}`)}const t=yield n.json();if(!t.text)throw R(v.TRANSCRIPTION_FAILED,"Invalid response from transcription service");return{text:t.text,language:t.language||"unknown",confidence:t.confidence}}catch(e){if(e instanceof TypeError&&e.message.includes("fetch"))throw R(v.NETWORK_ERROR,"Could not connect to transcription service");if(e&&"object"==typeof e&&"type"in e)throw e;throw R(v.TRANSCRIPTION_FAILED,e instanceof Error?e.message:"Unknown transcription error")}}))}),M=(0,f.useCallback)((r=>{b((e=>Object.assign(Object.assign({},e),{isTranscribing:!1,lastTranscription:r,hasError:!1}))),e(r),D()}),[e,D]),N=(0,f.useCallback)((e=>{b((e=>Object.assign(Object.assign({},e),{isTranscribing:!1,hasError:!0}))),null==r||r(e)}),[r]),_=(0,f.useCallback)((e=>pe(void 0,void 0,void 0,(function*(){try{b((e=>Object.assign(Object.assign({},e),{isTranscribing:!0,hasError:!1})));const r=yield P.mutateAsync(e);M(r)}catch(e){N({type:"transcription_failed",message:"Could not transcribe audio. Please try speaking more clearly.",originalError:e})}}))),[P,M,N]),F=(0,f.useCallback)((()=>pe(void 0,void 0,void 0,(function*(){if(!s)if(L)j(),null==t||t();else try{yield O(),null==n||n()}catch(e){const n=e;b((e=>Object.assign(Object.assign({},e),{hasError:!0}))),null==r||r(n)}}))),[s,L,O,j,n,t,r]);(0,f.useEffect)((()=>{if(y===g.COMPLETED&&x)try{(e=>{if(e.size>10485760)throw R(v.RECORDING_FAILED,"Audio file is too large. Please record a shorter message.");if(!e.type.startsWith("audio/"))throw R(v.RECORDING_FAILED,"Invalid file type. Please record audio only.")})(w(x.blob));const e=w(x.blob);_(e)}catch(e){N(e)}}),[y,x,_,N]),(0,f.useEffect)((()=>{C&&(b((e=>Object.assign(Object.assign({},e),{hasError:!0}))),null==r||r(C))}),[C,r]);const z=()=>h.hasError?"Error occurred":h.isTranscribing?"Transcribing...":y===g.PROCESSING?"Processing...":L?"Recording...":c,U=h.hasError||y===g.ERROR;return(0,o.jsxs)(te,{variant:i,size:a,disabled:s,className:u,children:[(0,o.jsxs)(ae,{variant:i,size:a,isRecording:L,hasError:U,onClick:F,disabled:s||h.isTranscribing,title:z(),children:[h.isTranscribing?(0,o.jsx)(ue,{}):(0,o.jsx)(T,{type:h.hasError?$.MicrophoneOff:L?$.Stop:$.Microphone,size:he(a)}),d&&L&&(0,o.jsx)(se,{size:a,children:(0,o.jsx)(ce,{level:A.level,isActive:A.isActive})})]}),l&&L&&(0,o.jsx)(de,{variant:i,children:E(I)}),i!==Z.COMPACT&&(0,o.jsx)(le,{variant:i,isError:U,children:z()})]})};var me;!function(e){e.Sent="sent",e.Received="received"}(me||(me={}));const be=c.Ay.div`
  background: ${({theme:e})=>e.color.background.secondary};
  padding: 1em;
  border-radius: 10px;
  margin-bottom: 1em;
  max-width: 80%;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  align-self: flex-end;
`,ye=({type:e,message:r})=>{const n=e===me.Sent?B.End:B.Start;return(0,o.jsx)(U,{justification:n,alignment:G.Center,children:(0,o.jsx)(be,{type:e,message:r,children:r})})},ge=c.Ay.button`
  background: ${({enabled:e,theme:r})=>e?r.color.background.primary:r.color.background.secondary};
  color: ${({theme:e})=>e.color.text.primary};
  border: 2px solid ${({enabled:e,theme:r})=>e?"#4CAF50":r.color.border.primary};
  border-radius: 8px;
  padding: 10px 15px;
  font-size: 18px;
  cursor: ${({disabled:e})=>e?"not-allowed":"pointer"};
  transition: all 0.2s ease;
  min-width: 50px;

  &:hover:not(:disabled) {
    background: ${({enabled:e,theme:r})=>e?"#45a049":r.color.background.primary};
    transform: translateY(-1px);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
  }

  ${({isPlaying:e})=>e&&"\n    animation: pulse 1s infinite;\n\n    @keyframes pulse {\n      0% { opacity: 1; }\n      50% { opacity: 0.7; }\n      100% { opacity: 1; }\n    }\n  "}
`,ve=[{path:"/",element:(0,o.jsx)((()=>{const[e,r]=(0,f.useState)(),[n,t]=(0,f.useState)([]),[i,a]=(0,f.useState)(false),[s,c]=(0,f.useState)(!1),d=(0,f.useRef)(null),{mutate:l,isPending:u,isError:p,data:h,error:b}=(0,m.n)({mutationFn:e=>S(void 0,void 0,void 0,(function*(){const r=yield fetch("http://localhost:8080/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:e})});if(!r.ok)throw new Error("Failed to send message");return console.log("response",r),yield r.text()}))}),y=(0,m.n)({mutationFn:e=>S(void 0,void 0,void 0,(function*(){try{const r=yield fetch(`${k}/synthesize`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:e.text,language:e.language||"en"})});if(!r.ok){const e=yield r.text();throw R(v.SYNTHESIS_FAILED,`Speech synthesis service error: ${r.status} - ${e}`)}const n=yield r.blob();if(!n||0===n.size)throw R(v.SYNTHESIS_FAILED,"Invalid response from speech synthesis service");return{audioBlob:n,language:e.language||"en",text:e.text,duration:void 0}}catch(e){if(e instanceof TypeError&&e.message.includes("fetch"))throw R(v.NETWORK_ERROR,"Could not connect to speech synthesis service");if(e&&"object"==typeof e&&"type"in e)throw e;throw R(v.SYNTHESIS_FAILED,e instanceof Error?e.message:"Unknown speech synthesis error")}}))}),g=()=>{if(!e)return;const o={type:me.Sent,message:e};t([...n,o]),l(e),r("")};return f.useEffect((()=>{if(!h)return;const e={type:me.Received,message:h};var r,o,a,s,l;t([...n,e]),i&&(r=h,o=void 0,a=void 0,l=function*(){if(i&&r.trim())try{c(!0),d.current&&A(d.current);const o=yield y.mutateAsync({text:r.trim(),language:"en"}),i=yield(e=o.audioBlob,n=()=>{c(!1),d.current=null},t=e=>{console.error("TTS playback error:",e),c(!1),d.current=null},x(void 0,void 0,void 0,(function*(){try{if("undefined"==typeof window||!window.Audio||"function"!=typeof window.Audio)throw R(v.BROWSER_NOT_SUPPORTED,"Browser does not support audio playback");const r=URL.createObjectURL(e),o=new Audio(r);return o.onended=()=>{URL.revokeObjectURL(r),null==n||n()},o.onerror=()=>{URL.revokeObjectURL(r);const e=R(v.PLAYBACK_FAILED,"Failed to play audio");null==t||t(e)},yield o.play(),o}catch(e){if(e instanceof Error){if("NotAllowedError"===e.name)throw R(v.PLAYBACK_FAILED,"Audio playback blocked by browser. Please allow audio autoplay.");if("NotSupportedError"===e.name)throw R(v.PLAYBACK_FAILED,"Audio format not supported by browser")}throw R(v.PLAYBACK_FAILED,e instanceof Error?e.message:"Failed to play audio")}})));d.current=i}catch(e){console.error("TTS synthesis error:",e),c(!1)}var e,n,t},new((s=void 0)||(s=Promise))((function(e,r){function n(e){try{i(l.next(e))}catch(e){r(e)}}function t(e){try{i(l.throw(e))}catch(e){r(e)}}function i(r){var o;r.done?e(r.value):(o=r.value,o instanceof s?o:new s((function(e){e(o)}))).then(n,t)}i((l=l.apply(o,a||[])).next())})))}),[h,i]),console.log(n),(0,o.jsx)(H,{title:"Ero-Ero Chatroom ~.~",children:(0,o.jsxs)(K,{children:[(0,o.jsxs)(W,{children:[n.map(((e,r)=>(0,o.jsx)(ye,Object.assign({},e),r))),u&&(0,o.jsxs)(Q,{children:[(0,o.jsx)("div",{}),(0,o.jsx)("div",{}),(0,o.jsx)("div",{})]})]}),(0,o.jsx)(V,{children:(0,o.jsxs)(U,{children:[(0,o.jsx)(q,{type:"text",value:e||"",onChange:e=>{r(e.target.value)},placeholder:"Enter your message or use voice input",onKeyPress:e=>{"Enter"!==e.key||u||g()}}),(0,o.jsx)(fe,{onTranscription:e=>{const r=e.text.trim();if(r){const e={type:me.Sent,message:r};t([...n,e]),l(r)}},onError:e=>{console.error("Voice input error:",e)},variant:Z.PRIMARY,size:ee.MEDIUM,showAudioLevel:!0,showDuration:!0,disabled:u,placeholder:"Click to record"}),(0,o.jsx)(ge,{onClick:()=>{a(!i),!i&&d.current&&(A(d.current),c(!1),d.current=null)},enabled:i,isPlaying:s,disabled:u,children:s||i?"🔊":"🔇"}),(0,o.jsx)("button",{onClick:g,disabled:u||!e,children:u?"Sending...":"Send Message"})]})}),p&&(0,o.jsxs)("p",{style:{color:"red"},children:["Error: ",b instanceof Error?b.message:"Unknown error"]})]})})}),{}),icon:$.ChatBubbleFill,showOnSideNav:!0}],xe=({mountPoint:e,mountOptions:r})=>{const n=null==r?void 0:r.basename,t=void 0===n?(0,h.Ys)(Object.values(ve)):(0,h.Ys)(Object.values(ve),{basename:n}),c=new i.E,d=s.createRoot(e);return d.render((0,o.jsx)(a.Ht,{client:c,children:(0,o.jsx)(p,{router:t})})),()=>queueMicrotask((()=>d.unmount()))}}}]);