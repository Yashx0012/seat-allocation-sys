import React from 'react';
import SplitText from '../components/SplitText';
import { Shield, Zap, FileText, Users, Award, Target } from 'lucide-react';

// --- Component for Team Member Card ---
const TeamMemberCard = ({ initials, name, role, description, index }) => (
    <div 
        className="glass-card p-6 text-center hover:scale-[1.02] hover:shadow-2xl hover:shadow-orange-500/10 transition-all duration-300 w-full sm:w-64 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_22px_rgba(192,192,192,0.2)] dark:shadow-[0_0_22px_rgba(138,138,138,0.24)] hover:border-orange-500 dark:hover:border-orange-400 group"
        style={{
            animation: `fadeInUp 0.5s ease-out ${index * 0.1}s forwards`,
            opacity: 0
        }}
    >
        {/* Avatar with gradient border */}
        <div className="relative w-24 h-24 mx-auto mb-4">
            <div className="absolute inset-0 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
            <div className="relative w-24 h-24 rounded-full flex items-center justify-center text-3xl font-bold bg-gradient-to-br from-orange-500 to-amber-500 text-white border-4 border-white dark:border-gray-800 shadow-lg group-hover:scale-110 transition-transform">
                {initials}
            </div>
        </div>
        
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">{name}</h3>
        <p className="text-orange-600 dark:text-orange-400 font-semibold mb-3 text-sm">{role}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
            {description}
        </p>
    </div>
);

// --- Component for Core Value Card ---
const ValueCard = ({ icon: Icon, title, description, index }) => (
    <div 
        className="glass-card p-8 hover:scale-[1.02] hover:shadow-2xl hover:shadow-orange-500/10 transition-all duration-300 border-2 border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_26px_rgba(192,192,192,0.22)] dark:shadow-[0_0_26px_rgba(138,138,138,0.26)] hover:border-orange-500 dark:hover:border-orange-400 group"
        style={{
            animation: `fadeInUp 0.5s ease-out ${index * 0.15}s forwards`,
            opacity: 0
        }}
    >
        <div className="flex flex-col items-center text-center">
            {/* Icon Badge */}
            <div className="relative mb-6">
                <div className="absolute inset-0 bg-gradient-to-r from-orange-500 to-amber-500 rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
                <div className="relative bg-gradient-to-br from-orange-500 to-amber-500 p-4 rounded-2xl shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all">
                    <Icon className="text-white" size={32} />
                </div>
            </div>
            
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 uppercase tracking-wide">{title}</h3>
            <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed">{description}</p>
        </div>
    </div>
);

