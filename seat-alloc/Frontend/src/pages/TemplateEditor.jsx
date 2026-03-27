import React, { useState, useEffect, useCallback } from 'react';
import { getToken } from '../utils/tokenStorage';
import SplitText from '../components/SplitText';
import StyledButton from '../components/Template/StyledButton.jsx'; 
import StyledInput from '../components/Template/StyledInput.jsx'; 
import { useTheme } from '../contexts/ThemeContext.jsx';
import { useSession } from '../contexts/SessionContext.jsx';

import { 
    Save, 
    RefreshCw, 
    Download, 
    CheckCircle, 
    XCircle, 
    User,
    FileText,
    Image,
    Building,
    Upload,
    Eye,
    AlertCircle,
    Calendar,
    UserCheck
} from 'lucide-react';

const initialTemplateState = {
    // Seating Plan Fields
    dept_name: '',
    seating_plan_title: '',
    exam_details: '',
    current_year: new Date().getFullYear(),
    coordinator_name: '',
    coordinator_title: '',
    banner_image_path: '',
    
    // Attendance Sheet Fields
    attendance_dept_name: '',
    attendance_year: new Date().getFullYear(),
    attendance_exam_heading: 'SESSIONAL EXAMINATION',
    attendance_banner_path: '',
};

function TemplateEditor({ showToast }) {
    const { theme } = useTheme();
    const { session, loading: sessionLoading } = useSession();

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

    const getAuthHeaders = useCallback(() => {
        const token = session?.token || getToken();
        return {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
        };
    }, [session]);

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
                // Don't set loading=true here if we want background updates, 
                // but for initial load it's fine.
                // setLoading(true); 
                
                const response = await fetch('/api/template/config', { 
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
                    // Optional: showToast('Configuration loaded', 'success');
                } else {
                    console.error("Template load error:", data.error);
                    // Don't set global error here to avoid blocking UI on minor fetch errors
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

        setSaving(true);
        setError('');
        setMessage('');

        const formData = new FormData();
        Object.keys(template).forEach(key => {
            // Append all fields to FormData
            if (key !== 'banner_image_path' && template[key]) {
                formData.append(key, template[key]);
            }
        });

        // Append file if selected
        const fileInput = document.getElementById('bannerImage');
        if (fileInput?.files[0]) {
            formData.append('bannerImage', fileInput.files[0]);
        }

        // Add template name explicitly
        formData.append('template_name', 'default');

        try {
            const response = await fetch('/api/template/config', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}` 
                    // NO Content-Type header here! Browser adds it automatically.
                },
                body: formData
            });
            const data = await response.json();
            
            if (response.ok && data.success) {
                setMessage('Template saved successfully!');
                setTemplate(data.template); 
                if (fileInput) fileInput.value = '';
                if(showToast) showToast('Saved successfully!', 'success');
                
                // OPTIONAL: Auto-generate PDF after successful save
                // generateTestPDF(); 
            } else {
                setError(data.error || 'Failed to save.');
            }
        } catch (err) {
            setError('Save failed: ' + err.message);
        } finally {
            setSaving(false);
        }
    };

    const generateTestPDF = async () => {
        const token = session?.token || getToken();
        if (!token) {
            setError('Please log in to generate PDFs');
            return;
        }

        setGenerating(true);
        setError('');
        setMessage('');

        try {
            const response = await fetch('/api/test-pdf', { 
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                setError('Session expired. Please log in again.');
                setGenerating(false);
                return;
            }

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
                if(showToast) showToast('Test PDF generated!', 'success');
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
                            <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Template Configuration</span>
                        </div>
                        <SplitText text="PDF Template Editor" className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent" splitType="chars" delay={30} />
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Customize your PDF templates for seating plans
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
                    <div className="glass-card border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-emerald-500 p-6">
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
                    <div className="glass-card border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-red-500 p-6">
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

                <div className="space-y-6">
                    
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
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

                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <Building className="text-orange-600 dark:text-orange-400" size={24} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Branch & Room Information</h3>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                                    <Calendar size={16} className="text-orange-500" />
                                    Current Exam Year
                                </label>
                                <StyledInput
                                    type="number"
                                    value={template.current_year || ''}
                                    onChange={(e) => handleInputChange('current_year', e.target.value)}
                                    placeholder="e.g., 2024"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
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

                    {/* Banner Image Upload */}
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                            <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                                <Image className="text-orange-600 dark:text-orange-400" size={24} />
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
                                    Supported formats: PNG, JPG, JPEG, GIF. Max size: 5MB.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-4 justify-center pt-6 border-t border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <button
                            onClick={handleSubmit}
                            disabled={saving}
                            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 transition-all duration-200 font-semibold disabled:opacity-60 disabled:cursor-not-allowed shadow-lg hover:scale-[1.02] group"
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
                            onClick={generateTestPDF}
                            disabled={generating}
                            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl hover:from-orange-600 hover:to-amber-600 transition-all duration-200 font-semibold disabled:opacity-60 disabled:cursor-not-allowed shadow-lg hover:scale-[1.02] group"
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
                            onClick={() => window.location.reload()}
                            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200 font-semibold shadow-lg hover:scale-[1.02] group"
                        >
                            <RefreshCw size={18} className="group-hover:rotate-180 transition-transform duration-500" />
                            Reload Template
                        </button>
                    </div>
                </div>

                <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a]">
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[#c0c0c0] dark:border-[#8a8a8a]">
                        <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                            <Eye className="text-orange-600 dark:text-orange-400" size={24} />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">Current Configuration Preview</h3>
                    </div>
                    
                    <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl border-2 border-dashed border-[#c0c0c0] dark:border-[#8a8a8a] space-y-3 text-sm">
                        {[
                            { label: 'Department', value: template.dept_name },
                            { label: 'Title', value: template.seating_plan_title },
                            { label: 'Exam Details', value: template.exam_details },
                            { label: 'Current Year', value: template.current_year },
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
        </div>
    );
}

export default TemplateEditor;