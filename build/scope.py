"""
Scope rules: which ISSCC / VLSI sessions and papers count as
"digital / architecture / accelerator" work.

Two layers:

1. Session rules (regex on the session name, first match wins):
     CORE    - every paper in the session is in scope
     MIXED   - the session mixes digital work with something else
               (memory, sensors, PLLs, biomedical ...); each paper is
               checked individually with the keyword rules below
     EXCLUDE - nothing from the session
   Sessions that match nothing fall through to MIXED, so a new session
   name in a future program is never silently dropped or fully admitted.
   VLSI years without circuit-session names (2010-2013, 2015, 2020, 2022)
   are handled by the session / paper id (T = technology track, C = circuits).

2. Per-paper keyword rules, used for MIXED sessions:
     STRONG    - the title shows digital / architecture / accelerator content
                 (processor, accelerator, CIM, crypto engine, DVFS ...)
     DEVICE    - technology-track markers (FET, ferroelectric, epitaxy ...):
                 a device paper even when the title mentions machine learning
     HARD_VETO - things that are never the subject of a digital paper
                 (imager, qubit, electrode, ultrasound, radar ...)
     SOFT_VETO - analog / memory / RF subjects that often *carry* a digital
                 keyword in a "for / with" clause ("SRAM for Arm HPC
                 Processor", "RX for Microprocessor Applications"). Such a
                 paper is dropped when the veto word comes first and a
                 connector separates it from the digital keyword.

Edit the lists, re-run build.py, and read build/report.txt.
"""

import re

_I = re.I

# ---------------------------------------------------------------------------
# Session rules
# ---------------------------------------------------------------------------

ISSCC_CORE = [
    r"^processors?\b",                          # Processors / Processors and Communication SoCs
    r"processor-power management",
    r"enterprise processors",
    r"low-power processors",
    r"digital processors",
    r"high-performance socs",
    r"multimedia",
    r"media processing",
    r"media accelerators",
    r"mobile systems-on-chip",
    r"low-power socs",
    r"socs for mobile",
    r"^soc building blocks",
    r"high-performance digital",
    r"low-power digital",
    r"energy-aware digital",
    r"energy-efficient digital",
    r"adaptive & low-power circuits",
    r"adaptive digital",
    r"adaptive circuits and digital regulators",
    r"digital circuits",                        # Digital Circuits & Sensors / for Computing / Emerging ...
    r"digital circuit techniques",
    r"digital techniques",                      # ... for Clocking / Power Management / System Adaptation
    r"digital accelerators",
    r"digital processing",
    r"digital voltage regulators",
    r"digital power delivery",
    r"next generation processing",
    r"ultra-efficient computing",
    r"deep-learning processors",
    r"machine learning",                        # Machine Learning / ... and Signal Processing / & Digital LDO / Accelerators
    r"\bml processors",
    r"\bml chips",
    r"\bml accelerators",
    r"ai.accelerators",
    r"^highlighted chip releases(: (modern digital|digital))?$",
    r"highlighted chip releases for ai",
    r"domain.specific",                         # Domain-Specific Processors / Computing / Technology and Circuits for ...
    r"^compute-in-memory$",
    r"^computation in memory",
    r"compute-in-memory processors",
    r"compute-in-memory based processors",
    r"sram compute-in-memory",
    r"hardware security",
    r"^security",
    r"circuits enabling security",
    r"secure, efficient circuits",
    r"iot & security",
    r"design-technology optimization",
]

ISSCC_MIXED = [
    r"digital plls and",                        # ... Building Blocks / SoC Building Blocks / Security Circuits
    r"neuromorphic, clocking and security",
    r"smart socs",
    r"sram & comput",                           # SRAM & Computation-in-Memory / SRAM & Compute-In-Memory
    r"compute-in-memory and sram",
    r"non-volatile memory and compute-in-memory",
    r"non-volatile devices for future architecture",
    r"embedded memories & ising",
    r"low-power circuits for iot",
    r"innovations in low-power and secure iot",
    r"cryo-circuits and ultra-low-power",
    r"highlighted chip releases",               # remaining mixed highlight sessions (5G/radar, quantum ...)
    r"industry invited|invited industry",
    r"ideas for the future",
    r"emerging sensing and computing",
    r"cool computation",
    r"circuits for ai and ai for circuits",
    r"neural interfaces and edge intelligence",
    r"intelligent (neural|biomedical)",
    r"neural and biomedical interfaces",
    r"robot",
]

