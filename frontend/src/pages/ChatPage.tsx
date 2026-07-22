import { useEffect, useMemo, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Bot, Copy, Mic, MicOff, PanelRightClose, RefreshCcw, Sparkles, Volume2, VolumeX } from 'lucide-react';
import { chatService } from '@/services/chat.service';
import MarkdownRenderer from '@/components/MarkdownRenderer';

type Message = {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  confidence?: number;
  intent?: string;
  queryKind?: string;
  language?: string;
  suggestions?: string[];
  dataSources?: string[];
  reasoning?: string;
  prediction?: string;
  isStreaming?: boolean;
};

type ChatSession = {
  id: number;
  title: string;
  messages: Message[];
};

declare global {
  interface Window {
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
    SpeechRecognition?: new () => SpeechRecognitionLike;
  }
}

type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: { results: ArrayLike<Array<{ transcript: string }>> }) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

export default function ChatPage() {
  const [language, setLanguage] = useState<'English' | 'Kannada'>('English');
  const [question, setQuestion] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([{ id: 1, title: 'New conversation', messages: [{ id: 1, role: 'assistant', content: 'I can assist with case summaries, investigations, trends, hotspots, and predictive insights.', language }] }]);
  const [activeSessionId, setActiveSessionId] = useState(1);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  const activeSession = useMemo(() => sessions.find((session) => session.id === activeSessionId) ?? sessions[0], [activeSessionId, sessions]);

  const mutation = useMutation({
    mutationFn: async (input: string) => {
      const response = await chatService.sendMessage(input, { source: 'frontend' }, language);
      return response;
    },
    onMutate: (input) => {
      setSessions((prev) => prev.map((session) => session.id === activeSessionId ? {
        ...session,
        title: session.title === 'New conversation' ? input.slice(0, 32) : session.title,
        messages: [...session.messages, { id: Date.now(), role: 'user', content: input, language }],
      } : session));
      setSessions((prev) => prev.map((session) => session.id === activeSessionId ? {
        ...session,
        messages: [...session.messages, { id: Date.now() + 1, role: 'assistant', content: '', isStreaming: true, language }],
      } : session));
    },
    onSuccess: (response) => {
      const assistantText = response?.answer ?? 'No answer was returned.';
      const metadata = {
        confidence: response?.confidence,
        intent: response?.intent,
        queryKind: response?.query_kind,
        language: response?.response_language || language,
        suggestions: response?.suggestions ?? [],
        dataSources: Object.keys(response?.data ?? {}),
        reasoning: response?.data?.error ? `The backend reported: ${response.data.error}` : `The assistant used intent ${response?.intent ?? 'unknown'} with query kind ${response?.query_kind ?? 'unknown'}.`,
        prediction: response?.data?.prediction_dashboard ? 'Prediction summary available in the returned data payload.' : undefined,
      };

      setSessions((prev) => prev.map((session) => session.id === activeSessionId ? {
        ...session,
        messages: session.messages.map((message) => message.role === 'assistant' && message.isStreaming ? { ...message, ...metadata, content: '', isStreaming: true } : message),
      } : session));

      let streamed = '';
      const chars = assistantText.split('');
      let index = 0;
      const interval = window.setInterval(() => {
        streamed += chars[index] ?? '';
        index += 1;
        setSessions((prev) => prev.map((session) => session.id === activeSessionId ? {
          ...session,
          messages: session.messages.map((message) => message.role === 'assistant' && message.isStreaming ? { ...message, content: streamed, ...metadata } : message),
        } : session));
        if (index >= chars.length) {
          window.clearInterval(interval);
          setSessions((prev) => prev.map((session) => session.id === activeSessionId ? {
            ...session,
            messages: session.messages.map((message) => message.role === 'assistant' && message.isStreaming ? { ...message, content: assistantText, isStreaming: false } : message),
          } : session));
        }
      }, 16);
    },
    onError: () => {
      setSessions((prev) => prev.map((session) => session.id === activeSessionId ? {
        ...session,
        messages: session.messages.map((message) => message.role === 'assistant' && message.isStreaming ? { ...message, content: 'The assistant could not respond right now. Please try again in a moment.', isStreaming: false } : message),
      } : session));
    },
  });

  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) return;
    const SpeechRecognitionCtor = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) return;
    const recognition = new SpeechRecognitionCtor();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = language === 'Kannada' ? 'kn-IN' : 'en-US';
    recognition.onresult = (event: { results: ArrayLike<Array<{ transcript: string }>> }) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript ?? '')
        .join(' ');
      setQuestion(transcript);
      setIsListening(false);
    };
    recognition.onerror = () => {
      setIsListening(false);
    };
    recognition.onend = () => {
      setIsListening(false);
    };
    recognitionRef.current = recognition;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language]);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!question.trim()) return;
    mutation.mutate(question.trim());
    setQuestion('');
  };

  const handleCopy = async (content: string) => {
    await navigator.clipboard.writeText(content);
  };

  const handleSpeak = (content: string) => {
    if (!('speechSynthesis' in window)) return;
    const utterance = new SpeechSynthesisUtterance(content);
    utterance.lang = language === 'Kannada' ? 'kn-IN' : 'en-US';
    setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const handleRegenerate = () => {
    const lastUser = [...activeSession.messages].reverse().find((message) => message.role === 'user');
    if (lastUser) {
      mutation.mutate(lastUser.content);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm text-sky-400">AI investigator</p>
          <h2 className="text-2xl font-semibold">Conversational intelligence workspace</h2>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setLanguage('English')} className={`rounded-full px-3 py-2 text-sm ${language === 'English' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-300'}`}>English</button>
          <button onClick={() => setLanguage('Kannada')} className={`rounded-full px-3 py-2 text-sm ${language === 'Kannada' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-300'}`}>Kannada</button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[280px_1fr]">
        <motion.aside initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-sm text-sky-400">History</p>
              <p className="text-xs text-slate-400">Context-aware conversations</p>
            </div>
            <button onClick={() => {
              const nextId = Date.now();
              setSessions((prev) => [{ id: nextId, title: 'New conversation', messages: [{ id: nextId + 1, role: 'assistant', content: 'Ask anything about cases, trends, hotspots, or network insights.', language }] }, ...prev]);
              setActiveSessionId(nextId);
            }} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">New</button>
          </div>
          <div className="space-y-2">
            {sessions.map((session) => (
              <button key={session.id} onClick={() => setActiveSessionId(session.id)} className={`w-full rounded-2xl border px-3 py-3 text-left text-sm ${activeSessionId === session.id ? 'border-sky-500/30 bg-sky-500/10 text-slate-100' : 'border-slate-800 bg-slate-950/60 text-slate-400'}`}>
                <div className="flex items-center gap-2">
                  <Sparkles size={14} />
                  {session.title}
                </div>
              </button>
            ))}
          </div>
        </motion.aside>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl border border-slate-800 bg-slate-900/70 p-4 md:p-6">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sky-400">
              <Bot size={18} />
              <span className="text-sm">Secure backend assistant</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={handleRegenerate} className="rounded-full border border-slate-700 p-2 text-slate-300" title="Regenerate response"><RefreshCcw size={16} /></button>
              <button className="rounded-full border border-slate-700 p-2 text-slate-300" title="Toggle side panel"><PanelRightClose size={16} /></button>
            </div>
          </div>

          <div className="mb-4 space-y-3 rounded-3xl border border-slate-800 bg-slate-950/60 p-4">
            {activeSession.messages.map((message) => (
              <div key={message.id} className={`rounded-2xl border px-4 py-3 ${message.role === 'user' ? 'border-sky-500/20 bg-sky-500/10 text-slate-100' : 'border-slate-800 bg-slate-900/80 text-slate-200'}`}>
                {message.role === 'assistant' ? (
                  <div className="space-y-3">
                    <MarkdownRenderer content={message.content || 'Thinking…'} />
                    {(message.confidence !== undefined || message.intent || message.queryKind || message.dataSources?.length || message.suggestions?.length || message.prediction) && (
                      <div className="space-y-3 border-t border-slate-800 pt-3 text-sm">
                        {message.confidence !== undefined ? <div className="inline-flex rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-sky-300">Confidence {Math.round(message.confidence * 100)}%</div> : null}
                        {message.intent ? <p className="text-slate-400">Intent: {message.intent}</p> : null}
                        {message.queryKind ? <p className="text-slate-400">Query kind: {message.queryKind}</p> : null}
                        {message.dataSources?.length ? <div><p className="mb-2 text-slate-400">Data sources</p><ul className="list-disc space-y-1 pl-5 text-slate-300">{message.dataSources.map((source) => <li key={source}>{source}</li>)}</ul></div> : null}
                        {message.reasoning ? <div><p className="mb-2 text-slate-400">Reasoning</p><p className="text-slate-300">{message.reasoning}</p></div> : null}
                        {message.prediction ? <div><p className="mb-2 text-slate-400">Prediction</p><p className="text-slate-300">{message.prediction}</p></div> : null}
                        {message.suggestions?.length ? <div><p className="mb-2 text-slate-400">Suggested follow-ups</p><div className="flex flex-wrap gap-2">{message.suggestions.map((suggestion) => <button key={suggestion} onClick={() => { setQuestion(suggestion); }} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">{suggestion}</button>)}</div></div> : null}
                      </div>
                    )}
                  </div>
                ) : (
                  <p>{message.content}</p>
                )}
                {message.role === 'assistant' ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button onClick={() => handleCopy(message.content)} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">Copy</button>
                    <button onClick={() => handleSpeak(message.content)} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">{isSpeaking ? 'Speaking…' : 'Speak'}</button>
                    <button onClick={() => window.print()} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">Export PDF</button>
                  </div>
                ) : null}
              </div>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="flex flex-col gap-3 md:flex-row">
              <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder={language === 'Kannada' ? 'ಕೇಸ್ಗಳು, ಟ್ರೆಂಡ್ಗಳು ಅಥವಾ ಹಾಟ್ಸ್ಪಾಟ್ಗಳ ಬಗ್ಗೆ ಕೇಳಿ' : 'Ask about cases, trends, hotspots, or suspects'} className="flex-1 rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm outline-none" />
              <div className="flex gap-2">
                <button type="button" onClick={() => {
                  if (recognitionRef.current) {
                    if (isListening) {
                      recognitionRef.current.stop();
                      setIsListening(false);
                    } else {
                      recognitionRef.current.start();
                      setIsListening(true);
                    }
                  }
                }} className={`rounded-2xl border px-4 py-3 text-sm ${isListening ? 'border-rose-500/30 bg-rose-500/10 text-rose-300' : 'border-slate-700 bg-slate-950/70 text-slate-300'}`}>
                  {isListening ? <MicOff size={16} /> : <Mic size={16} />}
                </button>
                <button type="submit" disabled={mutation.isPending} className="rounded-2xl bg-sky-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-70">
                  {mutation.isPending ? 'Thinking…' : 'Send'}
                </button>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {['Show crime trends for 2026', 'Show hotspots in Bengaluru', 'Show case details for FIR 123/2026'].map((suggestion) => (
                <button key={suggestion} type="button" onClick={() => setQuestion(suggestion)} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">{suggestion}</button>
              ))}
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
