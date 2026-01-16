import React, { useRef } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import SplitText from '../components/SplitText';
import { 
    Shield, Zap, FileText, Users, Award, Target, 
    Cpu, Globe, Layers, MousePointer2, Sparkles, 
    ChevronRight, Github, ExternalLink, Code2
} from 'lucide-react';

// --- Animated Background Component ---
const BackgroundBranding = () => (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <motion.div 
            animate={{
                scale: [1, 1.2, 1],
                x: [0, 50, 0],
                y: [0, -30, 0],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-orange-500/5 dark:bg-orange-500/10 blur-[120px]"
        />
        <motion.div 
            animate={{
                scale: [1, 1.1, 1],
                x: [0, -40, 0],
                y: [0, 60, 0],
            }}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="absolute bottom-[-10%] right-[-10%] w-[45%] h-[45%] rounded-full bg-amber-500/5 dark:bg-amber-500/10 blur-[100px]"
        />
        <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] dark:bg-[radial-gradient(#1f2937_1px,transparent_1px)] [background-size:40px_40px] opacity-20"></div>
    </div>
);

// --- Component for Team Member Card ---
const TeamMemberCard = ({ initials, name, role, description, index }) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-50px" });

    return (
        <motion.div 
            ref={ref}
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: index * 0.1, ease: [0.21, 0.47, 0.32, 0.98] }}
            whileHover={{ y: -8 }}
            className="relative group h-full"
        >
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/20 to-amber-500/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative h-full flex flex-col bg-white/70 dark:bg-white/5 backdrop-blur-xl border border-white/40 dark:border-white/10 rounded-3xl p-8 shadow-2xl shadow-gray-200/50 dark:shadow-none transition-all duration-300 group-hover:border-orange-500/50">
                <div className="relative mb-6">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center text-2xl font-black text-white shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300">
                        {initials}
                    </div>
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1 leading-tight">{name}</h3>
                <span className="text-orange-500 dark:text-orange-400 text-sm font-semibold tracking-wide mb-4 block uppercase whitespace-nowrap overflow-hidden text-ellipsis">{role}</span>
                <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed mb-6 font-medium">
                    {description}
                </p>
                <div className="mt-auto pt-6 flex gap-3 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                    <button className="p-2 rounded-xl bg-gray-100 dark:bg-white/10 text-gray-600 dark:text-gray-300 hover:text-orange-500 transition-colors">
                        <Github size={18} />
                    </button>
                    <button className="p-2 rounded-xl bg-gray-100 dark:bg-white/10 text-gray-600 dark:text-gray-300 hover:text-orange-500 transition-colors">
                        <ExternalLink size={18} />
                    </button>
                </div>
            </div>
        </motion.div>
    );
};

// --- Component for Core Value Card ---
const ValueCard = ({ icon: Icon, title, description, index }) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-50px" });

    return (
        <motion.div 
            ref={ref}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5, delay: index * 0.15 }}
            whileHover={{ scale: 1.02 }}
            className="relative group p-8 rounded-3xl overflow-hidden"
        >
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-transparent dark:from-orange-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="relative z-10">
                <div className="mb-6 p-4 rounded-2xl bg-orange-100 dark:bg-orange-500/20 text-orange-600 dark:text-orange-400 w-fit group-hover:scale-110 group-hover:bg-orange-600 group-hover:text-white transition-all duration-300">
                    <Icon size={32} />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 uppercase tracking-tight leading-none">{title}</h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed font-medium">
                    {description}
                </p>
            </div>
            <div className="absolute -bottom-1 -right-1 opacity-10 group-hover:opacity-20 transition-opacity">
                <Icon size={120} />
            </div>
        </motion.div>
    );
};

// --- Tech Stack Item ---
const TechItem = ({ icon: Icon, label }) => (
    <motion.div 
        whileHover={{ y: -5 }}
        className="flex items-center gap-3 px-6 py-3 rounded-2xl bg-white/50 dark:bg-white/5 backdrop-blur-md border border-gray-200 dark:border-white/10 shadow-sm hover:border-orange-500/50 transition-colors cursor-default"
    >
        <Icon size={20} className="text-orange-500" />
        <span className="font-bold text-gray-700 dark:text-gray-300 text-sm whitespace-nowrap">{label}</span>
    </motion.div>
);

