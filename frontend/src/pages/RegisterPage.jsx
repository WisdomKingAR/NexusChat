import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(email, password, displayName);
      toast.success('Account created successfully');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to register');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-background-secondary p-8 shadow-xl border border-slate-800">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-accent">Join NexusChat v3</h1>
          <p className="mt-2 text-text-secondary">Create a new account</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary">Display Name</label>
              <input
                type="text"
                required
                className="mt-1 block w-full rounded-lg bg-background border border-slate-700 px-4 py-2 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary">Email</label>
              <input
                type="email"
                required
                className="mt-1 block w-full rounded-lg bg-background border border-slate-700 px-4 py-2 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary">Password (min. 8 chars)</label>
              <input
                type="password"
                required
                minLength={8}
                className="mt-1 block w-full rounded-lg bg-background border border-slate-700 px-4 py-2 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-accent py-2 font-semibold text-white hover:bg-accent-hover transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center text-sm text-text-secondary">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-accent hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
