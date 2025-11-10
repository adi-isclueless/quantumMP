"""
Lab configuration and metadata
Contains theory content, quiz questions, and lab information for all experiments
"""

LABS = {
    "Measurement in Different Bases": {
        "id": "different_states",
        "module": "different_states",
        "title": "Measurement in Different Bases",
        "description": "Learn how quantum states behave when measured in different bases (Z, X, Y).",
        "category": "Quantum Foundations",
        "difficulty": "Beginner",
        "theory": """
# Measurement in Different Bases

## Introduction

Quantum measurement is one of the most fundamental and mysterious aspects of quantum mechanics. Unlike classical measurement, which simply reveals a pre-existing property, quantum measurement fundamentally alters the state of the system being measured.

## Key Concepts

### 1. Quantum Bases

A **basis** is a set of orthogonal states that can be used to describe any quantum state. The most common bases are:

- **Z-basis (Computational basis)**: {|0⟩, |1⟩}
- **X-basis (Hadamard basis)**: {|+⟩, |-⟩} where |+⟩ = (|0⟩ + |1⟩)/√2 and |-⟩ = (|0⟩ - |1⟩)/√2
- **Y-basis**: {|+i⟩, |-i⟩} where |+i⟩ = (|0⟩ + i|1⟩)/√2 and |-i⟩ = (|0⟩ - i|1⟩)/√2

### 2. Measurement Postulate

When a quantum state is measured in a particular basis:
1. The state **collapses** to one of the basis states
2. The probability of collapsing to each basis state is given by the squared magnitude of the amplitude
3. After measurement, the state is in the measured basis state

### 3. States Used in This Lab

- **|+⟩ state**: Created by applying a Hadamard gate to |0⟩
  - In Z-basis: 50% probability of |0⟩, 50% probability of |1⟩
  - In X-basis: 100% probability of |+⟩ (deterministic)
  - In Y-basis: 50% probability of |+i⟩, 50% probability of |-i⟩

- **|i⟩ state**: Created by applying H and S gates to |0⟩
  - In Z-basis: 50% probability of |0⟩, 50% probability of |1⟩
  - In X-basis: 50% probability of |+⟩, 50% probability of |-⟩
  - In Y-basis: 100% probability of |+i⟩ (deterministic)

### 4. Bloch Sphere Representation

The Bloch sphere is a geometric representation of a quantum state:
- **Z-basis measurements**: Along the Z-axis (north/south pole)
- **X-basis measurements**: Along the X-axis (east/west)
- **Y-basis measurements**: Along the Y-axis (front/back)

## Applications

- **Quantum cryptography**: Basis choice is crucial in protocols like BB84
- **Quantum error correction**: Understanding measurement in different bases helps detect and correct errors
- **Quantum algorithms**: Many algorithms rely on measurements in specific bases

## Exercises

1. Prepare the |+⟩ state and measure it in the Z-basis. What probabilities do you observe?
2. Measure the |+⟩ state in the X-basis. Why is the result deterministic?
3. Compare measurements of |i⟩ in different bases. What patterns do you notice?
        """,
        "quiz": [
            {
                "question": "What happens when you measure the |+⟩ state in the Z-basis?",
                "options": ["Always |0⟩", "Always |1⟩", "50% |0⟩, 50% |1⟩", "100% |+⟩"],
                "correct": 2,
                "explanation": "The |+⟩ state is an equal superposition of |0⟩ and |1⟩, so measuring in Z-basis gives equal probabilities."
            },
            {
                "question": "What is the result of measuring |+⟩ in the X-basis?",
                "options": ["Random", "50% |+⟩, 50% |-⟩", "100% |+⟩", "50% |0⟩, 50% |1⟩"],
                "correct": 2,
                "explanation": "Since |+⟩ is already an eigenstate of the X-basis, it always measures as |+⟩."
            },
            {
                "question": "Which gate creates the |i⟩ state from |0⟩?",
                "options": ["H only", "H then S", "X then H", "Z then H"],
                "correct": 1,
                "explanation": "The |i⟩ state is created by applying Hadamard (H) followed by Phase (S) gate."
            },
            {
                "question": "What is the key difference between Z and X basis measurements?",
                "options": ["Z is faster", "X uses different gates", "They measure along different axes on the Bloch sphere", "No difference"],
                "correct": 2,
                "explanation": "Z and X bases measure along perpendicular axes on the Bloch sphere, representing different observables."
            },
            {
                "question": "Why is quantum measurement different from classical measurement?",
                "options": ["It's faster", "It reveals pre-existing values", "It collapses the quantum state", "It's more accurate"],
                "correct": 2,
                "explanation": "Quantum measurement collapses the superposition into a definite state, unlike classical measurement which just reveals existing values."
            }
        ]
    },
    "Random Number Generator": {
        "id": "random",
        "module": "random",
        "title": "Quantum Random Number Generator",
        "description": "Generate truly random numbers using quantum superposition and measurement.",
        "category": "Quantum Foundations",
        "difficulty": "Beginner",
        "theory": """
# Quantum Random Number Generator

## Introduction

Random number generation is crucial for cryptography, simulations, and security applications. Classical computers can only generate **pseudo-random** numbers using algorithms, which are deterministic and predictable if you know the algorithm and seed. Quantum computers can generate **truly random** numbers based on fundamental quantum uncertainty.

## Key Concepts

### 1. Quantum Superposition

When a qubit is in a superposition state:
- |ψ⟩ = α|0⟩ + β|1⟩
- |α|² is the probability of measuring |0⟩
- |β|² is the probability of measuring |1⟩
- For a balanced superposition: |α|² = |β|² = 0.5

### 2. Hadamard Gate

The Hadamard gate creates a balanced superposition:
- H|0⟩ = (|0⟩ + |1⟩)/√2 = |+⟩
- H|1⟩ = (|0⟩ - |1⟩)/√2 = |-⟩

### 3. Quantum Randomness

Quantum randomness comes from:
- **Heisenberg Uncertainty Principle**: Cannot predict measurement outcomes
- **Wave function collapse**: Measurement forces a random collapse
- **No hidden variables**: The randomness is fundamental, not due to our ignorance

### 4. QRNG Circuit

1. Initialize qubits in |0⟩ state
2. Apply Hadamard gate to each qubit (creates superposition)
3. Measure all qubits
4. Convert binary result to decimal number

### 5. Statistical Properties

- **Uniformity**: All outcomes should be equally likely
- **Independence**: Each measurement is independent
- **Unpredictability**: Cannot predict next outcome from previous ones

### 6. Entropy Measures

- **Min-Entropy (H∞)**: Worst-case unpredictability (most important for cryptography)
- **Shannon Entropy (H)**: Average information content
- **Collision Entropy (Hc)**: Probability of getting same value twice

## Applications

- **Cryptography**: Key generation, nonces, one-time pads
- **Gaming**: Fair random number generation
- **Monte Carlo simulations**: Scientific computing
- **Security**: Password generation, tokens

## Advantages Over Classical RNGs

1. **True randomness**: Not pseudo-random
2. **Unpredictability**: Cannot be predicted even with full knowledge
3. **Security**: Essential for cryptographic applications
4. **No seed required**: Doesn't need initial seed value

## Statistical Tests

- **Chi-square test**: Tests for uniform distribution
- **P-value**: Should be > 0.05 for good randomness
- **Frequency analysis**: All values should appear equally often
        """,
        "quiz": [
            {
                "question": "What makes quantum random numbers truly random?",
                "options": ["Complex algorithms", "Quantum superposition and measurement", "Better hardware", "Larger seed values"],
                "correct": 1,
                "explanation": "Quantum randomness comes from the fundamental uncertainty in quantum measurement, not algorithms."
            },
            {
                "question": "Which gate is used to create superposition in a QRNG?",
                "options": ["X gate", "Z gate", "Hadamard gate", "CNOT gate"],
                "correct": 2,
                "explanation": "The Hadamard gate creates an equal superposition of |0⟩ and |1⟩ states."
            },
            {
                "question": "What is the key advantage of QRNGs over classical RNGs?",
                "options": ["Faster generation", "Smaller size", "True randomness", "Lower cost"],
                "correct": 2,
                "explanation": "QRNGs provide true randomness based on quantum mechanics, unlike pseudo-random classical RNGs."
            },
            {
                "question": "Which entropy measure is most important for cryptography?",
                "options": ["Shannon entropy", "Min-entropy", "Collision entropy", "All are equal"],
                "correct": 1,
                "explanation": "Min-entropy measures worst-case unpredictability, which is crucial for cryptographic security."
            },
            {
                "question": "What does a p-value > 0.05 in chi-square test indicate?",
                "options": ["Poor randomness", "Good randomness", "Invalid test", "Too many samples"],
                "correct": 1,
                "explanation": "A p-value > 0.05 indicates the distribution is uniform, suggesting good randomness."
            }
        ]
    },
    "Parity Check with Ancilla Qubit": {
        "id": "parity",
        "module": "parity",
        "title": "Parity Check with Ancilla Qubit",
        "description": "Use an ancilla qubit to determine the parity of multi-qubit states.",
        "category": "Quantum Logic & Operations",
        "difficulty": "Intermediate",
        "theory": """
# Parity Check with Ancilla Qubit

## Introduction

Parity checking is a fundamental operation in both classical and quantum computing. It determines whether the number of 1s in a binary string is even or odd. In quantum computing, we use an **ancilla qubit** (helper qubit) to compute parity without directly measuring the input qubits.

## Key Concepts

### 1. Parity Definition

- **Even parity**: Number of 1s is even (0, 2, 4, ...)
- **Odd parity**: Number of 1s is odd (1, 3, 5, ...)

### 2. Ancilla Qubit

An **ancilla qubit** is an auxiliary qubit used to:
- Store intermediate computational results
- Perform computations without disturbing input qubits
- Enable reversible quantum operations

### 3. Parity Check Circuit

For a 3-qubit input (q0, q1, q2):
1. Initialize ancilla qubit (q3) in |0⟩
2. Apply CNOT from each input qubit to ancilla:
   - CNOT(q0, q3)
   - CNOT(q1, q3)
   - CNOT(q2, q3)
3. Measure ancilla qubit
   - Result 0 = Even parity
   - Result 1 = Odd parity

### 4. CNOT Gate Operation

CNOT (Controlled-NOT) gate:
- If control qubit is |0⟩: target qubit unchanged
- If control qubit is |1⟩: target qubit flipped (X gate applied)

### 5. How It Works

- Each CNOT flips the ancilla if input qubit is |1⟩
- Even number of flips → ancilla returns to |0⟩
- Odd number of flips → ancilla becomes |1⟩
- Ancilla state encodes the parity information

### 6. Reversibility

- The input qubits are not measured directly
- Their states are preserved (in ideal case)
- Only ancilla is measured to get parity

## Applications

- **Error detection**: Classical and quantum error correction
- **Quantum algorithms**: Many algorithms use parity operations
- **Quantum error correction**: Detecting bit-flip errors
- **Quantum communication**: Parity-based protocols

## Advantages

1. **Non-destructive**: Input qubits not directly measured
2. **Reversible**: Can be undone if needed
3. **Efficient**: Single ancilla for any number of input qubits
4. **Quantum**: Works with superposition states

## Example

For input |101⟩:
- q0=1: CNOT flips ancilla to |1⟩
- q1=0: CNOT does nothing (ancilla stays |1⟩)
- q2=1: CNOT flips ancilla back to |0⟩
- Result: Even parity (two 1s)
        """,
        "quiz": [
            {
                "question": "What is an ancilla qubit?",
                "options": ["An input qubit", "A helper qubit for computations", "A measured qubit", "A noisy qubit"],
                "correct": 1,
                "explanation": "An ancilla qubit is an auxiliary qubit used to store intermediate results in quantum computations."
            },
            {
                "question": "What does the ancilla qubit store in a parity check?",
                "options": ["The input state", "The parity (even/odd)", "The measurement result", "Random data"],
                "correct": 1,
                "explanation": "The ancilla qubit stores the parity information: |0⟩ for even, |1⟩ for odd."
            },
            {
                "question": "How many CNOT gates are needed for a 3-qubit parity check?",
                "options": ["1", "2", "3", "4"],
                "correct": 2,
                "explanation": "One CNOT gate from each input qubit to the ancilla, so 3 CNOT gates for 3 input qubits."
            },
            {
                "question": "What is the parity of |101⟩?",
                "options": ["Even", "Odd", "Cannot determine", "Depends on measurement"],
                "correct": 0,
                "explanation": "|101⟩ has two 1s, which is an even number, so it has even parity."
            },
            {
                "question": "Why is the ancilla approach useful?",
                "options": ["It's faster", "It preserves input qubit states", "It uses less memory", "It's more accurate"],
                "correct": 1,
                "explanation": "The ancilla approach allows parity computation without directly measuring the input qubits, preserving their quantum states."
            }
        ]
    },
    "Effect of Noise on Bell States": {
        "id": "noise",
        "module": "noise",
        "title": "Effect of Noise on Bell States",
        "description": "Explore how different types of noise affect entangled Bell states.",
        "category": "Quantum Entanglement & Noise",
        "difficulty": "Intermediate",
        "theory": """
# Effect of Noise on Bell States

## Introduction

Quantum states are fragile and easily affected by their environment. This interaction with the environment is called **decoherence** or **noise**. Understanding how noise affects quantum states, especially entangled states like Bell states, is crucial for quantum computing and quantum communication.

## Key Concepts

### 1. Bell States

Bell states are maximally entangled two-qubit states:
- |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
- |Φ⁻⟩ = (|00⟩ - |11⟩)/√2
- |Ψ⁺⟩ = (|01⟩ + |10⟩)/√2
- |Ψ⁻⟩ = (|01⟩ - |10⟩)/√2

### 2. Entanglement

- **Maximal entanglement**: Bell states have maximum entanglement
- **Non-locality**: Measurement on one qubit instantly affects the other
- **Correlation**: Perfect correlation between qubits

### 3. Types of Noise

#### Depolarizing Noise
- Randomly applies X, Y, or Z gates with equal probability
- Causes complete decoherence at high strength
- Most general type of noise

#### Amplitude Damping
- Models energy dissipation
- |1⟩ state decays to |0⟩
- Important for physical qubits

#### Phase Damping
- Causes loss of phase information
- Preserves energy but destroys coherence
- Also called dephasing

### 4. Fidelity

Fidelity measures how close a noisy state is to the ideal state:
- Fidelity = 1: Perfect match
- Fidelity = 0: Completely different
- Higher fidelity = better state preservation

### 5. Noise Effects on Bell States

- **Depolarizing**: Gradually destroys all correlations
- **Amplitude damping**: Causes asymmetric decay
- **Phase damping**: Destroys phase coherence but preserves some correlations

### 6. Measurement Outcomes

- **Ideal Bell state**: Perfect correlations (e.g., |00⟩ and |11⟩ only)
- **Noisy state**: Introduces errors (e.g., |01⟩ and |10⟩ appear)
- **Error rate**: Increases with noise strength

## Applications

- **Quantum error correction**: Understanding noise helps design error correction
- **Quantum communication**: Noise limits communication distance
- **Quantum computing**: Noise is the main obstacle to large-scale quantum computers
- **Quantum sensing**: Understanding noise improves sensor performance

## Mitigation Strategies

1. **Error correction codes**: Detect and correct errors
2. **Error mitigation**: Post-process to reduce noise effects
3. **Better hardware**: Reduce environmental noise
4. **Fault tolerance**: Operate despite noise
        """,
        "quiz": [
            {
                "question": "What are Bell states?",
                "options": ["Single qubit states", "Maximally entangled two-qubit states", "Noisy states", "Classical states"],
                "correct": 1,
                "explanation": "Bell states are four maximally entangled two-qubit states that show perfect correlations."
            },
            {
                "question": "What does depolarizing noise do?",
                "options": ["Adds energy", "Randomly applies X, Y, or Z gates", "Only affects phase", "Only affects amplitude"],
                "correct": 1,
                "explanation": "Depolarizing noise randomly applies Pauli gates (X, Y, Z) with equal probability."
            },
            {
                "question": "What is fidelity?",
                "options": ["Noise strength", "Measure of state similarity", "Error rate", "Gate count"],
                "correct": 1,
                "explanation": "Fidelity measures how close a quantum state is to an ideal state, ranging from 0 to 1."
            },
            {
                "question": "How does amplitude damping affect |1⟩?",
                "options": ["No effect", "Decays to |0⟩", "Becomes |+⟩", "Becomes |-⟩"],
                "correct": 1,
                "explanation": "Amplitude damping models energy dissipation, causing |1⟩ to decay to |0⟩."
            },
            {
                "question": "Why is noise a problem for quantum computing?",
                "options": ["It's expensive", "It destroys quantum states and correlations", "It's slow", "It's hard to implement"],
                "correct": 1,
                "explanation": "Noise destroys quantum coherence and entanglement, which are essential for quantum computing."
            }
        ]
    },
    "BB84 Quantum Key Distribution": {
        "id": "bb84",
        "module": "bb84",
        "title": "BB84 Quantum Key Distribution",
        "description": "Learn the first quantum key distribution protocol for secure communication.",
        "category": "Quantum Communication Protocols",
        "difficulty": "Advanced",
        "theory": """
# BB84 Quantum Key Distribution

## Introduction

BB84 is the first quantum key distribution (QKD) protocol, invented by Charles Bennett and Gilles Brassard in 1984. It allows two parties (Alice and Bob) to establish a shared secret key using quantum mechanics, with guaranteed detection of any eavesdropping.

## Key Concepts

### 1. Protocol Steps

1. **Alice prepares qubits**: Randomly chooses bit (0 or 1) and basis (Z or X)
2. **Quantum transmission**: Sends qubits to Bob through quantum channel
3. **Bob measures**: Randomly chooses measurement basis (Z or X)
4. **Basis reconciliation**: Publicly compare bases, keep matching ones (~50%)
5. **Error estimation**: Sacrifice some bits to estimate error rate (QBER)
6. **Privacy amplification**: Use remaining bits as secret key

### 2. Quantum Bases

- **Z-basis (computational)**: {|0⟩, |1⟩}
- **X-basis (Hadamard)**: {|+⟩, |-⟩}

### 3. Security Principle

- **No-cloning theorem**: Cannot perfectly copy quantum states
- **Measurement disturbance**: Measuring disturbs the state
- **Eavesdropping detection**: Any interception introduces errors

### 4. Quantum Bit Error Rate (QBER)

- Measures percentage of errors in sifted key
- QBER < 11%: Channel is secure
- QBER ≥ 11%: Possible eavesdropping detected

### 5. Sifting Efficiency

- Only ~50% of bits survive basis reconciliation
- This is expected and necessary for security
- Remaining bits form the sifted key

### 6. Eavesdropping (Eve)

If Eve intercepts:
- Must measure qubits (disturbs them)
- Cannot know correct basis
- Resends disturbed states to Bob
- Introduces errors that Alice and Bob detect

## Applications

- **Secure communication**: Bank transfers, government communications
- **Quantum networks**: Building quantum internet
- **Cryptography**: Unconditionally secure key distribution
- **Research**: Quantum communication protocols

## Advantages

1. **Unconditional security**: Based on physics, not computational difficulty
2. **Eavesdropping detection**: Any interception is detectable
3. **Information-theoretic security**: No assumptions about computational power
4. **Future-proof**: Secure against future quantum computers

## Limitations

- **Distance**: Limited to ~100 km in fiber, ~1000 km via satellite
- **Rate**: Key generation rates are relatively slow
- **Cost**: Requires specialized quantum hardware
- **Infrastructure**: Needs quantum channels
        """,
        "quiz": [
            {
                "question": "What is the main purpose of BB84?",
                "options": ["Quantum computing", "Secure key distribution", "Error correction", "State preparation"],
                "correct": 1,
                "explanation": "BB84 is a quantum key distribution protocol for establishing shared secret keys securely."
            },
            {
                "question": "What happens during basis reconciliation?",
                "options": ["Keys are compared", "Bases are publicly compared, matching bits kept", "Errors are corrected", "Qubits are measured"],
                "correct": 1,
                "explanation": "Alice and Bob publicly compare their basis choices and keep only bits where bases matched."
            },
            {
                "question": "What is the security threshold for QBER?",
                "options": ["5%", "11%", "25%", "50%"],
                "correct": 1,
                "explanation": "If QBER is below 11%, the channel is considered secure. Above 11% indicates possible eavesdropping."
            },
            {
                "question": "Why can't Eve perfectly intercept BB84?",
                "options": ["It's illegal", "Measurement disturbs quantum states", "She doesn't have the right equipment", "It's too expensive"],
                "correct": 1,
                "explanation": "The no-cloning theorem and measurement disturbance mean any interception introduces detectable errors."
            },
            {
                "question": "What percentage of bits typically survive sifting?",
                "options": ["25%", "50%", "75%", "100%"],
                "correct": 1,
                "explanation": "Since bases are chosen randomly, approximately 50% of bits have matching bases and survive sifting."
            }
        ]
    },
    "Superdense Coding": {
        "id": "supcod",
        "module": "supcod",
        "title": "Superdense Coding",
        "description": "Transmit two classical bits using a single qubit through quantum entanglement.",
        "category": "Quantum Communication Protocols",
        "difficulty": "Intermediate",
        "theory": """
# Superdense Coding

## Introduction

Superdense coding is a quantum communication protocol that allows Alice to transmit **two classical bits** of information to Bob using only **one qubit**, by leveraging a shared entangled Bell pair. This demonstrates the power of quantum entanglement for communication.

## Key Concepts

### 1. Protocol Setup

1. **Shared entanglement**: Alice and Bob share a Bell pair |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
2. **Alice encodes**: Applies one of four operations to her qubit based on 2-bit message:
   - 00: Identity (I) - no operation
   - 01: X gate
   - 10: Z gate
   - 11: X then Z gate
3. **Alice sends**: Sends her qubit to Bob
4. **Bob decodes**: Performs Bell measurement to recover the 2-bit message

### 2. Encoding Operations

The four operations transform the Bell state:
- I: |Φ⁺⟩ → |Φ⁺⟩
- X: |Φ⁺⟩ → |Ψ⁺⟩
- Z: |Φ⁺⟩ → |Φ⁻⟩
- XZ: |Φ⁺⟩ → |Ψ⁻⟩

### 3. Bell Measurement

Bob performs:
1. CNOT(Alice's qubit, Bob's qubit)
2. Hadamard on Alice's qubit
3. Measure both qubits
4. Measurement result directly gives the 2-bit message

### 4. Information Advantage

- **Classical**: 1 bit per qubit (at most)
- **Superdense coding**: 2 bits per qubit
- **Factor of 2 improvement**: But requires shared entanglement

### 5. Entanglement as Resource

- Entanglement must be established beforehand
- This requires quantum communication
- The advantage is in **communication efficiency**, not total resources

### 6. Measurement Results

- |00⟩ → Message was 00
- |01⟩ → Message was 01
- |10⟩ → Message was 10
- |11⟩ → Message was 11

## Applications

- **Quantum communication**: Efficient information transmission
- **Quantum networks**: Building quantum internet
- **Quantum protocols**: Foundation for other protocols
- **Research**: Understanding quantum information theory

## Advantages

1. **2:1 compression**: Two bits in one qubit
2. **Perfect fidelity**: No errors in ideal case
3. **Secure**: Entanglement provides security
4. **Demonstrates entanglement**: Shows power of quantum correlations

## Limitations

- **Requires entanglement**: Must establish Bell pair first
- **No net advantage**: Total resources (entanglement + communication) same
- **One-way**: Only Alice to Bob communication
- **Ideal case**: Real implementations have noise and errors
        """,
        "quiz": [
            {
                "question": "How many classical bits can be transmitted with one qubit in superdense coding?",
                "options": ["1 bit", "2 bits", "3 bits", "4 bits"],
                "correct": 1,
                "explanation": "Superdense coding allows transmission of 2 classical bits using 1 qubit."
            },
            {
                "question": "What resource is required for superdense coding?",
                "options": ["Multiple qubits", "Shared entanglement", "Classical channel", "Quantum computer"],
                "correct": 1,
                "explanation": "Superdense coding requires a shared entangled Bell pair between Alice and Bob."
            },
            {
                "question": "What operation does Alice apply for message '01'?",
                "options": ["I gate", "X gate", "Z gate", "X then Z"],
                "correct": 1,
                "explanation": "Alice applies X gate to encode the message '01' in superdense coding."
            },
            {
                "question": "What does Bob perform to decode the message?",
                "options": ["X measurement", "Z measurement", "Bell measurement", "Hadamard measurement"],
                "correct": 2,
                "explanation": "Bob performs a Bell measurement (CNOT + H + measure) to decode the 2-bit message."
            },
            {
                "question": "What is the main advantage of superdense coding?",
                "options": ["Faster communication", "2:1 bit compression", "Lower cost", "Better security"],
                "correct": 1,
                "explanation": "Superdense coding provides 2:1 compression, transmitting 2 bits using 1 qubit."
            }
        ]
    },
    "Teleportation of a Quantum State": {
        "id": "tele",
        "module": "tele",
        "title": "Teleportation of a Quantum State",
        "description": "Transfer a quantum state from Alice to Bob using entanglement and classical communication.",
        "category": "Quantum Communication Protocols",
        "difficulty": "Advanced",
        "theory": """
# Quantum Teleportation

## Introduction

Quantum teleportation is a protocol that allows Alice to transfer an unknown quantum state to Bob using a shared entangled pair and classical communication. Despite its name, it doesn't transfer matter or energy faster than light - it transfers quantum information.

## Key Concepts

### 1. Protocol Steps

1. **Shared entanglement**: Alice and Bob share a Bell pair |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
2. **State to teleport**: Alice has qubit in unknown state |ψ⟩ = α|0⟩ + β|1⟩
3. **Bell measurement**: Alice performs Bell measurement on her two qubits
4. **Classical communication**: Alice sends 2 classical bits to Bob
5. **Correction**: Bob applies correction gates based on Alice's message
6. **Result**: Bob's qubit is now in state |ψ⟩

### 2. Bell Measurement

Alice measures her qubits in Bell basis:
- Measures both qubits
- Gets one of four outcomes: 00, 01, 10, 11
- Each outcome corresponds to a different Bell state

### 3. Correction Operations

Based on Alice's measurement result, Bob applies:
- 00: No operation (I)
- 01: X gate
- 10: Z gate
- 11: X then Z gate

### 4. Why It Works

- Entanglement creates correlations
- Bell measurement projects onto entangled states
- Classical bits communicate which correction is needed
- Correction restores the original state

### 5. Important Properties

- **No cloning**: Original state is destroyed (no-cloning theorem)
- **Classical communication**: Requires 2 classical bits
- **No faster-than-light**: Classical communication limits speed
- **Perfect in theory**: Ideal case has 100% fidelity

### 6. Resource Requirements

- 1 shared Bell pair (entanglement)
- 2 classical bits (communication)
- Local quantum operations
- Total: Entanglement + classical communication

## Applications

- **Quantum networks**: Transferring quantum states
- **Quantum computing**: Moving qubits between processors
- **Quantum communication**: Building quantum internet
- **Quantum repeaters**: Extending communication distance

## Advantages

1. **No physical transfer**: State is recreated, not moved
2. **Works for unknown states**: Don't need to know the state
3. **Perfect fidelity**: In ideal case
4. **Fundamental protocol**: Basis for many quantum protocols

## Limitations

- **Destroys original**: Original state is measured (destroyed)
- **Requires entanglement**: Must share Bell pair first
- **Classical communication**: Needs 2 classical bits
- **No net advantage**: Total resources are the same
        """,
        "quiz": [
            {
                "question": "What is quantum teleportation?",
                "options": ["Moving matter instantly", "Transferring quantum state using entanglement", "Classical communication", "Quantum computing"],
                "correct": 1,
                "explanation": "Quantum teleportation transfers a quantum state from Alice to Bob using entanglement and classical communication."
            },
            {
                "question": "How many classical bits are needed for quantum teleportation?",
                "options": ["0 bits", "1 bit", "2 bits", "4 bits"],
                "correct": 2,
                "explanation": "Quantum teleportation requires 2 classical bits to communicate the Bell measurement result."
            },
            {
                "question": "What happens to Alice's original qubit after teleportation?",
                "options": ["It's unchanged", "It's destroyed", "It's copied", "It's entangled"],
                "correct": 1,
                "explanation": "The original state is destroyed during Bell measurement, consistent with the no-cloning theorem."
            },
            {
                "question": "What measurement does Alice perform?",
                "options": ["Z measurement", "X measurement", "Bell measurement", "Y measurement"],
                "correct": 2,
                "explanation": "Alice performs a Bell measurement on her two qubits (the state to teleport and her half of the Bell pair)."
            },
            {
                "question": "Why is quantum teleportation not faster than light?",
                "options": ["It is faster than light", "Requires classical communication", "Quantum is slow", "Entanglement is limited"],
                "correct": 1,
                "explanation": "Classical communication of the measurement result limits the speed, so it cannot exceed light speed."
            }
        ]
    },
    "Tomography of Quantum States": {
        "id": "tomography",
        "module": "tomography",
        "title": "Tomography of Quantum States",
        "description": "Reconstruct unknown quantum states through measurements in different bases.",
        "category": "Quantum State Characterization",
        "difficulty": "Advanced",
        "theory": """
# Quantum State Tomography

## Introduction

Quantum state tomography is the process of reconstructing an unknown quantum state by performing measurements on many copies of the state. It's analogous to medical tomography (CT scans) but for quantum states.

## Key Concepts

### 1. The Problem

- We have many copies of an unknown quantum state |ψ⟩
- We want to determine the state completely
- Single measurement doesn't give full information
- Need measurements in multiple bases

### 2. Measurement Bases

For a single qubit, we need measurements in three bases:
- **Z-basis**: {|0⟩, |1⟩} - measures σz
- **X-basis**: {|+⟩, |-⟩} - measures σx
- **Y-basis**: {|+i⟩, |-i⟩} - measures σy

### 3. Density Matrix

A quantum state can be represented as a density matrix:
- **Pure state**: |ψ⟩⟨ψ|
- **Mixed state**: Σᵢ pᵢ|ψᵢ⟩⟨ψᵢ|
- Contains all information about the state

### 4. Reconstruction Process

1. **Prepare many copies** of the state
2. **Measure in Z-basis**: Get probabilities P(|0⟩) and P(|1⟩)
3. **Measure in X-basis**: Get probabilities P(|+⟩) and P(|-⟩)
4. **Measure in Y-basis**: Get probabilities P(|+i⟩) and P(|-i⟩)
5. **Reconstruct density matrix**: From measurement statistics
6. **Verify**: Compare with theoretical state

### 5. Bloch Vector

The state can be represented on the Bloch sphere:
- **x-component**: From X-basis measurements
- **y-component**: From Y-basis measurements
- **z-component**: From Z-basis measurements
- **Vector length**: Indicates purity (1 for pure states)

### 6. Fidelity

Fidelity measures reconstruction quality:
- Fidelity = Tr(√(√ρₜₕₑₒᵣᵧ ρₑₓₚ√ρₜₕₑₒᵣᵧ)²)
- Fidelity = 1: Perfect reconstruction
- Fidelity < 1: Imperfect (due to noise, finite samples)

## Applications

- **Quantum characterization**: Understanding quantum devices
- **Error analysis**: Detecting and quantifying errors
- **Calibration**: Calibrating quantum hardware
- **Research**: Studying quantum states and processes

## Challenges

1. **Many copies needed**: Requires many identical states
2. **Measurement overhead**: Grows exponentially with qubits
3. **Noise**: Real measurements have errors
4. **Computational cost**: Reconstruction can be expensive

## Techniques

- **Maximum likelihood**: Find most likely state
- **Linear inversion**: Direct matrix inversion
- **Bayesian methods**: Probabilistic reconstruction
- **Compressed sensing**: For sparse states
        """,
        "quiz": [
            {
                "question": "What is quantum state tomography?",
                "options": ["Measuring one qubit", "Reconstructing unknown quantum states", "Creating quantum states", "Destroying quantum states"],
                "correct": 1,
                "explanation": "Quantum state tomography reconstructs an unknown quantum state through measurements in multiple bases."
            },
            {
                "question": "How many measurement bases are needed for single-qubit tomography?",
                "options": ["1 basis", "2 bases", "3 bases", "4 bases"],
                "correct": 2,
                "explanation": "Single-qubit tomography requires measurements in Z, X, and Y bases to fully characterize the state."
            },
            {
                "question": "What does the Bloch vector represent?",
                "options": ["Gate operations", "Quantum state on Bloch sphere", "Measurement results", "Error rates"],
                "correct": 1,
                "explanation": "The Bloch vector represents the quantum state's position on the Bloch sphere, with components from X, Y, Z measurements."
            },
            {
                "question": "What is fidelity?",
                "options": ["Error rate", "Measure of reconstruction quality", "Gate count", "Measurement time"],
                "correct": 1,
                "explanation": "Fidelity measures how well the reconstructed state matches the theoretical state, ranging from 0 to 1."
            },
            {
                "question": "Why do we need many copies of the state?",
                "options": ["For speed", "To get accurate statistics", "For security", "For entanglement"],
                "correct": 1,
                "explanation": "Many copies are needed to obtain accurate measurement statistics in each basis for reliable reconstruction."
            }
        ]
    }
}

def get_lab(lab_id: str):
    """Get lab configuration by ID"""
    for lab_name, lab_config in LABS.items():
        if lab_config["id"] == lab_id:
            return lab_config
    return None

def get_all_labs():
    """Get all lab configurations"""
    return LABS

def get_labs_by_category():
    """Get labs organized by category"""
    categories = {}
    for lab_name, lab_config in LABS.items():
        category = lab_config["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append((lab_name, lab_config))
    return categories

