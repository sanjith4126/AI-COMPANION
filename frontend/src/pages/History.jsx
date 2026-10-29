import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchHistory = async () => {
      try {
        const res = await api.getMoodHistory();
        if (mounted && res.history) {
          // Format for chart
          const formatted = res.history.map(item => ({
            date: new Date(item.logged_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
            score: item.mood_score,
            emotion: item.emotion_label,
            note: item.note
          }));
          setData(formatted);
        }
      } catch (err) {
        console.error('Failed to fetch history', err);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    
    fetchHistory();
    return () => { mounted = false; };
  }, []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-companion-surface border border-white/10 p-3 rounded-lg shadow-xl text-sm">
          <p className="font-semibold text-white">{label}</p>
          <p className="text-companion-accentLight">Score: {data.score}/10</p>
          <p className="text-companion-textSubtle capitalize">Emotion: {data.emotion}</p>
          {data.note && <p className="text-xs text-white/50 mt-1 italic">"{data.note}"</p>}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-companion-bg text-white p-6 md:p-12">
      <header className="flex justify-between items-center mb-12 max-w-4xl mx-auto">
        <div>
          <h1 className="text-3xl font-light">Your Mood History</h1>
          <p className="text-companion-textSubtle text-sm mt-1">Last 30 check-ins</p>
        </div>
        <button 
          onClick={() => navigate('/companion')} 
          className="text-sm font-medium border border-white/20 px-4 py-2 rounded-lg hover:bg-white/5 transition-colors"
        >
          Back to Companion
        </button>
      </header>

      <main className="max-w-4xl mx-auto">
        <div className="bg-companion-surface p-6 md:p-8 rounded-2xl border border-white/5 h-[60vh] min-h-[400px]">
          {loading ? (
            <div className="h-full flex items-center justify-center animate-pulse">Loading data...</div>
          ) : data.length === 0 ? (
            <div className="h-full flex items-center justify-center text-companion-textSubtle text-center">
              <p>No mood logs yet.</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                <XAxis 
                  dataKey="date" 
                  stroke="#9CA3AF" 
                  tick={{ fill: '#9CA3AF', fontSize: 12 }} 
                  axisLine={false} 
                  tickLine={false} 
                />
                <YAxis 
                  domain={[1, 10]} 
                  stroke="#9CA3AF" 
                  tick={{ fill: '#9CA3AF', fontSize: 12 }} 
                  axisLine={false} 
                  tickLine={false} 
                />
                <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)' }} />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#7C3AED" 
                  strokeWidth={3} 
                  dot={{ fill: '#9333EA', strokeWidth: 2, r: 4 }} 
                  activeDot={{ r: 6, fill: '#fff', stroke: '#7C3AED' }} 
                  animationDuration={1500}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </main>
    </div>
  );
}