ISSCC_EXCLUDE = [
    r"plenary",
    r"innovations from outside",
    r"invited: innovations",
    r"quantum",
    r"cryo-cmos",
    r"^sram$|\bdram\b|embedded memor|embedded sram|emerging memor|non-?volatile memor|nand|flash|memory interface|memory and interface|high-density memor",
    r"pll|clock synthesis|frequenc|oscillator|vco|lo generation",
    r"adc|dac|converter|nyquist|delta-sigma|oversampling|data converter",
    r"wireline|link|transceiver|receiver|transmitter|\btx\b|\brx\b|radio|\brf\b|mm-wave|millimeter|thz|wireless|cellular|5g|optical|photonic|die-to-die|d2d|cdr|equaliz|data networks|dense interconnect|\bads\b|\bids\b|high concepts|components for beyond",
    r"power amplif|power conver|power manag|power deliver|switching power|power control|dc-dc|dc/dc|gan|isolat|harvest|wireless power|charger|supply modulator|usb|compute power",
    r"analog|amplifier|sensor|mems|imager|imaging|image sensor|display|audio|user interaction",
    r"biomedical|health|body|brain|implant|physiolog|diagnos|ultrasound|biochemical|medical",
    r"emerging technolog|technology directions|extending silicon|innovative circuits|innovations in (circuits|technolog)|designing in emerging|design in emerging|heterogeneous integration|next-generation systems|extreme environments|unusual interconnects|electromagnetic interface",
]

VLSI_CORE = [
    r"^signal processing$",
    r"soc circuits & processors",
    r"digital architectures",
    r"hardware security",
    r"^security$",
    r"machine / deep learning",
    r"video processing",
    r"circuits for security",
    r"processors and soc",
    r"machine learning",
    r"adaptive and application specific digital",
    r"robotics",
    r"high performance computing",
    r"energy efficient computing",
    r"ldos for high performance digital",
    r"accelerators for security",
    r"ai accelerators",
    r"^new computing$",                         # VLSI 2019 JFS1 (annealing, SpMM, refocusing ...)
    r"technology and system for ai",
    r"secure and energy efficient",
    r"application-specific processors",
    r"processor architectures",
    r"^computing-in-memory$",
    r"^processors",                             # Processors [Suzaku III] / Processors I / Processors II
    r"digital systems",
    r"advanced memories for ai",
    r"digital building blocks",
    r"advanced nns",
    r"pim/cim",
    r"power and security control",
    r"ai/ml accelerators",
    r"transformer processors",
    r"processing for ai",
    r"^digital circuits",
    r"processors & compute",
    r"memory-centric computing",
    r"cim and quantum-inspired",
    r"cim-based",
    r"innovati\w* computing systems",
    r"communication and processors",
    r"ai and ml hardware",
]

VLSI_MIXED = [
    r"joint focus",                             # every Circuits/Technology joint focus session
    r"^jfs",
    r"design with emerging technologies",
    r"innovative systems for a smart society",
    r"biomedical socs",
    r"neural",                                  # Neural Interfaces / Neural Recording ... (classifier SoCs hide here)
    r"ultra low power for iot",
    r"circuits for iot",
    r"computing beyond von neumann",
    r"wireless for biomedical and iot",
    r"iot & sensor",
    r"sram and dram",
    r"non-volatile memory and low power sram",
    r"new computing",                           # VLSI 2023 JFS1 (cryo, quantum, p-bits, FPGA annealing)
    r"ar/vr",
    r"automotive",
    r"3d/heterogeneous|3d system integration",
    r"clocking techniques",
    r"memory circuits",
    r"die-to-die",
    r"design enablement",
    r"brain state classification",
    r"power devices and circuits",
]

