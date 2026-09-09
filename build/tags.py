"""
Topic tags for digital / architecture / accelerator papers.

Each tag is a dict with:
  id      - stable slug used in the data file and in URLs
  label   - shown on the site
  group   - grouping for the tag picker
  desc    - one line, shown as a tooltip on the site
  pattern - regex over the folded title (case-insensitive, verbose mode)

A paper gets every tag whose pattern matches its title. A paper that matches
nothing receives a fallback tag from its session name (SESSION_FALLBACK), and
if that fails too it is tagged 'other' so it never disappears from a filter.

Tags are matched on titles only, not abstracts, so every year is tagged with
the same evidence. Keep patterns explicit; word boundaries are added around
each alternation.
"""

import re

GROUPS = ["Architecture", "AI & ML", "Applications", "Circuits & Techniques"]

TAGS = [
    # ---------------------------------------------------------------- Architecture
    dict(id="cpu", label="CPU / Processor Core", group="Architecture",
         desc="General-purpose processor cores and multi-core CPUs: x86, ARM, RISC-V, server and mobile CPUs.",
         pattern=r"""
            x86(-64)?|ia-32|armv?\d|\barm\b|cortex-[amr]\w*|risc-?v|\bmips\b|itanium|sparc\w*|
            xeon|power ?\d+|power ?\d+tm|z1\d\b|znext|system z|zenterprise|telum|zen ?\d?[a-z]?\b|
            microprocessors?|processor cores?|cpu subsystem|\bcpus?\b|\d+-core|\d+ cores?\b|octa-core|quad-core|hexa-core|deca-core|dual-core|
            many-?core|manycore|multi-?core (processor|cpu|soc|mobile)|out-of-order|superscalar|\bsmt\d?\b|
            vector (processor|machine|co-processor)|microservers?|supercomputer|
            core processor|core count|cores? with|processor family|processor system|
            \bia\b|broadwell|haswell|westmere|skylake|lakefield|ivytown|core i[357]|atom(tm)? processor|intel atom|neoverse|
            \d+-processor|processor array|steamroller|bulldozer|jaguar|godson|a64fx|\d+ cores?\b
         """),
    dict(id="gpu", label="GPU & Graphics", group="Architecture",
         desc="Graphics processing units and graphics/rendering pipelines: rasterization, ray tracing, neural rendering.",
         pattern=r"""
            \bgpus?\b|gpgpu|graphics|radeon|geforce|\bcdna\b|instinct|a100|shader|shading|
            ray-?tracing|ray-?casting|render\w*|nerf|gaussian splatting|\d?d ?gs processor|3d ?gs\b|4dgs|
            light-field|refocusing|vertex|photorealistic
         """),
    dict(id="mobile-soc", label="Mobile / Application SoC", group="Architecture",
         desc="Smartphone and mobile application processors, flagship mobile SoCs and their subsystems.",
         pattern=r"""
            mobile (soc|application|soc performance|platform|device|gaming|cpu|processor)|smartphone|application processors?|
            flagship|exynos|snapdragon|hexagon|mediatek|5g mobile|mobile soc|
            handheld|tablet|for mobile\b
         """),
    dict(id="server", label="Server / Datacenter", group="Architecture",
         desc="Server, mainframe, datacenter and cloud-scale processors and systems.",
         pattern=r"""
            (?<!client-)servers?\b|datacenter|data ?center|data-center|cloud\b|enterprise|mainframe|mission-critical|
            infrastructure|hyperscale|exascale|exa-class|petaflops|supercomputer|\bhpc\b|
            high-performance computing|high performance computing|networking|switch chip
         """),
    dict(id="accelerator", label="Domain-Specific Accelerator / DSP", group="Architecture",
         desc="Fixed-function or domain-specific hardware accelerators, engines and DSPs that are not general-purpose cores.",
         pattern=r"""
            accelerat\w*|\bengines?\b|processing unit|\bxpu\b|domain-specific|domain specific|
            \bpu\b|\bppu\b|\bvpu\b|\bnpu\b|\bapu\b|\bdsps?\b|digital signal processor
         """),
    dict(id="reconfigurable", label="Reconfigurable / FPGA / CGRA", group="Architecture",
         desc="FPGAs, coarse-grained reconfigurable arrays, dataflow and spatial architectures.",
         pattern=r"""
            \bfpgas?\b|efpga|reconfigurable (array|fabric|processor|computing|dataflow|architecture|logic|spatial|hybrid)|
            \bcgras?\b|coarse-?grained|programmable logic|dataflow|data-flow|spatial (array|accelerator|architecture)|
            \bvliw\b|dynamically reconfigurable|reconfigurable (dense|matrix|cnn|processor)
         """),
    dict(id="noc", label="NoC / Interconnect", group="Architecture",
         desc="On-chip networks, mesh and crossbar fabrics, routers and die-to-die links seen from the architecture side.",
         pattern=r"""
            network-?on-?chips?|\bnocs?\b|on-chip (network|interconnect|ring|link|signaling|bus)|
            mesh (network|noc|interconnect|topology|on-chip|over)|\d+x\d+ mesh|mesh-based|[23]d mesh|scalable mesh|routers?\b|switch fabric|crossbar|interconnect fabric|swizzle|
            die-to-die|\bd2d\b|chip-to-chip|\bc2c\b|ucie|nvlink|inter-chiplet|inter-dielet|\baib\b|
            off-chip bandwidth|global interconnect|interconnect circuits|charge-recycling bus|shared bus
         """),
    dict(id="memory-hierarchy", label="Memory / SRAM / DRAM / Cache", group="Architecture",
         desc="Papers built around SRAM/DRAM/eDRAM/HBM, caches, register files, memory bandwidth or on-chip memory organization.",
         pattern=r"""
            \bcaches?\b|v-cache|\bl[123]\b|\bhbm\d?e?\b|edram|memory hierarchy|memory bandwidth|
            register files?|scratchpad|on-chip memory|on-chip (sram|weight)|weight storage|
            \bsrams?\b|\bdrams?\b|gddr\d?|memory controller|\bssds?\b|memory expansion|memory-centric|
            \btcam\b|content addressable|content-addressable|gain-cell|last[- ]level cache
         """),
    dict(id="nvm", label="Emerging NVM", group="Architecture",
         desc="Compute or systems built on non-volatile memory: RRAM/ReRAM, MRAM, PCM, FeRAM/FeFET, flash and other eNVM.",
         pattern=r"""
            \brrams?\b|reram|memristor|\bmrams?\b|stt-?m?ram|sot-mram|\bmtjs?\b|\bpcm\b|phase[- ]change|
            feram|fefets?|ferroelectric|\bflash\b|\bnand\b|nonvolatile|non-volatile|\bnvm\b|\benvm\b|charge-trap|\botp\b|
            oxide-based|atom switch|floating body|resistive (ram|memory)|magnetic (ram|memory)
         """),
    dict(id="chiplet-3d", label="Chiplet / 3D Integration", group="Architecture",
         desc="Chiplets, 2.5D/3D stacking, interposers, hybrid bonding and multi-chip packaging of digital systems.",
         pattern=r"""
            chiplets?|dielets?|3d[- ]stack\w*|3d-ic|\b3d ic\b|stacked (on|over|memory|processor|sram|cache|cmos)|
            \btsvs?\b|interposer|hybrid-?bond\w*|wafer-scale|wafer scale|2\.5d|3\.5d|3d integrat\w*|
            monolithic 3d|multi-?chip|\bmcm\b|multi-chip-module|package-on-package|\bsip\b|system-in-package|
            cowos|face-to-face|inductive-coupling|inductive coupling|multi-die|multi-tile|3d logic
         """),
    dict(id="iot-mcu", label="Microcontroller / IoT / ULP", group="Architecture",
         desc="Microcontrollers, IoT end-nodes, energy-harvesting and ultra-low-power always-on systems.",
         pattern=r"""
            microcontrollers?|\bmcus?\b|cortex-m\w*|\biot\b|\bioe\b|aiot|sensor nodes?|wireless sensor|
            energy[- ]harvest\w*|self-powered|battery-?less|batteryless|battery-indifferent|solar-powered|
            always-on|wake-?up|\bnw\b|nanowatt|sub-nw|\bulp\b|ultra-low-power|ultra low power|
            normally-off|nonvolatile (processor|microcontroller|soc|logic)|non-volatile (processor|microcontroller)|
            state[- ]retenti\w*|end-nodes?|edge nodes?|mote\b|dust-size|\bpw\b|picowatt
         """),

    # ---------------------------------------------------------------- AI & ML
    dict(id="dnn", label="Deep Learning Accelerator", group="AI & ML",
         desc="Neural-network inference/training hardware: CNN, DNN, RNN processors and NPUs.",
         pattern=r"""
            \bdnns?\b|\bcnns?\b|\brnns?\b|\bnns?\b|\bmlps?\b|\blstm\b|\bgru\b|convnets?|
            neural[- ]?networks?|neural (engine|processing unit|processor|decision|cpu|inverse|path|rendering|video|graphics)|
            deep[- ]learning|deep[- ]neural|deep[- ]convolutional|machine[- ]learning|
            \bnpus?\b|neural processing|tops/w|tflops/w|tops\b|tflops\b|gops/w|
            ai (accelerator|processor|chip|soc|core|inference|training|edge|processing|applications)|
            ai-(accelerator|processor|soc|edge|iot)|edge-?ai|\bml\b|tinyml|
            inference|convolution\w*|\bmacs?\b|multiply-accumulate|systolic|tensor|
            learning processor|learning accelerator|neural-network|neuro-controller|
            autoencoder|u-net|feature extract\w*|classifier|classification|perceptron|hyperdimensional
         """),
    dict(id="transformer-llm", label="Transformer / LLM / GenAI", group="AI & ML",
         desc="Transformer, attention, large-language-model and generative-AI accelerators: LLM inference and training, speculative decoding, MoE, VLMs, state-space models, diffusion and autoregressive generation, AI agents.",
         pattern=r"""
            transformers?|\bllms?\b|large[- ]language|language[- ](models?|processing unit|generation)|(?<!channel )attention|
            \bbert\b|\bgpt\b|llama|\btokens?\b|token/s|speculative[- ]decoding|mixture-of-experts|\bmoe\b|
            state-space model|\bssm\b|mamba|vision-language|\bvlm\b|multimodal|multi-modal|
            gemm|softmax|kv-?cache|prefill|decoding language|\bqkv\b|
            generative|gen-?ai\b|chain-of-thought|\bcot\b|distill\w*|foundation models?|billion-parameter|
            (ai|social|multi-ai|llm) agents?|agentic|autoregressive|text-to-\w+|
            (?<!drift-)(?<!drift )diffusion(?![- ]fet)|classifier-free|rotation-based|outlier-free
         """),
    dict(id="generative", label="Generative AI (Diffusion / GAN)", group="AI & ML",
         desc="Generative model processors: diffusion, GANs, text-to-image/motion and visual autoregressive generation.",
         pattern=r"""
            (?<!drift-)(?<!drift )diffusion(?![- ]fet)|\bgans?\b|generative|gen-?ai\b|autoregressive|text-to-\w+|
            image generation|content generation|denoising|\bvae\b|classifier-free
         """),
    dict(id="cim", label="Compute-in-Memory", group="AI & ML",
         desc="Compute-in-memory and processing-in-memory macros and processors (SRAM, eDRAM, RRAM, MRAM, flash, DRAM).",
         pattern=r"""
            compute-?in-?memory|computing-?in-?memory|computation-?in-?memory|in-?memory[- ]comput\w*|
            in-?memory (computing|computation|encryption|processing|search\w*|convolution|annealing|matrix|machine|encoding|bwn|dynamic|approximate|point)|
            \bcims?\b|\bpim\b|\bimc\b|\bacim\b|processing-?in-?memory|process-near-memory|processing-in-sensor|
            near-memory|compute-near|compute sram|conv-ram|xnor-sram|sandwich-ram|
            accelerator-in-memory|logic-in-memory|memory-boundary|in-edram|in-sensor
         """),
    dict(id="neuromorphic", label="Neuromorphic / SNN", group="AI & ML",
         desc="Spiking neural networks, neuromorphic processors, synapse/neuron circuits and brain-inspired computing.",
         pattern=r"""
            neuromorphic|spiking|\bsnns?\b|spike-?(driven|based|domain|sorting|only|detection)|
            synapses?|synaptic|neurons?\b|\bstdp\b|brain-inspired|neocortical|neuro-inspired|bionic|
            event-driven (visual|intelligent|wake|spiking|neural|neuromorphic|processor|architecture|binary|smart|bionic|feature|processing|convolution|spike|vision|computing|accelerator|snn|sensing|object)|
            event-based|event camera|reservoir computing|loihi|\bsops?\b|pj/sop
         """),
    dict(id="sparsity", label="Sparsity", group="AI & ML",
         desc="Hardware that exploits sparse weights or activations: zero-skipping, pruning, sparse matrix engines.",
         pattern=r"""
            spars\w*|pruning|pruned|zero-?skip\w*|zero skipping|redundancy skipping|non-zeros|nonzero|
            early exit|early-exit|computation skipping|skipping|token-attention-weight redundancy
         """),
    dict(id="precision", label="Quantization / Precision", group="AI & ML",
         desc="Reduced- or variable-precision arithmetic: INT4/INT8, FP8/BF16, posits, binary/ternary networks, bit-serial datapaths.",
         pattern=r"""
            int-?\d{1,2}\b|fp-?\d{1,2}\b|bf16|bfloat|mxfp\d?|microscaling|posit\w*|
            binary (neural|weight|cnn|dnn|autoencoder|network)|binarized|binary/ternary|ternary|
            bit-?serial|bit-precision|bit-width|bitwidth|precision-scalable|variable-precision|
            mixed-precision|mixed precision|multi-precision|low-bit|quantiz\w*|log-quantized|logarithmic|
            \d{1,2}b-to-\d{1,2}b|\d-to-\d{1,2}b|\d{1,2}-bit (weight|precision|mac|quantiz|float|integer)|
            floating-point|floating point|number format|dual-quantized|per-vector scaled|block floating
         """),
    dict(id="training", label="On-Device Training", group="AI & ML",
         desc="Chips that perform learning on-chip: training processors, fine-tuning, online/continual learning.",
         pattern=r"""
            \btraining\b|(?<!deep )(?<!deep-)learning processor|on-?chip (learning|training|adaptation)|on-?device (learning|training)|
            online[- ]learning|online-tuning|fine-?tun\w*|continual|life-long|lifelong|backpropagation|back-propagation|
            reinforcement|deep rl\b|\brl\b accelerator|meta-learning|few-shot|one-shot learning|transfer learning|
            self-learning|unsupervised|forward-gradient|zeroth-order|direct feedback alignment|
            weight update|weight updating|\bepochs?\b|(?<!deep )(?<!deep-)(?<!machine )(?<!machine-)learning (accelerator|engine|soc|classifier)
         """),
    dict(id="edge-ai", label="Edge AI / TinyML", group="AI & ML",
         desc="Always-on and edge inference under milliwatt budgets: keyword spotting, wake-up, tiny models.",
         pattern=r"""
            edge (device|ai|comput\w*|intelligen\w*|inferenc\w*|robotic|node|applicat\w*|platform|llm|process\w*|machine|mote)|
            edge-?ai|ai-?edge|ai edge|tinyml|tiny-?ml|tiny (ai|classifier|convolutional|versatile)|
            at the edge|on the edge|for edge\b|extreme edge|
            keyword[- ]spotting|\bkws\b|wake-?up (chip|function|module|device)|always-on|
            sub-mw|nj/(class|inference|classification|decision)|uj/(class|inference|frame|token)|
            intelligent (iot|wake-up|vision|neural)
         """),

    # ---------------------------------------------------------------- Applications
    dict(id="vision", label="Vision / Image Processing", group="Applications",
         desc="Image and vision processors: recognition, detection, tracking, depth, ISP, super-resolution, SLAM.",
         pattern=r"""
            \bvision\b|\bvisual\b|\bimage\b|\bimages\b|imaging|\bvideo\b|object (detection|recognition|tracking|classification|matching|viewpoint)|
            face\b|facial|gesture|hand pose|pose estimation|super-resolution|super resolution|
            \bisp\b|image signal processor|optical flow|\bdepth\b|stereo|disparity|\bslam\b|segmentation|
            point-?cloud|scene|pixel\w*|\bfps\b|frames?/s|mj/frame|uj/frame|nj/pixel|pj/pixel|
            camera|lidar|feature extraction|descriptor|vocabulary|image matching|object matching|recognition processor|
            gaze|hyperspectral|light-field|hdr|high-dynamic-range|neural graphics|neural rendering|4k|8k|uhd|full-hd|1920x1080|1080p|720p
         """),
    dict(id="video-codec", label="Video Codec", group="Applications",
         desc="Video encoders/decoders and codec engines: H.264/AVC, H.265/HEVC, AV1, CABAC, motion estimation.",
         pattern=r"""
            h\.26[45]|hevc|\bavc\b|\bav1\b|\bvvc\b|\bvp9\b|codec|cabac|motion estimation|video (en|de)cod\w*|
            (en|de)coder chip|\bmvc\b|super hi-vision|3dtv|intra-frame|set-top box|streaming|
            blu-ray|tv soc|television|hdtv|uhdtv|4320p|2160p
         """),
    dict(id="robotics", label="Robotics / Autonomous", group="Applications",
         desc="Robot, drone and autonomous-navigation processors: path planning, odometry, motion control, driving.",
         pattern=r"""
            robot\w*|autonomous|navigation|path[- ]?planning|motion[- ]?planning|motion-control|odometry|
            drones?|\buav\b|manipulation|footstep|humanoid|swarm|bristle|driving processor|self-driving|
            end-to-end driving|localization|surveillance
         """),
    dict(id="automotive", label="Automotive", group="Applications",
         desc="Automotive-grade processors and SoCs: ADAS, ISO 26262/ASIL, in-vehicle computing.",
         pattern=r"""
            automotive|\badas\b|\basil\b|asil-[abcd]|iso ?26262|vehicles?|\bcar\b|black-box|
            driving|aec-q100|auto-g1|autonomous-driving|motor (control|timer)
         """),
    dict(id="ar-vr", label="AR / VR / Spatial Computing", group="Applications",
         desc="Processors for AR/VR headsets, smart glasses, spatial computing and the metaverse.",
         pattern=r"""
            ar/vr|augmented reality|virtual reality|\bvr/mr\b|\bmr\b applications|metaverse|\bhmd\b|
            smart ?glasses|spatial computing|head-mounted|headset|immersive|mind imagery|hyper-realistic
         """),
    dict(id="speech", label="Speech / Audio", group="Applications",
         desc="Speech recognition, keyword spotting, voice activity detection and audio processing.",
         pattern=r"""
            speech|voice|keyword[- ]spotting|\bkws\b|\bvad\b|voice-activity|spoken|speaker|
            audio|acoustic|hearing|sound|\basr\b|microphone|filter bank|vowel|
            text-to-motion|social agent|language-understanding
         """),
    dict(id="comm", label="Communication / Baseband DSP", group="Applications",
         desc="Baseband and channel-coding digital signal processing: MIMO detectors, LDPC/polar/turbo decoders, modems, FFT, GPS.",
         pattern=r"""
            baseband|\bmimo\b|mu-mimo|\bldpc\b|polar (decoder|code)|\bturbo\b|\bfec\b|forward error correction|
            (bch|viterbi|reed|huffman|nb-ldpc|sc|scl|ofec|bp) decoder|decoder for|soft-?(decision|detection|output)|
            \b[45]g\b|\b6g\b|b5g|\blte\b|wimax|\bofdm\w*|\botfs\b|\bmodem\b|channel estimation|
            (mimo|massive mimo|sphere|message-passing|list|belief-propagation|belief propagation) (detector|decoder)|
            software-defined radio|\bsdr\b|cognitive radio|digital beamform\w*|beamformer|beamforming|
            \bgps\b|\bgnss\b|802\.1[15]|bluetooth|zigbee|\bwlan\b|wpan|\bfft\b|fourier|
            forward error correction|error correction engine|error-correcting code|equaliz\w*|precoder|detector-decoder|detection and decoding|
            \bmac processor\b|network routing|packet|ethernet|communication (soc|systems|gateway)|
            10gbase|read channel|multi-?standard|\brsma\b|\burllc\b
         """),
    dict(id="security", label="Security / Cryptography", group="Applications",
         desc="Crypto engines, PUFs, TRNGs, side-channel countermeasures, post-quantum and homomorphic encryption.",
         pattern=r"""
            security|secure|crypto\w*|\baes\b|\baes-\d+\b|sha-?\d|\brsa\b|\becc\b|elliptic|isogeny|sqisign|lattice|
            homomorphic|\bfhe\b|ckks|paillier|mlwe|kyber|dilithium|post-quantum|quantum-secure|\bpqc\b|\bkem\b|
            \bpufs?\b|physically[- ]unclonable|\btrng\b|random[- ]number|entropy|
            encrypt\w*|decrypt\w*|cipher|sms4|camellia|prince|\bdtls\b|masking|masked|
            side-channel|side channel|\bsca\b|\bsca-|dpa|power analysis|leakage-?shift|
            attack|tamper|glitch|probing|fault-injection|fault injection|laser voltage|camouflaged|obfuscat\w*|
            authentication|privacy|trustworthy|trojan|smart card|smart-card|chip id|chip-id|
            bitcoin|mining engine|\bghash\b|self-destruction|anti-spoofing|monitor.*attack
         """),
    dict(id="genomics", label="Genomics / Bioinformatics", group="Applications",
         desc="Accelerators for DNA/genome sequencing and analysis.",
         pattern=r"""
            genom\w*|\bdna\b|sequencing|hidden-markov|\bhmm\b|bioinformatic\w*|genetic variant|
            next-generation sequencing|read alignment
         """),
    dict(id="scientific", label="Scientific / HPC Computing", group="Applications",
         desc="Accelerators for scientific and high-performance workloads: linear algebra, PDE solvers, FP64, physics simulation.",
         pattern=r"""
            \bhpc\b|high-performance computing|high performance computing|supercomputer|exascale|exa-class|
            petaflops|gflops|dp-gflop|stencil|linear algebra|linear-algebra|sparse matrix|matrix-matrix|
            \bblas\b|partial differential|\bpde\b|finite (difference|element)|physics|scientific computing|
            fp64|double-precision|double precision|fpu utilization|floating point unit|
            \bfpu\b|nonlinear function kernels|matrix multipl\w*|matrix-multiply
         """),
    dict(id="optimization", label="Ising / SAT / Probabilistic Computing", group="Applications",
         desc="Combinatorial-optimization and probabilistic hardware: Ising machines, annealers, SAT solvers, p-bits, Bayesian inference.",
         pattern=r"""
            \bising\b|anneal\w*|\bsat\b|k-sat|3-sat|satisfiability|combinatorial|
            quadratic optimization|\bspins?\b|spin-spin|\d+-spin|p-bits?|probabilistic|bayesian|gibbs|
            stochastic (comput\w*|self-annealing|oscillation|sampling|flash|analog)|sampling machines?|boltzmann|
            quantum-inspired|optimization problems|solver\b|solvability|metamorphic
         """),
    dict(id="data-analytics", label="Graph / Data Analytics", group="Applications",
         desc="Graph processing, recommendation, database/search, compression and other data-centric accelerators.",
         pattern=r"""
            recommendation|\bgraph\b|\bgnns?\b|graph neural|database|data analytics|big[- ]data|
            search engine|search accelerator|similarity search|nearest[- ]neighbou?r|\bk-?nn\b|\bann search|
            hash\w*|compression|decompression|gzip|huffman|regular expression|regex|
            text search|full-text|string (matching|processing)|query|\bqps\b|filter-based search|data processing|
            data-driven machine|analytics|event processing|associative memory
         """),
    dict(id="biomedical", label="Biomedical / Health Signal Processing", group="Applications",
         desc="Digital processing for health and neural signals: seizure detection, ECG/EEG classifiers, brain-machine interfaces.",
         pattern=r"""
            seizure|epilep\w*|\becg\b|\beeg\b|\bemg\b|\bexg\b|\becog\b|\begm\b|neural signal|
            brain-?machine|brain-?computer|\bbmi\b|\bbci\b|brain-to-text|spike[- ]sorting|spike discrimination|
            physiological|cardiac|arrhythmia|biomedical|\bhealth\b|healthcare|medical|
            neural (interface|recording|commanding|probe|stimulat\w*|readout|decoding)|neuroprosthe\w*|prosthe\w*|
            implant\w*|olfactory|bio-?signal|biopotential|patient|hearing aid|
            ventricular|electrophysiolog\w*|neuromodulat\w*|brain state|neural-recording
         """),

    # ---------------------------------------------------------------- Circuits & Techniques
    dict(id="power-mgmt", label="Power Management / DVFS", group="Circuits & Techniques",
         desc="Digital power techniques: DVFS, droop mitigation, digital LDOs and integrated regulators, power gating, body bias.",
         pattern=r"""
            \bdvfs\b|\bdvs\b|\bavs\b|\babb\b|droop|power[- ]manag\w*|power[- ]deliver\w*|power[- ]gating|
            voltage regulat\w*|regulator|\bldos?\b|low-?dropout|\bivr\b|micro-?regulators?|
            adaptive voltage|adaptive (body|back)|body[- ]bias\w*|back[- ]bias\w*|body-?biasing|
            energy minimization|energy-?performance|current (sensor|sensing|density|steering|efficiency)|power (sensor|estimation|budget|supply|impedance|reduction|efficiency|adaptation)|
            leakage|guard-?band|voltage[- ]stack\w*|supply[- ]noise|supply regulation|
            dynamic voltage|voltage scaling|voltage (scalable|boost|enhancement|margin|droop)|frequency boost|
            \bpdn\b|power-?on|retention|sleep|standby|thermal|temperature|
            switched-capacitor (converter|voltage|dc-dc|adiabatic)|dc-dc|buck|
            energy-efficient operation|energy-optimal|power allocation|peak current|current-limiting|
            power-?saving|power (management|delivery) (unit|network|scheme|system)|pmu\b|
            performance-regulated|energy-aware
         """),
    dict(id="clocking", label="Clocking / PLL", group="Circuits & Techniques",
         desc="Clock generation and distribution in digital sessions: adaptive and resonant clocking, digital PLLs/MDLLs, clock gating.",
         pattern=r"""
            clock\w*|clocked|\bplls?\b|adpll|\bmdll\b|\bdlls?\b|\bdco\b|fractional-?n|
            frequency (divider|generat\w*|multipli\w*|locked|synthesi\w*|scaling|boost|tracking)|
            fractional (output )?divider|injection-?locked|jitter|resonant|skew|duty-?cycle|
            \btdc\b|time-to-digital|phase-locked|oscillator|multiplier with|\bssc\b|spread[- ]spectrum|
            direct digital frequency|\bddfs\b
         """),
    dict(id="resilience", label="Adaptive / Resilient Circuits", group="Circuits & Techniques",
         desc="Variation and error tolerance: Razor-style timing-error detection, in-situ monitors, aging/NBTI sensing, near-threshold operation.",
         pattern=r"""
            razor|timing[- ]error|timing[- ]margin|timing[- ]slack|error[- ]detect\w*|error[- ]correct\w*|error[- ]tolerant|
            in-?situ|variation-?(tolerant|resilient|aware|adaptive)|variation (tolerance|resilien\w*)|
            resilien\w*|aging|\bnbti\b|\bpbti\b|degradation|reliab\w*|wear-?out|
            soft[- ]error|fault-?tolerant|metastability|\bpvt\b|pvt-|
            near-?threshold|sub-?threshold|subthreshold|ultra-low-voltage|low-voltage operation|wide-operating-range|
            \bvmin\b|slack (monitor|regulation)|critical-?path|monitor\w*|self-tuning|self-calibrat\w*|
            adaptive (clock|body|frequency|performance|power|precision|voltage)|functional safety|dependable
         """),
    dict(id="digital-circuits", label="Digital Circuit Techniques", group="Circuits & Techniques",
         desc="Logic-level techniques: flip-flops and latches, standard cells, arithmetic units, level shifters, synthesizable/asynchronous design.",
         pattern=r"""
            flip-?flops?|latch\w*|standard[- ]cells?|std-?cell|logic family|domino|schmitt-trigger|
            \badders?\b|multipliers?\b|fused multiply|\bfma\b|floating-point unit|\bfpu\b|\balu\b|arithmetic|datapath|
            \bsimd\b|permutation|register file|level shifter|
            synthesizable|synthesized|fully digital|all-digital|asynchronous|adiabatic|charge-recovery|charge recovery|
            charge-recycling|pulsed|single-phase|dual-edge|wired-logic|via-programm\w*|
            logic (gates?|circuits?|cells?|bit-cell|process)|standard-cell-based|\bscan\b|\bbist\b|testab\w*|
            \bfir\b|\biir\b|filter\b|repeater|signaling|on-chip link|current-mode|
            zero-short-circuit|schmitt|contention-free|energy-delay|time-borrowing
         """),
    dict(id="emerging", label="Emerging / Unconventional Computing", group="Circuits & Techniques",
         desc="Non-CMOS or non-digital compute substrates: superconducting logic, cryogenic, photonic, analog/mixed-signal, stochastic, thin-film and CNT circuits.",
         pattern=r"""
            superconduct\w*|josephson|\bsfq\b|single-flux-quantum|cryo\w*|quantum|
            photonic|optical (analog|processor|comput\w*|interconnect)|electro-optical|
            stochastic|approximate[- ]comput\w*|approximate arithmetic|analog (comput\w*|neuron|matrix|neuronal|cnn|processor|k-sat|solver|calculation|memory)|
            mixed-signal (comput\w*|processing|processor|accelerator|neuromorphic|binary|oscillator|k-sat|3d|gps|cim|spatial)|
            oscillator-based|coupled (oscillator|ring)|charge-domain|time-domain (cnn|comput\w*|mac|neuromorphic|generative|dtw)|
            carbon nanotube|\bcnts?\b|\bcnfet\b|thin-film|\btft\b|flexible (8b|microprocessor|electronics|substrate)|printed electronics|organic (electronics|transistor)|metal-oxide|
            in-ga-zn|igzo|oxide semiconductor|relay|\bmems\b logic|memristor|ferroelectric|
            wired-logic|network-on-textiles|textiles|hyperdimensional|reservoir|p-bit
         """),
    dict(id="dtco", label="DTCO / Design Methodology", group="Circuits & Techniques",
         desc="Design-technology co-optimization, PPA methodology, EDA/AI-assisted design and design-flow papers.",
         pattern=r"""
            \bdtco\b|\bstco\b|co-optimiz\w*|co-design|design methodology|\bppa\b|physical design|
            \beda\b|place-and-route|synthesis flow|design flow|compiler|hardware design|
            ai-enabled|ai for (design|circuits)|inverse-designed|design complexity|design enablement|
            hardware-compiler|technology co-|holistic|design considerations|lessons from
         """),
]

