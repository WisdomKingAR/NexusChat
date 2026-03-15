import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatPanel from '../components/ChatPanel';
import useLenis from '../hooks/useLenis';

const Dashboard = () => {
  useLenis();
  const [selectedRoom, setSelectedRoom] = useState(null);

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar onRoomSelect={setSelectedRoom} selectedRoom={selectedRoom} />
      
      <main className="flex-1 flex flex-col bg-background relative">
        {selectedRoom ? (
          <ChatPanel room={selectedRoom} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-6 animate-in fade-in zoom-in duration-500">
            <div className="w-24 h-24 rounded-3xl bg-accent/10 flex items-center justify-center text-accent">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-white">Welcome to NexusChat v3</h2>
              <p className="text-text-secondary max-w-sm">
                Select a room from the sidebar to start collaborating with your team in real-time.
              </p>
            </div>
            <div className="flex gap-4">
              <div className="px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-xs font-bold text-slate-400">
                JWT SECURED
              </div>
              <div className="px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-xs font-bold text-slate-400">
                REAL-TIME WEBSOCKETS
              </div>
            </div>
          </div>
        )}
        
        {/* Subtle decorative elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/5 blur-[120px] pointer-events-none" />
      </main>
    </div>
  );
};

export default Dashboard;
