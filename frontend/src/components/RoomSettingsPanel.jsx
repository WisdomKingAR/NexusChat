import { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'sonner';
import { X, UserPlus, UserMinus, Search, Shield } from 'lucide-react';

const RoomSettingsPanel = ({ isOpen, onClose, room }) => {
  const [members, setMembers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen && room) {
      fetchData();
    }
  }, [isOpen, room]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [membersRes, usersRes] = await Promise.all([
        api.get(`/api/rooms/${room.id}/members`),
        api.get('/api/users')
      ]);
      setMembers(membersRes.data);
      setAllUsers(usersRes.data);
    } catch (error) {
      toast.error('Failed to load room data');
    } finally {
      setLoading(false);
    }
  };

  const addMember = async (userId) => {
    try {
      await api.post(`/api/rooms/${room.id}/members`, { user_ids: [userId] });
      toast.success('Member added');
      fetchData();
    } catch (error) {
      toast.error('Failed to add member');
    }
  };

  const removeMember = async (userId) => {
    try {
      await api.delete(`/api/rooms/${room.id}/members/${userId}`);
      toast.success('Member removed');
      fetchData();
    } catch (error) {
      toast.error('Failed to remove member');
    }
  };

  if (!isOpen) return null;

  const nonMembers = allUsers.filter(u => 
    !members.some(m => m.id === u.id) &&
    u.display_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="w-full max-w-xl bg-background-secondary rounded-2xl border border-slate-800 shadow-2xl overflow-hidden animate-in zoom-in duration-300">
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Shield className="text-accent" size={20} /> Room Settings: #{room?.name}
            </h2>
            <p className="text-sm text-text-secondary">Manage access and members</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-8 max-h-[70vh] overflow-y-auto custom-scrollbar">
          {/* Current Members Section */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Current Members</h3>
            <div className="space-y-2">
              {loading ? (
                <div className="text-center py-4 text-text-secondary text-sm">Loading members...</div>
              ) : members.length === 0 ? (
                <div className="text-center py-4 text-text-secondary text-sm">No members found</div>
              ) : (
                members.map(member => (
                  <div key={member.id} className="flex items-center justify-between p-3 bg-background rounded-xl border border-slate-800/50">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold">
                        {member.display_name.substring(0, 2)}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-medium">{member.display_name}</span>
                        <span className="text-[10px] text-slate-500 uppercase font-bold">{member.role}</span>
                      </div>
                    </div>
                    {member.role !== 'admin' && (
                      <button 
                        onClick={() => removeMember(member.id)}
                        className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                        title="Remove Member"
                      >
                        <UserMinus size={16} />
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Add Members Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest text-accent">Invites</h3>
              <div className="relative w-48">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" size={12} />
                <input 
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Find users..."
                  className="w-full bg-background border border-slate-800 rounded-lg py-1 pl-8 pr-3 text-[11px] focus:border-accent outline-none"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {nonMembers.slice(0, 10).map(u => (
                <button
                  key={u.id}
                  onClick={() => addMember(u.id)}
                  className="flex items-center justify-between p-2.5 bg-background hover:bg-slate-800 rounded-xl border border-transparent hover:border-slate-700 transition-all text-left group"
                >
                  <div className="flex items-center gap-2">
                    <div className="h-6 w-6 rounded-full bg-slate-700 flex items-center justify-center text-[9px] font-bold">
                      {u.display_name.substring(0, 2)}
                    </div>
                    <span className="text-xs font-medium truncate max-w-[80px]">{u.display_name}</span>
                  </div>
                  <UserPlus size={14} className="text-slate-500 group-hover:text-accent transition-colors" />
                </button>
              ))}
              {nonMembers.length === 0 && !loading && (
                <div className="col-span-2 text-center py-4 text-text-secondary text-xs italic">
                  No more users to invite
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="p-6 bg-slate-900/50 border-t border-slate-800 flex justify-end">
          <button 
            onClick={onClose}
            className="px-6 py-2 rounded-lg bg-slate-800 font-bold hover:bg-slate-700 transition-colors"
          >
            Finished
          </button>
        </div>
      </div>
    </div>
  );
};

export default RoomSettingsPanel;
