
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Bell, Search, ChevronDown, Target, Filter, Users, Settings, LogOut } from 'lucide-react';

const leadData = [
  { name: 'Lead A', score: 98 },
  { name: 'Lead B', score: 92 },
  { name: 'Lead C', score: 85 },
  { name: 'Lead D', score: 78 },
  { name: 'Lead E', score: 72 },
  { name: 'Lead F', score: 65 },
  { name: 'Lead G', score: 58 },
];

const pipelineData = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 300 },
  { name: 'Mar', value: 600 },
  { name: 'Apr', value: 800 },
  { name: 'May', value: 500 },
  { name: 'Jun', value: 700 },
];

const leads = [
  { id: 1, name: 'John Doe', company: 'Acme Inc.', score: 98, status: 'Hot' },
  { id: 2, name: 'Jane Smith', company: 'Stark Industries', score: 92, status: 'Hot' },
  { id: 3, name: 'Peter Jones', company: 'Wayne Enterprises', score: 85, status: 'Warm' },
  { id: 4, name: 'Mary Johnson', company: 'Cyberdyne Systems', score: 78, status: 'Warm' },
  { id: 5, name: 'David Williams', company: 'Ollivanders', score: 72, status: 'Cold' },
];

const App: React.FC = () => {
  return (
    <div className="bg-gray-900 text-white min-h-screen flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <LeadScoringChart />
            <PipelineChart />
          </div>
          <div className="mt-8">
            <LeadsTable />
          </div>
        </main>
      </div>
    </div>
  );
};

const Sidebar: React.FC = () => {
  return (
    <div className="w-64 bg-gray-800 p-4 flex flex-col">
      <div className="text-2xl font-bold text-electric-green mb-8">Lead Sniper</div>
      <nav className="flex-1">
        <ul>
          <li className="mb-4"><a href="#" className="flex items-center text-gray-300 hover:text-white"><Target className="mr-2" /> Dashboard</a></li>
          <li className="mb-4"><a href="#" className="flex items-center text-gray-300 hover:text-white"><Users className="mr-2" /> Leads</a></li>
          <li className="mb-4"><a href="#" className="flex items-center text-gray-300 hover:text-white"><Filter className="mr-2" /> Pipeline</a></li>
        </ul>
      </nav>
      <div>
        <ul>
          <li className="mb-4"><a href="#" className="flex items-center text-gray-300 hover:text-white"><Settings className="mr-2" /> Settings</a></li>
          <li><a href="#" className="flex items-center text-gray-300 hover:text-white"><LogOut className="mr-2" /> Logout</a></li>
        </ul>
      </div>
    </div>
  );
};

const Header: React.FC = () => {
  return (
    <header className="bg-gray-800 p-4 flex justify-between items-center">
      <div className="flex items-center">
        <Search className="text-gray-400 mr-2" />
        <input type="text" placeholder="Search..." className="bg-gray-700 text-white rounded-md px-3 py-1" />
      </div>
      <div className="flex items-center">
        <Bell className="mr-4" />
        <div className="flex items-center">
          <img src="https://i.pravatar.cc/40" alt="User" className="rounded-full w-8 h-8 mr-2" />
          <span>Admin</span>
          <ChevronDown className="ml-1" />
        </div>
      </div>
    </header>
  );
};

const LeadScoringChart: React.FC = () => {
  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Lead Scoring</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={leadData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
          <XAxis dataKey="name" stroke="#A0AEC0" />
          <YAxis stroke="#A0AEC0" />
          <Tooltip contentStyle={{ backgroundColor: '#2D3748', border: 'none' }} />
          <Legend />
          <Bar dataKey="score" fill="#38B2AC" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

const PipelineChart: React.FC = () => {
  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Pipeline Monitoring</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={pipelineData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
          <XAxis dataKey="name" stroke="#A0AEC0" />
          <YAxis stroke="#A0AEC0" />
          <Tooltip contentStyle={{ backgroundColor: '#2D3748', border: 'none' }} />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#38B2AC" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const LeadsTable: React.FC = () => {
  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Leads</h2>
      <table className="w-full">
        <thead>
          <tr className="text-left text-gray-400">
            <th className="pb-2">Name</th>
            <th className="pb-2">Company</th>
            <th className="pb-2">Score</th>
            <th className="pb-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {leads.map(lead => (
            <tr key={lead.id} className="border-b border-gray-700">
              <td className="py-2">{lead.name}</td>
              <td className="py-2">{lead.company}</td>
              <td className="py-2">{lead.score}</td>
              <td className="py-2">
                <span className={`px-2 py-1 rounded-full text-sm ${lead.status === 'Hot' ? 'bg-red-500' : lead.status === 'Warm' ? 'bg-yellow-500' : 'bg-green-500'}`}>
                  {lead.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;
