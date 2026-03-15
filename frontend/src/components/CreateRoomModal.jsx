import { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'sonner';
import { X, Lock, Hash, Users, Check } from 'lucide-react';

const CreateRoomModal = ({ isOpen, onClose, onRoomCreated }) => {
  const [name, setName] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [allUsers, setAllUsers] = useState([]);
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchUsers();
      setName('');
      setIsPrivate(false);
      setSelectedMembers([]);
      setSearchQuery('');
    }
  }, [isOpen]);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/api/users');
      setAllUsers(res.data);
    } catch (error) {
      toast.error('Failed to load users');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    
    setLoading(true);
    try {
      const payload = {
        name: name.trim(),
        is_private: isPrivate,
        members: isPrivate ? selectedMembers : []
      };
      const res = await api.post('/api/rooms', payload);
      toast.success(`Room #${name} created`);
      onRoomCreated(res.data);
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create room');
    } finally {
      setLoading(false);
    }
  };

  const toggleMember = (userId) => {
    setSelectedMembers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId) 
        : [...prev, userId]
    );
  };

  const filteredUsers = allUsers.filter(u => 
    u.display_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="w-full max-w-md bg-background-secondary rounded-2xl border border-slate-800 shadow-2xl overflow-hidden animate-in zoom-in duration-300">
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <h2 className="text-xl font-bold">Create New Room</h2>
          <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Room Name</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-bold">#</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="general-chat"
                className="w-full bg-background border border-slate-800 rounded-lg py-2 pl-7 pr-4 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all"
                required
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-background rounded-xl border border-slate-800/50">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${isPrivate ? 'bg-amber-500/10 text-amber-500' : 'bg-accent/10 text-accent'}`}>
                {isPrivate ? <Lock size={18} /> : <Hash size={18} />}
              </div>
              <div>
                <p className="text-sm font-bold">{isPrivate ? 'Private Room' : 'Public Room'}</p>
                <p className="text-[10px] text-text-secondary">
                  {isPrivate ? 'Only members can see and join' : 'Everyone on the server can join'}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsPrivate(!isPrivate)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ring-2 ring-transparent ring-offset-2 ring-offset-background
                ${isPrivate ? 'bg-amber-500' : 'bg-slate-700'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isPrivate ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>

          {isPrivate && (
            <div className="space-y-3 animate-in fade-in slide-in-from-top-2 duration-300">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                <Users size={14} /> Invite Members
              </label>
              
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search users..."
                className="w-full bg-background border border-slate-800 rounded-lg py-1.5 px-3 text-sm focus:border-accent outline-none transition-all"
              />

              <div className="max-h-40 overflow-y-auto space-y-1 pr-2 custom-scrollbar">
                {filteredUsers.map(u => (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => toggleMember(u.id)}
                    className={`w-full flex items-center justify-between p-2 rounded-lg transition-all text-left
                      ${selectedMembers.includes(u.id) ? 'bg-accent/10 border border-accent/20' : 'hover:bg-slate-800 border border-transparent'}`}
                  >
                    <div className="flex items-center gap-3">
                        <div className="h-7 w-7 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold">
                            {u.display_name.substring(0, 2)}
                        </div>
                        <span className="text-sm">{u.display_name}</span>
                    </div>
                    {selectedMembers.includes(u.id) && <Check size={14} className="text-accent" />}
                  </button>
                ))}
              </div>
              <p className="text-[10px] text-text-secondary text-right">
                {selectedMembers.length} members selected
              </p>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 rounded-lg bg-slate-800 font-bold hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="flex-1 px-4 py-2 rounded-lg bg-accent font-bold hover:bg-accent-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Room'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateRoomModal;
