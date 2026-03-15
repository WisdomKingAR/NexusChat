import { useState, useEffect } from 'react';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { Plus, Hash, Settings, LogOut, Users, Lock, MessageSquare } from 'lucide-react';
import ManageUsersPanel from './ManageUsersPanel';
import CreateRoomModal from './CreateRoomModal';

const Sidebar = ({ onRoomSelect, selectedRoom, onDmSelect, selectedDm }) => {
  const { user, logout } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [users, setUsers] = useState([]);
  const [dms, setDms] = useState([]);
  const [showManageUsers, setShowManageUsers] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      const [roomsRes, usersRes, dmsRes] = await Promise.all([
        api.get('/api/rooms').catch(() => ({ data: [] })),
        api.get('/api/users').catch(() => ({ data: [] })),
        api.get('/api/dm/channels').catch(() => ({ data: [] }))
      ]);
      setRooms(roomsRes.data);
      setUsers(usersRes.data);
      setDms(dmsRes.data);
    } catch (error) {
      toast.error('Failed to load sidebar data');
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateRoom = async (roomData) => {
    try {
      await api.post('/api/rooms', roomData);
      await fetchData();
      toast.success('Room created');
      setIsCreateModalOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create room');
    }
  };

  const startDm = async (recipientId) => {
    if (recipientId === user.id) return;
    try {
      const res = await api.post(`/api/dm/channels?recipient_id=${recipientId}`);
      await fetchData();
      const otherUser = getUserDetails(recipientId);
      onDmSelect({ ...res.data, other_user: otherUser });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start DM');
    }
  };

  const getUserDetails = (userId) => {
    return users.find(u => u.id === userId);
  };

  return (
    <aside className="w-72 border-r border-slate-800 bg-background-secondary flex flex-col h-full shadow-2xl overflow-hidden shrink-0">
      <div className="flex-1 overflow-y-auto p-4 space-y-8 custom-scrollbar">
        {/* Rooms Section */}
        <div>
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-[11px] font-bold text-slate-500 uppercase tracking-[0.2em]">Rooms</h2>
            {user?.role === 'admin' && (
              <button 
                onClick={() => setIsCreateModalOpen(true)}
                className="text-accent hover:bg-accent/10 p-1 rounded transition-colors"
              >
                <Plus size={16} />
            </button>
            )}
          </div>
          <div className="space-y-1">
            {rooms.map(room => (
              <button
                key={room.id}
                onClick={() => onRoomSelect(room)}
                className={`w-full group flex items-center justify-between px-3 py-2 rounded-lg transition-all 
                  ${selectedRoom?.id === room.id 
                    ? 'bg-accent text-white shadow-lg shadow-accent/20' 
                    : 'text-text-secondary hover:bg-slate-800 hover:text-white'}`}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <Hash size={16} className={`shrink-0 ${selectedRoom?.id === room.id ? 'text-white' : 'text-slate-500'}`} />
                  <span className="font-medium truncate">{room.name}</span>
                </div>
                {room.is_private && (
                  <Lock size={12} className={selectedRoom?.id === room.id ? 'text-white/80' : 'text-slate-500'} />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* DMs Section */}
        <div>
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-[11px] font-bold text-slate-500 uppercase tracking-[0.2em]">Direct Messages</h2>
            <MessageSquare size={14} className="text-slate-500" />
          </div>
          <div className="space-y-1">
            {dms.map(dm => {
              const otherUserId = dm.participants.find(p => p !== user.id);
              const otherUser = getUserDetails(otherUserId);
              
              if (!otherUser) return null;
              
              return (
                <button
                  key={dm.id}
                  onClick={() => onDmSelect({ ...dm, other_user: otherUser })}
                  className={`w-full group flex items-center gap-3 px-3 py-2 rounded-lg transition-all 
                    ${selectedDm?.id === dm.id 
                      ? 'bg-accent text-white shadow-lg shadow-accent/20' 
                      : 'text-text-secondary hover:bg-slate-800 hover:text-white'}`}
                >
                  <div className={`h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold uppercase shrink-0
                    ${selectedDm?.id === dm.id ? 'bg-white/20 text-white' : 'bg-slate-700 text-slate-300'}`}>
                    {otherUser.display_name.substring(0, 2)}
                  </div>
                  <span className="font-medium truncate">{otherUser.display_name}</span>
                </button>
              );
            })}
            {dms.length === 0 && (
              <div className="px-3 py-2 text-xs text-slate-500 italic">No direct messages yet</div>
            )}
          </div>
        </div>

        {/* Users Section */}
        <div>
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-[11px] font-bold text-slate-500 uppercase tracking-[0.2em]">Users</h2>
            <Users size={14} className="text-slate-500" />
          </div>
          <div className="space-y-3">
            {users.map(u => (
              <div 
                key={u.id} 
                className={`flex items-center gap-3 px-2 group ${u.id !== user.id ? 'cursor-pointer hover:bg-slate-800/50 p-1.5 -mx-1.5 rounded-lg transition-colors' : ''}`}
                onClick={() => {
                  if (u.id !== user.id) startDm(u.id);
                }}
              >
                <div className="relative shrink-0">
                  <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center text-[10px] font-bold uppercase ring-2 ring-slate-800">
                    {u.display_name.substring(0, 2)}
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-teal-500 border-2 border-background-secondary" />
                </div>
                <div className="flex flex-col min-w-0 flex-1">
                  <span className="text-sm font-medium text-slate-200 truncate group-hover:text-white transition-colors">
                    {u.display_name} {u.id === user.id && <span className="text-slate-500 font-normal">(You)</span>}
                  </span>
                  <span className={`text-[9px] uppercase font-bold
                    ${u.role === 'admin' ? 'text-role-admin' : u.role === 'moderator' ? 'text-role-moderator' : 'text-role-participant'}`}>
                    {u.role}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* User Area Footer */}
      <div className="p-4 bg-slate-900/50 border-t border-slate-800 space-y-4 shrink-0">
        {user?.role === 'admin' && (
          <button 
            onClick={() => setShowManageUsers(true)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-all border border-slate-800"
          >
            <Settings size={16} />
            <span>Manage System</span>
          </button>
        )}
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-9 w-9 shrink-0 rounded-xl bg-accent flex items-center justify-center font-bold text-white shadow-lg shadow-accent/20">
              {user?.display_name.substring(0, 2).toUpperCase()}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-bold text-white truncate">{user?.display_name}</span>
              <span className="text-[10px] text-slate-500 truncate">{user?.email}</span>
            </div>
          </div>
          <button 
            onClick={logout}
            className="text-slate-500 hover:text-red-400 p-2 rounded-lg transition-colors shrink-0"
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>

      <ManageUsersPanel isOpen={showManageUsers} onClose={() => setShowManageUsers(false)} />
      
      {isCreateModalOpen && (
        <CreateRoomModal 
          isOpen={isCreateModalOpen} 
          onClose={() => setIsCreateModalOpen(false)} 
          onCreate={handleCreateRoom}
          users={users.filter(u => u.id !== user.id)}
        />
      )}
    </aside>
  );
};

export default Sidebar;
