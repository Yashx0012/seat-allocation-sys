# SeatWise - Frontend (React)

The administrative portal for SeatWise, built with React 18 and optimized for high-performance seating visualization and layout management.

**Version:** v2.4 | **Last Updated:** February 2026

## 🎨 Design Philosophy

The interface follows a **Modern Glassmorphism** aesthetic, designed to provide a premium, professional experience for educational administrators.

- **Glassy Navbar**: Subtle, transparent navigation boundaries that blend with the backdrop-blur effect
- **Dynamic Grid**: High-fidelity seating visualization handling 200+ students per room with zero lag
- **Micro-Animations**: Smooth transitions powered by GSAP and Framer Motion for enhanced user feedback
- **Responsive Layout**: Mobile-first design supporting tablets and desktop displays
- **Dark Mode Ready**: Theme-aware components with context-based styling

## 🛠️ Tech Stack

- **Framework**: React 18 with Hooks
- **Styling**: Vanilla CSS (Layouts) + Tailwind CSS (Components) + PostCSS
- **Animations**: GSAP (PillNav) + Framer Motion (Page Transitions)
- **Routing**: React Router DOM v6
- **State Management**: React Context API with custom hooks
- **HTTP Client**: Axios with interceptors for API calls
- **Build Tool**: Create React App

## 🔑 Key Components

### Navigation & Layout
- **Navbar**: Global navigation with theme toggling and glassmorphism styling
- **PillNav**: GSAP-animated pill-style navigation for secondary menus
- **Layout**: Sticky navbar with sidebar navigation on desktop

### Seating Management
- **Seating Designer**: Interactive tool for:
  - Configuring room dimensions (rows × columns)
  - Marking broken/unavailable seats
  - Selecting batch configurations
  - Choosing seating parameters
  
- **Seating Grid** 🆕: Enhanced visualization with:
  - Real-time student placement animation
  - Batch color-coding with legend
  - Paper set indicator (A/B) display
  - Zoom & pan functionality
  - Click-to-inspect seat details

- **Batch Configuration** 🆕: 
  - Multi-batch selection with toggles
  - Batch color picker
  - Roll number range input
  - Adjacent seating toggle for single-batch mode
  - Variable block structure input

### Dashboard & Analytics
- **Allocation Dashboard** 🆕: Live view with:
  - Constraint validation symbols
  - Paper set distribution chart
  - Batch-wise student count table
  - Export options (PDF, CSV)
  
- **Session Management**:
  - Active session display
  - Session history sidebar
  - Quick actions (Undo, Redo, Finalize)
  
- **Plan History**:
  - Recent allocations listing
  - Plan comparison view
  - Archive & restore functionality

### PDF & Reporting 🆕
- **Single Room PDF**: Export individual exam hall seating plans
- **Master Plan PDF**: Generate comprehensive A4 document with room-wise aggregation, branch identification, and institutional header

### Feedback System 🆕
- **Feedback Form**: Structured submission for constraint violations and seating issues
- **Feedback History**: View previously submitted feedback with status

## 📁 Project Structure

```
Frontend/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── robots.txt
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Navbar.jsx
│   │   ├── PillNav.jsx
│   │   ├── SeatingGrid.jsx
│   │   ├── BatchConfig.jsx
│   │   ├── FeedbackForm.jsx
│   │   └── ...
│   ├── pages/               # Page-level route components
│   ├── contexts/            # Global state management
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API client wrappers
│   ├── utils/               # Utilities & helpers
│   ├── App.jsx
│   ├── App.css
│   ├── index.js
│   └── index.css
├── docs/                    # Docusaurus documentation
├── package.json
├── postcss.config.js
├── tailwind.config.js
└── README.md
```

## 🚀 Development

### Installation
```bash
cd Frontend
npm install
```

### Environment Setup
```bash
cp .env.example .env
# Configure REACT_APP_API_URL=http://localhost:5000
```

### Available Scripts

- `npm start`: Development mode (http://localhost:3000)
- `npm run build`: Production build
- `npm test`: Test runner
- `npm run eject`: Eject from Create React App

### Documentation

```bash
cd docs
npm start    # Docusaurus development
npm run build # Production build
```

## 🌐 API Integration

All API calls use Axios with automatic interceptors. Key endpoints:

```
POST /api/generate-seating        # Generate seating plan
POST /api/generate-pdf             # Export single room PDF
POST /api/master-plan-pdf          # Export master plan (v2.4)
POST /api/feedback                 # Submit feedback (v2.4)
POST /api/sessions/start           # Start session
GET  /api/sessions/active          # Get active session
```

## 🎯 New Features in v2.4

- **Enhanced Seating Grid**: Zoom, pan, seat inspection
- **Batch Configuration**: Multi-batch UI with color picker
- **Master Plan Export**: Aggregate PDF generation
- **Feedback System**: Issue reporting and tracking
- **Session History**: Timeline and comparison views
- **Template Management**: Custom PDF templates

## 🔐 Authentication

- JWT token-based auth
- Context-based state management
- Automatic token refresh
- Protected routes

## ♿ Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- WCAG AA compliance

---

*SeatWise Frontend Team | v2.4 | Last Updated: February 2026*
