# Paper History

A public, searchable list of every **digital / architecture / accelerator** paper
presented at **ISSCC (2010–2026)** and the **Symposium on VLSI Technology and
Circuits (2010–2025)**, tagged by topic and charted by year.

**Site:** https://hyunwon.blog/Personal.Paper_history/
(`hyunwonch.github.io/Personal.Paper_history/` redirects there, because the
account's GitHub Pages use the custom domain.)

Plain static HTML, CSS and JavaScript, hosted on GitHub Pages. No build step
is needed to serve it; `index.html` works from a local file too.

## What is in it

| Conference | Years | Papers |
|---|---|---:|
| ISSCC | 2010–2026 | 696 |
| VLSI Symposium | 2010–2025 | 393 |
| **Total** | | **1,089** |

Each paper carries: conference, year, session number and name, paper number,
title, authors, affiliations, a DOI or IEEE Xplore link, and one or more of
40 topic tags in four groups:

- **Architecture** – CPU / processor core, GPU & graphics, mobile SoC,
  server / datacenter, domain-specific accelerator / DSP, reconfigurable /
  FPGA / CGRA, NoC / interconnect, memory / SRAM / DRAM / cache, emerging
  NVM, chiplet / 3D integration, microcontroller / IoT / ULP
- **AI & ML** – deep-learning accelerator, transformer / LLM, generative AI,
  compute-in-memory, neuromorphic / SNN, sparsity, quantization / precision,
  on-device training, edge AI / TinyML
- **Applications** – vision, video codec, robotics / autonomous, automotive,
  AR / VR, speech / audio, communication / baseband DSP, security /
  cryptography, genomics, scientific / HPC, Ising / SAT / probabilistic,
  graph / data analytics, biomedical signal processing
- **Circuits & Techniques** – power management / DVFS, clocking / PLL,
  adaptive / resilient circuits, digital circuit techniques, emerging /
  unconventional computing, DTCO / design methodology

Only program metadata is published (titles, authors, affiliations, sessions).
No abstracts or PDFs are hosted; links go to the DOI or an IEEE Xplore search.

## Using the site

- **Search** matches title, authors, affiliations and session. Terms are
  AND-ed; use `"quoted phrases"`, `-exclude`, and the prefixes `title:`,
  `author:`, `inst:`, `session:`, `year:`, `conf:`.
- **Topics**: click a topic chip to require it, click again to clear it. With
  several topics selected, a paper must carry all of them. Counts on the chips
  show how many of the current results carry each topic.
- **Trends** switches to two charts: papers per year for the current
  selection (stacked ISSCC / VLSI), and one line per selected topic. Every
  chart has a table view underneath.
- **Export CSV** downloads the current result set; **Copy link** captures the
  whole view in the URL hash so it can be shared.

## How the list is built

`build/build.py` reads the merged program index that the
[Personal.Python](https://github.com/hyunwonch) workspace produces
(`paper_search/index.json`, itself built from the ISSCC and VLSI advance
programs plus IEEE metadata) and writes `data/papers.json` and
`data/papers.js`.

```bash
# expects ../Personal.Python next to this repository
python build/build.py
# or point at the index explicitly
python build/build.py --index /path/to/paper_search/index.json
```

Two rule files decide what you see:

- `build/scope.py` – which sessions count. Sessions run by the digital
  architectures, digital circuits, machine-learning and security committees
  are taken whole (*core*). Sessions that mix digital work with memory,
  sensors, PLLs or biomedical circuits (*mixed*), and the VLSI years whose
  programs carry no session names, are filtered paper by paper with keyword
  rules: a title must show digital / architecture / accelerator content, must
  not be a device-technology paper, and must not be an analog subject that
  merely mentions a processor ("SRAM for Arm HPC Processor").
- `build/tags.py` – the topic taxonomy and the title-keyword rule for each
  tag. Tags are assigned from titles only, so every year is tagged with the
  same evidence.

`build/overrides.json` holds manual corrections keyed by
`<CONF>-<year>-<paper id>` (force a paper in or out, replace / add / remove
tags). After editing any of the three files, re-run the build and read
`build/report.txt`: it lists every session decision, every per-paper decision
in mixed sessions, and every paper that no tag rule matched.

Tags are a keyword first pass, not ground truth. If you spot a wrong session,
a missing paper or a bad tag, an override or a rule tweak fixes it in one line.

## Layout

```
index.html          the site
assets/app.js       search, filters, list rendering, SVG trend charts
assets/style.css    light / dark theme
data/papers.js      dataset as window.PAPER_DATA (loaded by index.html)
data/papers.json    the same dataset for scripts
build/build.py      generator
build/scope.py      session and per-paper scope rules
build/tags.py       topic taxonomy
build/overrides.json manual corrections
```
