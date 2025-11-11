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
        "title": "Q-Random Number Generator",
        "description": "Generate truly random numbers using quantum superposition and measurement.",
        "category": "Quantum Foundations",
        "difficulty": "Beginner",
        "theory": """

### Introduction

Random number generation is crucial for cryptography, simulations, and security applications. Classical computers can only generate **pseudo-random** numbers using algorithms, which are deterministic and predictable if you know the algorithm and seed. Quantum computers can generate **truly random** numbers based on fundamental quantum uncertainty.


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

### Introduction

Parity checking is a fundamental operation in both classical and quantum computing. It determines whether the number of 1s in a binary string is even or odd. In quantum computing, we use an **ancilla qubit** (helper qubit) to compute parity without directly measuring the input qubits.

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
        "title": "Bell State Analysis and Noise Effects",
        "description": "Analyze all four Bell states, their measurement outcomes, correlations, and how noise affects entanglement.",
        "category": "Quantum Entanglement & Noise",
        "difficulty": "Intermediate",
        "theory": """

## Part 1: Bell State Analysis

### 1. The Four Bell States

Bell states are four maximally entangled two-qubit states:

- **|Φ⁺⟩ = (|00⟩ + |11⟩)/√2**: Perfect positive correlation
- **|Φ⁻⟩ = (|00⟩ - |11⟩)/√2**: Perfect positive correlation (phase difference)
- **|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2**: Perfect negative correlation (anti-correlation)
- **|Ψ⁻⟩ = (|01⟩ - |10⟩)/√2**: Perfect negative correlation (phase difference)

### 2. Creation Circuits

**|Φ⁺⟩**: H on qubit 0, then CNOT(0,1)
**|Φ⁻⟩**: H on qubit 0, CNOT(0,1), then Z on qubit 0
**|Ψ⁺⟩**: H on qubit 0, CNOT(0,1), then X on qubit 1
**|Ψ⁻⟩**: H on qubit 0, CNOT(0,1), then X on qubit 1 and Z on qubit 0

### 3. Measurement Correlations

**|Φ⁺⟩ and |Φ⁻⟩:**
- Perfect positive correlation
- Measurement outcomes: |00⟩ or |11⟩ only
- If one qubit is |0⟩, the other must be |0⟩
- If one qubit is |1⟩, the other must be |1⟩

**|Ψ⁺⟩ and |Ψ⁻⟩:**
- Perfect negative correlation (anti-correlation)
- Measurement outcomes: |01⟩ or |10⟩ only
- If one qubit is |0⟩, the other must be |1⟩
- If one qubit is |1⟩, the other must be |0⟩

### 4. Bell State Properties

- **Maximal Entanglement**: All Bell states are maximally entangled
- **Non-locality**: Demonstrate quantum non-locality
- **Perfect Correlations**: Measuring one qubit determines the other
- **Basis**: Bell states form an orthonormal basis for two-qubit space

### 5. Applications

- Quantum teleportation
- Superdense coding
- Quantum cryptography (BB84)
- Quantum error correction
- Tests of quantum mechanics (Bell tests)

## Part 2: Effect of Noise on Bell States

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

### Introduction

BB84 is the first quantum key distribution (QKD) protocol, invented by Charles Bennett and Gilles Brassard in 1984. It allows two parties (Alice and Bob) to establish a shared secret key using quantum mechanics, with guaranteed detection of any eavesdropping.


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
### Introduction

Superdense coding is a quantum communication protocol that allows Alice to transmit **two classical bits** of information to Bob using only **one qubit**, by leveraging a shared entangled Bell pair. This demonstrates the power of quantum entanglement for communication.

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
        "title": "Quantum Teleportation",
        "description": "Transfer a quantum state from Alice to Bob using entanglement and classical communication.",
        "category": "Quantum Communication Protocols",
        "difficulty": "Advanced",
        "theory": """
### Introduction

Quantum teleportation is a protocol that allows Alice to transfer an unknown quantum state to Bob using a shared entangled pair and classical communication. Despite its name, it doesn't transfer matter or energy faster than light - it transfers quantum information.

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
    },
    "Multi-Qubit Superposition": {
        "id": "multi_qubit_superposition",
        "module": "multi_qubit_superposition",
        "title": "Multi-Qubit Superposition",
        "description": "Prepare a 3-qubit equal superposition state and verify uniform probability distribution.",
        "category": "Quantum Foundations",
        "difficulty": "Beginner",
        "theory": """

