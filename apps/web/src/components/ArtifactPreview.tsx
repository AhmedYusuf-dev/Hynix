'use client';

import React from 'react';
import { Terminal, Code, Layout, Box, Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Artifact {
  id: string;
  type: 'html' | 'code' | 'mermaid' | 'markdown';
  title: string;
  content: string;
  language?: string;
}

interface ArtifactPreviewProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactPreview: React.FC<ArtifactPreviewProps> = ({ artifact, onClose }) => {
  if (!artifact) return null;

  return (
    <div className="h-full flex flex-col bg-slate-900 border-l border-slate-800 shadow-2xl">
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950/50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/10 rounded-lg">
            {artifact.type === 'html' && <Layout className="w-5 h-5 text-purple-400" />}
            {artifact.type === 'code' && <Code className="w-5 h-5 text-blue-400" />}
            {artifact.type === 'mermaid' && <Box className="w-5 h-5 text-green-400" />}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">{artifact.title}</h3>
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">{artifact.type}</span>
          </div>
        </div>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-200 transition-colors">
          <Copy className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-0 bg-[#0d1117]">
        {artifact.type === 'html' ? (
          <iframe
            srcDoc={artifact.content}
            className="w-full h-full border-none bg-white"
            title="Artifact Preview"
            sandbox="allow-scripts"
          />
        ) : (
          <pre className="p-6 text-sm font-mono leading-relaxed text-slate-300 overflow-x-auto">
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
};
