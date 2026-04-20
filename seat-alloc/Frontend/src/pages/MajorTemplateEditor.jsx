import React, { useState, useEffect } from 'react';
import { getToken } from '../utils/tokenStorage';
import SplitText from '../components/SplitText';
import StyledButton from '../components/Template/StyledButton.jsx'; 
import StyledInput from '../components/Template/StyledInput.jsx'; 
import { useSession } from '../contexts/SessionContext.jsx';

import { 
    Save, 
    RefreshCw, 
    CheckCircle, 
    XCircle, 
    User,
    FileText,
    Image,
    Building,
    AlertCircle,
    UserCheck
} from 'lucide-react';

const initialTemplateState = {
    // Major Exam Fields
    major_exam_dept_name: '',
    major_exam_heading: '',
    major_exam_title: '',
    major_banner_path: '',
    major_coordinator_name: '',
    major_coordinator_title: '',
    major_hod_name: '',
    major_hod_title: '',
};

function MajorTemplateEditor({ showToast }) {
    const { session, loading: sessionLoading } = useSession();

    const [template, setTemplate] = useState(initialTemplateState);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleInputChange = (field, value) => {
        setTemplate(prev => ({ ...prev, [field]: value }));
    };

    useEffect(() => {
        // 1. Wait for session to finish loading
        if (sessionLoading) return;

        // 2. Check for token (Context or LocalStorage)
        const token = session?.token || getToken();

        // 3. If no token, just stop loading and return (User sees Auth Required screen)
        if (!token) {
            setLoading(false);
            return;
        }

        // 4. Define fetch logic INSIDE effect to prevent dependency loops
        const fetchTemplate = async () => {
            try {
                const response = await fetch('/api/major-exam/template/config', { 
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (response.status === 401) {
                    setError('Session expired. Please log in again.');
                    return;
                }
                
                if (data.success) {
                    setTemplate(data.template || initialTemplateState);
                } else {
                    console.error("Template load error:", data.error);
                }
            } catch (err) {
                console.error("Connection error:", err);
                setError('Could not load template configuration.');
            } finally {
                setLoading(false);
            }
        };

        fetchTemplate();

    }, [sessionLoading, session?.token]); // ✅ Depends ONLY on primitive values (Stable)

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = session?.token || getToken();
        if (!token) return setError('Please log in to save');

        // Validate required fields
        const requiredFields = [
            'major_exam_dept_name',
            'major_exam_heading',
            'major_coordinator_name',
            'major_coordinator_title'
        ];

        const missing = requiredFields.filter(f => !template[f] || template[f].trim() === '');
        if (missing.length > 0) {
            setError(`Missing required fields: ${missing.join(', ')}`);
            return;
        }

        setSaving(true);
        setError('');
        setMessage('');

        try {
            const response = await fetch('/api/major-exam/template/config', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(template)
            });
            const data = await response.json();
            
            if (response.ok && data.success) {
                setMessage('Template saved successfully!');
                setTemplate(data.template); 
                if(showToast) showToast('Saved successfully!', 'success');
            } else {
                setError(data.error || 'Failed to save.');
            }
        } catch (err) {
            setError('Save failed: ' + err.message);
        } finally {
            setSaving(false);
        }
    };

    const handleReset = async () => {
        const token = session?.token || getToken();
        if (!token) return setError('Please log in');

        if (!window.confirm('Reset all template settings to defaults?')) return;

        setSaving(true);
        setError('');
        setMessage('');

        try {
            const response = await fetch('/api/major-exam/template/config/reset', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            
            if (response.ok && data.success) {
                setMessage('Template reset to defaults successfully!');
                setTemplate(data.template);
                if(showToast) showToast('Reset to defaults!', 'success');
            } else {
                setError(data.error || 'Failed to reset template.');
            }
        } catch (err) {
            setError('Reset failed: ' + err.message);
        } finally {
            setSaving(false);
        }
    };

    // Show loading spinner while session is being checked
    if (sessionLoading || loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center">
                <div className="text-center">
                    <RefreshCw className="animate-spin mx-auto mb-4 text-orange-600" size={40} />
                    <p className="text-gray-600 dark:text-gray-400 font-medium">Loading configuration...</p>
                </div>
            </div>
        );
    }

    // Show Auth Required ONLY if session loading is done AND no token exists
    const token = session?.token || getToken();
    if (!token) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center p-4">
                <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] max-w-md text-center">
                    <div className="w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center mx-auto mb-4">
                        <AlertCircle className="text-orange-600 dark:text-orange-400" size={32} />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Authentication Required</h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                        Please log in to access the template editor.
                    </p>
                    <button
                        onClick={() => window.location.href = '/login'}
                        className="px-6 py-3 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl hover:from-orange-600 hover:to-amber-600 transition-all duration-200 font-semibold"
                    >
                        Go to Login
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
            <div className="max-w-6xl mx-auto space-y-8">
                
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="relative w-3 h-3">
                                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
                            </div>
                            <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Major Exam Template</span>
                        </div>
                        <SplitText text="Major Exam PDF Template Editor" className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent" splitType="chars" delay={30} />
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Customize your PDF templates for major exam seating plans
                        </p>
                    </div>
                    
                    <div className="flex items-center gap-3 px-4 py-2 bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-200 dark:border-orange-800 rounded-lg">
                        <User className="text-orange-600 dark:text-orange-400" size={20} />
                        <div>
                            <p className="text-xs text-gray-600 dark:text-gray-400">Editing as</p>
                            <p className="text-sm font-bold text-orange-600 dark:text-orange-400">
                                {session?.username || 'Admin'}
                            </p>
                        </div>
                    </div>
                </div>

                {message && (
                    <div className="glass-card border-l-4 border-emerald-500 dark:border-emerald-400 bg-emerald-50 dark:bg-emerald-900/10 p-6">
                        <div className="flex items-center gap-4">
                            <div className="flex-shrink-0">
                                <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                                    <CheckCircle className="text-emerald-600 dark:text-emerald-400" size={24} />
                                </div>
                            </div>
                            <div>
                                <p className="text-lg font-bold text-gray-900 dark:text-white">Success</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="glass-card border-l-4 border-red-500 dark:border-red-400 bg-red-50 dark:bg-red-900/10 p-6">
                        <div className="flex items-center gap-4">
                            <div className="flex-shrink-0">
                                <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                                    <XCircle className="text-red-600 dark:text-red-400" size={24} />
                                </div>
                            </div>
                            <div>
                                <p className="text-lg font-bold text-gray-900 dark:text-white">Error</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    
                    {/* Header Information */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <FileText className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Exam Header Information</h3>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <Building size={16} className="text-orange-500" />
                                    Department Name *
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.major_exam_dept_name || ''}
                                    onChange={(e) => handleInputChange('major_exam_dept_name', e.target.value)}
                                    placeholder="e.g., Department of Computer Science & Engineering"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <FileText size={16} className="text-orange-500" />
                                    Exam Heading *
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.major_exam_heading || ''}
                                    onChange={(e) => handleInputChange('major_exam_heading', e.target.value)}
                                    placeholder="e.g., MAJOR EXAMINATION"
                                    required
                                />
                            </div>
                        </div>
                        
                        <div className="mt-6 space-y-2">
                            <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                <FileText size={16} className="text-orange-500" />
                                Exam Title
                            </label>
                            <StyledInput 
                                type="text"
                                value={template.major_exam_title || ''}
                                onChange={(e) => handleInputChange('major_exam_title', e.target.value)}
                                placeholder="e.g., Seating Plan - Major Examination"
                            />
                        </div>
                    </div>

                    {/* Coordinator Information */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <User className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Exam Coordinator Information</h3>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <User size={16} className="text-orange-500" />
                                    Coordinator Name *
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.major_coordinator_name || ''}
                                    onChange={(e) => handleInputChange('major_coordinator_name', e.target.value)}
                                    placeholder="e.g., Dr. Exam Coordinator"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <FileText size={16} className="text-orange-500" />
                                    Coordinator Title *
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.major_coordinator_title || ''}
                                    onChange={(e) => handleInputChange('major_coordinator_title', e.target.value)}
                                    placeholder="e.g., Dept. Exam Coordinator"
                                    required
                                />
                            </div>
                        </div>

                        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <UserCheck size={16} className="text-orange-500" />
                                    HOD Name
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.major_hod_name || ''}
                                    onChange={(e) => handleInputChange('major_hod_name', e.target.value)}
                                    placeholder="e.g., Dr. Head of Department"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <FileText size={16} className="text-orange-500" />
                                    HOD Title
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.major_hod_title || ''}
                                    onChange={(e) => handleInputChange('major_hod_title', e.target.value)}
                                    placeholder="e.g., Head of Department"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Banner Image */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <Image className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Banner Image</h3>
                        </div>
                        
                        <div className="space-y-4">
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Current banner path: <span className="font-mono text-orange-600 dark:text-orange-400">{template.major_banner_path || 'Not set'}</span>
                            </p>
                            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                                <p className="text-sm text-blue-700 dark:text-blue-300">
                                    💡 Banner management coming soon. Upload and manage banner images from the dashboard.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-4 justify-end pt-6 border-t border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <StyledButton
                            type="button"
                            onClick={handleReset}
                            disabled={saving}
                            className="px-6 py-3"
                        >
                            <RefreshCw size={18} className={saving ? 'animate-spin' : ''} />
                            Reset to Defaults
                        </StyledButton>
                        <StyledButton
                            type="submit"
                            disabled={saving}
                            className="px-8 py-3 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600"
                        >
                            <Save size={18} />
                            {saving ? 'Saving...' : 'Save Template'}
                        </StyledButton>
                    </div>
                </form>

            </div>
        </div>
    );
}

export default MajorTemplateEditor;
