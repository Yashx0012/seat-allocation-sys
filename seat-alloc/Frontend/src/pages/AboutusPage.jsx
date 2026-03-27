// aboutus.jsx - Updated TeamMemberCard with TiltCard
import React, { useRef, useState } from 'react';
import { motion, useScroll, useTransform, useInView, useMotionValue, useSpring } from 'framer-motion';
import SplitText from '../components/SplitText';
import { 
    Shield, Zap, FileText, Users, Award, Target, 
    Cpu, Globe, Layers, MousePointer2, Sparkles, 
    ChevronRight, Github, ExternalLink, Code2
} from 'lucide-react';
import LensCard from '../components/LensCard';

// --- Animated Background Component (Simplified) ---
const BackgroundBranding = () => (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-orange-500/[0.03] dark:bg-orange-500/[0.06] blur-[80px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[45%] h-[45%] rounded-full bg-amber-500/[0.03] dark:bg-amber-500/[0.06] blur-[60px]" />
        <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] dark:bg-[radial-gradient(#1f2937_1px,transparent_1px)] [background-size:40px_40px] opacity-[0.15]"></div>
    </div>
);

// --- ✅ NEW: Team Member Card with Tilt + Spotlight Effect ---
const TeamMemberCard = ({ initials, name, role, description, index }) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-50px" });
    const [isHovering, setIsHovering] = useState(false);

    // Motion values for tilt
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    // Spring animation for smooth movement
    const springConfig = { stiffness: 400, damping: 30 };
    const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), springConfig);
    const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-10, 10]), springConfig);

    // Spotlight position
    const spotlightX = useMotionValue(50);
    const spotlightY = useMotionValue(50);

    const handleMouseMove = (e) => {
        if (!ref.current) return;

        const rect = ref.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        // Normalize to -0.5 to 0.5
        const normalizedX = (e.clientX - centerX) / rect.width;
        const normalizedY = (e.clientY - centerY) / rect.height;

        mouseX.set(normalizedX);
        mouseY.set(normalizedY);

        // Spotlight follows mouse (0-100%)
        const spotX = ((e.clientX - rect.left) / rect.width) * 100;
        const spotY = ((e.clientY - rect.top) / rect.height) * 100;
        spotlightX.set(spotX);
        spotlightY.set(spotY);
    };

    const handleMouseLeave = () => {
        setIsHovering(false);
        mouseX.set(0);
        mouseY.set(0);
        spotlightX.set(50);
        spotlightY.set(50);
    };

    return (
        <motion.div 
            ref={ref}
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: index * 0.1, ease: [0.25, 0.1, 0.25, 1] }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={handleMouseLeave}
            style={{
                rotateX,
                rotateY,
                transformStyle: 'preserve-3d',
                perspective: 1000,
            }}
            className="relative group h-full cursor-pointer"
        >
            {/* Card container */}
            <div className="relative h-full flex flex-col bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-6 transition-colors duration-200 group-hover:border-orange-500/40">
                
                {/* ✅ Spotlight/Lens effect */}
                <motion.div
                    className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden"
                    style={{
                        background: `radial-gradient(circle 120px at ${spotlightX.get()}% ${spotlightY.get()}%, rgba(251,146,60,0.15) 0%, transparent 70%)`,
                    }}
                />

                {/* ✅ Shine sweep effect on hover */}
                <motion.div
                    initial={{ x: '-100%', opacity: 0 }}
                    animate={isHovering ? { x: '200%', opacity: 1 } : { x: '-100%', opacity: 0 }}
                    transition={{ duration: 0.6, ease: 'easeInOut' }}
                    className="pointer-events-none absolute inset-0 rounded-2xl"
                    style={{
                        background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%)',
                        width: '50%',
                    }}
                />

                {/* Content with 3D lift */}
                <div style={{ transform: 'translateZ(30px)' }}>
                    {/* Avatar */}
                    <motion.div 
                        className="relative mb-5"
                        style={{ transform: 'translateZ(40px)' }}
                    >
                        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center text-xl font-bold text-white shadow-lg group-hover:scale-105 transition-transform duration-200">
                            {initials}
                        </div>
                    </motion.div>

                    {/* Info */}
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1 leading-tight">
                        {name}
                    </h3>
                    <span className="text-orange-600 dark:text-orange-400 text-xs font-semibold tracking-wide mb-3 block uppercase">
                        {role}
                    </span>
                    <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed mb-4">
                        {description}
                    </p>

                    {/* Social links */}
                    <div className="mt-auto pt-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-all duration-200 transform translate-y-1 group-hover:translate-y-0">
                        <button className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:text-orange-500 dark:hover:text-orange-400 transition-colors">
                            <Github size={16} />
                        </button>
                        <button className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:text-orange-500 dark:hover:text-orange-400 transition-colors">
                            <ExternalLink size={16} />
                        </button>
                    </div>
                </div>

                {/* Edge glow */}
                <div className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-inset ring-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
        </motion.div>
    );
};

// --- Component for Core Value Card (Simplified) ---
const ValueCard = ({ icon: Icon, title, description, index }) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-50px" });

    return (
        <motion.div 
            ref={ref}
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className="relative group p-6 rounded-2xl bg-white/50 dark:bg-gray-900/50 border border-gray-200/60 dark:border-gray-800/60 hover:border-orange-500/40 transition-colors duration-200"
        >
            <div className="relative z-10">
                <div className="mb-4 p-3 rounded-xl bg-orange-100 dark:bg-orange-500/20 text-orange-600 dark:text-orange-400 w-fit group-hover:scale-105 transition-transform duration-200">
                    <Icon size={28} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{title}</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                    {description}
                </p>
            </div>
        </motion.div>
    );
};

