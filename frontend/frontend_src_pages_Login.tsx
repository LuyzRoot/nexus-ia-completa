import React, { useState } from "react";
import api from "../api/client";
import { setToken } from "../utils/auth";

export default function Login(){
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [err, setErr] = useState<string>("");

  const submit = async (e:React.FormEvent)=>{
    e.preventDefault();
    try{
      const resp = await api.post("/v1/auth/login", new URLSearchParams({
        username: email, password
      }));
      // server returns {"access_token": "..."} or Token model; adjust if needed
      const token = resp.data?.access_token || resp.data?.token || resp.data?.accessToken;
      if(token){
        setToken(token);
        window.location.href = "/";
      } else {
        setErr("Token não retornado");
      }
    }catch(err:any){
      setErr(err?.response?.data?.detail || err.message || "Erro ao logar");
    }
  };

  return (
    <div className="card" style={{maxWidth:480,margin:"0 auto"}}>
      <h2>Entrar</h2>
      <form onSubmit={submit} style={{display:"grid",gap:8}}>
        <input className="input" placeholder="E-mail" value={email} onChange={(e)=>setEmail(e.target.value)} />
        <input className="input" type="password" placeholder="Senha" value={password} onChange={(e)=>setPassword(e.target.value)} />
        <div style={{display:"flex",gap:8}}>
          <button className="button" type="submit">Entrar</button>
        </div>
        {err && <div className="small" style={{color:"#fca5a5"}}>{err}</div>}
      </form>
    </div>
  );
}