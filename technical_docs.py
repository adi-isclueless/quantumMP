"""
Technical Documentation for Quantum Playground
"""

TECHNICAL_DOCUMENTATION = """

### System Architecture
```
┌─────────────────┐
│   Streamlit     │ ← Frontend Framework
│   (Python)      │
└────────┬────────┘
         │
    ┌────▼─────┐
    │   Auth   │ ← OTP-based Email Authentication
    └────┬─────┘
         │
┌────────▼──────────┐
│   Main App        │
│  - Lab Router     │
│  - Progress Track │
└────────┬──────────┘
         │
    ┌────▼─────────────┐
    │  Lab Modules     │
    │  (14 experiments)│
    └────┬─────────────┘
         │
┌────────▼──────────┐     ┌──────────────┐
│   Qiskit Engine   │────▶│  AerSimulator│
│  (Quantum Sim)    │     └──────────────┘
└───────────────────┘
         │
    ┌────▼─────┐
    │ MongoDB  │ ← Progress & User Data
    └──────────┘
```

## 2. Technology Stack

### Frontend
- Framework: Streamlit 1.30+
- UI Components: Native Streamlit widgets
- Styling: Custom CSS via markdown and HTML components
- Responsiveness: Automatic mobile/desktop detection

### Backend
- Language: Python 3.10+
- Quantum Engine: Qiskit 1.0+ (qiskit-aer for simulation)
- Database: MongoDB Atlas (cloud-hosted)
- Authentication: Custom OTP system with email delivery

### Visualization
- Plotting: Matplotlib 3.8+, Plotly 5.18+
- Quantum Circuits: Qiskit circuit_drawer
- LaTeX Rendering: Streamlit native st.latex()
- Report Generation: ReportLab (PDF)

### Dependencies
```python
streamlit>=1.30.0
qiskit>=1.0.0
qiskit-aer>=0.13.0
matplotlib>=3.8.0
plotly>=5.18.0
numpy>=1.24.0
pandas>=2.0.0
pymongo>=4.6.0
reportlab>=4.0.0
pillow>=10.0.0
scipy>=1.11.0
```

## 3. Core Features

### Authentication System
- OTP Generation: 6-digit random codes
- Email Delivery: SMTP-based (configurable)
- Session Management: Streamlit session_state
- Security: Bcrypt password hashing (optional enhancement)

### Lab Module Structure
Each lab implements:
- `run()` - Main simulation function
- Circuit creation with Qiskit
- Interactive parameter controls
- Real-time visualization
- Data storage for reports

### Progress Tracking
- Storage: MongoDB collections: `users`, `lab_progress`
- Metrics: Quiz scores, simulation completion, certificates
- Persistence: Auto-save on every action
- Sync: Cross-device via user_id

### Report Generation
- Format: PDF via ReportLab
- Contents: Theory, metrics, figures, circuits
- Fallback: Preloaded default figures from `lab_figures.py`
- Storage: In-memory BytesIO → download button

## 4. Quantum Experiments (14 Labs)

| Lab ID | Title | Category | Difficulty |
|--------|-------|----------|-----------|
| `different_states` | Measurement in Different Bases | Measurement | Beginner |
| `randomng` | Quantum Random Number Generator | Randomness | Beginner |
| `multi_qubit_superposition` | Multi-Qubit Superposition | Superposition | Beginner |
| `parity` | Parity Check with Ancilla | Measurement | Intermediate |
| `circuit_identity` | Circuit Identity Verification | Fundamentals | Intermediate |
| `noise` | Bell State Analysis & Noise | Entanglement | Intermediate |
| `ghz_state` | GHZ State (3-Qubit Entanglement) | Entanglement | Intermediate |
| `w_state` | W State (3-Qubit Entanglement) | Entanglement | Intermediate |
| `bb84` | BB84 Quantum Key Distribution | Cryptography | Advanced |
| `supcod` | Superdense Coding | Communication | Advanced |
| `tele` | Quantum Teleportation | Communication | Advanced |
| `tomography` | Quantum State Tomography | Measurement | Advanced |
| `phase_flip_code` | 3-Qubit Phase Flip Code | Error Correction | Advanced |
| `bit_flip_code` | 3-Qubit Bit Flip Code | Error Correction | Advanced |

## 5. Performance & Scalability

### Optimization
- Session-based caching for repeated computations
- Precomputed defaults for common use cases
- Efficient state management

### Database
- MongoDB Atlas cloud-hosted
- Indexes: user_id, lab_id (compound index)
- Queries: Fast average latency
- Backup: Automatic daily snapshots

### Caching Strategy
- `@st.cache_data` for expensive computations
- Session state for UI persistence
- Preloaded figures in `lab_figures.py`

## 6. Security

### Authentication
- OTP via email (6-digit code)
- Session timeout: 24 hours
- No passwords stored (OTP-only design)

### Data Privacy
- User data: email, name, progress (no PII beyond email)
- MongoDB connections over TLS
- Environment variables for secrets (.env file)

### Input Validation
- Streamlit widgets (type-safe by default)
- Range constraints on sliders
- Sanitized PDF generation (no user-controlled file paths)

## 7. Mobile Optimization

### Responsive Design
- Automatic layout adjustment via Streamlit
- Collapsible sidebar on mobile
- Touch-friendly buttons (use_container_width=True)
- Reduced chart sizes on small screens

### Mobile-Specific Features
- Bottom navigation for labs (mobile only)
- Swipe-friendly tabs
- Simplified sidebar (fewer expanders)

## 8. Contact & Support

Developers:
- Aditya Upasani (Lead Developer)
- Abhishek Vishwakarma
- Yash Mahajan
- Ryan D'Souza

Mentor:
Dr. Ranjan Bala Jain (EXTC, VESIT)

Institution:
Vivekanand Education Society's Institute of Technology, Mumbai

License: MIT (Educational Use)

---
Last Updated: November 2025
Version: 1.0.0
"""