# Tags that every paper in a session receives, on top of the title rules.
# Fields: conf (regex or None), session (regex on the session name), min_year, tag.
# The ISSCC "AI Accelerators" sessions (2025 on) are the LLM / generative-AI
# sessions of the program; earlier sessions with that name (VLSI 2019) hold
# CNN/DNN chips and are left to the title rules.
SESSION_TAGS = [
    dict(conf=r"^ISSCC$", session=r"^ai.accelerators?$", min_year=2025, tag="transformer-llm"),
]

# When a title matches no tag, the session name still says what the paper is.
SESSION_FALLBACK = [
    (r"processor|soc", "cpu"),
    (r"machine learning|\bml\b|ai|deep-learning|neural|nn", "dnn"),
    (r"compute-in-memory|computation in memory|computing-in-memory|cim|pim", "cim"),
    (r"security|secure", "security"),
    (r"clocking|pll", "clocking"),
    (r"power|regulator|ldo", "power-mgmt"),
    (r"adaptive|resilien", "resilience"),
    (r"accelerator", "accelerator"),
    (r"digital", "digital-circuits"),
]

OTHER = dict(id="other", label="Other Digital", group="Circuits & Techniques",
             desc="In scope by session, but no topic rule matched the title yet.")


def _flatten(pattern):
    """Join a multi-line pattern, dropping indentation but keeping the single
    spaces inside phrases (re.VERBOSE would eat those)."""
    return re.sub(r"\s*\n\s*", "", pattern.strip())


