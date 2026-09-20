---
title: "AI coding agents in bioinformatics in 2026: Wastewater metagenomics"
date: 2026-09-19
---

## Pathogen surveillance

Over the past two decades, most of the outbreaks were recognized late. SARS surfaced in Foshan, Guangdong in November 2002 and did not trigger a WHO global alert until March 2003 ([Feng et al. 2009](https://doi.org/10.1111/j.1365-3156.2008.02145.x)). SARS‑CoV‑2 was already circulating in the US before the country's first case was identified on 19 January 2020, residual blood donations collected from 13 December 2019 onward carried neutralizing antibodies ([Basavaraju et al. 2021](https://academic.oup.com/cid/article/72/12/e1004/6012472)). H5N1 spread through US dairy herds across multiple states before anyone thought to test a cow: genomic reconstruction traced the whole outbreak to a single wild bird to cattle transmission around December 2023, months ahead of the March 2024 confirmation ([Nguyen et al. 2025](https://doi.org/10.1126/science.adq0900)).

There is a formal target for how fast this should go: **7‑1‑7**, which aims to detect a suspected outbreak within seven days of emergence, notify within one day of detection, mount an early response within seven days of notification ([Frieden et al. 2021](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(21)01250-2/fulltext)). Measured against 41 real public health events across Brazil, Ethiopia, Liberia, Nigeria and Uganda, only 54% met the detection target, 71% the notification target and 49% the response target, and just **a quarter of events cleared all three at once** ([five-country review, 2023](https://www.thelancet.com/journals/langlo/article/PIIS2214-109X(23)00133-X/fulltext)). In practice the target is hard to hit, and the early response step is where most events fall down.

Taking a few outbreaks as examples, the table below shows how each was actually caught:

| Route                     | Case                 | Emergence → alarm                                                                           | Lag                          |
| ------------------------- | -------------------- | ------------------------------------------------------------------------------------------- | ---------------------------- |
| Clinical / syndromic      | SARS                 | first case Foshan, 16 Nov 2002 → WHO global alert, 12 Mar 2003                              | ~4 months                    |
| Clinical / syndromic      | SARS‑CoV‑2 in the US | circulating by 13 Dec 2019 (retrospective serology) → first identified US case, 19 Jan 2020 | ~5 weeks                     |
| Veterinary / agricultural | H5N1 in dairy cattle | single wild bird to cattle spillover ~Dec 2023 → confirmation in herds, late Mar 2024       | ~3 months                    |
| Blood screening           | HIV via transfusion  | ~12,000 US transfusion recipients infected 1978–1984 before a screening assay existed       | years                        |

Those lags run from weeks to years, against a target of seven days. That gap exists because most pathogens circulate quietly inside a population, and the system only wakes up once someone feels sick enough to seek care, gets tested correctly, has that test reported to the correct authority, and a clinician recognizes the pattern as something new. Every one of those steps is a filter, and a virus or a pathogen with a long incubation period or a high asymptomatic fraction slips through all of them. Like a ninja, the thing it is best at is not being seen. 🥷 🇯🇵

Those delays killed people. HIV, hepatitis B, hepatitis C and HTLV each circulated for years before they were identified, the result is that HIV infected an estimated 12,000 US transfusion recipients between 1978 and 1984, and nearly a quarter of transfusion recipients contracted HCV in the decade before screening began in the early 1990s ([Justen et al. 2026](https://doi.org/10.64898/2026.02.06.26345722)). Those deaths are the reason catching these things earlier matters.

**Wastewater monitoring** aims to fix the reactivity problem by sampling the population instead of the patient. One sample from a sewershed captures what everyone upstream is shedding, symptomatic, presymptomatic, asymptomatic, and never-sought-care alike, with no dependence on healthcare-seeking behaviour at all.

Finding a pathogen's sequence in wastewater doesn't mean anyone is sick. Sequencing reads nucleic acid rather than infectivity, and a sewer is a hostile place, so much of what comes back is degraded material from particles that could no longer infect anything. Shedding starts before symptoms and continues well after recovery. And plenty of what's in a sewer never passed through a person: food waste, agricultural and industrial discharge, animal faeces, stormwater. It still works as a screening signal.

H5N1 is the clean example. When influenza A rose sharply at Texas and North Carolina treatment plants in March and April 2024, the increase did not track human influenza activity at all, and the H5 signal showed up in sewersheds receiving industrial discharge of cow milk ([Wolfe et al. 2024](https://pubs.acs.org/doi/10.1021/acs.estlett.4c00331)). A California sewershed analysis modelled the possible inputs and reached the same conclusion: contaminated milk or infected poultry were the most likely sources ([Boehm et al. 2025](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12355958/)). The virus was there and the RNA was real, but it had not come from people.

Overall, researchers aim to use wastewater to tell us something is present and which way it's trending, which is enough to trigger targeted follow-up: clinical testing, case-finding, a look at the farms upstream.

## Wastewater monitoring using untargeted metagenomics

"Wastewater monitoring" typically include three methods:

| Approach | How it works | Finds | Misses |
| --- | --- | --- | --- |
| Targeted (qPCR, dPCR, amplicon) | primers/probes for a pre-specified target | known targets, cheaply and sensitively | anything not on the list; loses sensitivity when mutations land in primer-binding sites |
| Hybrid capture | probe panels enrich sequences similar to known pathogens | known pathogens and divergent relatives (tolerates 20–30% divergence) | genuinely novel agents outside panel similarity |
| Untargeted metagenomics (WW‑MGS) | sequence everything, classify afterwards | known, novel and unexpected, in one assay | nothing by design, though the target is a vanishing fraction of the library |

Most operational programs today run the first row. It's cheap, sensitive, and mature. However, **a targeted assay can only ever confirm a hypothesis you already had.** Every new target needs assay design plus validation, which costs time during exactly the event that motivates it.

Untargeted metagenomics is a solution to that. It means sequencing the DNA or RNA of all organisms in the sample and working out what it was afterwards, computationally, instead of deciding in advance what to look for. No primers, no probe panel, no target list.

But **untargeted is not the same as unbiased**. You still have to get nucleic acid out of a sewer and into a sequencer, and every step of that chain enriches for something. In practice untargeted wastewater work splits into two families that answer different questions:

|                     | Total nucleic acid shotgun                                                                                                                                                                                               | Viral (RNA) metagenomics                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| Wet lab             | extract total DNA, fragment randomly, sequence the lot                                                                                                                                                                   | concentrate virus-like particles, extract RNA, synthesise cDNA, ribodeplete           |
| Sees well           | bacteria, the DNA resistome, fungi, DNA viruses                                                                                                                                                                          | RNA viruses, down to very low abundance                                               |
| Sees poorly         | RNA viruses                                                                                                                                                                                                              | bacteria and the DNA resistome, removed at the bench                                  |
| Representative work | global sewage AMR surveys: 79 sites across 60 countries ([Hendriksen et al. 2019](https://www.nature.com/articles/s41467-019-08853-3)), later 101 countries ([2022](https://www.nature.com/articles/s41467-022-34312-7)) | CASPER ([Justen, Rushford et al. 2026](https://doi.org/10.64898/2026.03.05.26345726)) |
| Usual quarry        | resistome, bacterial pathogens, microbial ecology                                                                                                                                                                        | emerging and novel human-infecting viruses                                            |

Both are genuinely untargeted, but they differ in which half of the sample gets discarded before sequencing begins.

**Shotgun metagenomics** is what most of microbiology means by "metagenomics": extract total DNA, sequence, sort out what it was computationally. It's what gut microbiome research runs on, with following analysis using Kraken2 and MetaPhlAn to say who is there, HUMAnN to say what they can do, assembly and binning to pull out genomes. In wastewater it handles bacteria, community composition, bacterial pathogens, and above all the resistome, which is the oldest and the most common non-viral application.

**Viral metagenomics** keeps the no-target-list principle but changes the bench work in three ways. It physically concentrates virus-like particles first, stripping bacteria and host cells out before extraction. It selects RNA instead of DNA, which means reverse transcription to cDNA before library prep. And it ribodepletes, since ribosomal RNA would otherwise swamp everything. Then it sequences far deeper than for a bacterial study, because the quarry is rare: a vertebrate-infecting virus can sit at 10⁻⁷ or 10⁻⁸ of the material in the tube.

One thing worth clarifying. For an RNA virus, the RNA *is* the genome, so sequencing RNA virus genomes is also metagenomics. For the bacteria sitting in the same tube, that same RNA is transcripts, so for bacteria an RNA library behaves more like metatranscriptomics.

Underneath both branches the rule is the same: **what the bench discards is not recoverable downstream, however good the analysis.** The protocol settles which questions the data can answer, long before anyone opens a terminal.

### CASPER

The clearest picture of the viral branch at scale is CASPER, the Coalition for Agnostic Sequencing of Pathogens from Environmental Reservoirs:

| Dimension             | Value                                                       | Why it matters                                                                 |
| --------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Samples               | 1,206, collected Dec 2023 to Dec 2025                       | two years of continuous collection rather than a one-off survey                |
| Sites                 | 27 distinct catchments across 9 states                      | treatment plants plus hospital and airport sites                               |
| Population covered    | ~13 million people                                          | one sample stands in for an entire sewershed                                   |
| Sequencing depth      | ~1 billion read pairs per sample                            | "far deeper than most previous efforts", the price of detecting rare taxa      |
| Total data            | 1.2 trillion read pairs, 357 terabases                      | the volume any analysis layer has to survive                                   |
| Nucleic acid targeted | RNA                                                         | viral concentration and cDNA synthesis; bacteria largely excluded at the bench |
| Processing labs       | 2: University of Missouri (1,078 samples), SecureBio (128)  | both run Boston's two DITP sites, so protocols can be compared directly        |
| Share of public data  | 67% of untargeted wastewater sequencing on NCBI SRA         | most of what exists publicly is this one network                               |

**The CASPER public data release on March 2026** uses viral (RNA) metagenomics rather than total-DNA shotgun, and it is the largest untargeted wastewater sequencing effort published to date. The population figure counts each physical catchment once and excludes hospital and airport sites, which have no reliable sewershed estimate. Data are published at NCBI BioProject PRJNA1247874; an earlier 13 Tb Los Angeles pilot is at PRJNA1198001.

Results show that virus abundance trends track nationwide PCR and clinical data for SARS‑CoV‑2, influenza A and RSV, while the pathogen-agnostic approach separately caught H5N1 during the initial dairy cattle outbreaks, along with West Nile virus and measles, the things nobody had written an assay for yet.

More specifically, the University of Missouri and SecureBio process samples independently, including the same physical samples from Boston:

| Step                     | University of Missouri                                                                    | SecureBio                                                                      |
| ------------------------ | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Input                    | 24‑h composite influent, 150 mL                                                           | 24‑h composite influent, 200 mL from a 1 L sample                              |
| Free virions from solids | not performed                                                                             | Tween 20 to 0.1%, vortex, sonicate at 40 kHz                                   |
| Clarify                  | centrifuge 2,000 × g, 5 min, 4°C                                                          | centrifuge 10,000 × g, 5 min, 4°C                                              |
| Remove bacteria          | filter through 0.22 µm                                                                    | filter through 0.45 µm PES                                                     |
| Concentrate virus        | PEG precipitation: 50% PEG + 1.2 M NaCl, 1 h, then 12,000 × g for 2 h                     | InnovaPrep Concentrating Pipette Select, Ultra tip, eluted into DNA/RNA Shield |
| Extract                  | QIAamp Viral RNA Mini Kit (Qiagen), carrier RNA and DNase both omitted                    | Quick‑Viral RNA/DNA Miniprep Kit (Zymo)                                        |
| Remove DNA               | not performed                                                                             | TURBO DNA‑free Kit (Thermo Fisher)                                             |
| Remove ribosomal RNA     | not routine; RNase A/DNase pretreatment was trialled early, then dropped for not helping  | Pan‑Bacterial RiboPOOLs (siTOOLs Biotech)                                      |
| Library prep             | Illumina Stranded mRNA Prep, with the mRNA capture step deliberately omitted              | xGen RNA Library Prep Kit (IDT), unique dual indexes                           |
| Sequencing               | NovaSeq 6000, later NovaSeq X, 2×150 bp                                                   | NovaSeq X at Broad Clinical Labs, 2×150 bp                                     |
| Process control          | RT‑qPCR for PMMoV before library prep, to confirm viral concentration worked              | not performed                                                                  |

SecureBio destroys DNA enzymatically and strips bacterial rRNA with capture probes, while Missouri simply never converts DNA into a library, omitting DNase entirely and skipping Illumina's mRNA capture step so that fragmentation runs straight into cDNA synthesis. Those choices leave a measurable trace: quality filtering discarded a median of 0.5% of reads from Missouri libraries against 10.1% from SecureBio's.

Those percentages measure how many raw reads failed adapter and quality filtering, which is a property of library chemistry and insert size. They say little about how much usable signal survives. SecureBio ribodepletes and Missouri doesn't, so SecureBio discards a larger share of reads up front while spending more of what remains on non-ribosomal material. The paper shows this from the other direction: when ribodepletion probes were accidentally left out of a batch in mid‑2025, those samples came back with more ribosomal reads and *reduced effective depth* on the targets that matter. To rank the two protocols you would need to compare effective depth on vertebrate-virus reads, which is a different measurement entirely.

The PMMoV process control deserves explanation, since it uses a virus that has nothing to do with human disease. [Pepper mild mottle virus](https://pubs.acs.org/doi/full/10.1021/acsestwater.4c00866) infects chilli and bell pepper plants. It has no interest in people at all, but it survives the journey through the human gut, which makes it one of the most abundant RNA viruses in human stool and a reliable fixture of any sewer serving people who eat peppers.

That reliability is what makes it useful twice over. Across the field it serves as a fecal-strength denominator, indicating how much human waste a given sample actually contains. Here it does a narrower job: Missouri runs RT‑qPCR for PMMoV *before* committing to library prep, and a decent signal confirms that viral concentration and RNA extraction worked. A plant virus that arrives through people's diets ends up as the instrument confirming the protocol behaved, before the expensive part begins.

Downstream analysis runs through SecureBio's [Viral Metagenomics Pipeline](https://github.com/securebio/nao-mgs-workflow) (v3.0.1), implemented in [Nextflow](https://www.nextflow.io/) and executed on AWS Batch, which splits into two passes:

- **Shallow taxonomic profiling**, on about a million subsampled read pairs per index group: Seqtk to subsample, FASTP to trim and quality-filter, BBDuk to split ribosomal from non-ribosomal reads against SILVA, then **Kraken2** against the standard RefSeq database to say what's present.
- **Deep vertebrate-virus profiling**, on every read: BBDuk k‑mer screening against a masked virus database to throw out the obvious non-viral majority, FASTP and Cutadapt to clean what survives, then **Bowtie2** alignment against the vertebrate-virus genome database, keeping up to ten alignments per read for lowest-common-ancestor analysis, followed by contaminant filtering against human, cow, pig and carp genomes.

Kraken2 matches read k‑mers against a reference database and assigns taxonomy by lowest common ancestor, and is not specific to any sample type. Its standard database already contains RefSeq genomes for bacteria, archaea and viruses, alongside the human genome and vector sequences. It became identified with gut metagenomics mostly because that's where shotgun sequencing was busiest ([Ye et al. 2019](https://doi.org/10.1016/j.cell.2019.07.010) benchmarked twenty such classifiers).

The job it's given here is narrow. Kraken2 runs on a subsample and answers a census question: what fraction of this library is bacterial, archaeal, eukaryotic, viral, ribosomal, unclassifiable. The detection work happens in the deep pass, where Bowtie2 aligns against a curated vertebrate-virus database with LCA assignment and contaminant filtering. K‑mer classification against a broad database is fast but too blunt for a divergent virus sitting at 10⁻⁷, while alignment against a narrow, curated database is slower and more precise.

### What makes this an agent problem

The CASPER paper names three barriers to routine adoption:

**Cost.** Vertebrate-infecting viruses are a small fraction of the nucleic acid in wastewater, so sensitive detection needs deep and expensive sequencing.

**Volume.** "Computational infrastructure must scale to hundreds of terabases," and 357 TB is a single release, with more samples arriving every week. But this is workflow engineering, and can be solved by Nextflow, AWS Batch, parallel execution.

**Interpretation.** This is ***the agent problem***. "Interpretation of detections is challenged by the diverse sources of nucleic acids in wastewater." Deciding whether a low-abundance hit is real signal, a database artifact, index hopping, or somebody's lunch is a judgment made per detection, in context, drawing on how the sample was collected, which protocol produced the library, what the reference database does and doesn't contain, and how the organism actually behaves. 💻 🧠 📊

That judgment is the bottleneck because it doesn't scale the way the rest does. Volume scales with compute, while interpretation scales with expert attention, and the pool of people holding wet-lab protocol knowledge, bioinformatics fluency and pathogen biology *at once* is small. Surveillance is continuous, so it generates judgment calls faster than that pool can make them. The H5N1 milk signal shows what one missed call looks like.

Put plainly: **the pipeline is already fully automated, and the remaining manual work is deciding what its output means.** An agent's job would begin where the Nextflow run ends.

That is also the task agents are currently worst at. ABC‑Bench found that agents did well on work drawing on published knowledge and documented protocols, and **more weakly on the task requiring novel bioinformatics reasoning** ([Liu et al. 2026](https://arxiv.org/abs/2606.11150)). BioSecBench‑Surveillance found the same shape at scale: agents almost always reached for the right tool, then undercut themselves on the choices around it, such as which reference, which threshold, which filter, which normalization. Agents can run the pipeline. The judgment afterwards is where they fumble, and that judgment is the reason to point them at this work in the first place. For anyone building a benchmark rather than running surveillance, one more feature matters: this task has **verifiable ground truth**, since you can know what was in the sample, while still demanding open-ended reasoning to reach it. That combination is rare, and it's what makes genomic surveillance a good testbed as well as an important application.