VLSI_EXCLUDE = [
    r"plenary|welcome|award|remarks|late news|evening|panel|^highlights?$",
    r"quantum|cryo",
    r"analog|amplifier|oscillator|adc|dac|converter|nyquist|delta-sigma|sigma|oversampl|pipelined|sar\b|data conversion|data converter|continuous-time|high-resolution",
    r"wireline|link|transceiver|receiver|\brx\b|\btx\b|radio|\brf\b|mm-?wave|millimeter|thz|wireless|cellular|5g|optical|photonic|i/os|i/o\b|phased",
    r"power|dc-dc|dc/dc|gan|isolat|harvest|charger|regulat|ldo|voltage",
    r"pll|phase-locked|clock and frequency|clock generat|frequency|synthesi",
    r"sensor|sensing|transducer|mems|imager|image sensor|imaging|images? for|display|audio|acoustic|spad|time-of-flight|time of flight|tof\b|ranging|physical",
    r"biomedical|bio|health|body|brain|implant|physiolog|diagnos|ultrasound|human|sequencing|stimulation|readout",
    r"^sram|^dram|sram design|advanced sram|nand|flash|non-?volatile memor|otp|\bmemor(y|ies)\b|emerging memory|the future of memory|mram|rram|reram|pcram|pcm|x-point|ferroelectric|fefet",
    r"finfet|cmos|fdsoi|soi|nanowire|nanosheet|mosfet|fet\b|tfet|hemt|ge\b|iii-v|germanium|silicon|substrate|gate|channel|mobility|\bprocess(?!or)|technolog(?!y and system)|device|beyond cmos|reliability|variab|stability|noise|rtn|characteri|modeling|scaling|node|interconnect|packaging|assembly|integration|bonding|materials|exploratory|more than moore|novel|oxides|stco|dtco",
]

# VLSI sessions with a blank name. The session id (or, when that is blank
# too, the paper id) still carries the track:
#   T*, TFS*, PL*, EVP*, S2..S21 (2020)  technology / plenary  -> exclude
#   CA*, CC* (2020)                       architectures, digital circuits -> core
#   CB*, CD*, CP*, CW* (2020)             bio, data converters, power, wireline -> exclude
#   everything else (C*, JFS*, JC*, S1)   circuits, decided per paper
_UNNAMED_EXCLUDE = re.compile(r"^(T|TFS|PL|EVP|S(?!1$)\d|C[BDPW]\d)", re.I)
_UNNAMED_CORE = re.compile(r"^C[AC]\d", re.I)


# ---------------------------------------------------------------------------
# Per-paper keyword rules
# ---------------------------------------------------------------------------

def _flatten(pattern):
    """Join a multi-line pattern, dropping indentation but keeping the single
    spaces inside phrases (re.VERBOSE would eat those)."""
    return re.sub(r"\s*\n\s*", "", pattern.strip())


def _rx(pattern):
    return re.compile(_flatten(pattern), re.I)


_CORE_WORD = r"(\d+|two|four|six|eight|twelve|sixteen|dual|quad|hexa|octa|deca|many|multi|kilo|killo|tri)"

