import React, { useState } from "react";

export default function RAG(){
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [answer, setAnswer] = useState<string>("");

  const run = async ()=>{
    setResults([]);
    setAnswer("");
    try{
      const resp = await fetch("/inference/retrieve", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({query, top_k:5, rerank:true})
      });
      const data = await resp.json();
      setResults(data.retrieved || []);
      setAnswer(data.answer?.text || "");
    }catch(err:any){
      setAnswer("Erro: " + (err.message || err));
    }
  };

  return (
    <div className="card">
      <h3>RAG — Retrieval</h3>
      <div style={{display:"flex",gap:8}}>
        <input className="input" value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Pergunta para recuperar contexto..." />
        <button className="button" onClick={run}>Buscar</button>
      </div>
      <div style={{marginTop:12}}>
        <strong>Answer:</strong>
        <div className="small">{answer}</div>
      </div>
      <div style={{marginTop:12}}>
        <strong>Retrieved:</strong>
        {results.map((r,i)=>(
          <div key={i} className="card" style={{marginTop:8}}>
            <div><strong>{r.id}</strong> — score: {r.score?.toFixed?.(3) ?? r.score}</div>
            <div className="small">{r.text?.slice(0,400)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}