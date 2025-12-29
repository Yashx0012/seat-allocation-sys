import React from 'react';
import SplitText from '../components/SplitText';
import { Upload, Layout, MapPin, Download, Zap, ArrowRight, CheckCircle, Sparkles } from 'lucide-react';

const LandingPage = ({ setCurrentPage }) => {
  const features = [
    {
      icon: Upload,
      title: 'Upload Student Data',
      description: 'Import student information via CSV for quick setup',
      color: 'from-orange-500 to-amber-500'
    },
    {
      icon: Layout,
      title: 'Configure Layout',
      description: 'Set up classroom seating arrangements with ease',
      color: 'from-amber-500 to-orange-600'
    },
    {
      icon: MapPin,
      title: 'Smart Allocation',
      description: 'Automatically allocate seats based on your criteria',
      color: 'from-orange-600 to-red-500'
    },
    {
      icon: Download,
      title: 'Export Results',
      description: 'Download seat maps as PDF for printing and distribution',
      color: 'from-amber-500 to-orange-500'
    }
  ];

  const benefits = [
    'Save hours of manual work',
    'Eliminate allocation errors',
    'Ensure fair distribution',
    'Generate professional PDFs'
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-phantom-black transition-colors duration-300 overflow-hidden">
      
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-orange-500/10 to-amber-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-amber-500/10 to-orange-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* Hero Section */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-100 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-800 rounded-full mb-8 animate-fadeIn">
            <Sparkles className="text-orange-500" size={16} />
            <span className="text-sm font-semibold text-orange-700 dark:text-orange-300">
              Intelligent Seat Allocation System
            </span>
          </div>

          {/* Main Heading */}
          <h1 className="animate-fadeInUp">
            <SplitText
              text={`Seat Allocation\nMade Simple`}
              className="text-5xl md:text-7xl font-black text-gray-900 dark:text-white mb-6 leading-tight"
              splitType="chars"
              delay={35}
              duration={0.6}
            />
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
            Streamline your examination seating process with our intelligent allocation system.
            Upload, configure, and generate seat maps in minutes.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            <button
              onClick={() => setCurrentPage('signup')}
              className="group relative px-8 py-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl text-lg font-bold hover:from-orange-600 hover:to-amber-600 transition-all shadow-lg hover:shadow-xl hover:scale-105 overflow-hidden"
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                Get Started
                <ArrowRight className="group-hover:translate-x-1 transition-transform" size={20} />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-amber-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </button>
            <button
              onClick={() => setCurrentPage('login')}
              className="px-8 py-4 bg-white dark:bg-gray-800 text-orange-600 dark:text-orange-400 rounded-xl text-lg font-bold border-2 border-orange-600 dark:border-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-all shadow-md hover:shadow-lg"
            >
              Login
            </button>
          </div>

          {/* Benefits List */}
          <div className="inline-flex flex-wrap justify-center gap-4 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            {benefits.map((benefit, idx) => (
              <div key={idx} className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                <CheckCircle className="text-emerald-500" size={16} />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{benefit}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-32 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="glass-card p-8 hover:scale-105 transition-all duration-300 group border-2 border-gray-200 dark:border-gray-700 hover:border-orange-500 dark:hover:border-orange-400"
              style={{
                animation: `fadeInUp 0.5s ease-out ${index * 0.1}s forwards`,
                opacity: 0
              }}
            >
              {/* Icon with gradient background */}
              <div className="relative mb-6">
                <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity`}></div>
                <div className={`relative bg-gradient-to-br ${feature.color} w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all`}>
                  <feature.icon className="text-white" size={28} />
                </div>
              </div>

              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Workflow Section */}
        <div className="mt-32 glass-card rounded-3xl shadow-2xl p-12 border-2 border-gray-200 dark:border-gray-700">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-100 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-800 rounded-full mb-4">
              <Zap className="text-orange-500" size={16} />
              <span className="text-sm font-semibold text-orange-700 dark:text-orange-300">
                Simple Process
              </span>
            </div>
            <SplitText
              text={`How It Works`}
              className="text-4xl md:text-5xl font-black text-gray-900 dark:text-white"
              splitType="chars"
              delay={30}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              { num: 1, title: 'Upload Data', desc: 'Import your student list and exam details', icon: Upload },
              { num: 2, title: 'Configure Rooms', desc: 'Set up classroom layouts and constraints', icon: Layout },
              { num: 3, title: 'Generate & Export', desc: 'Get your seat allocation map instantly', icon: Download }
            ].map((step, idx) => (
              <div key={idx} className="relative text-center group">
                {/* Connector Line (hidden on last item) */}
                {idx < 2 && (
                  <div className="hidden md:block absolute top-8 left-1/2 w-full h-0.5 bg-gradient-to-r from-orange-500 to-amber-500 opacity-30"></div>
                )}

                {/* Number Badge */}
                <div className="relative mb-6">
                  <div className="absolute inset-0 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
                  <div className="relative bg-gradient-to-br from-orange-500 to-amber-500 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-black mx-auto shadow-lg group-hover:scale-110 transition-transform">
                    {step.num}
                  </div>
                </div>

                {/* Icon */}
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-orange-100 dark:bg-orange-900/30 mb-4 group-hover:scale-110 transition-transform">
                  <step.icon className="text-orange-600 dark:text-orange-400" size={24} />
                </div>

                <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                  {step.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Final CTA Section */}
        <div className="mt-32 text-center">
          <div className="glass-card p-12 rounded-3xl border-2 border-orange-200 dark:border-orange-800">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Ready to streamline your seat allocation?
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
              Join hundreds of institutions already using our platform to save time and eliminate errors.
            </p>
            <button
              onClick={() => setCurrentPage('signup')}
              className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl text-lg font-bold hover:from-orange-600 hover:to-amber-600 transition-all shadow-lg hover:shadow-xl hover:scale-105"
            >
              Get Started Now
              <ArrowRight className="group-hover:translate-x-1 transition-transform" size={20} />
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

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

        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out;
        }

        .animate-fadeInUp {
          animation: fadeInUp 0.6s ease-out;
        }
      `}</style>
    </div>
  );
};

export default LandingPage;