# Evidence that the paper itself is digital / architecture / accelerator work.
STRONG = _rx(r"""
    \b(
      processors?|microprocessors?|co-?processors?|multiprocessors?|mpsoc|accelerators?|accelerator-in-memory|
      \bcpus?\b|\bgpus?\b|gpgpu|\bnpus?\b|\btpu\b|\bdsps?\b|digital signal processor|\bmcus?\b|microcontrollers?|
      cortex-?[amr]\w*|risc-?v|x86|ia-32|\bia\b \d+ ?nm processors|xeon|sparc\w*|power\d|itanium|\bzen\b|telum|
      radeon|instinct|geforce|nvidia|atom(tm)? processor|core i[357]|neoverse|ibm z\d*|z1\d\b|
      """ + _CORE_WORD + r"""-cores?\b(?!.*\b(oscillator|vco|class-[a-z]|amplifier|mixer|lna)\b)|\d+ cores\b|(many|multi)-?core|
      neural[ -]?networks?|\bnns?\b|\bcnns?\b|\bdnns?\b|\bsnns?\b|\brnns?\b|\bgnns?\b|\bgcn\b|\blstm\b|\bmlp\b|\bann\b|\bbnn\b|
      deep[ -]learning|machine[ -]learning|neural (processing|engine|processor|decision|cpu|inverse)|
      transformers?\b(?![ -](based (hybrid|digital|isolator)|coupled))|\bllms?\b|large[ -]language|language model|language processing unit|
      diffusion (model|accelerator|processor)|generative (ai|adversarial|diffusion|model)|autoregressive|attention (accelerator|engine|score|token|-based)|self-attention|
      inference|classifiers?\b|classification (soc|processor|accelerator|engine|chip|hardware)|\w+-classification soc|
      (object|face|image|speech|gesture|gaze|activity|keyword|pattern|scene|human activity|action|viewpoint) recogni\w*|recognition (processor|soc|accelerator|engine|system|microsystem|chip)|
      on-?chip learning|on-?device (learning|training)|online[ -]learning|on-line learning|one-shot learning|few-shot|continual learning|reinforcement learning|
      learning (processor|accelerator|classifier|engine|soc)|
      neuromorphic|spiking|synapses?\b|neurons?\b|neurosynaptic|spike[ -]sorting|hyperdimensional|
      compute[ -]?in[ -]?memory|computing[ -]?in[ -]?memory|computation[ -]?in[ -]?memory|in[ -]?memory[ -](approximate |analog |digital |hybrid |dynamic |bnn |bwn )?comput\w*|
      \bcims?\b|\bdcim\b|\bacim\b|\bimc\b|\bpim\b|processing[ -]?in[ -]?memory|process-near-memory|near[ -]memory|compute-near|logic-in-memory|
      in-memory (search\w*|encryption|annealing|convolution|matrix|machine|processing|point)|memory-centric comput\w*|
      ai[ -](accelerators?|processors?|chips?|socs?|edge|inference|training|engines?|applications|processing)|edge[ -]ai|ai-?iot|ai/ml|for ai\b|
      \bising\b|annealers?\b|annealing (processor|machine|system|computer|chip|compute)|self-annealing|quantum-inspired|
      sat solver|k-sat|3-sat|satisfiability|combinatorial[ -]optimization|quadratic optimization|optimization (engine|problems)|p-bits?\b|
      probabilistic (computing|inference|bit|self-annealing)|bayesian (inference|decision|neural)|stochastic (comput\w*|neural|sampling|self-annealing|synapses)|gibbs sampling|
      crypto\w*|\baes\b|\baes-?\d+|sha-?\d|\brsa\b|elliptic|ecc (processor|engine|accelerator)|homomorphic|\bfhe\b|ckks|paillier|post-quantum|\bpqc\b|lattice(-based| cryptography)|
      \bpufs?\b|physically unclonable|\btrng\b|random[ -]number generat\w*|random-number|encrypt\w*|decrypt\w*|ciphers?\b|side-channel|\bsca-|sca/|
      authentication|secure\b|security|(-| )attack|tamper|glitch (detector|detection)|laser voltage probing|probing attack|fault[ -]injection|camouflaged|obfuscat\w*|trojan|
      \bldpc\b|polar (decoder|code)|turbo[ -]?(decoder|encoder|code)|\bfec\b|forward error correction|viterbi|error correction engine|soft-(decision|detection) decod\w*|
      (belief|message)[ -]propagation|sphere decod\w*|mimo (detector|detection|decoder|precoder|sphere|detection-decoding)|mu-mimo detector|massive mu-mimo|massive-mimo|
      baseband (processor|soc|accelerator|engine|and mac|architecture|for)|digital baseband|\bmodem\b|ofdma baseband|
      fft (core|processor|chip|accelerator)|point (fft|fourier)|fourier-transform chip|software-defined radios?|\bsdr\b (mpsoc|processor|baseband)|
      digital beamform\w*|gps (accelerator|acquisition|correlat\w*)|
      codecs?\b|h\.26[45]|hevc|\bavc\b|\bav1\b|\bvvc\b|cabac|video (en|de)cod\w*|(en|de)coder (chip|lsi|asic)|motion estimation|jpeg encoder|
      \bslam\b|nerf|gaussian splatting|\b3d[ -]?gs\b|4dgs|ray-?(tracing|casting)|render\w* (processor|accelerator|unit|engine|soc)|neural rendering|
      robot\w*|autonomous (navigation|driving|mobile|vehicle|robot\w*|multi-robot|3d|swarm|nano|micro)|autonomous-driving|autonomous and collaborative|
      navigation|path[- ]?planning|motion[- ]?planning|odometry|driving processor|end-to-end driving|automated driving|self-driving|
      keyword[ -]spotting|\bkws\b|speech (recogni\w*|enhancement|denoising|decoding|processor|recognizer|-to-text)|spoken-language|
      voice[ -](activity|commands?)|\bvad\b|speaker verification|filter bank|audio (feature|processor|processing|and image)|
      vision (processor|soc|accelerator|engine|system|chip|transformer)|computer vision|smart vision|always-on vision|(visual|vision) (data|object|tracking|recognition|context|autoregressive)|
      visual-inertial|object (detection|recognition|tracking|matching|classification|viewpoint|processing)|face (recognition|detection|analysis|alignment)|
      super-resolution|image (signal processor|processor|processing soc|processing unit|recognition|reconstruction processor|matching)|imaging processor|\bisp\b|
      depth (estimation|processor|signal processing|fusion)|stereo[ -](depth|vision)|optical flow|feature extraction (processor|accelerator|engine)|feature-extraction accelerator|
      point-?cloud|segmentation|hyperspectral image processor|video (processor|processing|analytics|recording soc)|television|tv soc|blu-ray|
      dvfs|voltage[ -]droop|droop (mitigation|detector|monitor|tolerance|reduction|allocation)|adaptive clock\w*|resonant clock\w*|clock distribution|clock networks?|
      clock-gating|clock gating|clock tree|clock (generator|generation) for (an? |the )?\w* ?(processor|microprocessor|cpu|soc|core)|per-core|
      razor|timing[ -]error|timing[ -]margin|(soft|in-situ|in situ)[ -]error|error[ -]detection and correction|error-detection (register|flip|latch|circuit)|
      in-?situ (error|timing|slack|delay|monitor)|variation-(tolerant|resilient|aware)|resilient (processor|core|router|register|microprocessor|cpu|soc)|
      near-threshold (voltage )?(processor|router|register|cpu|core|soc|system|3d|jpeg|dsp|microprocessor|ia-32|arm|computing)|
      sub-?threshold (processor|arm|cpu|microcontroller|mcu|core|cortex)|
      digital (ldos?|low-dropout|regulator|voltage regulator|linear regulator|power|current sensor)|all-digital ldo|synthesizable|
      adaptive voltage scaling|\bavs\b|dynamic voltage scaling|voltage-stack\w*|voltage stacking|power gating (for|technique|in)|fine-grained power gating|
      body-bias\w* (soc|processor|for)|back-bias\w* (regulator|generator)|thread-level power|peak current regulation|power-limited|current-limiting|throttling|guard-?band|
      power delivery (in|network|monitor|analysis|design|solution|architecture)|diagnosis of power|on-die power|power-supply noise analyzer|power supply noise in|
      flip-?flops?|latch-based (ising|trng|design|true)|pulsed latch\w*|clocked storage|level shifters?|register files?|standard[ -]cells?|std-?cells?|logic family|domino (logic|register|circuit)|
      adder (prototype|tree)|matrix (multipl\w*|generation engine|processor|-vector)|matrix-multiply|linear algebra|linear-algebra|stencil|fp64|double-precision|
      floating-point (unit|fused|register|fma|multiply)|\bfpu\b|arithmetic (logic|unit)|\balu\b|datapath|\bsimd\b|\bvliw\b|vector permutation|fused multiply-add|fma unit|
      network-?on-?chips?|\bnocs?\b|mesh (network|network-on-chip|noc|interconnect|on-chip|topology)|\d+x\d+ mesh|mega-mesh|
      router (in \d|resilient|noc|on-chip)|(on-chip|interconnect|switch|crossbar|manycore|self-arbitrating) (fabric|network)|switch fabric|crossbar switch|swizzle network|
      on-chip (network|interconnect|ring interconnect|signaling)|global interconnect|interconnect circuits for|
      chiplets? (platform|architecture|ai|soc|processor|design|system|for|with|-based (ai|processor|soc|accelerator))|""" + _CORE_WORD + r"""-chiplet|chiplet ai|chiplet (support|design)|inter-chiplet|modular chiplet|reusable chiplets|dielets?\b|
      v-cache|cache (memory|stacked|coherent|slice|hierarchy)|last[ -]level cache|l[123] cache|on-die l3|cache-coherent|
      wake-?up (chip|functions?|module|processor|soc|architecture)|intelligent wake-?up|cognitive wake-?up|always-on (?!reference)|
      event-driven (visual|intelligent|wake|spiking|neural|neuromorphic|processor|architecture|binary|smart|bionic|feature|processing|convolution)|spike-based|
      (ai|ml|neural|dnn|cnn|digital|baseband|multimedia|vision|robot\w*|autonomous|automotive|iot|aiot|application|mobile|gaming|console|5g|smartphone|driving|tinyml|heterogeneous|many-core|multi-core|multiprocessor|crypto|secure|hpc|server|networking|gateway|inference|perception|processor|risc-v|arm|cortex\S*|x86|intelligent|classification|classifier|computing|compute|spatial computing|social agent|mobile intelligence|smart|ulp|ultra-low-power|low-power|energy-performance-aware|epilepsy management|seizure prediction|self-powered|energy-harvesting|imaging|image processing|image-processing|signal processing|video|codec|accelerator|deep-learning|ml inference|micro-robotic|robotic vision|spike sorting|mind imagery and control|biomedical ai|nonvolatile|reconfigurable spatial|domain-specific|ai edge|edge-ai) socs?\b|
      socs? (with|featuring|integrating|for|based on) (\S+ ){0,5}(cortex|cpus?|dnn|cnn|ml|ai|neural|risc|accelerat\w*|dsp|processors?|cores|npu|classifier|learning|inference|machine|multi-core|heterogeneous|vision|codec|baseband|crypto|deep|intelligence|gaming|autonomous)|
      \bfpgas?\b|efpga|3d-fpga|\bcgras?\b|coarse-?grained|
      reconfigurable (\w+[- ])?(processor|accelerator|array|dataflow|computing|neural|cnn|dnn|hybrid|dense|matrix|spatial|logic|cim|architecture|k-nearest|in-memory|nn|deep|ising|neuromorphic|multi-core|register|crossbar|noc|seizure)|
      dynamically reconfigurable (processor|dataflow)|dataflow (accelerator|architecture|processor|-centric|engine|computing)|domain-specific (soc|accelerator|computing|processor|reconfigurable|deep)|
      tensor (processor|contraction|core|-train|engine|accelerator)|4d-tensor|[gtp]flops|tops/w|\btops\b|gops/w|gops/mw|gmacs|tmacs|ops/sec|billion ops|
      genom\w*|genetic variant|for (next-generation |dna )?sequencing|
      sparse (accelerator|neural|dnn|cnn|matrix|coding|convolution|transformer|deep|linear|blas|processor|neuromorphic|mixture|spatio|event-driven|attention|code|-blas)|sparsity|spmm|sparse-matrix|
      (de)?compression (accelerator|engine|processor|asic)|gzip|huffman|regular expression|regex|lookup engine|search engine|search accelerator|similarity search|
      nearest-neighbou?r|k-nearest|knn accelerator|hashing accelerator|hash engine|bitcoin|blockchain|mining (asic|engine|accelerator)|
      recommendation (system|engine|accelerator)|graph (accelerator|processor|neural|processing|learning|analytics|asic)|database|query processing|text search|full-text|
      packet (processing|classification)|network (routing|processor|accelerators)|big[ -]data|
      single-flux-quantum|\bsfq\b|josephson|adiabatic (quantum-flux|superconduct\w*|integration architecture|logic|processor)|superconductor (single|josephson|logic)|superconducting (logic|digital|processor|microprocessor)|
      approximate comput\w*|approximate (arithmetic|error correction|dnn|multiplier)|
      (optimization|inference|search|lookup|cryptographic|crypto|aes|hash|ecc|dtls|error correction|matrix generation|neural|compute|gzip|decompression|rendering|dual attention|physics computing|k-sat|sat|annealing|learning|recognition|decompression) engines?|
      multimedia|graphics|computing platform|mcu platform|
      nonvolatile (processor|microcontroller|logic|soc|intelligent processor)|non-volatile (processor|logic-based)|normally-off (cpu|processor|computing|instant-on)
    )
""")

