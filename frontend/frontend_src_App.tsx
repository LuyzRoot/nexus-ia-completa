import React from "react";
import { Routes, Route, Link, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Agents from "./pages/Agents";
import RAG from "./pages/RAG";
import Settings from "./pages/Settings";
import { getToken, logout } from "./utils/auth";

function Header(){
  const token = getToken();
  return (
    <header className="header">
      <div style={{display:"flex",gap:12,alignItems:"center"}}>
        <strong>NEXUS</strong>
        <nav style={{display:"flex",gap:12}}>
          <Link to="/" className="small">Home</Link>
          <Link to="/chat" className="small">Chat</Link>
          <Link to="/agents" className="small">Agents</Link>
          <Link to="/rag" className="small">RAG</Link>
        </nav>
      </div>
      <div>
        {token ? (
          <button className="button" onClick={()=>{ logout(); window.location.href="/login"; }}>Sair</button>
        ) : (
          <Link to="/login"><button className="button">Entrar</button></Link>
        )}
      </div>
    </header>
  );
}

export default function App(){
  return (
    <div className="app">
      <Header />
      <div className="container">
        <div className="sidebar card">
          <div><strong>Bem-vindo ao NEXUS</strong></div>
          <div className="small" style={{marginTop:8}}>Painel de administração e uso dos agentes</div>
        </div>
        <main className="content">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Private><Dashboard /></Private>} />
            <Route path="/chat" element={<Private><Chat /></Private>} />
            <Route path="/agents" element={<Private><Agents /></Private>} />
            <Route path="/rag" element={<Private><RAG /></Private>} />
            <Route path="/settings" element={<Private><Settings /></Private>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function Private({children}:{children:React.ReactNode}){
  if(!getToken()){
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}