### 1. Product State Superposition

When we apply Hadamard gates to n qubits independently:
- Each qubit becomes (|0⟩ + |1⟩)/√2
- The combined state is a product of individual superpositions
- Result: (1/√2ⁿ) Σ|x⟩ for all x from 0 to 2ⁿ-1

### 2. Equal Superposition

For n qubits, we get:
- |ψ⟩ = (1/√2ⁿ) (|0...0⟩ + |0...1⟩ + ... + |1...1⟩)
- All 2ⁿ basis states have equal amplitude: 1/√2ⁿ
- All states have equal probability: 1/2ⁿ

### 3. No Entanglement

The multi-qubit superposition created by independent Hadamard gates is:
- A product state (not entangled)
- Can be written as: |+⟩ ⊗ |+⟩ ⊗ ... ⊗ |+⟩
- Each qubit is independent

### 4. Measurement Statistics

- Total number of states: 2ⁿ
- Probability of each state: 1/2ⁿ
- Uniform distribution across all states
- Chi-square test can verify uniformity

### 5. Applications

- Quantum algorithms: Many algorithms start with equal superposition
- Quantum search: Grover's algorithm uses uniform superposition
- Quantum Fourier transform: Input is often uniform superposition
- Random number generation: Uniform superposition provides randomness

## Mathematical Formulation

For n qubits with Hadamard gates:
- H⊗ⁿ|0⟩⊗ⁿ = (1/√2ⁿ) Σₓ₌₀^(2ⁿ⁻¹) |x⟩
- Each basis state |x⟩ has amplitude 1/√2ⁿ
- Probability of measuring |x⟩ is |1/√2ⁿ|² = 1/2ⁿ

## Verification

To verify uniform superposition:
1. Measure many times (shots)
2. Count occurrences of each state
3. Check if all states appear equally often
4. Use chi-square test for statistical validation
        """,
        "quiz": [
            {
                "question": "What is the probability of each basis state in an n-qubit equal superposition?",
                "options": ["1/2", "1/n", "1/2^n", "1/√2^n"],
                "correct": 2,
                "explanation": "Each of the 2^n basis states has probability 1/2^n in an equal superposition."
            },
            {
                "question": "Is the multi-qubit superposition created by independent Hadamard gates entangled?",
                "options": ["Yes", "No", "Sometimes", "Depends on n"],
                "correct": 1,
                "explanation": "Independent Hadamard gates create a product state, which is not entangled."
            },
            {
                "question": "How many basis states are there for n qubits?",
                "options": ["n", "2n", "2^n", "n^2"],
                "correct": 2,
                "explanation": "For n qubits, there are 2^n possible basis states (each qubit can be 0 or 1)."
            },
            {
                "question": "What gate is used to create equal superposition on each qubit?",
                "options": ["X gate", "Z gate", "Hadamard gate", "CNOT gate"],
                "correct": 2,
                "explanation": "The Hadamard gate creates equal superposition: H|0⟩ = (|0⟩ + |1⟩)/√2."
            },
            {
                "question": "What is the amplitude of each state in an n-qubit equal superposition?",
                "options": ["1/2^n", "1/√2^n", "1/2", "1/n"],
                "correct": 1,
                "explanation": "The amplitude is 1/√2^n, which gives probability (1/√2^n)² = 1/2^n."
            }
        ]
    },
    "GHZ State": {
        "id": "ghz_state",
        "module": "ghz_state",
        "title": "Entanglement in 3 Qubits (GHZ State)",
        "description": "Create a GHZ state (|000⟩ + |111⟩)/√2 and show that measuring one qubit determines the others.",
        "category": "Quantum Entanglement & Noise",
        "difficulty": "Intermediate",
        "theory": """
