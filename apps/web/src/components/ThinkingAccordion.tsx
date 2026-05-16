'use client';

import React, { useState } from 'react';
import { Brain, ChevronRight, ChevronDown, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface ThinkingAccordionProps {
  content: string;
}

export const ThinkingAccordion: React.FC<ThinkingAccordionProps> = ({ content }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2 w-full max-w-2xl mb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all duration-300 w-fit",
          isOpen 
            ? "bg-slate-100 text-slate-900 border border-slate-200" 
            : "bg-transparent text-slate-400 hover:text-slate-600 border border-transparent"
        )}
      >
        <div className="relative">
          <Brain className={cn("w-3.5 h-3.5", isOpen && "text-slate-900")} />
          {isOpen && <Sparkles className="absolute -top-1 -right-1 w-1.5 h-1.5 text-slate-400" />}
        </div>
        <span>{isOpen ? "Hide Thinking Process" : "View Thinking Process"}</span>
        {isOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="p-4 rounded-xl bg-slate-50 border border-slate-200/60 shadow-sm"
          >
            <div className="flex items-start gap-3">
              <div className="mt-1.5 flex-shrink-0 w-1 h-1 rounded-full bg-slate-300" />
              <p className="text-[13px] text-slate-500 italic leading-relaxed font-serif">
                {content}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
