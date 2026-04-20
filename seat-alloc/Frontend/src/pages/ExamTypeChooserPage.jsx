import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BookOpen, FileText, ArrowRight, ArrowLeft } from 'lucide-react';
import SplitText from '../components/SplitText';
import { useAuth } from '../contexts/AuthContext';
import {
  clearCreatePlanStickyMode,
  getCreatePlanStickyMode,
  setMinorCreatePlanStickyMode,
} from '../utils/examTypeRouting';

const examCards = [
  {
    type: 'minor',
    title: 'Minor Exam',
    description: 'Standard planning with allocation, templates, and attendance workflows.',
    highlights: ['Batch-wise planning', 'Template editor access', 'Database-backed sessions'],
    icon: BookOpen,
    accent: 'from-blue-500 to-sky-500',
    border: 'border-blue-500/40 hover:border-blue-400/80'
  },
  {
    type: 'major',
    title: 'Major Exam',
    description: 'Upload branch sheets, configure rooms, and generate major-exam PDFs.',
    highlights: ['Excel branch upload', 'Room allocation by branch', 'Major attendance + master plan'],
    icon: FileText,
    accent: 'from-orange-500 to-amber-500',
    border: 'border-orange-500/40 hover:border-orange-400/80'
  }
];

const ExamTypeChooserPage = () => {
  const navigate = useNavigate();
  const { setExamType } = useAuth();

  useEffect(() => {
    if (getCreatePlanStickyMode() === 'minor') {
      setExamType('minor');
      navigate('/minor-exam/create-plan', { replace: true });
    }
  }, [navigate, setExamType]);

  const handleSelect = (type) => {
    setExamType(type);

    if (type === 'major') {
      clearCreatePlanStickyMode();
      navigate('/major-exam/create-plan');
      return;
    }

    setMinorCreatePlanStickyMode();
    navigate('/minor-exam/create-plan');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] px-4 py-10">
      <div className="max-w-6xl mx-auto space-y-8">
        <button
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300/70 dark:border-gray-700 bg-white/80 dark:bg-gray-900/70 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <ArrowLeft size={16} /> Dashboard
        </button>

        <div>
          <SplitText
            text="Choose Exam Type"
            className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
            splitType="chars"
            delay={25}
          />
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Select a mode before entering the plan workspace.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {examCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <motion.button
                key={card.type}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                onClick={() => handleSelect(card.type)}
                className={`text-left bg-white/90 dark:bg-[#0a0a0a] border ${card.border} rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all`}
              >
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${card.accent} text-white mb-4`}>
                  <Icon size={24} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{card.title}</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{card.description}</p>
                <div className="mt-4 space-y-1.5">
                  {card.highlights.map((item) => (
                    <p key={item} className="text-xs text-gray-500 dark:text-gray-400">{`• ${item}`}</p>
                  ))}
                </div>
                <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-gray-800 dark:text-gray-200">
                  Continue <ArrowRight size={16} />
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ExamTypeChooserPage;
