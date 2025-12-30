import React, { useState, useEffect, useCallback } from 'react';
import SplitText from '../components/SplitText';

// --- Component Imports ---
import StyledButton from '../components/Template/StyledButton.jsx'; 
import StyledInput from '../components/Template/StyledInput.jsx'; 
import { useTheme } from '../context/ThemeContext';

import { 
    Save, 
    RefreshCw, 
    Settings, 
    Download, 
    CheckCircle, 
    XCircle, 
    User,
    FileText,
    Image as ImageIcon,
    Building,
    Upload,
    Eye
} from 'lucide-react';

// Initial state for the template fields
const initialTemplateState = {
    dept_name: '',
    seating_plan_title: '',
    exam_details: '',
    branch_text: '',
    room_number: '',
    coordinator_name: '',
    coordinator_title: '',
    banner_image_path: '',
};

function TemplateEditor({ showToast }) {
    const { theme } = useTheme();

    const [template, setTemplate] = useState(initialTemplateState);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const clearMessages = useCallback(() => {
        const timer = setTimeout(() => {
            setMessage('');
            setError('');
        }, 5000);
        return () => clearTimeout(timer);
    }, []);

    // Backend logic
    const loadTemplate = useCallback(async () => {
        setError('');
        setMessage('');
        try {
            setLoading(true);
            const response = await fetch('/api/template-config');
            const data = await response.json();
            
            if (data.success) {
                setTemplate(data.template || initialTemplateState);
                setMessage('Template loaded successfully.');
            } else {
                setError(data.error || 'Failed to load template configuration.');
            }
        } catch (err) {
            setError('Failed to connect to server: ' + err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadTemplate();
    }, [loadTemplate]);
    
    useEffect(() => {
        return clearMessages();
    }, [message, error, clearMessages]);

    const handleInputChange = (field, value) => {
        setTemplate(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError('');
        setMessage('');

        const formData = new FormData();
        
        Object.keys(template).forEach(key => {
            if (key !== 'banner_image_path' && template[key]) {
                formData.append(key, template[key]);
            }
        });

        const fileInput = document.getElementById('bannerImage');
        if (fileInput?.files[0]) {
            formData.append('bannerImage', fileInput.files[0]);
        }

        try {
            const response = await fetch('/api/template-config', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                setMessage(data.message || 'Template saved successfully!');
                setTemplate(data.template); 
                if (fileInput) fileInput.value = '';
            } else {
                setError(data.error || 'Failed to save template.');
            }
        } catch (err) {
            setError('Failed to save template: ' + err.message);
        } finally {
            setSaving(false);
        }
    };

    const generateTestPDF = async () => {
        setGenerating(true);
        setError('');
        setMessage('');

        try {
            const response = await fetch('/api/test-pdf', { method: 'GET' });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `test_seating_plan_${new Date().getTime()}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                
                setMessage('Test PDF generated and downloaded successfully!');
            } else {
                const errorData = await response.json().catch(() => ({ error: 'Unknown server error.' }));
                setError(errorData.error || `Failed to generate test PDF (Status: ${response.status})`);
            }
        } catch (err) {
            setError('Failed to generate test PDF: ' + err.message);
        } finally {
            setGenerating(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center">
                <div className="text-center">
                    <RefreshCw className="animate-spin mx-auto mb-4 text-orange-600" size={40} />
                    <p className="text-gray-600 dark:text-gray-400 font-medium">Loading template configuration...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
            <div className="max-w-6xl mx-auto space-y-8">
                
                {/* Hero Section */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-t-0 border-r-0 border-l-0 border-[#c0c0c0] dark:border-[#8a8a8a] bg-transparent shadow-none dark:shadow-none">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="relative w-3 h-3">
                                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
                            </div>
                            <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Template Configuration</span>
                        </div>
                        <SplitText text={`PDF Template Editor`} className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent" splitType="chars" delay={30} />
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Customize your PDF templates for seating plans
                        </p>
                    </div>
                    
                    <div className="flex items-center gap-3 px-4 py-2 bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-200 dark:border-orange-800 rounded-lg">
                        <User className="text-orange-600 dark:text-orange-400" size={20} />
                        <div>
                            <p className="text-xs text-gray-600 dark:text-gray-400">Editing as</p>
                            <p className="text-sm font-bold text-orange-600 dark:text-orange-400">test_user</p>
                        </div>
                    </div>
                </div>

                {/* Message and Error Alerts */}
                {message && (
                    <div className="glass-card border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-emerald-500 p-6 animate-fadeIn shadow-[0_0_24px_rgba(192,192,192,0.22)] dark:shadow-[0_0_24px_rgba(138,138,138,0.24)]">
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
                    <div className="glass-card border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-red-500 p-6 animate-fadeIn shadow-[0_0_24px_rgba(192,192,192,0.22)] dark:shadow-[0_0_24px_rgba(138,138,138,0.24)]">
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

                {/* Main Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    
                    {/* Header Information */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <FileText className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Header Information</h3>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <Building size={16} className="text-orange-500" />
                                    Department Name
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.dept_name || ''}
                                    onChange={(e) => handleInputChange('dept_name', e.target.value)}
                                    placeholder="e.g., Department of Computer Science & Engineering"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <FileText size={16} className="text-orange-500" />
                                    Seating Plan Title
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.seating_plan_title || ''}
                                    onChange={(e) => handleInputChange('seating_plan_title', e.target.value)}
                                    placeholder="e.g., Seating Plan"
                                />
                            </div>
                        </div>
                        
                        <div className="mt-6 space-y-2">
                            <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                <FileText size={16} className="text-orange-500" />
                                Exam Details
                            </label>
                            <StyledInput 
                                type="textarea"
                                rows="2"
                                value={template.exam_details || ''}
                                onChange={(e) => handleInputChange('exam_details', e.target.value)}
                                placeholder="e.g., Minor-II Examination (2025 Admitted), November 2025"
                            />
                        </div>
                    </div>

                    {/* Branch and Room Information */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <Building className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Branch & Room Information</h3>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <FileText size={16} className="text-orange-500" />
                                    Branch Text
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.branch_text || ''}
                                    onChange={(e) => handleInputChange('branch_text', e.target.value)}
                                    placeholder="e.g., Branch: B.Tech(CSE & CSD Ist year)"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <Building size={16} className="text-orange-500" />
                                    Room Number
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.room_number || ''}
                                    onChange={(e) => handleInputChange('room_number', e.target.value)}
                                    placeholder="e.g., Room no. 103A"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Coordinator Information */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <User className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Coordinator Information</h3>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <User size={16} className="text-orange-500" />
                                    Coordinator Name
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.coordinator_name || ''}
                                    onChange={(e) => handleInputChange('coordinator_name', e.target.value)}
                                    placeholder="e.g., Dr. Dheeraj K. Dixit"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <FileText size={16} className="text-orange-500" />
                                    Coordinator Title
                                </label>
                                <StyledInput
                                    type="text"
                                    value={template.coordinator_title || ''}
                                    onChange={(e) => handleInputChange('coordinator_title', e.target.value)}
                                    placeholder="e.g., Dept. Exam Coordinator"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Banner Image */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <ImageIcon className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Banner / Logo Image</h3>
                        </div>
                        
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <Eye size={16} className="text-orange-500" />
                                    Current Banner Path
                                </label>
                                <input
                                    type="text"
                                    value={template.banner_image_path || 'No image set'}
                                    readOnly
                                    className="w-full px-4 py-3 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] cursor-not-allowed"
                                />
                            </div>
                            
                            <div className="space-y-2">
                                <label htmlFor="bannerImage" className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <Upload size={16} className="text-orange-500" />
                                    Upload New Banner (Optional)
                                </label>
                                <input
                                    type="file"
                                    id="bannerImage"
                                    accept="image/*"
                                    className="w-full text-sm text-gray-700 dark:text-gray-300
                                        file:mr-4 file:py-3 file:px-6
                                        file:rounded-lg file:border-2 file:border-orange-500 dark:file:border-orange-400
                                        file:text-sm file:font-bold
                                        file:bg-orange-50 dark:file:bg-orange-900/20 file:text-orange-700 dark:file:text-orange-300
                                        hover:file:bg-orange-100 dark:hover:file:bg-orange-900/30 file:cursor-pointer
                                        file:transition-all file:duration-300
                                        cursor-pointer"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                    Supported formats: PNG, JPG, JPEG. The file will be sent via FormData.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-wrap gap-4 justify-center pt-6 border-t border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <button
                            type="submit"
                            disabled={saving}
                            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 transition-all duration-200 font-semibold disabled:opacity-60 disabled:cursor-not-allowed shadow-lg hover:shadow-xl hover:scale-[1.02] group"
                        >
                            {saving ? (
                                <>
                                    <RefreshCw className="animate-spin" size={18} />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save size={18} className="group-hover:scale-110 transition-transform" />
                                    Save Template
                                </>
                            )}
                        </button>

                        <button
                            type="button"
                            onClick={generateTestPDF}
                            disabled={generating}
                            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl hover:from-orange-600 hover:to-amber-600 transition-all duration-200 font-semibold disabled:opacity-60 disabled:cursor-not-allowed shadow-lg hover:shadow-xl hover:scale-[1.02] group"
                        >
                            {generating ? (
                                <>
                                    <RefreshCw className="animate-spin" size={18} />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Download size={18} className="group-hover:translate-y-1 transition-transform" />
                                    Generate Test PDF
                                </>
                            )}
                        </button>

                        <button
                            type="button"
                            onClick={loadTemplate}
                            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] group"
                        >
                            <RefreshCw size={18} className="group-hover:rotate-180 transition-transform duration-500" />
                            Reload Template
                        </button>
                    </div>
                </form>

                {/* Preview Section */}
                <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.24)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)]">
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                            <Eye className="text-orange-600 dark:text-orange-400" size={24} />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Current Configuration Preview</h3>
                    </div>
                    
                    <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl border-2 border-dashed border-[#c0c0c0] dark:border-[#8a8a8a] space-y-3 text-sm shadow-[0_0_20px_rgba(192,192,192,0.2)] dark:shadow-[0_0_20px_rgba(138,138,138,0.22)]">
                        {[
                            { label: 'Department', value: template.dept_name },
                            { label: 'Title', value: template.seating_plan_title },
                            { label: 'Exam Details', value: template.exam_details },
                            { label: 'Branch Text', value: template.branch_text },
                            { label: 'Room', value: template.room_number },
                            { label: 'Coordinator', value: `${template.coordinator_name || 'Not set'} - ${template.coordinator_title || 'Not set'}` },
                            { label: 'Banner Path', value: template.banner_image_path }
                        ].map((item, idx) => (
                            <div key={idx} className="flex">
                                <span className="font-bold text-orange-600 dark:text-orange-400 min-w-[140px]">{item.label}:</span>
                                <span className="text-gray-700 dark:text-gray-300">{item.value || 'Not set'}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <style jsx>{`
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
            `}</style>
        </div>
    );
}

export default TemplateEditor;