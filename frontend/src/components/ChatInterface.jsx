import { useState, useRef, useEffect } from 'react';
import {
  ArrowLeft,
  Send,
  Bot,
  User,
  Loader2,
  Sparkles,
} from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  'What patterns do you see in this dataset?',
  'Which features are most important for predictions?',
  'Are there any anomalies or outliers I should know about?',
  'How should I handle the missing values?',
  "What's the expected accuracy of the recommended model?",
];

export default function ChatInterface({ dataset, onBack }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (content) => {
    if (!content.trim() || isLoading) return;

    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Updated to call your local FastAPI Backend
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dataset_id: dataset.id, // Links to the persistent ChromaDB collection
          message: content.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error('Server error: Failed to get response');
      }

      const data = await response.json();
      
      const assistantMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer, // Matches the JSON key from your FastAPI return
      };

      setMessages((prev) => [...prev, assistantMessage]);

    } catch (err) {
      console.error(err);
      alert(err.message || 'Failed to connect to backend');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] bg-white rounded-xl shadow-sm border p-4">
      {/* Header */}
      <div className="flex items-center gap-4 pb-4 border-b">
        <button
          onClick={onBack}
          className="p-2 rounded-md hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-gray-900">
            Ask about {dataset.name}
          </h1>
          <p className="text-sm text-gray-500">
            Persistent RAG session active
          </p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-4 px-2">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-lg font-semibold">Ready to Analyze</h2>
            <p className="text-gray-500 mb-6 max-w-sm text-sm">
              Your dataset is indexed in ChromaDB. Ask questions about patterns or model recommendations.
            </p>

            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="px-4 py-2 text-xs bg-gray-50 hover:bg-blue-50 hover:text-blue-600 border rounded-full transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-blue-600" />
                </div>
              )}

              <div
                className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'
                }`}
              >
                {m.content}
              </div>

              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <Bot className="w-4 h-4 text-blue-600" />
            </div>
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-none">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="pt-4 border-t flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          placeholder="Ask about feature importance, anomalies..."
          className="flex-1 px-4 py-3 bg-gray-50 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-sm"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-5 py-3 bg-blue-600 text-white rounded-xl disabled:bg-gray-300 transition-colors shadow-sm shadow-blue-200"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}