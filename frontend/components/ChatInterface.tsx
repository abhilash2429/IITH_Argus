/**
 * ChatInterface — Full chat UI with RAG.
 * User messages right-aligned blue. AI messages left-aligned grey.
 * Sources badge per response. Suggested starter questions.
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { chatWithCamV1 } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

interface ChatInterfaceProps {
  companyId: string;
  companyName: string;
}

const STARTER_QUESTIONS = [
  'What are the key risk factors for this company?',
  'Summarize the financial health in 3 bullet points.',
  'Are there any litigation red flags?',
  'What is the recommended loan structure?',
  'Explain the DSCR and debt-to-equity situation.',
];

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export default function ChatInterface({ companyId, companyName }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    if (!UUID_REGEX.test(companyId)) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'This appraisal session is invalid or expired. Please run analysis again from Upload.',
        },
      ]);
      return;
    }

    const userMsg: Message = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatWithCamV1(companyId, text);
      const assistantMsg: Message = {
        role: 'assistant',
        content: response?.response || 'No response available for this question yet.',
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const detail =
        err?.response?.data?.data?.message ||
        err?.response?.data?.detail ||
        err?.message ||
        'Please try again.';
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Sorry, I encountered an error. ${detail}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {messages.length === 0 && (
          <div className="text-center mt-8">
            <p className="text-slate-400 mb-6">Ask anything about {companyName}&apos;s credit appraisal</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {STARTER_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="px-3 py-2 text-sm bg-slate-800/60 border border-slate-600 rounded-lg text-slate-300 hover:text-white hover:border-blue-500 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-2xl px-4 py-3 ${msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700/80 text-slate-200'
                }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {msg.sources.map((s, j) => (
                    <span
                      key={j}
                      className="px-2 py-0.5 text-xs rounded-full bg-blue-900/50 text-blue-300 border border-blue-700/50"
                    >
                      📄 {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700/80 rounded-2xl px-4 py-3">
              <p className="text-slate-400 text-sm animate-pulse">Thinking...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-700 p-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
            placeholder="Ask about this credit appraisal..."
            className="flex-1 px-4 py-3 bg-slate-800/60 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 text-white rounded-xl font-medium transition-all"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