# Technology-track markers: the paper is about a device or process even when
# the title also mentions computing.
DEVICE = _rx(r"""
    \b(
      ferroelectric|fefets?|\bhzo\b|hf\w*zr|mosfets?|finfets? (technology|platform|device|with|for|and|logic)|\bfets?\b|
      transistors? (technology|design|stacking|with|for|featuring|based)|nanosheets?|nanowires?|\bcfet\b|\bgaa\b|gate-all-around|ribbonfet|
      epitax\w*|\bbeol\b|\bfeol\b|gate (stack|length|pitch|first)|metal pitch|high-k|work-?function|
      rapid thermal|microwave anneal\w*|thermal anneal\w*|laser anneal\w*|deposition|lithograph\w*|\beuv\b|ovonic|\bots\b|contact resist\w*|damascene|
      technology node|nm node|process technology|platform technology|logic technology|soc technology|(finfet|cmos|nm) platform|
      \bdtco\b|\bstco\b|tcad|3d sequential|wafer-to-wafer|wafer on wafer|wafer-scale in-situ|packaging technology|heterogeneous integration|3d integration|hybrid bonding|
      spin qubits?|qubits?|quantum (comput\w*|dot|well|processors?|systems?)|cryogenic|cryo-?cmos|
      synaptic device|memristor|crossbar array|analog in-memory computing|phase change memory|pcm-based|rram-based (non|analog)|reservoir computing|
      photonic|photonics|waveguide|electro-absorption|iii-v|\bge\b|\bsige\b|tunnel fet|\btfet\b|\bhemt\b|mobility|variability|dopant|
      semiconductor (technolog\w*|platform)|2d material|back[ -]?side (power|design|pdn|routing)|powervia|\bimt\b|thin-film|\btft\b|\bigzo\b|in-ga-zn|oxide semiconductor|c-axis|
      design-technology co-optimization|technology co-optimization|technology optimization|^fabrication of|si capacitor|mim capacitor|decoupling capacitor|bits?/cell|1f1r
    )\b
""")

