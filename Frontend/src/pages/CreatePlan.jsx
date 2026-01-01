import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SplitText from '../components/SplitText';
import { Upload, Layout, Monitor, Clock, ArrowRight } from 'lucide-react';

const CreatePlan = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [hoveredCard, setHoveredCard] = useState(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem('plans');
      const parsed = raw ? JSON.parse(raw) : [];
      setPlans(parsed.reverse());
    } catch (e) {
      setPlans([]);
    }
  }, []);

  const goAllocate = () => navigate('/allocation');
  const goUpload = () => navigate('/upload');
  const goClassroom = () => navigate('/classroom');

  const actions = [
    {
      title: 'Allocate Manually',
      description: 'Create custom seat arrangements',
      icon: Layout,
      color: 'orange',
      bgColor: 'bg-orange-500 dark:bg-orange-600',
      hoverBorder: 'hover:border-orange-500 dark:hover:border-orange-400',
      onClick: goAllocate
    },
    {
      title: 'Upload Data',
      description: 'Import student and room data',
      icon: Upload,
      color: 'amber',
      bgColor: 'bg-amber-500 dark:bg-amber-600',
      hoverBorder: 'hover:border-amber-500 dark:hover:border-amber-400',
      onClick: goUpload
    },
    {
      title: 'Manage Registry',
      description: 'Configure classroom settings',
      icon: Monitor,
      color: 'orange',
      bgColor: 'bg-orange-600 dark:bg-orange-700',
      hoverBorder: 'hover:border-orange-600 dark:hover:border-orange-500',
      onClick: goClassroom
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-t-0 border-r-0 border-l-0 border-[#c0c0c0] dark:border-[#8a8a8a] bg-transparent shadow-none dark:shadow-none">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Planning Mode</span>
            </div>
            <SplitText
              text={`Create Your Plan`}
              className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
              splitType="chars"
              delay={30}
            />
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Choose how you'd like to organize your seating arrangements
            </p>
          </div>
          
          <div className="flex gap-4">
            <div className="text-right">
              <div className="micro-label mb-1">Active Plans</div>
              <div className="font-mono text-2xl text-orange-600 dark:text-orange-400 stat-number">{plans.length}</div>
            </div>
          </div>
        </div>

        {/* Action Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={action.onClick}
              onMouseEnter={() => setHoveredCard(index)}
              onMouseLeave={() => setHoveredCard(null)}
              className={`glass-card relative overflow-hidden p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_24px_rgba(192,192,192,0.22)] dark:shadow-[0_0_24px_rgba(138,138,138,0.24)] ${action.hoverBorder} hover:shadow-2xl hover:shadow-${action.color}-500/10 transition-all duration-300 group`}
              style={{
                opacity: 0,
                animation: `fadeInUp 0.5s ease-out ${index * 0.1}s forwards`
              }}
            >
              {/* Background Gradient Effect */}
              <div className={`absolute inset-0 ${action.bgColor} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
              
              {/* Background Icon */}
              <div className="absolute top-0 right-0 p-4 opacity-5 transform rotate-12 group-hover:scale-110 transition-transform duration-500">
                <action.icon className="w-32 h-32 text-gray-900 dark:text-gray-100" />
              </div>

              <div className="relative z-10 flex flex-col items-start gap-4">
                {/* Icon */}
                <div className={`${action.bgColor} p-4 rounded-xl shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
                  <action.icon className="text-white" size={28} />
                </div>

                {/* Content */}
                <div className="flex-1 text-left">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </p>
                </div>

                {/* Arrow Indicator */}
                <div className="self-end">
                  <ArrowRight 
                    className={`text-gray-400 group-hover:text-orange-500 group-hover:translate-x-1 transition-all duration-300 ${
                      hoveredCard === index ? 'opacity-100' : 'opacity-0'
                    }`} 
                    size={20} 
                  />
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Recent Plans Section */}
        <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)]">
          <div className="flex items-center justify-between mb-6">
            <div>
              <SplitText text={`Recent Plans`} className="text-2xl font-bold text-gray-900 dark:text-gray-100" splitType="chars" delay={20} />
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Your latest seating arrangements</p>
            </div>
            <div className="flex items-center gap-2 text-xs font-mono text-orange-500 bg-orange-500/10 px-3 py-2 rounded-full">
              <Clock className="w-4 h-4" />
              <span>{plans.length} Total</span>
            </div>
          </div>

          {plans.length === 0 ? (
            <div className="text-center py-16 border-2 border-dashed border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl bg-gray-50 dark:bg-gray-800/50 shadow-[0_0_20px_rgba(192,192,192,0.2)] dark:shadow-[0_0_20px_rgba(138,138,138,0.22)]">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 mb-4">
                <Layout className="text-gray-400 dark:text-gray-500" size={32} />
              </div>
              <p className="text-gray-600 dark:text-gray-400 font-semibold text-lg mb-2">No plans created yet</p>
              <p className="text-sm text-gray-500 dark:text-gray-500">Select an option above to get started with your first plan</p>
            </div>
          ) : (
            <div className="space-y-3">
              {plans.map((p, idx) => (
                <div
                  key={idx}
                  className="group flex items-center justify-between p-5 rounded-xl bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750 transition-all duration-300 border border-[#c0c0c0] dark:border-[#8a8a8a] hover:border-orange-500 dark:hover:border-orange-400 shadow-[0_0_20px_rgba(192,192,192,0.18)] dark:shadow-[0_0_20px_rgba(138,138,138,0.22)] hover:shadow-lg cursor-pointer"
                  style={{
                    opacity: 0,
                    animation: `fadeIn 0.3s ease-out ${idx * 0.05}s forwards`
                  }}
                >
                  <div className="flex items-center gap-4 flex-1">
                    {/* Plan Number Badge */}
                    <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 text-white font-bold text-lg shadow-md">
                      {plans.length - idx}
                    </div>

                    {/* Plan Details */}
                    <div className="flex-1">
                      <div className="font-bold text-gray-900 dark:text-white text-lg group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                        {p.name || `Plan ${plans.length - idx}`}
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock className="w-3 h-3 text-gray-400" />
                        <span className="text-xs font-mono text-gray-500 dark:text-gray-400">
                          {p.createdAt ? new Date(p.createdAt).toLocaleString() : 'No date available'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Plan Type Badge */}
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-orange-600 dark:text-orange-400 bg-orange-500/10 px-4 py-2 rounded-lg border border-orange-500/20">
                      {p.type || 'Manual'}
                    </span>
                    <ArrowRight className="text-gray-400 group-hover:text-orange-500 group-hover:translate-x-1 transition-all duration-300" size={20} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default CreatePlan;