import React, { useEffect, useRef } from "react";

export default function ChatWindow({messages}:{messages:{role:"user"|"assistant",text:string}[]}) {
  const ref = useRef<HTMLDivElement|null>(null);
  useEffect(()=>{
    if(ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [messages]);
  return (
    <div className="chat-window">
      <div ref={ref} className="messages">
        {messages.map((m,i)=>(
          <div key={i} className={`msg ${m.role==="user"?"user":"assistant"}`}><div dangerouslySetInnerHTML={{__html:m.text.replace(/\n/g,"<br/>")}} /></div>
        ))}
      </div>
    </div>
  );
}