def _compile(pattern):
    # Wrap every alternation in word boundaries so 'arm' never matches 'harm'.
    return re.compile(r"\b(?:" + _flatten(pattern) + r")\b", re.I)


COMPILED = [(t, _compile(t["pattern"])) for t in TAGS]
FALLBACK_COMPILED = [(re.compile(rx, re.I), tag) for rx, tag in SESSION_FALLBACK]
SESSION_TAGS_COMPILED = [
    (re.compile(r["conf"], re.I) if r.get("conf") else None, re.compile(r["session"], re.I), r.get("min_year", 0), r["tag"])
    for r in SESSION_TAGS
]


def session_tags(conf, year, session_name_folded):
    """Extra tag ids that the session itself confers on every paper in it."""
    out = []
    for conf_rx, sess_rx, min_year, tag in SESSION_TAGS_COMPILED:
        if conf_rx and not conf_rx.search(conf or ""):
            continue
        if year < min_year:
            continue
        if sess_rx.search((session_name_folded or "").strip()):
            out.append(tag)
    return out


def tag_title(title_folded, session_name_folded="", conf="", year=0):
    """Return the list of tag ids for one paper."""
    tags = [t["id"] for t, rx in COMPILED if rx.search(title_folded)]
    for t in session_tags(conf, year, session_name_folded):
        if t not in tags:
            tags.append(t)
    if not tags:
        for rx, tag in FALLBACK_COMPILED:
            if rx.search(session_name_folded):
                tags.append(tag)
                break
    if not tags:
        tags.append(OTHER["id"])
    return tags


def all_tags():
    """Tag definitions in display order, including the fallback tag."""
    out = [dict(id=t["id"], label=t["label"], group=t["group"], desc=t["desc"]) for t in TAGS]
    out.append(dict(OTHER))
    return out
