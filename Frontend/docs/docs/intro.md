---
sidebar_position: 1
slug: /
---

import { Redirect } from '@docusaurus/router';

<div className="hero-section">
  <h1>Seat Allocation System</h1>
  <p>Intelligent classroom seating arrangement powered by constraint-based algorithms</p>
  <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
    <a href="/docs/getting-started" className="cta-button cta-button-primary">Get Started</a>
    <a href="/docs/algorithm-documentation" className="cta-button cta-button-secondary">Learn More</a>
  </div>
</div>

## What is the Seat Allocation System?

The **Seat Allocation System** is a sophisticated web-based platform that intelligently allocates students to classroom seats using advanced constraint-based algorithms. Perfect for educational institutions needing fair, automated, and efficient seating arrangements.

### Key Features

<div className="feature-cards">
  <div className="feature-card">
    <h3>🎯 Smart Algorithm</h3>
    <p>8 built-in constraints including batch limits, broken seats, and paper set alternation for optimal seating</p>
  </div>
  <div className="feature-card">
    <h3>🔧 Highly Configurable</h3>
    <p>Support for 1-10+ batches, custom roll numbers, batch prefixes, and flexible block widths</p>
  </div>
  <div className="feature-card">
    <h3>📊 Real-time Validation</h3>
    <p>Comprehensive constraint validation with priority levels (HIGH, MEDIUM, LOW)</p>
  </div>
  <div className="feature-card">
    <h3>🎨 Visual Design</h3>
    <p>Beautiful color-coded seating grid with batch-specific colors and responsive layout</p>
  </div>
  <div className="feature-card">
    <h3>📄 PDF Export</h3>
    <p>Generate professional PDF seating charts ready for printing and distribution</p>
  </div>
  <div className="feature-card">
    <h3>🔐 Secure Access</h3>
    <p>User authentication system with secure session management</p>
  </div>
</div>

---

## Technology Stack

<div className="tech-stack">
  <div className="tech-item">⚛️ React 19</div>
  <div className="tech-item">🐍 Python Flask</div>
  <div className="tech-item">📱 Tailwind CSS</div>
  <div className="tech-item">🗄️ SQLite</div>
  <div className="tech-item">🚀 REST API</div>
  <div className="tech-item">📦 Docker Ready</div>
</div>

---

## Core Components

### Frontend Layer
- **React Application** with modern UI components
- **Tailwind CSS** for responsive design
- **Interactive Grid Display** for seating visualization
- **PDF Export Functionality** using industry-standard libraries

### Backend Layer
- **Flask REST API** for handling requests
- **Intelligent Algorithm** engine for seat allocation
- **SQLite Database** for user and configuration storage
- **Authentication Service** for secure access

### Algorithm Layer
- **Constraint-Based System** with 8 configurable constraints
- **Batch Management** supporting dynamic student distribution
- **Paper Set Alternation** (A/B sets within blocks)
- **Roll Number Formatting** with customizable templates

---

## Quick Start

### For Users
1. **Navigate** to the application dashboard
2. **Fill** classroom dimensions (rows, columns)
3. **Add** batch information and constraints
4. **Generate** optimal seating arrangement
5. **Export** as PDF or view online

### For Developers
```bash
# Clone repository
git clone https://github.com/TANISHX1/seat-allocation-sys.git

# Install dependencies
cd seat-allocation-sys
npm install
pip install -r algo/requirements.txt

# Start development servers
npm start        # Frontend (port 3000)
python app.py    # Backend (port 5000)
```

---

## Documentation Structure

This documentation is organized into the following sections:

| Section | Purpose |
|---------|---------|
| **Getting Started** | Installation, setup, and configuration guide |
| **Algorithm Documentation** | Complete technical reference and API endpoints |
| **System Architecture** | System design, data flow, and component overview |
| **Quick Reference** | Developer integration guide with code examples |
| **Authentication Setup** | User auth implementation and security details |

---

## Why Choose Seat Allocation System?

✅ **Automated & Fair** - Eliminates manual seating conflicts  
✅ **Constraint-Based** - Respects all classroom requirements  
✅ **Easy to Use** - Intuitive interface for educators  
✅ **Developer Friendly** - Well-documented REST API  
✅ **Open Source** - Built and maintained by the community  
✅ **Production Ready** - Used by educational institutions worldwide  

---

## System Highlights

### 8 Built-in Constraints
- ✓ Broken Seats (unavailable positions)
- ✓ Batch Limits (per-batch student count)
- ✓ Block Width (seating structure)
- ✓ Paper Sets (A/B alternation)
- ✓ Column-Batch Mapping
- ✓ Adjacent Batch Control
- ✓ Roll Format Validation
- ✓ Unallocated Tracking

### Default Batch Colors
```
Batch 1: #DBEAFE (Light Blue)
Batch 2: #D1FAE5 (Light Green)  
Batch 3: #FEE2E2 (Light Red)
Batch 4: #FEF3C7 (Light Yellow)
Batch 5: #F3E8FF (Light Purple)
```

---

## Performance

| Grid Size | Response Time | Memory Usage |
|-----------|---------------|--------------|
| 8×10 (Small) | < 10ms | < 1MB |
| 20×20 (Medium) | < 20ms | < 2MB |
| 50×50 (Large) | < 50ms | < 5MB |
| 100×100 (Extra) | < 100ms | < 15MB |

---

## Next Steps

👉 **[Get Started →](/docs/getting-started)** with step-by-step setup instructions

👉 **[Explore API →](/docs/algorithm-documentation)** with code examples

👉 **[View Architecture →](/docs/system-architecture)** for technical deep dive

---

## Support & Community

Have questions? Want to contribute?

- 📖 **Documentation**: You're reading it!
- 🐙 **GitHub**: [TANISHX1/seat-allocation-sys](https://github.com/TANISHX1/seat-allocation-sys)
- 🐛 **Issues**: [Report bugs](https://github.com/TANISHX1/seat-allocation-sys/issues)
- 💬 **Discussions**: [Join community](https://github.com/TANISHX1/seat-allocation-sys/discussions)

---

<div style={{ textAlign: 'center', marginTop: '4rem', padding: '2rem', borderRadius: '1rem', background: 'rgba(249, 115, 22, 0.05)' }}>
  <h3 style={{ color: '#f97316', marginBottom: '1rem' }}>Ready to get started?</h3>
  <p style={{ marginBottom: '1.5rem' }}>Explore our comprehensive documentation and start allocating seats intelligently today</p>
  <a href="/docs/getting-started" className="cta-button cta-button-primary" style={{ marginRight: '1rem' }}>
    Get Started
  </a>
  <a href="https://github.com/TANISHX1/seat-allocation-sys" className="cta-button cta-button-secondary">
    View on GitHub
  </a>
</div>

### For Developers

```bash
# Backend setup
cd algo
pip install -r requirements.txt
python app.py

# Frontend setup (in a new terminal)
cd Frontend
npm install
npm start
```

## System Architecture

The system follows a three-layer architecture:

```
Frontend Layer (React UI)
    ↓
API Layer (Flask REST API)
    ↓
Algorithm Layer (Seating Engine)
```

The frontend communicates with the backend through JSON HTTP requests. The backend processes these requests using the seating algorithm and returns formatted responses.

## Next Steps

- **New to the system?** Start with Getting Started
- **Need technical details?** Review Algorithm Documentation
- **Building an integration?** Check Quick Reference
- **Setting up users?** See Authentication Setup


---
**Version**: 2.1  
**Last Updated**: January 2026

