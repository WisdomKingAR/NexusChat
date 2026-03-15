import { useEffect, useState, useRef } from 'react';
import wsManager from '../utils/ws';
import api from '../utils/api';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';
import { Send, Trash2, ShieldAlert } from 'lucide-react';
import { parseCommand } from '../utils/commandParser';
import anime from 'animejs';

const ChatPanel = ({ room }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!room) return;

    const fetchMessages = async () => {
      try {
        const res = await api.get(`/api/rooms/${room.id}/messages`);
        setMessages(res.data);
      } catch (error) {
        toast.error('Failed to load messages');
      }
    };

    fetchMessages();

    // Connect WebSocket
    const token = localStorage.getItem('token');
    setIsConnecting(true);
    
    wsManager.connect(room.id, token, {
      onConnect: () => setIsConnecting(false),
      onMessage: (data) => {
        if (data.type === 'new_message') {
          setMessages(prev => [...prev, data.message]);
        } else if (data.type === 'delete_message') {
          setMessages(prev => prev.filter(m => m.id !== data.message_id));
        } else if (data.type === 'role_updated') {
            // Locally update role in messages if sender_id matches
            setMessages(prev => prev.map(m => m.sender_id === data.user_id ? { ...m, sender_role: data.new_role } : m));
        }
      },
      onDisconnect: () => setIsConnecting(false),
      onError: () => {
        toast.error('Connection error');
        setIsConnecting(false);
      }
    });

    return () => wsManager.disconnect();
  }, [room]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
    
    // Animate the last message if added
    if (messages.length > 0) {
        const lastMsgId = messages[messages.length - 1].id;
        anime({
            targets: `[data-msg-id="${lastMsgId}"]`,
            translateY: [20, 0],
            opacity: [0, 1],
            duration: 800,
            easing: 'easeOutElastic(1, .8)'
        });
    }
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const cmd = parseCommand(input);
    if (cmd) {
      try {
        const res = await api.post('/api/commands', { 
            command: cmd.command, 
            args: cmd.args, 
            room_id: room.id 
        });
        // Add system message to local state
        const systemMsg = {
            id: 'sys-' + Date.now(),
            content: res.data.message,
            sender_id: 'system',
            sender_name: 'Nexus SYSTEM',
            sender_role: 'system',
            created_at: new Date().toISOString(),
            is_system: true
        };
        setMessages(prev => [...prev, systemMsg]);
        setInput('');
        return;
      } catch (error) {
        toast.error('Failed to execute command');
      }
    }

    try {
      await api.post(`/api/rooms/${room.id}/messages`, { content: input });
      setInput('');
    } catch (error) {
      toast.error('Failed to send message');
    }
  };

  const handleDelete = async (msgId) => {
    try {
      await api.delete(`/api/messages/${msgId}`);
      toast.success('Message deleted');
    } catch (error) {
      toast.error('Failed to delete message');
    }
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Room Header */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-background-secondary px-6 py-3">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-accent">#</span>
          <h2 className="text-lg font-semibold">{room.name}</h2>
          {isConnecting && <span className="text-xs text-text-secondary animate-pulse">Connecting...</span>}
        </div>
      </div>

      {/* Messages List */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar"
      >
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            data-msg-id={msg.id}
            className={`group flex items-start gap-3 ${msg.sender_id === user.id ? 'flex-row-reverse' : ''} ${msg.is_system ? 'justify-center w-full !my-6' : ''}`}
          >
            {!msg.is_system && (
                <div className={`flex h-8 w-8 items-center justify-center rounded-full bg-slate-700 text-xs font-bold uppercase ring-2 ring-slate-800`}>
                {msg.sender_name.substring(0, 2)}
                </div>
            )}
            
            <div className={`space-y-1 ${msg.is_system ? 'max-w-xl w-full' : 'max-w-[70%]'}`}>
              {!msg.is_system && (
                <div className={`flex items-center gap-2 ${msg.sender_id === user.id ? 'justify-end' : ''}`}>
                    <span className="text-xs font-bold text-text-secondary">{msg.sender_name}</span>
                    <span className={`text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded font-bold
                    ${msg.sender_role === 'admin' ? 'text-role-admin bg-role-admin/10' : 
                        msg.sender_role === 'moderator' ? 'text-role-moderator bg-role-moderator/10' : 
                        'text-role-participant bg-role-participant/10'}`}>
                    {msg.sender_role}
                    </span>
                </div>
              )}

              <div className={`rounded-2xl px-4 py-2 relative group transition-all duration-300
                ${msg.is_system 
                    ? 'bg-accent/5 border border-accent/20 text-accent text-center rounded-xl p-4 flex flex-col items-center' 
                    : msg.sender_id === user.id 
                        ? 'bg-accent text-white rounded-tr-none shadow-lg shadow-accent/20' 
                        : 'bg-slate-800 text-slate-100 rounded-tl-none border border-slate-700/50'}`}>
                
                {msg.is_system && <ShieldAlert className="mb-2 opacity-50" size={24} />}
                <p className={`text-sm whitespace-pre-wrap ${msg.is_system ? 'font-medium' : ''}`}>{msg.content}</p>
                
                {!msg.is_system && (user.role === 'admin' || user.role === 'moderator' || msg.sender_id === user.id) && (
                  <button 
                    onClick={() => handleDelete(msg.id)}
                    className={`absolute -top-1 ${msg.sender_id === user.id ? '-left-8' : '-right-8'} p-1.5 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all`}
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
              
              {!msg.is_system && (
                <p className={`text-[10px] text-text-secondary ${msg.sender_id === user.id ? 'text-right' : ''}`}>
                    {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Message Input */}
      <form onSubmit={handleSend} className="p-4 bg-background-secondary border-t border-slate-800">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder={`Message #${room.name}...`}
            className="flex-1 rounded-lg bg-background border border-slate-700 px-4 py-2 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all text-sm"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button 
            type="submit"
            className="rounded-lg bg-accent p-2 text-white hover:bg-accent-hover transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatPanel;