# Never the subject of a digital paper, whatever else the title says.
HARD_VETO = _rx(r"""
    \b(
      power impedance|imagers?|image sensors?|\bspad\b|pixel sensor|neural probe|microelectrode|electrode array|electrodes?\b|stimulators?|
      prosthes\w*|retinal|cochlea|ultrasound|ultrasonic|\bnmr\b|\bmri\b|fluoresc\w*|microfluidic|biosensor|electrochemical|tomography|urine|glucose|bioreactor|
      antenna|radar|phased-?array|backscatter\w*|magnetoelectric|nanowire|atom switch|spin logic|piezo\w*|thermoelectric|energy-harvester|harvesters?\b|
      neural recording|neural-recording|recording neural|simultaneous recording|neural (interface ic|sensor|probe)|stimulation|
      dna (detection|synthesizer|analysis soc)|bioluminescence|transceivers?|wireline|serdes
    )\b
""")

# Analog / memory / RF subjects. A digital keyword that only appears after
# one of these, behind a connector, is a qualifier ("SRAM for ... Processor").
SOFT_VETO = _rx(r"""
    \b(
      \brx\b|\btx\b|receivers?|transmitters?|\bcdr\b|equalizers?|\bdfe\b|\badcs?\b|\bdacs?\b|amplifiers?|\blna\b|\bplls?\b|dpll|adpll|\bmdll\b|
      \bvcos?\b|\bdco\b|oscillators?|jitter|\btdcs?\b|rectifiers?|converters?\b|chargers?|drivers?\b|\bmems\b|microphones?|accelerometers?|gyroscopes?|
      implant\w*|impedance|wireless power|\bwpt\b|touch|readout|sense amplifiers?|\bsrams?\b|\bdrams?\b|sdram|lpddr|ddr\d|memory interface|flash|\btcam\b|\botp\b|
      \bfram\b|feram|stt-?ram|mram|\brram\b|reram|\bpcm\b|bitline|wordline|bit-line|word-line|\bvmin\b|write-assist|read-assist|magnetic|isolat\w*|\besd\b|
      radio\b|wireless|bluetooth|wifi|wi-fi|\blte\b|\bgsm\b|cellular|\bpa\b|harvest\w*|photovoltaic|battery-?less|sensor node|ldo\b(?! .*digital)
    )\b
""")

