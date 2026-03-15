import { useState, useEffect } from 'react';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { Plus, Hash, Settings, LogOut, Users } from 'lucide-react';
import ManageUsersPanel from './ManageUsersPanel';

const Sidebar = ({ onRoomSelect, selectedRoom }) => {
  const { user, logout } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [users, setUsers] = useState([]);
  const [showManageUsers, setShowManageUsers] = useState(false);

  const fetchData = async () => {
    try {
      const [roomsRes, usersRes] = await Promise.all([
        api.get('/api/rooms'),
        api.get('/api/users')
      ]);
      setRooms(roomsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      toast.error('Failed to load sidebar data');
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const createRoom = async () => {
    const name = prompt('Enter room name:');
    if (!name) return;
    try {
      await api.post('/api/rooms', { name });
      await fetchData();
      toast.success('Room created');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create room');
    }
  };

  return (
    <aside className="w-72 border-r border-slate-800 bg-background-secondary flex flex-col h-full shadow-2xl">
      {/* Rooms Section */}
      <div className="flex-1 overflow-y-auto p-4 space-y-8 custom-scrollbar">
        <div>
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-[11px] font-bold text-slate-500 uppercase tracking-[0.2em]">Rooms</h2>
            {user?.role === 'admin' && (
              <button 
                onClick={createRoom}
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
                className={`w-full group flex items-center gap-2 px-3 py-2 rounded-lg transition-all 
                  ${selectedRoom?.id === room.id 
                    ? 'bg-accent text-white shadow-lg shadow-accent/20' 
                    : 'text-text-secondary hover:bg-slate-800 hover:text-white'}`}
              >
                <Hash size={16} className={selectedRoom?.id === room.id ? 'text-white' : 'text-slate-500'} />
                <span className="font-medium">{room.name}</span>
              </button>
            ))}
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
              <div key={u.id} className="flex items-center gap-3 px-2 group">
                <div className="relative">
                  <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center text-[10px] font-bold uppercase ring-2 ring-slate-800">
                    {u.display_name.substring(0, 2)}
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-teal-500 border-2 border-background-secondary" />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-sm font-medium text-slate-200 truncate">{u.display_name}</span>
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
      <div className="p-4 bg-slate-900/50 border-t border-slate-800 space-y-4">
        {user?.role === 'admin' && (
          <button 
            onClick={() => setShowManageUsers(true)}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-all border border-slate-800"
          >
            <Settings size={16} />
            <span>Manage System</span>
          </button>
        )}
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-accent flex items-center justify-center font-bold text-white shadow-lg shadow-accent/20">
              {user?.display_name.substring(0, 2).toUpperCase()}
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-white">{user?.display_name}</span>
              <span className="text-[10px] text-slate-500 truncate max-w-[100px]">{user?.email}</span>
            </div>
          </div>
          <button 
            onClick={logout}
            className="text-slate-500 hover:text-red-400 p-2 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
      <ManageUsersPanel isOpen={showManageUsers} onClose={() => setShowManageUsers(false)} />
    </aside>
  );
};

export default Sidebar;