// --- The Main About Us Component ---
const AboutUs = ({ showToast }) => {
    const teamMembers = [
        { initials: "TS", name: "Tanish Shivhare", role: "Project Lead / Algorithm Specialist", description: "Oversaw the entire system architecture and core constraints definition." },
        { initials: "HT", name: "Harshit Tiwari", role: "Project Lead / Backend Developer", description: "Primary engineer for the back-end allocation algorithm and API stability." },
        { initials: "LB", name: "Lavanya Bajpai", role: "Frontend Developer", description: "Optimized the constraint satisfaction problem (CSP) solver for speed and fairness." },
        { initials: "AN", name: "Ayush Nager", role: "UI/UX Designer", description: "Designed the dark theme interface and ensured high-fidelity user experience." },
        { initials: "YB", name: "Yash Baraskar", role: "Documentation & QA", description: "Handled rigorous testing and produced clear, accessible system documentation." },
    ];

    const coreValues = [
        {
            icon: Shield,
            title: "Integrity",
            description: "Ensuring a bias-free and cheat-proof environment by enforcing strict non-adjacent seating rules automatically."
        },
        {
            icon: Zap,
            title: "Efficiency",
            description: "Automating complex constraint-checking, reducing allocation time from hours to mere seconds."
        },
        {
            icon: FileText,
            title: "Clarity",
            description: "Providing simple, structured, and easy-to-read output, including the AI-generated Invigilation Guide."
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
            <div className="max-w-7xl mx-auto space-y-20">

                {/* --- Hero Section --- */}
                <section className="pb-12 border-b border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_4px_26px_rgba(192,192,192,0.22)] dark:shadow-[0_4px_26px_rgba(138,138,138,0.22)]">
                    <div className="flex items-center justify-center gap-2 mb-4">
                        <div className="relative w-3 h-3">
                            <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                            <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
                        </div>
                        <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">About the Project</span>
                    </div>
                    
                    <SplitText text={`Automated Seat\nAllocation System`} className="text-4xl sm:text-6xl md:text-7xl font-black text-center uppercase leading-tight mb-6 bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent" splitType="chars" delay={25} />
                    
                    <div className="flex items-center justify-center gap-3">
                        <div className="h-px w-12 bg-gradient-to-r from-transparent to-orange-500"></div>
                        <SplitText text={`Simplifying Exam Integrity`} className="text-xl sm:text-2xl md:text-3xl font-light text-orange-600 dark:text-orange-400 tracking-wide text-center" splitType="chars" delay={20} />
                        <div className="h-px w-12 bg-gradient-to-l from-transparent to-orange-500"></div>
                    </div>
                </section>

                {/* --- Mission Section --- */}
                <section className="max-w-4xl mx-auto">
                    <div className="glass-card p-8 md:p-12 border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-orange-500 shadow-[0_0_28px_rgba(192,192,192,0.24)] dark:shadow-[0_0_28px_rgba(138,138,138,0.26)]">
                        <div className="flex items-center gap-3 mb-6">
                            <Target className="text-orange-500" size={32} />
                            <h2 className="text-3xl font-bold uppercase text-gray-900 dark:text-white">
                                Our Mission
                            </h2>
                        </div>
                        <p className="text-lg leading-relaxed text-gray-600 dark:text-gray-300">
                            The <span className="font-semibold text-orange-600 dark:text-orange-400">Automated Seat Allocation System</span> is driven by a single mission: to modernize and simplify the administrative burden of conducting large-scale examinations. We aim to replace error-prone manual processes with a fast, fair, and reliable technological solution that ensures integrity and maximizes efficiency.
                        </p>
                    </div>
                </section>

                {/* --- Core Values Section --- */}
                <section className="py-8">
                    <div className="text-center mb-12">
                        <div className="flex items-center justify-center gap-3 mb-4">
                            <Award className="text-orange-500" size={32} />
                            <h2 className="text-3xl md:text-4xl font-bold uppercase text-gray-900 dark:text-white">
                                Our Core Values
                            </h2>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                            The principles that guide our development and define our commitment to excellence
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {coreValues.map((value, index) => (
                            <ValueCard 
                                key={index}
                                icon={value.icon}
                                title={value.title}
                                description={value.description}
                                index={index}
                            />
                        ))}
                    </div>
                </section>

                {/* --- Project Team Section --- */}
                <section className="py-8">
                    <div className="text-center mb-12">
                        <div className="flex items-center justify-center gap-3 mb-4">
                            <Users className="text-orange-500" size={32} />
                            <h2 className="text-3xl md:text-4xl font-bold uppercase text-gray-900 dark:text-white">
                                Project Developers
                            </h2>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                            Meet the talented team behind this innovative solution
                        </p>
                    </div>
                    
                    <div className="flex flex-wrap justify-center gap-8 mb-12">
                        {teamMembers.map((member, index) => (
                            <TeamMemberCard 
                                key={index} 
                                initials={member.initials}
                                name={member.name}
                                role={member.role}
                                description={member.description}
                                index={index}
                            />
                        ))}
                    </div>
                    
                    <div className="glass-card p-8 border border-[#c0c0c0] dark:border-[#8a8a8a] border-l-4 border-amber-500 max-w-3xl mx-auto shadow-[0_0_28px_rgba(192,192,192,0.24)] dark:shadow-[0_0_28px_rgba(138,138,138,0.26)]">
                        <div className="flex gap-4">
                            <div className="flex-shrink-0">
                                <div className="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                                    <span className="text-2xl">🎓</span>
                                </div>
                            </div>
                            <div>
                                <p className="text-sm font-bold text-gray-900 dark:text-white mb-1">Capstone Project</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                                    This system was developed as a Capstone Project aimed at bringing cutting-edge technology and optimization algorithms to academic logistics.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* --- Stats Section (Optional Enhancement) --- */}
                <section className="py-8">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        {[
                            { label: "Lines of Code", value: "10K+" },
                            { label: "Team Members", value: "5" },
                            { label: "Development Time", value: "6 Months" },
                            { label: "Algorithms Used", value: "3+" }
                        ].map((stat, index) => (
                            <div 
                                key={index}
                                className="glass-card p-6 text-center hover:scale-105 transition-transform duration-300 border border-[#c0c0c0] dark:border-[#8a8a8a] shadow-[0_0_24px_rgba(192,192,192,0.22)] dark:shadow-[0_0_24px_rgba(138,138,138,0.24)]"
                                style={{
                                    animation: `fadeIn 0.5s ease-out ${index * 0.1}s forwards`,
                                    opacity: 0
                                }}
                            >
                                <div className="text-4xl font-black text-orange-600 dark:text-orange-400 mb-2 stat-number">
                                    {stat.value}
                                </div>
                                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
                                    {stat.label}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
                
            </div>

            {/* Footer */}
            <div className="text-center mt-16 py-8 border-t border-[#c0c0c0] dark:border-[#8a8a8a]">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                    &copy; {new Date().getFullYear()} Automated Seat Allocation System. All rights reserved.
                </p>
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
}

export default AboutUs;