CONNECTOR = re.compile(r"\b(for|with|in|using|via|featuring|of|to|through|by|supporting|enabling|integrated|employing|utilizing|achieving)\b", re.I)

# Ligatures and dash variants that PDF extraction leaves in titles
# (written as escapes so this file stays pure ASCII).
_FOLD = {
    "ﬁ": "fi", "ﬂ": "fl",                       # fi / fl ligatures
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
    "‘": "'", "’": "'", "“": '"', "”": '"',
    " ": " ", " ": " ", " ": " ",   # non-breaking / thin spaces
}


def fold(text):
    """Fold ligatures and dash variants so regexes see plain ASCII."""
    if not text:
        return ""
    for src, dst in _FOLD.items():
        text = text.replace(src, dst)
    return text


def _first(rules, name):
    for rx in rules:
        if re.search(rx, name, _I):
            return rx
    return None


def session_mode(conf, session_id, session_name, paper_id=""):
    """Return ('core'|'mixed'|'exclude', matched_rule)."""
    name = fold(session_name or "").strip()
    if conf == "ISSCC":
        core, mixed, excl = ISSCC_CORE, ISSCC_MIXED, ISSCC_EXCLUDE
    else:
        core, mixed, excl = VLSI_CORE, VLSI_MIXED, VLSI_EXCLUDE

    if not name:
        ident = (session_id or "").strip() or (paper_id or "").strip()
        if conf == "VLSI" and _UNNAMED_EXCLUDE.match(ident):
            return "exclude", "unnamed technology/plenary track (%s)" % ident[:4]
        if conf == "VLSI" and _UNNAMED_CORE.match(ident):
            return "core", "unnamed digital track (%s)" % ident[:3]
        return "mixed", "unnamed session"

    rx = _first(core, name)
    if rx:
        return "core", rx
    rx = _first(mixed, name)
    if rx:
        return "mixed", rx
    rx = _first(excl, name)
    if rx:
        return "exclude", rx
    return "mixed", "no rule matched"


def paper_in_scope(title):
    """Per-paper decision for MIXED sessions: (bool, reason)."""
    t = fold(title)
    if t.upper().startswith("WITHDRAWN"):
        return False, "withdrawn"
    strong = STRONG.search(t)
    if not strong:
        return False, "no digital keyword"
    device = DEVICE.search(t)
    if device:
        return False, "device paper (%s)" % device.group(0)
    hard = HARD_VETO.search(t)
    if hard:
        return False, "non-digital subject (%s)" % hard.group(0)
    soft = SOFT_VETO.search(t)
    if soft and soft.start() < strong.start() and CONNECTOR.search(t[soft.end():strong.start()]):
        return False, "'%s' only qualifies '%s'" % (strong.group(0), soft.group(0))
    return True, "keyword '%s'" % strong.group(0)
