'use client';

import React, { useRef, useEffect } from 'react';
import { Sparkles, ArrowUp, User, Paperclip } from 'lucide-react';
import { ThinkingAccordion } from './ThinkingAccordion';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

// Project Identity: Hynix 1 Mini
// Pillar 4: Neural Dialogue Interface

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
  onSendMessage: (content: string) => void;
  onArtifactDetected: (artifact: { type: string, content: string }) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  messages, 
  streamingContent, 
  isStreaming,
  onSendMessage,
  onArtifactDetected 
}) => {
  const [input, setInput] = React.useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamingContent]);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    onSendMessage(input);
    setInput('');
  };

  const parseReasoning = (text: string) => {
    // Hardened regex: catches <think>, malformed </think>, and unclosed blocks
    const thinkStart = text.indexOf('<think>');
    if (thinkStart !== -1) {
      const remaining = text.slice(thinkStart + 7);
      const thinkEnd = remaining.match(/<\/think>|<>|Final Answer:/);
      
      if (thinkEnd) {
        const endIdx = thinkEnd.index!;
        let cleanContent = remaining.slice(endIdx + thinkEnd[0].length).trim();
        
        // Final Purge: Remove stray duplicate tags or persona identifiers
        cleanContent = cleanContent
          .replace(/<\/think>/g, '')
          .replace(/I'm your Teacher for Hynix 1 Mini\./g, '')
          .replace(/As the Teacher for Hynix 1 Mini,/g, '')
          .trim();

        return {
          reasoning: remaining.slice(0, endIdx).replace('Reasoning:', '').trim(),
          content: cleanContent
        };
      } else {
        // Fallback for unclosed block
        return {
          reasoning: remaining.replace('Reasoning:', '').trim(),
          content: ""
        };
      }
    }
    return { reasoning: null, content: text };
  };

  // Artifact Detection Logic
  useEffect(() => {
    if (streamingContent && !isStreaming) {
      const codeMatch = streamingContent.match(/```(html|svg|react|mermaid)([\s\S]*?)```/);
      if (codeMatch) {
        onArtifactDetected({ type: codeMatch[1], content: codeMatch[2].trim() });
      }
    }
  }, [streamingContent, isStreaming]);

  return (
    <div className="flex flex-col h-full bg-[#F9F8F6]">
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto py-12 px-6 space-y-10">
          {messages.map((msg, i) => {
            const { reasoning, content } = parseReasoning(msg.content);
            return (
              <div key={i} className={cn("flex gap-6", msg.role === 'user' ? "flex-row-reverse" : "flex-row")}>
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm",
                  msg.role === 'user' ? "bg-slate-200" : "bg-slate-900"
                )}>
                  {msg.role === 'user' ? <User className="w-4 h-4 text-slate-500" /> : <Sparkles className="w-4 h-4 text-white" />}
                </div>
                <div className="flex-1 space-y-3">
                  {reasoning && <ThinkingAccordion content={reasoning} />}
                  <div className={cn(
                    "text-[#212121] text-[15px] leading-relaxed prose prose-slate max-w-none",
                    msg.role === 'user' ? "bg-slate-100 px-4 py-2 rounded-2xl inline-block shadow-sm" : ""
                  )}>
                    <ReactMarkdown>{content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            );
          })}
          
          {streamingContent && (
            <div className="flex gap-6 animate-in fade-in slide-in-from-bottom-2">
              <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center flex-shrink-0 mt-1 shadow-lg">
                <Sparkles className="w-4 h-4 text-white animate-pulse" />
              </div>
              <div className="flex-1 space-y-3">
                {parseReasoning(streamingContent).reasoning && (
                  <ThinkingAccordion content={parseReasoning(streamingContent).reasoning!} />
                )}
                <div className="text-[#212121] text-[15px] leading-relaxed prose prose-slate max-w-none">
                  <ReactMarkdown>{parseReasoning(streamingContent).content}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="p-6">
        <div className="max-w-3xl mx-auto relative group">
          <div className="bg-white border border-slate-200 rounded-3xl shadow-sm focus-within:border-slate-400 focus-within:shadow-md transition-all px-2 pb-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder={isStreaming ? "Hynix is thinking..." : "Message Hynix 1 Mini..."}
              className="w-full bg-transparent px-4 py-4 text-[15px] text-[#212121] placeholder:text-slate-400 focus:outline-none resize-none min-h-[64px] h-[64px]"
            />
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-1">
                <button className="p-2.5 hover:bg-slate-50 rounded-full text-slate-400 transition-colors">
                  <Paperclip className="w-5 h-5" />
                </button>
              </div>
              <button
                onClick={handleSend}
                disabled={!input.trim() || isStreaming}
                className={cn(
                  "p-2.5 rounded-2xl transition-all shadow-sm",
                  input.trim() && !isStreaming ? "bg-slate-900 text-white shadow-lg" : "bg-slate-100 text-slate-300"
                )}
              >
                <ArrowUp className="w-5 h-5" />
              </button>
            </div>
          </div>
          <p className="mt-3 text-center text-[10px] text-slate-400 font-bold tracking-widest uppercase">
             Neural Link v1.0.1 • Lab Mode
          </p>
        </div>
      </div>
    </div>
  );
};
