import { useState, useEffect, useRef } from 'react';
import api from '../utils/api';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';
import { Send, User as UserIcon, Shield } from 'lucide-react';
import { dmWsManager } from '../utils/ws';
import anime from 'animejs';

const DmChatPanel = ({ channel, onClose }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!channel) return;
    
    fetchMessages();
    
    const token = localStorage.getItem('token');
    setIsConnecting(true);
    // Prefix with dm_ so the WebSocketManager knows to use the /ws/dm/ endpoint
    dmWsManager.connect(`dm_${channel.id}`, token, {
      onMessage: (data) => {
        // Backend sends 'new_dm' for DM messages
        if (data.type === 'new_dm') {
          setMessages(prev => [...prev, data.message]);
        }
      },
      onDisconnect: () => setIsConnecting(false),
      onConnect: () => setIsConnecting(false)
    });

    return () => {
      dmWsManager.disconnect();
    };
  }, [channel.id]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      
      // Fun animation for new messages
      anime({
        targets: scrollRef.current.lastElementChild,
        translateY: [20, 0],
        opacity: [0, 1],
        easing: 'easeOutElastic(1, .8)',
        duration: 800
      });
    }
  }, [messages]);

  const fetchMessages = async () => {
    try {
      const res = await api.get(`/api/dm/channels/${channel.id}/messages`);
      setMessages(res.data);
    } catch (error) {
      toast.error('Failed to load messages');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    try {
      await api.post(`/api/dm/channels/${channel.id}/messages`, { content: input });
      setInput('');
    } catch (error) {
      toast.error('Failed to send message');
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-background-secondary px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-slate-800 flex items-center justify-center text-accent shadow-inner">
            <UserIcon size={18} />
          </div>
          <div>
            <h2 className="text-lg font-bold flex items-center gap-2">
              {channel.other_user.display_name}
              <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase ${channel.other_user.role === 'admin' ? 'bg-role-admin/10 text-role-admin' : 'bg-slate-800 text-slate-500'}`}>
                {channel.other_user.role}
              </span>
            </h2>
            <p className="text-[10px] text-text-secondary flex items-center gap-1">
                {isConnecting ? (
                    <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" /> Connecting...</span>
                ) : (
                    <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-teal-500" /> Secure Direct Message</span>
                )}
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-slate-900/20 via-transparent to-transparent"
      >
        {messages.map((msg, idx) => (
          <div 
            key={msg.id || idx} 
            className={`flex flex-col ${msg.sender_id === user.id ? 'items-end' : 'items-start'}`}
          >
            <div className={`max-w-[70%] px-4 py-2 rounded-2xl text-sm shadow-sm
              ${msg.sender_id === user.id 
                ? 'bg-accent text-white rounded-br-none' 
                : 'bg-background-secondary border border-slate-800/50 rounded-bl-none'}`}
            >
              {msg.content}
            </div>
            <span className="text-[10px] text-slate-500 mt-1 px-1">
              {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="p-4 bg-background-secondary border-t border-slate-800">
        <div className="flex items-center gap-3 max-w-5xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Message @${channel.other_user.display_name}`}
            className="flex-1 bg-background border border-slate-800 rounded-xl px-4 py-3 text-sm focus:border-accent outline-none ring-accent/20 transition-all focus:ring-4"
          />
          <button
            type="submit"
            disabled={!input.trim()}
            className="p-3 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all shadow-lg shadow-accent/20 disabled:opacity-50 disabled:grayscale"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default DmChatPanel;