// --- Tech Stack Item (Simplified) ---
const TechItem = ({ icon: Icon, label }) => (
    <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/60 dark:bg-gray-900/60 border border-gray-200/60 dark:border-gray-800/60 hover:border-orange-500/40 transition-colors">
        <Icon size={16} className="text-orange-500" />
        <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">{label}</span>
    </div>
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
            description: "Proprietary algorithms ensure 100% bias-free allocations, mathematically enforcing safety and fairness."
        },
        {
            icon: Zap,
            title: "Peak Performance",
            description: "Processes thousands of data points and generates optimal patterns in milliseconds."
        },
        {
            icon: FileText,
            title: "Operational Clarity",
            description: "Transform chaotic data into structured, actionable insights with zero-friction interface."
        }
    ];

    return (
        <div ref={containerRef} className="relative min-h-screen bg-gray-50 dark:bg-[#050505] transition-colors duration-200">
            <BackgroundBranding />

            <div className="relative z-10 max-w-7xl mx-auto px-6 py-16 space-y-24">

                {/* --- Hero Section --- */}
                <header className="relative py-16">
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="flex flex-col items-center text-center space-y-6"
                    >
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-600 dark:text-orange-400 text-xs font-medium uppercase tracking-wider">
                            <Sparkles size={12} />
                            <span>System Evolution</span>
                        </div>
                        
                        <SplitText 
                            text={`Automated Seat\nAllocation System`} 
                            className="text-4xl sm:text-6xl md:text-7xl font-bold uppercase leading-[0.9] tracking-tight bg-gradient-to-b from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent" 
                            splitType="chars" 
                            delay={20}
                            duration={0.4}
                        />

                        <motion.p 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="text-base md:text-lg text-gray-600 dark:text-gray-400 max-w-xl"
                        >
                            Redefining academic logistical excellence through advanced automation and human-centric design.
                        </motion.p>

                        <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.6 }}
                            className="flex gap-3"
                        >
                            <button className="px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-semibold flex items-center gap-2 transition-colors">
                                Explore Features <ChevronRight size={18} />
                            </button>
                            <button className="px-6 py-3 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-xl font-semibold flex items-center gap-2 hover:border-orange-500/50 transition-colors">
                                View Source <Github size={18} />
                            </button>
                        </motion.div>
                    </motion.div>
                </header>

                {/* --- Mission & Values --- */}
                <section className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
                    <div className="lg:col-span-5 space-y-6">
                        <div className="space-y-3">
                            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white leading-tight">
                                OUR <span className="text-orange-500">MISSION</span>
                            </h2>
                            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                                We've built more than just a tool; we've built a framework for trust. Our mission is to eliminate manual allocation friction, empowering institutions to focus on education.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            <TechItem icon={Cpu} label="React 18" />
                            <TechItem icon={Globe} label="Python/Flask" />
                            <TechItem icon={Layers} label="SQLite" />
                            <TechItem icon={Code2} label="Algorithms" />
                        </div>
                    </div>

                    <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-4">
                        {coreValues.map((value, index) => (
                            <ValueCard key={index} {...value} index={index} />
                        ))}
                        <div className="p-6 rounded-2xl bg-gradient-to-br from-orange-500 to-amber-500 text-white">
                            <Award size={32} className="text-white/80 mb-3" />
                            <h3 className="text-lg font-bold mb-2">Excellence Guaranteed</h3>
                            <p className="text-sm text-white/90 leading-relaxed">
                                Trusted by coordinators to handle high-stakes distributions with zero margin for error.
                            </p>
                        </div>
                    </div>
                </section>

                {/* --- Project Team with Lens Effect --- */}
                <section className="space-y-12">
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                        <div className="space-y-2">
                            <div className="inline-flex items-center gap-2 text-orange-500 font-medium uppercase text-xs tracking-wider">
                                <Users size={14} /> Team Spotlight
                            </div>
                            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
                                The Visionaries
                            </h2>
                        </div>
                        <p className="text-gray-500 dark:text-gray-400 max-w-sm text-sm">
                            A multidisciplinary group of engineers and designers dedicated to solving complex puzzles.
                        </p>
                    </div>

                    {/* ✅ Team grid with lens/tilt effect cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                        {teamMembers.map((member, index) => (
                            <TeamMemberCard key={index} {...member} index={index} />
                        ))}
                    </div>
                </section>

                {/* --- Stats Counter --- */}
                <section className="relative p-8 md:p-12 rounded-2xl bg-gray-900 dark:bg-gray-900/50 border border-gray-800">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
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
                                className="text-center md:text-left"
                            >
                                <div className="text-3xl md:text-4xl font-bold text-orange-400">
                                    {stat.value}
                                </div>
                                <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mt-1">
                                    {stat.label}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* --- Footer CTA --- */}
                <footer className="text-center space-y-8 pb-12">
                    <div className="flex justify-center -space-x-3">
                        {teamMembers.map((m, i) => (
                            <div key={i} className="w-10 h-10 rounded-full border-2 border-gray-50 dark:border-[#050505] bg-gray-200 dark:bg-gray-800 flex items-center justify-center text-xs font-bold text-gray-600 dark:text-gray-300">
                                {m.initials}
                            </div>
                        ))}
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                        Ready to streamline your next session?
                    </h2>
                    <button className="inline-flex items-center gap-2 text-orange-500 hover:text-orange-600 font-semibold transition-colors">
                        Get Started Now <MousePointer2 size={18} />
                    </button>
                    
                    <div className="pt-12 border-t border-gray-200 dark:border-gray-800">
                        <p className="text-gray-500 text-xs uppercase tracking-wider">
                            &copy; {new Date().getFullYear()} Seat Allocation System
                        </p>
                    </div>
                </footer>
            </div>
        </div>
    );
};

export default AboutUs;