# GHZ State - Three-Qubit Entanglement

## Introduction

The GHZ state (Greenberger-Horne-Zeilinger state) is a maximally entangled three-qubit state. It demonstrates perfect correlations between all three qubits and is fundamental to quantum information science.

## Key Concepts

### 1. GHZ State Definition

The GHZ state is:
- |GHZ⟩ = (|000⟩ + |111⟩)/√2
- Equal superposition of |000⟩ and |111⟩
- Maximally entangled three-qubit state

### 2. Creation Circuit

To create a GHZ state:
1. Apply H gate to qubit 0: creates (|0⟩ + |1⟩)/√2
2. Apply CNOT(0,1): entangles qubits 0 and 1
3. Apply CNOT(0,2): entangles qubit 2 with the pair

### 3. Perfect Correlations

- Measuring any qubit determines the others
- If qubit 0 = 0 → qubits 1 and 2 must be 0
- If qubit 0 = 1 → qubits 1 and 2 must be 1
- Same for measuring qubit 1 or 2

### 4. Measurement Outcomes

- Only two outcomes possible: |000⟩ or |111⟩
- Each with 50% probability
- No other states observed (in ideal case)

### 5. Entanglement Properties

- **Maximal entanglement**: All three qubits are maximally entangled
- **Bipartite entanglement**: Tracing out one qubit leaves others in mixed state
- **Fragility**: Losing one qubit destroys all entanglement
- **Non-locality**: Demonstrates quantum non-locality

### 6. Applications

- Quantum teleportation networks
- Quantum error correction
- Quantum communication protocols
- Tests of quantum mechanics (Bell tests)
- Quantum metrology

## Mathematical Properties

- State: |GHZ⟩ = (|000⟩ + |111⟩)/√2
- Density matrix: ρ = |GHZ⟩⟨GHZ|
- Reduced density matrices: Tracing out one qubit gives mixed state
- Entanglement entropy: Maximum for tripartite entanglement

## Comparison with Other States

- **Product state**: No entanglement, independent measurements
- **Bell state**: Two-qubit entanglement
- **GHZ state**: Three-qubit maximal entanglement
- **W state**: Different type of three-qubit entanglement
        """,
        "quiz": [
            {
                "question": "What is the GHZ state?",
                "options": ["|000⟩", "|111⟩", "(|000⟩ + |111⟩)/√2", "(|001⟩ + |010⟩ + |100⟩)/√3"],
                "correct": 2,
                "explanation": "The GHZ state is (|000⟩ + |111⟩)/√2, an equal superposition of |000⟩ and |111⟩."
            },
            {
                "question": "What happens when you measure one qubit in a GHZ state?",
                "options": ["Random result", "Determines the other qubits", "No effect", "Creates entanglement"],
                "correct": 1,
                "explanation": "Measuring one qubit in a GHZ state immediately determines the state of the other two qubits due to perfect correlation."
            },
            {
                "question": "How many measurement outcomes are possible for a GHZ state?",
                "options": ["1", "2", "4", "8"],
                "correct": 1,
                "explanation": "Only two outcomes are possible: |000⟩ or |111⟩, each with 50% probability."
            },
            {
                "question": "What is the main difference between GHZ and W states?",
                "options": ["Number of qubits", "Robustness to qubit loss", "Measurement outcomes", "Creation method"],
                "correct": 1,
                "explanation": "GHZ state loses all entanglement if one qubit is lost, while W state retains some entanglement."
            },
            {
                "question": "Which gates are used to create a GHZ state?",
                "options": ["H, X", "H, CNOT", "X, Z", "H, Z"],
                "correct": 1,
                "explanation": "GHZ state is created using H gate on first qubit, then CNOT gates to entangle with other qubits."
            }
        ]
    },
    "W State": {
        "id": "w_state",
        "module": "w_state",
        "title": "Entanglement in 3 Qubits (W State)",
        "description": "Prepare the W state (|001⟩ + |010⟩ + |100⟩)/√3 and compare its robustness to qubit loss vs. GHZ state.",
        "category": "Quantum Entanglement & Noise",
        "difficulty": "Intermediate",
        "theory": """

