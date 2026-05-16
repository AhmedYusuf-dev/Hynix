import { useState, useEffect, useRef, useCallback } from 'react';

// Project Identity: Hynix 1 Mini
// Pillar 4: Hardened Neural Link WebSocket Hook

export function useHynixLink() {
  const url = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/chat';
  const [messages, setMessages] = useState<any[]>([]);
  const [streamingContent, setStreamingContent] = useState('');
  const [status, setStatus] = useState<'idle' | 'linking' | 'streaming' | 'error'>('idle');
  const [lastStatus, setLastStatus] = useState('');
  
  const socketRef = useRef<WebSocket | null>(null);
  const streamRef = useRef(''); // Ref for real-time accumulation
  const messagesRef = useRef<any[]>([]); // Ref to avoid closure staleness

  // Sync refs with state
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;
    
    setStatus('linking');
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      console.log('Hynix 1 Mini: Neural Link Established.');
      setStatus('idle');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'token') {
        setStatus('streaming');
        streamRef.current += data.content;
        setStreamingContent(streamRef.current);
      } else if (data.type === 'status') {
        setLastStatus(data.content);
        if (data.content.includes('logged')) {
          setStatus('idle');
          const finalContent = streamRef.current;
          setMessages(prev => [...prev, { role: 'assistant', content: finalContent }]);
          setStreamingContent('');
          streamRef.current = '';
        }
      } else if (data.type === 'error') {
        setStatus('error');
        setLastStatus(data.content);
      }
    };
    
    ws.onerror = (err) => {
      console.error('WebSocket Error:', err);
      setStatus('error');
    };
    
    ws.onclose = () => {
      console.log('Hynix 1 Mini: Neural Link Severed.');
      setStatus('idle');
    };
    
    socketRef.current = ws;
  }, [url]);

  useEffect(() => {
    connect();
    return () => socketRef.current?.close();
  }, [connect]);

  const sendMessage = useCallback((content: string) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn('Hynix 1 Mini: Link not ready. Reconnecting...');
      connect();
      return;
    }
    
    const newMsg = { role: 'user', content };
    const updatedMessages = [...messagesRef.current, newMsg];
    
    setMessages(updatedMessages);
    setStreamingContent('');
    streamRef.current = '';
    
    socketRef.current.send(JSON.stringify({ messages: updatedMessages }));
  }, [connect]);

  return { messages, streamingContent, status, lastStatus, sendMessage, connect };
}
