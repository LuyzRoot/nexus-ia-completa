import React, { useEffect, useState } from "react";
import api from "../api/client";

type Agent = {id:string,label:string,description?:string};

export default function Agents(){
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string| null>(null);

  useEffect(()=>{
    (async ()=>{
      try{
        const resp = await api.get("/v1/agents");
        // if registry returns list of dicts
        const data = resp.data;
        setAgents(Array.isArray(data) ? data : []);
      }catch(err:any){
        setError(err?.response?.data?.detail || err.message || "Erro");
      }finally{ setLoading(false); }
    })();
  },[]);

  const remove = async (id:string)=>{
    try{
      await api.delete(`/v1/agents/${encodeURIComponent(id)}`);
      setAgents(prev=>prev.filter(a=>a.id!==id));
    }catch(err:any){
      alert("Erro ao deletar: " + (err?.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="card">
      <h3>Agents</h3>
      {loading ? <div>Carregando...</div> : (
        <>
          {error && <div className="small" style={{color:"#fca5a5"}}>{error}</div>}
          <div className="list">
            {agents.map(a=>(
              <div key={a.id} style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                <div>
                  <strong>{a.label}</strong>
                  <div className="small">{a.description}</div>
                </div>
                <div style={{display:"flex",gap:8}}>
                  <button className="button" onClick={()=>navigator.clipboard.writeText(a.id)}>Copiar ID</button>
                  <button className="button" onClick={()=>remove(a.id)}>Remover</button>
                </div>
              </div>
            ))}
            {agents.length===0 && <div className="small">Nenhum agente encontrado.</div>}
          </div>
        </>
      )}
    </div>
  );
}