# QuantumPlayground

A comprehensive quantum computing education platform with interactive simulations, theory, quizzes, and certificates.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd quantumMiniProject
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - Streamlit (web framework)
   - Qiskit (quantum computing framework)
   - Matplotlib, Plotly (visualizations)
   - Pillow (certificate generation)
   - And other dependencies

## Running the Application

1. **Start the Streamlit application:**
   ```bash
   streamlit run main.py
   ```

2. **Access the application:**
   - The application will automatically open in your default web browser
   - If it doesn't, navigate to: `http://localhost:8501`
   - The terminal will show the URL if needed

## First Time Setup

### Default Login Credentials

- **Username:** `admin`
- **Password:** `admin123`

You can also register a new account from the login page.

## Usage Guide

### 1. Login/Register
- Use the default credentials or create a new account
- Registration is available on the login page

### 2. Home Page
- View all available labs organized by category
- See your progress for each lab (quiz passed, certificate earned)
- Click "Start Lab" on any experiment card to begin

### 3. Lab Sections
Each lab follows this structure:

1. **📚 Theory**
   - Read the theoretical background
   - Click "Next: Test Your Knowledge" to proceed

2. **📝 Test**
   - Answer quiz questions
   - Must score 70% or higher to pass
   - Review explanations after submission
   - Once passed, proceed to simulation

3. **⚛️ Simulation**
   - Interactive quantum simulation
   - Experiment with parameters
   - Learn through hands-on practice

4. **🏆 Certificate**
   - Generate your certificate of completion
   - Download as PNG image
   - Available after passing the quiz

### 4. Navigation
- Use the sidebar to switch between sections
- Click "Back to Home" to return to the experiment list
- Your progress is automatically saved

## Available Labs

### Quantum Foundations (Beginner)
1. **Measurement in Different Bases** - Learn how quantum states behave when measured in different bases
2. **Quantum Random Number Generator** - Generate truly random numbers using quantum superposition

### Quantum States & Entanglement (Intermediate)
3. **Multi-Qubit Superposition** - Explore superposition with multiple qubits
4. **GHZ State Creation** - Create and verify Greenberger-Horne-Zeilinger entangled states
5. **W State Creation** - Generate and analyze W-type entangled states
6. **Effect of Noise on Bell States** - Study how noise affects maximally entangled Bell states

### Quantum Information (Intermediate-Advanced)
7. **Parity Check with Ancilla Qubit** - Implement parity checking using ancilla qubits
8. **Circuit Identity Verification** - Verify equivalence of quantum circuits
9. **Superdense Coding** - Transmit classical bits using entanglement
10. **Teleportation of a Quantum State** - Teleport quantum states using entanglement and classical communication

### Quantum Error Correction (Advanced)
11. **3-Qubit Bit Flip Code** - Detect and correct bit-flip errors
12. **3-Qubit Phase Flip Code** - Detect and correct phase-flip errors
13. **Quantum Error Correction** - Comprehensive error correction implementation

### Advanced Topics (Advanced)
14. **BB84 Quantum Key Distribution** - Secure key distribution with eavesdropper detection
15. **Quantum State Tomography** - Reconstruct quantum states from measurements
16. **Quantum Phase Estimation** - Estimate eigenvalue phases of unitary operators
17. **Quantum Random Walk** - Simulate quantum walks on graphs

## Troubleshooting

### Port Already in Use
If port 8501 is already in use, Streamlit will automatically use the next available port (8502, 8503, etc.). Check the terminal for the correct URL.

### Module Not Found Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Certificate Generation Issues
- Certificates use system fonts. If fonts are not found, default fonts will be used.
- On Windows: Arial should be available by default
- On macOS/Linux: System fonts will be used, or defaults if not available

### User Data
- User accounts are stored securely in MongoDB Atlas
- Lab progress is automatically saved to the database
- Progress persists across sessions and devices
- **Security Note:** Default admin credentials (admin/admin123) should be changed immediately in production environments

## Stopping the Application

- Press `Ctrl+C` in the terminal to stop the server
- Close the browser tab/window

## Development

### Project Structure
```
quantumMiniProject/
├── main.py              # Main application file
├── auth.py              # Authentication system
├── lab_config.py        # Lab configurations and theory
├── quiz.py              # Quiz module
├── certificate.py       # Certificate generator
├── requirements.txt     # Python dependencies
├── users.json           # User database (created automatically)
└── labs/                # Lab simulation modules
    ├── bb84.py
    ├── different_states.py
    ├── noise.py
    ├── random.py
    ├── parity.py
    ├── tele.py
    ├── supcod.py
    └── tomography.py
```

## Features

- ✅ User authentication and registration
- ✅ Theory sections for each lab
- ✅ Interactive quizzes with scoring
- ✅ Quantum simulations using Qiskit
- ✅ Certificate generation
- ✅ Progress tracking
- ✅ Modern, intuitive UI

## License

© 2025 QuantumPlayground • Developed at VESIT

## Support

For issues or questions, please check the troubleshooting section or contact the development team.

