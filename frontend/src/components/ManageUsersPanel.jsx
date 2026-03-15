import { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'sonner';
import { X, Shield, ShieldCheck, User as UserIcon } from 'lucide-react';

const ManageUsersPanel = ({ isOpen, onClose }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchUsers();
    }
  }, [isOpen]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/users');
      setUsers(res.data);
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.put(`/api/users/${userId}/role`, { role: newRole });
      toast.success(`User updated to ${newRole}`);
      fetchUsers();
    } catch (error) {
      toast.error('Failed to update role');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="w-full max-w-2xl bg-background-secondary rounded-2xl border border-slate-800 shadow-2xl overflow-hidden animate-in zoom-in duration-300">
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div>
            <h2 className="text-xl font-bold">Manage Users</h2>
            <p className="text-sm text-text-secondary">Administrative console for role assignments</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-6 custom-scrollbar">
          {loading ? (
            <div className="py-10 text-center text-text-secondary">Loading users...</div>
          ) : (
            <div className="space-y-4">
              {users.map((u) => (
                <div key={u.id} className="flex items-center justify-between p-4 bg-background rounded-xl border border-slate-800/50 group hover:border-accent/30 transition-all">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center font-bold text-accent">
                      {u.display_name.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-bold">{u.display_name}</p>
                      <p className="text-xs text-text-secondary">{u.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {['participant', 'moderator', 'admin'].map((role) => (
                      <button
                        key={role}
                        onClick={() => handleRoleChange(u.id, role)}
                        className={`px-3 py-1.5 rounded-lg text-[10px] uppercase font-bold tracking-wider transition-all
                          ${u.role === role 
                            ? (role === 'admin' ? 'bg-role-admin text-white' : role === 'moderator' ? 'bg-role-moderator text-white' : 'bg-role-participant text-white')
                            : 'bg-slate-800 text-slate-500 hover:bg-slate-700'}`}
                      >
                        {role}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="p-6 bg-slate-900/50 border-t border-slate-800 flex justify-end">
          <button 
            onClick={onClose}
            className="px-6 py-2 rounded-lg bg-slate-800 font-bold hover:bg-slate-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ManageUsersPanel;