### Introduction

The W state is a three-qubit entangled state that is more robust to qubit loss than the GHZ state. It represents a different type of multipartite entanglement.

### 1. W State Definition

The W state is:
- |W⟩ = (|001⟩ + |010⟩ + |100⟩)/√3
- Equal superposition of states with exactly one qubit in |1⟩
- Symmetric under permutation of qubits

### 2. Creation Circuit

Creating a W state is more complex than GHZ:
- Requires rotation gates (RY) and controlled gates
- Multiple methods exist for W state preparation
- Typically uses θ = 2 arctan(√2) rotation angle

### 3. Measurement Properties

- Always measures exactly one qubit in |1⟩ state
- Three possible outcomes: |001⟩, |010⟩, or |100⟩
- Each outcome has probability 1/3
- Symmetric: P(1) = 1/3 for each qubit individually

### 4. Robustness to Qubit Loss

- **W State**: If one qubit is lost, remaining two qubits are still entangled
- **GHZ State**: If one qubit is lost, remaining two qubits become completely mixed
- This makes W state more robust for certain applications

### 5. Entanglement Structure

- All three qubits are entangled
- Bipartite entanglement persists after qubit loss
- Different entanglement structure than GHZ state
- Cannot be written as product of Bell states

### 6. Applications

- Quantum communication where robustness is important
- Quantum error correction
- Quantum networking
- Studies of multipartite entanglement types

## Comparison with GHZ State

| Property | W State | GHZ State |
|----------|---------|-----------|
| State | (|001⟩ + |010⟩ + |100⟩)/√3 | (|000⟩ + |111⟩)/√3 |
| Outcomes | |001⟩, |010⟩, |100⟩ | |000⟩, |111⟩ |
| Qubit Loss | Retains entanglement | Loses all entanglement |
| Symmetry | Permutation symmetric | Permutation symmetric |
| Applications | Robust protocols | Teleportation, tests |

## Mathematical Properties

- State: |W⟩ = (|001⟩ + |010⟩ + |100⟩)/√3
- Symmetry: |W⟩ is invariant under qubit permutation
- Reduced states: Tracing out one qubit leaves entangled pair
- Entanglement: Persistent bipartite entanglement after loss
        """,
        "quiz": [
            {
                "question": "What is the W state?",
                "options": ["(|000⟩ + |111⟩)/√2", "(|001⟩ + |010⟩ + |100⟩)/√3", "|000⟩", "|111⟩"],
                "correct": 1,
                "explanation": "The W state is (|001⟩ + |010⟩ + |100⟩)/√3, a superposition of states with exactly one |1⟩."
            },
            {
                "question": "What is the probability of measuring |1⟩ on any single qubit in a W state?",
                "options": ["1/2", "1/3", "1/4", "1"],
                "correct": 1,
                "explanation": "Each qubit has probability 1/3 of being measured as |1⟩ in a W state."
            },
            {
                "question": "What happens to entanglement when one qubit is lost from a W state?",
                "options": ["All entanglement lost", "Some entanglement retained", "No change", "Creates new entanglement"],
                "correct": 1,
                "explanation": "W state retains bipartite entanglement when one qubit is lost, unlike GHZ state."
            },
            {
                "question": "How many measurement outcomes are possible for a W state?",
                "options": ["1", "2", "3", "8"],
                "correct": 2,
                "explanation": "Three outcomes are possible: |001⟩, |010⟩, or |100⟩, each with probability 1/3."
            },
            {
                "question": "Why is W state more robust than GHZ state?",
                "options": ["More qubits", "Retains entanglement after qubit loss", "Easier to create", "Higher probability"],
                "correct": 1,
                "explanation": "W state retains bipartite entanglement when one qubit is lost, while GHZ state loses all entanglement."
            }
        ]
    },
    "Quantum Circuit Identity Verification": {
        "id": "circuit_identity",
        "module": "circuit_identity",
        "title": "Q-Circuit Identity Verification",
        "description": "Verify equivalence of circuits by comparing simulation outcomes.",
        "category": "Quantum Logic & Operations",
        "difficulty": "Intermediate",
        "theory": """

