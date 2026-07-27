import React, { useState, useRef } from "react";
import ChatWindow from "../components/ChatWindow";
import api from "../api/client";

export default function Chat(){
  const [messages, setMessages] = useState<{role:"user"|"assistant",text:string}[]>([]);
  const [text, setText] = useState("");
  const controllerRef = useRef<AbortController|null>(null);

  const send = async ()=>{
    if(!text.trim()) return;
    const userMsg = text.trim();
    setMessages(prev=>[...prev,{role:"user",text:userMsg}]);
    setText("");
    try{
      // Try stream endpoint using fetch and read streaming chunks
      const controller = new AbortController();
      controllerRef.current = controller;
      const resp = await fetch("/inference/stream", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({messages:[{role:"user",content:userMsg}], temperature:0.2}),
        signal: controller.signal
      });
      if(!resp.ok){
        const t = await resp.text();
        throw new Error(t || resp.statusText);
      }
      const reader = resp.body?.getReader();
      if(!reader) throw new Error("No stream available");
      let assistantText = "";
      while(true){
        const {done, value} = await reader.read();
        if(done) break;
        const chunk = new TextDecoder().decode(value);
        // server sends raw chunks; adapt if SSE format: strip "data: " lines
        assistantText += chunk;
        setMessages(prev=>{
          const withoutLast = prev.filter((_,i)=>i !== prev.length-1); // keep existing
          return [...withoutLast, {role:"assistant", text: assistantText}];
        });
      }
    }catch(err:any){
      setMessages(prev=>[...prev,{role:"assistant",text:`Erro: ${err.message}`}]);
    }finally{
      controllerRef.current = null;
    }
  };

  return (
    <div className="card">
      <h3>Chat</h3>
      <ChatWindow messages={messages} />
      <div className="chat-input">
        <input className="input" value={text} onChange={(e)=>setText(e.target.value)} onKeyDown={(e)=>{ if(e.key==="Enter"){ e.preventDefault(); send(); } }} />
        <button className="button" onClick={send}>Enviar</button>
      </div>
    </div>
  );
}