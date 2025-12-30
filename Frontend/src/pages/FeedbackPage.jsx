import React from 'react';
import SplitText from '../components/SplitText';
import { AlertCircle, Lightbulb, Upload, Send, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

const FeedbackPage = ({ showToast }) => {
    // State management for form fields
    const [issueType, setIssueType] = React.useState('Visual/Aesthetic Issue'); 
    const [priority, setPriority] = React.useState('Medium Priority');
    const [description, setDescription] = React.useState('');
    const [featureSuggestion, setFeatureSuggestion] = React.useState('');
    const [additionalInfo, setAdditionalInfo] = React.useState('');
    const [imageFile, setImageFile] = React.useState(null);
    const [isSubmitted, setIsSubmitted] = React.useState(false);

    // Issue type options with icons
    const issueOptions = [
        'Functionality Issue', 'Visual/Aesthetic Issue', 'Performance Issue', 
        'Security Issue', 'Data/Content Issue', 'Crash/Error Issue', 
        'Localization/Internationalization Issue', 'Usability/UX Issue', 'Other'
    ];

    // Priority options with corresponding colors
    const priorityOptions = [
        { 
            label: 'High Priority', 
            colorClass: 'bg-red-500 hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700',
            borderClass: 'border-red-500 dark:border-red-600',
            icon: AlertCircle
        },
        { 
            label: 'Medium Priority', 
            colorClass: 'bg-amber-500 hover:bg-amber-600 dark:bg-amber-600 dark:hover:bg-amber-700',
            borderClass: 'border-amber-500 dark:border-amber-600',
            icon: AlertTriangle
        },
        { 
            label: 'Low Priority', 
            colorClass: 'bg-emerald-500 hover:bg-emerald-600 dark:bg-emerald-600 dark:hover:bg-emerald-700',
            borderClass: 'border-emerald-500 dark:border-emerald-600',
            icon: Clock
        },
    ];

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Feedback Submitted:", { issueType, priority, description, featureSuggestion, additionalInfo, imageFile });
        
        setIsSubmitted(true);
        
        // Clear form after submission simulation
        setTimeout(() => {
            setIssueType('Visual/Aesthetic Issue');
            setPriority('Medium Priority');
            setDescription('');
            setFeatureSuggestion('');
            setAdditionalInfo('');
            setImageFile(null);
            setIsSubmitted(false);
        }, 3000);
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
            <div className="max-w-5xl mx-auto space-y-8">
                
                {/* Hero Section */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-t-0 border-r-0 border-l-0 border-[#c0c0c0] dark:border-[#8a8a8a] bg-transparent shadow-none dark:shadow-none">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="relative w-3 h-3">
                                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
                            </div>
                            <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Feedback System</span>
                        </div>
                        <SplitText
                            text={`Report Bugs & Suggest Features`}
                            className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent"
                            splitType="chars"
                            delay={30}
                        />
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Help us improve by sharing your feedback and suggestions
                        </p>
                    </div>
                    
                    <div className="flex gap-4">
                        <div className="text-right">
                            <div className="micro-label mb-1">Response Time</div>
                            <div className="font-mono text-xl text-orange-600 dark:text-orange-400">24-48h</div>
                        </div>
                    </div>
                </div>

                {/* Submission Success Message */}
                {isSubmitted && (
                    <div 
                        className="glass-card border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-emerald-500 p-6 animate-fadeIn shadow-[0_0_24px_rgba(192,192,192,0.22)] dark:shadow-[0_0_24px_rgba(138,138,138,0.24)]"
                    >
                        <div className="flex items-center gap-4">
                            <div className="flex-shrink-0">
                                <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                                    <CheckCircle className="text-emerald-600 dark:text-emerald-400" size={24} />
                                </div>
                            </div>
                            <div>
                                <p className="text-lg font-bold text-gray-900 dark:text-white">Feedback Submitted Successfully!</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Thank you for helping us improve. We'll review your feedback shortly.</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Main Form Container */}
                <div className="glass-card p-8 md:p-10 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_28px_rgba(192,192,192,0.24)] dark:shadow-[0_0_28px_rgba(138,138,138,0.26)]">
                    <form onSubmit={handleSubmit} className="space-y-8">
                        
                        {/* 1. Reason for Reporting (Issue Type Tags) */}
                        <div>
                            <label className="flex items-center gap-2 text-lg font-bold mb-4 text-gray-900 dark:text-white uppercase tracking-wide">
                                <AlertCircle className="text-orange-500" size={20} />
                                Issue Type
                            </label>
                            <div className="flex flex-wrap gap-3">
                                {issueOptions.map((issue, idx) => (
                                    <button
                                        key={issue}
                                        type="button"
                                        onClick={() => setIssueType(issue)}
                                        className={`px-4 py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 border-2 ${
                                            issueType === issue 
                                                ? 'bg-orange-500 dark:bg-orange-600 text-white border-orange-500 dark:border-orange-600 shadow-lg scale-105' 
                                                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-[#c0c0c0] dark:border-[#8a8a8a] hover:border-orange-500 dark:hover:border-orange-400 hover:shadow-md'
                                        }`}
                                        style={{
                                            animation: `fadeIn 0.3s ease-out ${idx * 0.05}s forwards`,
                                            opacity: 0
                                        }}
                                    >
                                        {issue}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* 2. Detailed Bug Description */}
                        <div>
                            <label htmlFor="description" className="flex items-center gap-2 text-lg font-bold mb-2 text-gray-900 dark:text-white uppercase tracking-wide">
                                <AlertCircle className="text-orange-500" size={20} />
                                Bug Description
                                <span className="font-normal text-gray-500 dark:text-gray-400 text-sm normal-case ml-1">Help us understand</span>
                            </label>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                Provide a detailed description of the bug, including steps to reproduce it, expected behavior, and actual behavior.
                            </p>
                            <textarea
                                id="description"
                                name="description"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                rows="10" 
                                placeholder="e.g., Step 1: Click the 'Home' tab. Step 2: Resize the window to mobile width. Expected: Nav bar collapses. Actual: Nav bar overlaps content."
                                required
                                className="w-full bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl p-4 focus:ring-2 focus:ring-orange-500 dark:focus:ring-orange-400 focus:border-orange-500 dark:focus:border-orange-400 placeholder-gray-400 dark:placeholder-gray-500 resize-y transition-all duration-300 outline-none"
                            ></textarea>
                        </div>
                        
                        {/* 3. Feature Suggestion Section */}
                        <div>
                            <label htmlFor="featureSuggestion" className="flex items-center gap-2 text-lg font-bold mb-2 text-gray-900 dark:text-white uppercase tracking-wide">
                                <Lightbulb className="text-orange-500" size={20} />
                                Feature Suggestions
                            </label>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                Describe any new features, improvements, or tools you would like to see added to the system.
                            </p>
                            <textarea
                                id="featureSuggestion"
                                name="featureSuggestion"
                                value={featureSuggestion}
                                onChange={(e) => setFeatureSuggestion(e.target.value)}
                                rows="6" 
                                placeholder="Example: It would be great to have an export button for the seating chart in PDF format."
                                className="w-full bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl p-4 focus:ring-2 focus:ring-orange-500 dark:focus:ring-orange-400 focus:border-orange-500 dark:focus:border-orange-400 placeholder-gray-400 dark:placeholder-gray-500 resize-y transition-all duration-300 outline-none"
                            ></textarea>
                        </div>

                        {/* 4. Bug Priority */}
                        <div>
                            <label className="flex items-center gap-2 text-lg font-bold mb-3 text-gray-900 dark:text-white uppercase tracking-wide">
                                <AlertTriangle className="text-orange-500" size={20} />
                                Priority Level
                            </label>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                                Choose the priority level of the bug: High/Medium/Low. Priority indicates the urgency and impact of the bug.
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {priorityOptions.map((opt, idx) => (
                                    <button
                                        key={opt.label}
                                        type="button"
                                        onClick={() => setPriority(opt.label)}
                                        className={`relative overflow-hidden px-6 py-4 text-sm font-bold rounded-xl text-white transition-all duration-200 border-2 ${
                                            priority === opt.label
                                                ? `${opt.colorClass} ${opt.borderClass} shadow-lg scale-105` 
                                                : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 border-[#c0c0c0] dark:border-[#8a8a8a]'
                                        }`}
                                        style={{
                                            animation: `fadeInUp 0.3s ease-out ${idx * 0.1}s forwards`,
                                            opacity: 0
                                        }}
                                    >
                                        <div className="flex items-center justify-center gap-2">
                                            <opt.icon size={18} />
                                            {opt.label}
                                        </div>
                                        {priority === opt.label && (
                                            <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
                                        )}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* 5. Attach Files */}
                        <div>
                            <label className="flex items-center gap-2 text-lg font-bold mb-2 text-gray-900 dark:text-white uppercase tracking-wide">
                                <Upload className="text-orange-500" size={20} />
                                Attach Files
                            </label>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                                Attach screenshots, screen recordings, or any other relevant files that illustrate the bug.
                            </p>
                            <div className="relative">
                                <input
                                    type="file"
                                    id="imageFile"
                                    name="imageFile"
                                    accept="image/*,video/*"
                                    onChange={(e) => setImageFile(e.target.files[0])}
                                    className="w-full text-sm text-gray-700 dark:text-gray-300
                                        file:mr-4 file:py-3 file:px-6
                                        file:rounded-lg file:border-2 file:border-orange-500 dark:file:border-orange-400
                                        file:text-sm file:font-bold
                                        file:bg-orange-50 dark:file:bg-orange-900/20 file:text-orange-700 dark:file:text-orange-300
                                        hover:file:bg-orange-100 dark:hover:file:bg-orange-900/30 file:cursor-pointer
                                        file:transition-all file:duration-300
                                        cursor-pointer
                                    "
                                />
                            </div>
                            {imageFile && (
                                <div className="mt-4 p-4 bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-200 dark:border-orange-800 rounded-lg">
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className="text-orange-600 dark:text-orange-400" size={20} />
                                        <div>
                                            <p className="text-sm font-semibold text-gray-900 dark:text-white">File attached successfully</p>
                                            <p className="text-xs text-gray-600 dark:text-gray-400">{imageFile.name}</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        {/* 6. Additional Information */}
                        <div>
                            <label htmlFor="additionalInfo" className="flex items-center gap-2 text-lg font-bold mb-2 text-gray-900 dark:text-white uppercase tracking-wide">
                                <AlertCircle className="text-orange-500" size={20} />
                                Additional Information
                            </label>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                Include any additional information that might be helpful in resolving the bug, such as error logs, console outputs, or relevant URLs.
                            </p>
                            <textarea
                                id="additionalInfo"
                                name="additionalInfo"
                                value={additionalInfo}
                                onChange={(e) => setAdditionalInfo(e.target.value)}
                                rows="6" 
                                placeholder="Paste error logs, URLs, or notes here."
                                className="w-full bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-[#c0c0c0] dark:border-[#8a8a8a] rounded-xl p-4 focus:ring-2 focus:ring-orange-500 dark:focus:ring-orange-400 focus:border-orange-500 dark:focus:border-orange-400 placeholder-gray-400 dark:placeholder-gray-500 resize-y transition-all duration-300 outline-none font-mono text-sm"
                            ></textarea>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            className="w-full py-4 px-6 bg-gradient-to-r from-orange-500 to-amber-500 text-white font-bold rounded-xl text-lg shadow-xl hover:from-orange-600 hover:to-amber-600 transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] flex items-center justify-center gap-3 group"
                        >
                            <Send size={20} className="group-hover:translate-x-1 transition-transform" />
                            Submit Feedback
                        </button>
                    </form>
                </div>

                {/* Info Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="glass-card border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-orange-500 p-6 shadow-[0_0_22px_rgba(192,192,192,0.22)] dark:shadow-[0_0_22px_rgba(138,138,138,0.24)]">
                        <div className="flex gap-4">
                            <div className="flex-shrink-0">
                                <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                                    <AlertCircle className="text-orange-500" size={20} />
                                </div>
                            </div>
                            <div>
                                <p className="text-sm font-bold text-gray-900 dark:text-white mb-1">Bug Reports</p>
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                    Be as detailed as possible when describing bugs. Include steps to reproduce, expected vs actual behavior.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-amber-500 p-6 shadow-[0_0_22px_rgba(192,192,192,0.22)] dark:shadow-[0_0_22px_rgba(138,138,138,0.24)]">
                        <div className="flex gap-4">
                            <div className="flex-shrink-0">
                                <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                                    <Lightbulb className="text-amber-500" size={20} />
                                </div>
                            </div>
                            <div>
                                <p className="text-sm font-bold text-gray-900 dark:text-white mb-1">Feature Requests</p>
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                    Share your ideas for new features or improvements. All suggestions are valuable to us!
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx>{`
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                    }
                    to {
                        opacity: 1;
                    }
                }

                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
}

export default FeedbackPage;