### Introduction

Quantum circuit identities are relationships showing that different sequences of gates produce the same result. Verifying these identities is crucial for circuit optimization and understanding quantum operations.


### 1. Circuit Equivalence

Two circuits are equivalent if:
- They produce the same operator (unitary matrix)
- They produce the same measurement outcomes for all input states
- They have the same effect on any quantum state

### 2. Common Identities

**Hadamard Conjugation:**
- HZH = X: Hadamard conjugates Z to X
- HXH = Z: Hadamard conjugates X to Z
- H² = I: Hadamard is self-inverse

**Pauli Gates:**
- X² = Y² = Z² = I: All Pauli gates are self-inverse
- XY = iZ, YZ = iX, ZX = iY: Pauli gate commutation

**CNOT Identities:**
- CNOT(a,b) CNOT(b,a) CNOT(a,b) = SWAP(a,b)
- CNOT is self-inverse when applied twice with same control

### 3. Verification Methods

**Method 1: Operator Comparison**
- Compute unitary matrices for both circuits
- Check if matrices are equivalent (within tolerance)
- Most direct method

**Method 2: Measurement Comparison**
- Test on multiple input states
- Compare measurement outcomes
- Statistical verification

### 4. Applications

- **Circuit Optimization**: Simplify circuits using identities
- **Gate Decomposition**: Break down complex gates
- **Error Correction**: Understand error correction circuits
- **Algorithm Design**: Use identities in algorithm construction

### 5. Mathematical Basis

- Unitary matrices: U₁ = U₂ if circuits are equivalent
- Operator norm: ||U₁ - U₂|| = 0 for equivalent circuits
- State equivalence: U₁|ψ⟩ = U₂|ψ⟩ for all |ψ⟩

## Important Identities

1. **HZH = X**: Conjugation of Z by H gives X
2. **HXH = Z**: Conjugation of X by H gives Z
3. **CNOT Swap**: Three CNOTs implement SWAP
4. **Self-Inverse**: H² = X² = Y² = Z² = I
5. **Phase Gates**: S² = Z, S⁴ = I

## Verification Process

1. Construct both circuits
2. Compute operators or run simulations
3. Compare results
4. Verify equivalence statistically
5. Understand the identity's implications
        """,
        "quiz": [
            {
                "question": "What does HZH equal?",
                "options": ["Z", "X", "Y", "I"],
                "correct": 1,
                "explanation": "HZH = X, meaning Hadamard gate conjugates Z gate to X gate."
            },
            {
                "question": "How many CNOT gates are needed to implement a SWAP?",
                "options": ["1", "2", "3", "4"],
                "correct": 2,
                "explanation": "Three CNOT gates in the sequence CNOT(a,b) CNOT(b,a) CNOT(a,b) implement a SWAP."
            },
            {
                "question": "Which gate is self-inverse?",
                "options": ["CNOT", "Hadamard", "T gate", "All of the above"],
                "correct": 1,
                "explanation": "Hadamard gate is self-inverse: H² = I. (Note: CNOT applied twice with same control also acts as identity)"
            },
            {
                "question": "What is HXH?",
                "options": ["X", "Y", "Z", "I"],
                "correct": 2,
                "explanation": "HXH = Z, meaning Hadamard conjugates X gate to Z gate."
            },
            {
                "question": "Why are circuit identities important?",
                "options": ["For fun", "Circuit optimization and gate decomposition", "To confuse students", "No reason"],
                "correct": 1,
                "explanation": "Circuit identities are crucial for optimizing quantum circuits and decomposing complex gates into simpler ones."
            }
        ]
    },
    "3-Qubit Bit Flip Code": {
        "id": "bit_flip_code",
        "module": "bit_flip_code",
        "title": "Error Detection with 3-Qubit Bit Flip Code",
        "description": "Encode a qubit into 3 qubits to detect single bit-flip errors and demonstrate error detection via measurement.",
        "category": "Quantum Error Correction",
        "difficulty": "Advanced",
        "theory": """


