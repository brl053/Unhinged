"use strict";(self.webpackChunkfrontend=self.webpackChunkfrontend||[]).push([[933],{933:(e,n,t)=>{t.r(n),t.d(n,{mount:()=>H});var r,i=t(848),o=t(323),a=t(665),d=t(338),s=t(581);!function(e){e.BASIC="Basic Theme"}(r||(r={}));const l={name:r.BASIC,color:{palette:{white:"#ffffff"},text:{primary:"#ffffff",secondary:"#000000"},background:{primary:"#562b70",secondary:"#8550a6",hovered:"#f0f0f0"},border:{primary:"#301442",secondary:"#ffffff"}},fonts:{main:"Arial, sans-serif",heading:"Roboto, sans-serif"}};var c=t(600);const h=s.DU`
  body {
    margin: 0;
    padding: 0;
    /* font-family: 'Roboto', sans-serif; */
  }
`,u=({router:e})=>(0,i.jsxs)(s.NP,{theme:l,children:[(0,i.jsx)(h,{}),(0,i.jsx)(c.p,{router:e})]});var p=t(536),m=t(540),f=t(423);const g=s.I4.div`
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
`,b=s.I4.header`
    grid-area: header;
    background: ${({theme:e})=>e.color.background.secondary};
    padding: 1em;
    border-bottom: 1px solid ${({theme:e})=>e.color.border.secondary};

`,x=s.I4.nav`
    grid-area: sidenav;
    background: ${({theme:e})=>e.color.background.secondary};
    padding: 0.5em;
    border-right: 1px solid ${({theme:e})=>e.color.border.secondary};

`,v=s.I4.main`
    grid-area: main;
    padding: 2em;
    overflow-y: auto;

`,y=s.I4.div`
    width: ${({size:e})=>e}px;
    height: ${({size:e})=>e}px;
    background-image: url('/assets/${({type:e})=>e}.svg');
    background-size: contain; // Ensure the SVG scales to fit the container
    background-repeat: no-repeat; // Prevent the SVG from repeating
    background-position: center; // Center the SVG within the container
`,w=({type:e,size:n})=>(0,i.jsx)(y,{type:e,size:n});var j,k;!function(e){e.DemonEmoji="demon_emoji",e.ChatBubbleFill="chat_bubble_fill",e.ChatBubbleLine="chat_bubble_line"}(j||(j={})),function(e){e[e.Small=16]="Small",e[e.Medium=24]="Medium",e[e.Large=32]="Large"}(k||(k={}));const S=s.Ay.div`
    width: 100%;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    background: ${({theme:e})=>e.color.background.secondary};
`,E=s.Ay.div``,$=s.Ay.div``,C=s.Ay.div``,z=(s.Ay.div``,({routes:e})=>(0,i.jsxs)(S,{children:[(0,i.jsx)(E,{}),(0,i.jsx)($,{children:e.map((e=>(0,i.jsx)(w,{size:k.Medium,type:e.icon})))}),(0,i.jsx)(C,{})]})),I=s.I4.div`
    display: flex;
    flex-direction: row;
    ${({size:e})=>void 0!==e&&`gap: ${e}px;`}
    ${({justification:e})=>e&&`justify-content: ${e};`}
    ${({alignment:e})=>e&&`align-items: ${e};`}
`,A=({size:e,justification:n,alignment:t,children:r})=>(0,i.jsx)(I,{size:e,justification:n,alignment:t,children:r});var B,P,M;!function(e){e.Start="start",e.Center="center",e.End="end",e.SpaceBetween="space-between",e.SpaceAround="space-around",e.SpaceEvenly="space-evenly"}(B||(B={})),function(e){e.Start="start",e.Center="center",e.End="end",e.Stretch="stretch",e.Baseline="baseline"}(P||(P={})),function(e){e[e.xSmall=12]="xSmall",e[e.Small=16]="Small",e[e.Medium=24]="Medium",e[e.Large=32]="Large"}(M||(M={}));const O=({title:e,subtitle:n,icon:t,children:r})=>(0,i.jsxs)(g,{children:[(0,i.jsx)(x,{children:(0,i.jsx)(z,{routes:q})}),(0,i.jsx)(b,{children:(0,i.jsxs)(A,{alignment:P.Center,size:M.xSmall,children:[(0,i.jsx)(w,{type:j.DemonEmoji,size:k.Large}),e,n]})}),(0,i.jsx)(v,{children:r})]}),R=s.I4.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 20px;
  background: ${({theme:e})=>e.color.border.primary};
`,F=s.I4.div`
  flex: 1;
  overflow-y: auto; // Enable vertical scrolling if content overflows
  padding: 1em;
  word-wrap: break-word; // Ensure long words break and wrap to the next line
  overflow-wrap: break-word; // Ensure long words break and wrap to the next line
  white-space: pre-wrap; // Preserve whitespace and wrap text
`,L=s.I4.div``,T=s.I4.input`
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
`,_=s.i7`
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
`,N=s.I4.div`
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
    animation: ${_} 1s infinite ease-in-out both;
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
`;var D;!function(e){e.Sent="sent",e.Received="received"}(D||(D={}));const G=s.Ay.div`
  background: ${({theme:e})=>e.color.background.secondary};
  padding: 1em;
  border-radius: 10px;
  margin-bottom: 1em;
  max-width: 80%;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  align-self: flex-end;
`,V=({type:e,message:n})=>{const t=e===D.Sent?B.End:B.Start;return(0,i.jsx)(A,{justification:t,alignment:P.Center,children:(0,i.jsx)(G,{type:e,message:n,children:n})})},q=[{path:"/",element:(0,i.jsx)((()=>{const[e,n]=(0,m.useState)(),[t,r]=(0,m.useState)([]),{mutate:o,isPending:a,isError:d,data:s,error:l}=(0,f.n)({mutationFn:e=>{return n=void 0,t=void 0,i=function*(){const n=yield fetch("http://localhost:8080/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:e})});if(!n.ok)throw new Error("Failed to send message");return console.log("response",n),yield n.text()},new((r=void 0)||(r=Promise))((function(e,o){function a(e){try{s(i.next(e))}catch(e){o(e)}}function d(e){try{s(i.throw(e))}catch(e){o(e)}}function s(n){var t;n.done?e(n.value):(t=n.value,t instanceof r?t:new r((function(e){e(t)}))).then(a,d)}s((i=i.apply(n,t||[])).next())}));var n,t,r,i}});return m.useEffect((()=>{if(!s)return;const e={type:D.Received,message:s};r([...t,e])}),[s]),console.log(t),(0,i.jsx)(O,{title:"Ero-Ero Chatroom ~.~",children:(0,i.jsxs)(R,{children:[(0,i.jsxs)(F,{children:[t.map(((e,n)=>(0,i.jsx)(V,Object.assign({},e),n))),a&&(0,i.jsxs)(N,{children:[(0,i.jsx)("div",{}),(0,i.jsx)("div",{}),(0,i.jsx)("div",{})]})]}),(0,i.jsx)(L,{children:(0,i.jsxs)(A,{children:[(0,i.jsx)(T,{type:"text",value:e,onChange:e=>{n(e.target.value)},placeholder:"Enter your message"}),(0,i.jsx)("button",{onClick:()=>{if(!e)return;const n={type:D.Sent,message:e};r([...t,n]),o(e)},disabled:a,children:a?"Sending...":"Send Message"})]})}),d&&(0,i.jsxs)("p",{style:{color:"red"},children:["Error: ",l instanceof Error?l.message:"Unknown error"]})]})})}),{}),icon:j.ChatBubbleFill,showOnSideNav:!0}],H=({mountPoint:e,mountOptions:n})=>{const t=null==n?void 0:n.basename,r=void 0===t?(0,p.Ys)(Object.values(q)):(0,p.Ys)(Object.values(q),{basename:t}),s=new o.E,l=d.createRoot(e);return l.render((0,i.jsx)(a.Ht,{client:s,children:(0,i.jsx)(u,{router:r})})),()=>queueMicrotask((()=>l.unmount()))}}}]);