// --- The Main About Us Component ---
const AboutUs = () => {
    const containerRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end end"]
    });

    const teamMembers = [
        { initials: "TS", name: "Tanish Shivhare", role: "Project Lead / Algorithm Specialist", description: "Architected the system backbone and defined sophisticated constraint-based allocation logic." },
        { initials: "HT", name: "Harshit Tiwari", role: "Project Lead / Backend Developer", description: "Engineered high-performance API endpoints and ensured rock-solid database integrity." },
        { initials: "LB", name: "Lavanya Bajpai", role: "Frontend Developer", description: "Refined the seating solver and brought experimental multi-room caching strategies to life." },
        { initials: "AN", name: "Ayush Nager", role: "UI/UX Designer", description: "Crafted the premium aesthetic, focusing on dark-mode excellence and seamless user flows." },
        { initials: "YB", name: "Yash Baraskar", role: "Documentation & QA", description: "Conducted rigorous system validation and produced clear architectural guides for scalability." },
    ];

    const coreValues = [
        {
            icon: Shield,
            title: "Absolute Integrity",
            description: "Proprietary algorithms ensure 100% bias-free allocations, mathematically enforcing safety and fairness throughout."
        },
        {
            icon: Zap,
            title: "Peak Performance",
            description: "Built for speed. Processes thousands of data points and generates optimal patterns in milliseconds, not hours."
        },
        {
            icon: FileText,
            title: "Operational Clarity",
            description: "We transform chaotic data into structured, actionable insights with a zero-friction reporting interface."
        }
    ];

    return (
        <div ref={containerRef} className="relative min-h-screen bg-[#fcfcfc] dark:bg-[#050505] selection:bg-orange-500 selection:text-white transition-colors duration-500 font-sans overflow-x-hidden">
            <BackgroundBranding />

            <div className="relative z-10 max-w-7xl mx-auto px-6 py-20 space-y-32">

                {/* --- Hero Section --- */}
                <header className="relative py-20">
                    <motion.div 
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="flex flex-col items-center text-center space-y-6"
                    >
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-600 dark:text-orange-400 font-mono text-xs uppercase tracking-widest shadow-sm">
                            <Sparkles size={14} className="animate-pulse" />
                            <span>System Evolution</span>
                        </div>
                        
                        <div className="relative">
                            <SplitText 
                                text={`Automated Seat\nAllocation System`} 
                                className="text-5xl sm:text-7xl md:text-8xl font-black uppercase leading-[0.9] tracking-tighter bg-gradient-to-b from-gray-900 to-gray-600 dark:from-white dark:to-gray-500 bg-clip-text text-transparent pb-4" 
                                splitType="chars" 
                                delay={25} 
                            />
                        </div>

                        <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.8 }}
                            className="flex flex-col items-center gap-6"
                        >
                            <p className="text-lg md:text-xl text-gray-500 dark:text-gray-400 max-w-2xl font-medium leading-relaxed">
                                Redefining academic logistical excellence through advanced automation and human-centric design.
                            </p>
                            <div className="flex gap-4">
                                <motion.button 
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="px-8 py-4 bg-orange-500 hover:bg-orange-600 text-white rounded-2xl font-bold flex items-center gap-2 shadow-lg shadow-orange-500/25 transition-all"
                                >
                                    Explore Features <ChevronRight size={20} />
                                </motion.button>
                                <motion.button 
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="px-8 py-4 bg-white dark:bg-white/5 text-gray-900 dark:text-white border border-gray-200 dark:border-white/10 rounded-2xl font-bold flex items-center gap-2 group transition-all"
                                >
                                    View Source <Github size={20} className="group-hover:rotate-12 transition-transform" />
                                </motion.button>
                            </div>
                        </motion.div>
                    </motion.div>

                    {/* Progress decorator */}
                    <motion.div 
                        className="absolute bottom-0 left-0 h-px bg-gradient-to-r from-transparent via-orange-500 to-transparent"
                        style={{ width: "100%", originX: 0, scaleX: scrollYProgress }}
                    />
                </header>

                {/* --- Mission & Values --- */}
                <section className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
                    <div className="lg:col-span-5 space-y-8">
                        <div className="space-y-4">
                            <h2 className="text-4xl md:text-5xl font-black text-gray-900 dark:text-white leading-tight">
                                OUR <span className="text-orange-500">MISSION</span> TO MODERNIZE.
                            </h2>
                            <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed font-medium">
                                We've built more than just a tool; we've built a framework for trust. Our mission is to eliminate the archaic friction of manual allocation, empowering institutions to focus on what truly matters: education.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <TechItem icon={Cpu} label="React 18" />
                            <TechItem icon={Globe} label="Python/Flask" />
                            <TechItem icon={Layers} label="SQLite" />
                            <TechItem icon={Code2} label="Algorithms" />
                        </div>
                    </div>

                    <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-4">
                            <ValueCard {...coreValues[0]} index={0} />
                            <ValueCard {...coreValues[1]} index={1} />
                        </div>
                        <div className="md:mt-12 space-y-4">
                            <ValueCard {...coreValues[2]} index={2} />
                            <div className="p-8 rounded-3xl bg-gradient-to-br from-orange-500 to-amber-500 text-white space-y-4 shadow-xl">
                                <Award size={40} className="text-white/80" />
                                <h3 className="text-xl font-bold">Excellence Guaranteed</h3>
                                <p className="text-sm text-white/90 leading-relaxed">
                                    Trusted by coordinators to handle high-stakes exam distributions with zero margin for error.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* --- Project Team --- */}
                <section className="space-y-16">
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                        <div className="space-y-4">
                            <div className="inline-flex items-center gap-2 text-orange-500 font-bold uppercase text-xs tracking-[0.2em]">
                                <Users size={16} /> Team Spotlight
                            </div>
                            <h2 className="text-4xl md:text-6xl font-black text-gray-900 dark:text-white uppercase leading-[0.8]">
                                The Visionaries <span className="text-gray-400 dark:text-gray-700">Behind</span>
                            </h2>
                        </div>
                        <p className="text-gray-500 dark:text-gray-400 max-w-sm text-sm font-medium">
                            A multidisciplinary group of engineers and designers dedicated to solving complex logistical puzzles.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
                        {teamMembers.map((member, index) => (
                            <TeamMemberCard key={index} {...member} index={index} />
                        ))}
                    </div>
                </section>

                {/* --- Stats Counter --- */}
                <section className="relative p-12 md:p-20 rounded-[4rem] bg-gray-900 dark:bg-white/5 border border-white/10 overflow-hidden">
                    <div className="absolute top-0 right-0 p-12 text-white/5">
                        <Target size={300} />
                    </div>
                    
                    <div className="relative z-10 grid grid-cols-2 lg:grid-cols-4 gap-12 md:gap-20">
                        {[
                            { label: "Execution Time", value: "<1s" },
                            { label: "Lines of Code", value: "10K+" },
                            { label: "Reliability", value: "99.9%" },
                            { label: "Efficiency Boost", value: "85%" }
                        ].map((stat, index) => (
                            <motion.div 
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="space-y-1"
                            >
                                <div className="text-4xl md:text-6xl font-black text-white bg-gradient-to-r from-orange-400 to-amber-400 bg-clip-text text-transparent">
                                    {stat.value}
                                </div>
                                <div className="text-[10px] md:text-xs font-bold text-gray-400 uppercase tracking-[0.3em]">
                                    {stat.label}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* --- CTA / Footer --- */}
                <footer className="text-center space-y-12 pb-20">
                    <div className="space-y-6">
                        <div className="flex justify-center -space-x-4">
                            {teamMembers.map((m, i) => (
                                <div key={i} className="w-12 h-12 rounded-full border-4 border-[#fcfcfc] dark:border-[#050505] bg-gray-200 dark:bg-gray-800 flex items-center justify-center text-[10px] font-bold">
                                    {m.initials}
                                </div>
                            ))}
                        </div>
                        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Ready to streamline your next session?</h2>
                        <motion.button 
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="inline-flex items-center gap-2 group"
                        >
                            <span className="text-lg font-bold text-orange-500 group-hover:underline underline-offset-4">Get Started Now</span>
                            <MousePointer2 size={20} className="text-orange-500 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                        </motion.button>
                    </div>
                    
                    <div className="pt-20 border-t border-gray-200 dark:border-white/10">
                        <p className="text-gray-500 dark:text-gray-500 text-xs font-medium tracking-widest uppercase">
                            &copy; {new Date().getFullYear()} Seat Allocation System &bull; Intelligent Logistics
                        </p>
                    </div>
                </footer>
            </div>
        </div>
    );
};

export default AboutUs;