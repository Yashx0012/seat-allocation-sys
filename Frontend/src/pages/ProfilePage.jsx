import React, { useState, useEffect } from 'react';
import SplitText from '../components/SplitText';
import { User, LogOut, Mail, Edit2, Check, X, Loader2, Shield, Calendar, ArrowUpRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ProfilePage = ({ showToast, setCurrentPage }) => {
  const { user, logout, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
  });

  // Update form when user changes
  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
      });
    }
  }, [user]);

  const handleSave = async () => {
    // Validate fields
    if (!formData.username.trim() || !formData.email.trim()) {
      showToast('Please fill in all fields', 'error');
      return;
    }

    setLoading(true);
    const result = await updateProfile(formData.username, formData.email);
    setLoading(false);

    if (result.success) {
      showToast('Profile updated successfully!', 'success');
      setIsEditing(false);
    } else {
      showToast(result.error || 'Failed to update profile', 'error');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      username: user?.username || '',
      email: user?.email || '',
    });
  };

  const handleLogout = async () => {
    await logout();
    showToast('Logged out successfully', 'success');
    setCurrentPage('landing');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin mx-auto mb-4 text-orange-600" size={40} />
          <p className="text-gray-600 dark:text-gray-400">Loading your profile...</p>
        </div>
      </div>
    );
  }

  const getInitials = (name) => {
    return name
      ?.split(' ')
      .map((part) => part[0])
      .join('')
      .toUpperCase() || 'U';
  };

  const roleColors = {
    admin: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800',
    student: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border border-orange-200 dark:border-orange-800',
    staff: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800',
  };

  const roleColor = roleColors[user?.role?.toLowerCase()] || roleColors.student;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505] py-8 px-4 transition-colors duration-300">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="relative w-3 h-3">
                <div className="absolute inset-0 bg-orange-500 rounded-full animate-ping opacity-75"></div>
                <div className="relative w-3 h-3 bg-orange-500 rounded-full border border-orange-400"></div>
              </div>
              <span className="text-xs font-mono text-orange-500 tracking-wider uppercase">Account Settings</span>
            </div>
            <SplitText text={`Your Profile`} className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500 dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 bg-clip-text text-transparent" splitType="chars" delay={30} />
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Manage your account information and preferences
            </p>
          </div>
        </div>

        {/* Main Profile Card */}
        <div className="glass-card overflow-hidden">
          {/* Decorative Header with Gradient */}
          <div className="relative bg-gradient-to-r from-orange-500 via-amber-500 to-orange-600 p-8 overflow-hidden">
            {/* Animated background elements */}
            <div className="absolute inset-0">
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 animate-pulse"></div>
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24 animate-pulse" style={{ animationDelay: '1s' }}></div>
            </div>

            <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
              {/* Avatar with animated border */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-orange-300 to-amber-300 rounded-full blur-md group-hover:blur-lg transition-all duration-300 opacity-50"></div>
                <div className="relative w-28 h-28 bg-gradient-to-br from-orange-400 to-amber-500 rounded-full flex items-center justify-center shadow-2xl border-4 border-white/30 group-hover:scale-105 transition-transform duration-300">
                  <span className="text-4xl font-bold text-white">{getInitials(user?.fullName)}</span>
                </div>
              </div>

              {/* User Info */}
              <div className="flex-1 text-white">
                <h2 className="text-3xl font-bold mb-2">{user?.fullName}</h2>
                <div className="flex items-center gap-2 text-orange-100 mb-4">
                  <Mail size={16} />
                  <p className="text-sm">{user?.email}</p>
                </div>
                <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold ${roleColor} bg-white/90 dark:bg-gray-800/90 capitalize shadow-md`}>
                  <Shield size={14} />
                  {user?.role}
                </div>
              </div>

              {/* Edit Button */}
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="inline-flex items-center gap-2 px-5 py-3 bg-white/20 backdrop-blur-md text-white border-2 border-white/30 rounded-lg hover:bg-white/30 transition-all duration-200 font-medium shadow-lg hover:shadow-xl hover:scale-105 group"
                >
                  <Edit2 size={18} className="group-hover:rotate-12 transition-transform" />
                  Edit Profile
                </button>
              )}
            </div>
          </div>

          {/* Profile Content */}
          <div className="p-8">
            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-gradient-to-br from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750 p-4 rounded-xl border border-orange-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Member Since</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white mt-1 stat-number">2024</p>
                  </div>
                  <Calendar className="text-orange-500" size={24} />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750 p-4 rounded-xl border border-orange-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Account Type</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white mt-1 capitalize">{user?.role}</p>
                  </div>
                  <User className="text-orange-500" size={24} />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-orange-50 to-amber-50 dark:from-gray-800 dark:to-gray-750 p-4 rounded-xl border border-orange-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Status</p>
                    <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-1">Active</p>
                  </div>
                  <div className="relative">
                    <div className="absolute inset-0 bg-emerald-500 rounded-full blur-md opacity-50"></div>
                    <div className="relative w-3 h-3 bg-emerald-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-6 mb-8">
              {/* Username Field */}
              <div className="group">
                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">
                  <User size={16} className="text-orange-500" />
                  Username
                </label>
                <div className="relative">
                  <input
                    type="text"
                    disabled={!isEditing}
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className={`w-full px-4 py-3.5 border-2 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all duration-200 focus:outline-none ${
                      isEditing 
                        ? 'border-gray-300 dark:border-gray-600 focus:border-orange-500 dark:focus:border-orange-400' 
                        : 'border-gray-200 dark:border-gray-700 cursor-not-allowed opacity-60'
                    }`}
                  />
                </div>
              </div>

              {/* Full Name Field (Read-only from Google) */}
              <div className="group">
                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">
                  <User size={16} className="text-orange-500" />
                  Full Name
                  <span className="text-xs font-normal text-gray-500 dark:text-gray-400 normal-case">(from Google)</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    disabled
                    value={user?.fullName || ''}
                    className="w-full px-4 py-3.5 border-2 border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-750 cursor-not-allowed text-gray-600 dark:text-gray-400 opacity-60"
                  />
                </div>
              </div>

              {/* Email Field */}
              <div className="group">
                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">
                  <Mail size={16} className="text-orange-500" />
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    disabled={!isEditing}
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className={`w-full px-4 py-3.5 border-2 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all duration-200 focus:outline-none ${
                      isEditing 
                        ? 'border-gray-300 dark:border-gray-600 focus:border-orange-500 dark:focus:border-orange-400' 
                        : 'border-gray-200 dark:border-gray-700 cursor-not-allowed opacity-60'
                    }`}
                  />
                </div>
              </div>

              {/* Role Field (Read-only) */}
              <div className="group">
                <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">
                  <Shield size={16} className="text-orange-500" />
                  Role
                </label>
                <div className="relative">
                  <input
                    type="text"
                    disabled
                    value={user?.role || ''}
                    className="w-full px-4 py-3.5 border-2 border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-750 cursor-not-allowed text-gray-600 dark:text-gray-400 capitalize opacity-60"
                  />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex gap-3 mb-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 transition-all duration-200 font-semibold disabled:opacity-60 disabled:cursor-not-allowed shadow-lg hover:shadow-xl hover:scale-[1.02]"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin" size={18} />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Check size={18} />
                      Save Changes
                    </>
                  )}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={loading}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200 font-semibold disabled:opacity-60"
                >
                  <X size={18} />
                  Cancel
                </button>
              </div>
            )}

            {/* Logout Section */}
            <div className="pt-8 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] group"
              >
                <LogOut size={20} className="group-hover:-translate-x-1 transition-transform" />
                Logout from Account
                <ArrowUpRight size={16} className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
              </button>
            </div>
          </div>
        </div>

        {/* Info Card */}
        <div className="glass-card border-l-4 border-orange-500 p-6">
          <div className="flex gap-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                <span className="text-lg">💡</span>
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">Profile Information</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your full name is fetched from your Google account and cannot be changed directly. Update your profile picture and name in your Google Account settings if needed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;