### 1. Encoding

**Logical States:**
- |0⟩_L = |000⟩ (logical 0 encoded as three 0s)
- |1⟩_L = |111⟩ (logical 1 encoded as three 1s)

**Encoding Circuit:**
1. Start with |ψ⟩|0⟩|0⟩
2. Apply CNOT(0,1): entangles qubits 0 and 1
3. Apply CNOT(0,2): entangles qubit 2 with qubit 0
4. Result: |ψ⟩|ψ⟩|ψ⟩ (three copies)

### 2. Error Detection (Syndrome Measurement)

**Syndrome Bits:**
- Syndrome bit 0: Parity of qubits 0 and 1
- Syndrome bit 1: Parity of qubits 0 and 2
- Syndrome identifies which qubit has error (if any)

**Syndrome Table:**
| Syndrome | Error Location | Meaning |
|----------|----------------|---------|
| 00 | None | No error detected |
| 01 | Qubit 2 | Error on qubit 2 |
| 10 | Qubit 1 | Error on qubit 1 |
| 11 | Qubit 0 | Error on qubit 0 |

### 3. Error Correction

Once error is detected:
- Apply X gate to the corrupted qubit
- This corrects the bit-flip error
- Restores the encoded state

### 4. Limitations

- **Only detects bit-flip errors**: Cannot detect phase errors
- **Single error only**: Cannot correct multiple errors
- **Overhead**: Requires 3 physical qubits for 1 logical qubit
- **Measurement**: Requires mid-circuit measurement

### 5. Applications

- Quantum error correction
- Fault-tolerant quantum computing
- Protecting quantum information
- Building blocks for more complex codes

## Mathematical Formulation

**Encoding:**
- |0⟩_L → |000⟩
- |1⟩_L → |111⟩
- |ψ⟩ = α|0⟩ + β|1⟩ → α|000⟩ + β|111⟩

**Error Model:**
- Bit-flip error: X gate applied to one qubit
- Three possible error locations
- Syndrome measurement detects which one

**Correction:**
- Apply X gate to corrupted qubit
- Restores original encoded state
        """,
        "quiz": [
            {
                "question": "What is encoded as |000⟩ in the bit-flip code?",
                "options": ["Logical |0⟩", "Logical |1⟩", "Error state", "Nothing"],
                "correct": 0,
                "explanation": "Logical |0⟩ is encoded as |000⟩ in the 3-qubit bit flip code."
            },
            {
                "question": "What does syndrome 01 indicate?",
                "options": ["No error", "Error on qubit 0", "Error on qubit 1", "Error on qubit 2"],
                "correct": 3,
                "explanation": "Syndrome 01 indicates an error on qubit 2 in the bit-flip code."
            },
            {
                "question": "How many physical qubits are needed for one logical qubit in the bit-flip code?",
                "options": ["1", "2", "3", "4"],
                "correct": 2,
                "explanation": "The 3-qubit bit flip code requires 3 physical qubits to encode 1 logical qubit."
            },
            {
                "question": "What type of errors can the bit-flip code detect?",
                "options": ["Bit-flip only", "Phase-flip only", "Both", "None"],
                "correct": 0,
                "explanation": "The bit-flip code can only detect and correct bit-flip (X) errors, not phase-flip (Z) errors."
            },
            {
                "question": "What gate is applied to correct a detected error?",
                "options": ["Z gate", "X gate", "H gate", "CNOT gate"],
                "correct": 1,
                "explanation": "X gate is applied to the corrupted qubit to correct a bit-flip error."
            }
        ]
    },
    "3-Qubit Phase Flip Code": {
        "id": "phase_flip_code",
        "module": "phase_flip_code",
        "title": "Error Detection with 3-Qubit Phase Flip Code",
        "description": "Extend bit-flip code idea to detect phase errors. Show that errors in |+⟩/|−⟩ basis can be caught.",
        "category": "Quantum Error Correction",
        "difficulty": "Advanced",
        "theory": """

