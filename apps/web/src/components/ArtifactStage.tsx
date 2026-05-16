'use client';

import React, { useState } from 'react';
import { Code2, Eye, Download, X, Copy, Check, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface Artifact {
  id: string;
  type: 'html' | 'react' | 'code' | 'mermaid' | 'svg';
  title: string;
  content: string;
  language?: string;
}

interface ArtifactStageProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactStage: React.FC<ArtifactStageProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div 
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="h-full flex flex-col bg-white border-l border-slate-200 shadow-xl z-20"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-4">
          <div className="flex bg-slate-200/50 p-0.5 rounded-lg">
            <button
              onClick={() => setActiveTab('preview')}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-all",
                activeTab === 'preview' ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
              )}
            >
              <Eye className="w-3.5 h-3.5" />
              Preview
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-all",
                activeTab === 'code' ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
              )}
            >
              <Code2 className="w-3.5 h-3.5" />
              Code
            </button>
          </div>
          <div className="h-4 w-[1px] bg-slate-200" />
          <span className="text-xs font-medium text-slate-500">{artifact.title}</span>
        </div>

        <div className="flex items-center gap-2">
          <button onClick={handleCopy} className="p-1.5 hover:bg-slate-100 rounded-md text-slate-400 transition-colors">
            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
          </button>
          <button className="p-1.5 hover:bg-slate-100 rounded-md text-slate-400 transition-colors">
            <Download className="w-4 h-4" />
          </button>
          <div className="h-4 w-[1px] bg-slate-200 mx-1" />
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-md text-slate-400 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden relative">
        <AnimatePresence mode="wait">
          {activeTab === 'preview' ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full h-full bg-white"
            >
              {artifact.type === 'html' || artifact.type === 'svg' ? (
                <iframe
                  srcDoc={artifact.content}
                  className="w-full h-full border-none"
                  title="Artifact Preview"
                  sandbox="allow-scripts"
                />
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-4">
                  <Box className="w-12 h-12 opacity-20" />
                  <p className="text-sm font-medium italic">Preview not available for this artifact type.</p>
                  <button onClick={() => setActiveTab('code')} className="text-xs text-blue-500 hover:underline">View Code instead</button>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="code"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full h-full bg-[#f8f9fa] overflow-auto p-6"
            >
              <pre className="text-sm font-mono text-slate-800 leading-relaxed">
                <code>{artifact.content}</code>
              </pre>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

const Box = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7c-2 0-3 1-3 3z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4" />
  </svg>
);
