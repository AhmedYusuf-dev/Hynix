'use client';

import React, { useState } from 'react';
import { ChatInterface } from '@/components/ChatInterface';
import { ArtifactStage } from '@/components/ArtifactStage';
import { useHynixLink } from '@/lib/hooks/useHynixLink';
import { Sparkles, ShieldCheck, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import { AnimatePresence } from 'framer-motion';

// Pillar 4: The Canvas - Split-Pane Architecture
// Production-Hardened for Vercel Deployment

interface Artifact {
  id: string;
  type: 'html' | 'react' | 'code' | 'mermaid' | 'svg';
  title: string;
  content: string;
  language?: string;
}

export default function Home() {
  const { messages, streamingContent, status, sendMessage } = useHynixLink();
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [showArtifacts, setShowArtifacts] = useState(false);

  const handleDetectedArtifact = (artifact: { type: any, content: string }) => {
    const fullArtifact: Artifact = {
      id: Math.random().toString(36).substr(2, 9),
      type: artifact.type,
      title: `${artifact.type.toUpperCase()} Component`,
      content: artifact.content
    };
    setActiveArtifact(fullArtifact);
    setShowArtifacts(true);
  };

  return (
    <main className="flex h-screen bg-[#F9F8F6] text-[#212121] overflow-hidden">
      {/* Dialogue Pane (Left) */}
      <div className={cn(
        "flex flex-col h-full transition-all duration-700 ease-in-out border-r border-slate-200",
        showArtifacts ? "w-1/2" : "w-full"
      )}>
        <header className="px-8 py-4 flex items-center justify-between border-b border-slate-100 bg-white/50 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
             <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow-lg shadow-slate-200">
                <Sparkles className="w-5 h-5" />
             </div>
             <div>
                <h1 className="text-sm font-bold tracking-tight">Hynix 1 Mini</h1>
                <div className="flex items-center gap-1.5">
                   <div className={cn("w-1.5 h-1.5 rounded-full", status === 'streaming' ? "bg-emerald-500 animate-pulse" : "bg-slate-300")} />
                   <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">OS Kernel v1.0.1</span>
                </div>
             </div>
          </div>
          
          <div className="flex items-center gap-4">
             <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-emerald-50/50 text-emerald-700 rounded-full border border-emerald-100 text-[10px] font-bold">
                <ShieldCheck className="w-3 h-3" />
                SECURE FLYWHEEL ACTIVE
             </div>
             {activeArtifact && !showArtifacts && (
               <button 
                onClick={() => setShowArtifacts(true)}
                className="flex items-center gap-2 px-3 py-1 bg-slate-900 text-white rounded-lg text-xs font-semibold shadow-md animate-in fade-in slide-in-from-right-2"
               >
                 <Activity className="w-3 h-3" />
                 Restore Canvas
               </button>
             )}
          </div>
        </header>

        <div className="flex-1 overflow-hidden">
           <ChatInterface 
            messages={messages} 
            streamingContent={streamingContent}
            isStreaming={status === 'streaming'}
            onSendMessage={sendMessage}
            onArtifactDetected={handleDetectedArtifact}
           />
        </div>
      </div>

      {/* Artifact Stage (Right) */}
      <AnimatePresence>
        {showArtifacts && (
          <div className="w-1/2 h-full bg-white shadow-2xl z-20">
            <ArtifactStage 
              artifact={activeArtifact} 
              onClose={() => setShowArtifacts(false)} 
            />
          </div>
        )}
      </AnimatePresence>
    </main>
  );
}