### 1. Encoding in X Basis

**Logical States:**
- |0⟩_L = |+++⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
- |1⟩_L = |---⟩ = (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2

**Encoding Circuit:**
1. Apply Hadamard to all qubits (switch to X basis)
2. Apply CNOT gates to create redundancy
3. Result: |+++⟩ or |---⟩ depending on logical state

### 2. Phase Flip Errors

**Phase Flip:**
- Z gate flips phase: Z|+⟩ = |-⟩ and Z|-⟩ = |+⟩
- In computational basis, this is a phase error
- In X basis, this becomes a bit flip

### 3. Syndrome Measurement

**In X Basis:**
- Measure parity in X basis using Hadamard gates
- Syndrome bit 0: Parity of qubits 0 and 1 in X basis
- Syndrome bit 1: Parity of qubits 0 and 2 in X basis

**Syndrome Table:**
| Syndrome | Error Location | Correction |
|----------|----------------|------------|
| 00 | None | None |
| 01 | Qubit 2 | Z on 2 |
| 10 | Qubit 1 | Z on 1 |
| 11 | Qubit 0 | Z on 0 |

### 4. Duality with Bit-Flip Code

- Bit-flip code: Works in Z basis, detects X errors
- Phase-flip code: Works in X basis, detects Z errors
- Related by Hadamard transformation
- Dual codes: H (bit-flip code) H = phase-flip code

### 5. Applications

- Quantum error correction for phase errors
- Protecting against phase decoherence
- Building blocks for Shor code
- Fault-tolerant quantum computing

## Mathematical Formulation

**Encoding:**
- |0⟩_L → |+++⟩
- |1⟩_L → |---⟩
- Encoding uses Hadamard basis

**Error Detection:**
- Phase flip (Z) in computational basis
- Becomes bit flip in X basis
- Detected by X-basis measurements

**Correction:**
- Apply Z gate to corrupted qubit
- Corrects phase error
- Restores encoded state
        """,
        "quiz": [
            {
                "question": "In which basis does the phase-flip code work?",
                "options": ["Z basis (|0⟩/|1⟩)", "X basis (|+⟩/|-⟩)", "Y basis", "Arbitrary basis"],
                "correct": 1,
                "explanation": "The phase-flip code works in X basis (|+⟩/|-⟩), which is the Hadamard basis."
            },
            {
                "question": "What type of errors does the phase-flip code detect?",
                "options": ["Bit-flip (X)", "Phase-flip (Z)", "Both", "None"],
                "correct": 1,
                "explanation": "The phase-flip code detects phase-flip (Z) errors, which are bit-flips in the X basis."
            },
            {
                "question": "What is the relationship between bit-flip and phase-flip codes?",
                "options": ["Same code", "Dual codes (related by Hadamard)", "Unrelated", "Opposite"],
                "correct": 1,
                "explanation": "Bit-flip and phase-flip codes are dual to each other, related by Hadamard transformation."
            },
            {
                "question": "What gate is applied to correct a phase error?",
                "options": ["X gate", "Z gate", "H gate", "Y gate"],
                "correct": 1,
                "explanation": "Z gate is applied to the corrupted qubit to correct a phase-flip error."
            },
            {
                "question": "How is logical |0⟩ encoded in the phase-flip code?",
                "options": ["|000⟩", "|111⟩", "|+++⟩", "|---⟩"],
                "correct": 2,
                "explanation": "Logical |0⟩ is encoded as |+++⟩ in the phase-flip code, using the X basis."
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

