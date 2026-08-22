---
title: AI coding agents in bioinformatics in 2026
date: 2026-08-20
---

## Can AI replace a bioinformatician?

Not yet, and “replace” is probably the wrong question.

I have to admit that I now rely heavily on AI. It acts as my coding partner and an interactive source of suggestions, accelerating many parts of my work: exploring files, writing and debugging code, invoking command-line tools, producing figures, and drafting interpretations.

But the biological question, analytical direction, reference databases, and final judgment still depend on me. Sometimes the agent pursues an unimportant detail too far, overlooks a statistical signal, or loses sight of the main question even when I provide a reference paper. It can produce a technically plausible analysis that answers the wrong question. I therefore have to question its analysis and ask it to correct its work, and sometimes that takes longer than doing the analysis myself.

This raises questions that many bioinformaticians now share: How accurate are AI coding agents on real analyses? Where do they fail? Can better tools, instructions, and validation make them more capable?

Several groups have begun to measure this with execution-based benchmarks rather than biology trivia or isolated coding questions:

| Benchmark                                                                        | Year | Group                                                                                                   | What it tests                                                                                     | Main result                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------- | ---: | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [BixBench](https://arxiv.org/abs/2503.00096)                                     | 2025 | [FutureHouse](https://www.futurehouse.org/) and [ScienceMachine](https://sciencemachine.ai/)            | 61 real-world analysis scenarios and 205 open-answer questions in a notebook environment          | The best tested agent reached **21% open-answer accuracy**; interpreting a completed analysis remained difficult.                                                                                                           |
| [BioAgent Bench](https://arxiv.org/abs/2601.21800)                               | 2026 | [Entropic](https://www.entropic.ltd/) and the University of Zagreb's [TakeLab](https://takelab.fer.hr/) | Ten end-to-end tasks, including RNA-seq, variant calling, and metagenomics, plus robustness tests | Frontier agents often completed the normal tasks, but performance and outputs degraded with corrupted inputs, decoy files, and irrelevant prompt text.                                                                      |
| [BioSecBench-Surveillance](https://github.com/latchbio/biosecbench-surveillance) | 2026 | [LatchBio](https://latch.bio/)                                                                          | 100 pathogen-genomics surveillance evaluations across seven task categories                       | The repository reports mean **pass rates from 14% to 50%** across 16 model–harness configurations; it attributes many errors to choices of references, thresholds, and normalization even when the correct tools were used. |

These scores should not be compared directly: the benchmarks use different tasks, models, agent harnesses, graders, and definitions of success. Together, they show different parts of the same problem: answer accuracy, workflow completion, and robustness are not equivalent.

![[bioinformatics-visual-selection.png]]

## A complete output is not necessarily trustworthy: BioAgent Bench

The metagenomics task in [BioAgent Bench](https://arxiv.org/html/2601.21800) is an example from my own research field. The agent received sequencing data from the Cuatro Ciénegas Basin for a control sample (`JC1A`) and a nutrient-enriched sample (`JP4D`). It had to classify bacterial taxa, estimate their relative abundances, and return a CSV containing each reported OTU, its kingdom and phylum, and its abundance in the two samples.

In plain language, the researchers **deliberately made the task messy and misleading to see whether the agent would notice**. They damaged the sequencing reads, planted the wrong type of reference database, and padded the prompt with distracting information. Their aim was to test whether producing the requested CSV actually meant that the underlying analysis was reliable.

They first ran the same GPT-5.2/Codex CLI configuration four times and compared the outputs, using Jaccard overlap for the reported phyla and Pearson correlation for abundance estimates shared across all runs. The phylum lists had a Jaccard overlap of 0.395, while the shared abundance estimates had a Pearson correlation of 0.746. They then stress-tested the agent. It recognized that reads with approximately 90% of bases replaced by `N` and all quality scores set to Phred 0 were corrupted, but still tried to continue. It also selected a decoy Kraken viral database instead of the bacterial database required for the task. Adding 871 words of irrelevant background reduced task completion by 100 percentage points.

The result is straightforward: the agent could follow the broad workflow and generate the requested CSV, but it did not reliably determine which taxa were present or whether the input data and reference database were appropriate. The taxonomic calls—and any biological conclusions based on them—therefore still required expert validation. **A completed output file alone was not evidence of a trustworthy analysis.**

## The chosen tools and settings can still be wrong: BioSecBench-Surveillance

[BioSecBench-Surveillance](https://github.com/latchbio/biosecbench-surveillance) uses shotgun metagenomic data differently: it grades a specific surveillance decision. Instead of stopping after classifying taxa and comparing their relative abundances, BioSecBench asks the agent to derive decision-relevant measurements from the sequencing reads, for example, the total antimicrobial-resistance burden or the number of viral lineage-defining sites with sufficient coverage. Thus, the final question is not simply **"Which organisms are present?"** but **"What surveillance conclusion does the sequencing evidence support?"**

The public examples specify the required calculations, although they do not prescribe which tools the agent must use. For the antimicrobial-resistance task, the agent must:

1. Analyze Illumina paired-end shotgun reads from U.S. municipal wastewater.
2. Detect antimicrobial-resistance genes (ARGs).
3. Calculate each detected ARG's abundance relative to the bacterial marker gene `rpoB`.
4. Sum those normalized abundances to obtain the total ARG burden, expressed as ARG copies per `rpoB` copy.
5. Return the result as `{"total_arg_rpob_burden": float}`.

The difficult part is that the agent must make the analytical choices itself. It needs a resistance reference database and a compatible method for detection and abundance estimation. CARD/RGI, AMRFinderPlus, and ResFinder illustrate different tool and database ecosystems, but they are not interchangeable, and some workflows require assembly or a separate quantification step. The agent must also choose identity and coverage thresholds, handle reads that map to multiple genes, quantify `rpoB`, and apply the normalization correctly. These are possible analytical choices, not tools confirmed to have been used in BioSecBench. A deterministic grader checks the final number, but the public release discloses only that it uses a numeric tolerance—not the precise tolerance rule or allowed range. The reads, ground truth, solution notes, grader, and agent trajectories are also withheld.

Together, these benchmarks show a consistent gap: current agents can perform substantial analytical work, but successful execution is not the same as sound scientific judgment. BixBench reported low open-answer accuracy, BioAgent Bench reported high completion but weak robustness, and the BioSecBench repository reports configuration-level pass rates no higher than about 50%. Their near-term role is therefore **copilot or junior analyst under review**, not autonomous scientific authority.

**The agent can do more of the mechanical work, but a domain expert still owns the question, validation, and conclusion.**

## What using an LLM agent in bioinformatics looks like today

Bioinformaticians can use coding agents such as Codex to inspect files, write and run Bash, R, or Python code, call installed tools, read errors and intermediate results, revise an analysis, and generate figures or reports. The [Codex panel in VS Code](https://developers.openai.com/codex/ide) is a convenient starting point: it can use files and selected text already open in the editor, edit the project, and run commands in its workspace. Start with a small, checkable task, such as “inspect these FASTQ files and write a FastQC Slurm job.” Review the proposed commands, run the job, and inspect the outputs before expanding to all samples.

On an HPC system such as the [Digital Research Alliance of Canada](https://alliancecan.ca/), keep the roles separate: the agent prepares and reviews code, while Slurm runs expensive jobs. Work locally or in an approved remote environment, put scripts under version control, and submit them through the scheduler.

Codex also offers features for larger or repeated tasks. A [Goal](https://developers.openai.com/codex/use-cases) gives the agent a durable objective for long-running work, such as porting a pipeline and testing it on a small dataset. It does not replace Slurm or keep a cluster job running. A [skill](https://developers.openai.com/codex/skills) stores a repeatable procedure, including its inputs, commands, checks, and expected outputs. With **Record & Replay**, you can demonstrate a workflow and let Codex draft a skill from it. Record a procedure only after it has been validated: recording a flawed analysis makes it repeatable, not correct. In the IDE or CLI, use `/skills` or `$` to select a skill explicitly; Codex can also choose one from the task description.

[MCP](https://developers.openai.com/codex/mcp) serves a different purpose: it connects the agent to an external tool or source, such as a literature service, sample database, or laboratory system. Use it only when that connection is needed; normal file editing and shell commands do not require MCP.

For efficient and reproducible bioinformatics work, also give the agent clear project rules and evidence requirements:

- Put accepted inputs, directory layout, standard commands, reference-database versions, cluster rules, and “never edit raw data” in `AGENTS.md`.
- Pin software and references with a container, Conda environment, lockfile, or module versions; record random seeds where relevant.
- Test first on a small dataset with known expectations, then scale up.
- Keep commands, logs, checksums, parameters, software versions, and output summaries.
- Use Git and review the diff. Require human review for sample inclusion, reference choice, thresholds, biological interpretation, and any destructive or expensive action.

The efficient pattern is simple: **give the agent a bounded task, make it show its work, validate on a small case, and let a workflow engine and scheduler handle repeatable computation at scale.**

## The emerging bioinformatics-agent ecosystem

| Layer                | Examples                                                                                                                              | Role                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Model                | GPT, Claude, Gemini, or an open-weight model                                                                                          | Generates plans, code, and interpretations                                          |
| Coding-agent harness | Codex, [Claude Code](https://code.claude.com/docs/en/features-overview), or [Gemini CLI](https://google-gemini.github.io/gemini-cli/) | Gives the model access to files, a terminal, tools, and an iterative execution loop |
| Project instructions | `AGENTS.md`, `CLAUDE.md`, or an equivalent project file                                                                               | Supplies persistent rules, commands, and constraints                                |
| Skill                | A validated single-cell QC or variant-calling procedure                                                                               | Packages reusable instructions, checks, and optional scripts                        |
| Tool                 | FastQC, samtools, minimap2, R, or Python                                                                                              | Performs the actual computation                                                     |
| MCP connection       | A literature service, sample database, or laboratory system                                                                           | Gives the agent controlled access to an external tool or data source                |
| Workflow engine      | Nextflow or Snakemake                                                                                                                 | Executes an established workflow consistently and at scale                          |
| Biomedical agent     | Biomni, BioMedAgent, or BioMaster                                                                                                     | Adds domain-specific planning, retrieval, and tool orchestration                    |

For those biomedical agents, there is also no single meaningful “Biomni accuracy.” In its published evaluation, [Biomni](https://doi.org/10.1126/science.adz4351) reported 74.4% accuracy on a selected LAB-Bench database-question subset and 81.9% on a sequence-question subset, but only 17.3% on 52 biomedical questions from Humanity's Last Exam. The LAB-Bench evaluation used a representative 12.5% subset of the full benchmark, so these numbers describe those test sets rather than all biomedical research. [BioMedAgent](https://doi.org/10.1038/s41551-026-01634-6) reported a 77% success rate on its authors' 327-task BioMed-AQA benchmark. [BioMaster](https://doi.org/10.1016/j.patter.2026.101611) completed 47 of 49 benchmark workflows across 102 tools, but workflow completion does not prove that every biological result or interpretation was correct. Because the tasks, metrics, models, and agent environments differ, these percentages cannot be compared as a ranking. The practical conclusion is to use specialized agents for better tool access and workflow organization, not as a substitute for independent QC, statistical review, and biological judgment.

## AI agents are not replacements for Nextflow or Snakemake

[Nextflow](https://nextflow.io/docs/latest/index.html) and [Snakemake](https://snakemake.readthedocs.io/en/stable/) are workflow engines: they encode a known computation as a dependency graph, track inputs and outputs, manage software environments, parallelize work, resume failed runs, and move the same pipeline between a laptop, HPC cluster, and cloud. An agent is a reasoning and interaction layer; it does not automatically provide the determinism, provenance, scheduling, or reproducibility of a workflow engine.

|                   | AI coding agent                                               | Nextflow / Snakemake                                            |
| ----------------- | ------------------------------------------------------------- | --------------------------------------------------------------- |
| Best at           | Open-ended choice, code generation, debugging, interpretation | Repeatable execution of an established workflow                 |
| Behavior          | Adaptive and probabilistic                                    | Defined by workflow code, configuration, tools, and inputs      |
| Scale             | Delegates jobs but is not itself a scheduler                  | Built for local, HPC, cluster, and cloud execution              |
| Reproducibility   | Must be engineered with logs, pinned tools, and tests         | First-class environments, dependency tracking, and run metadata |
| Main failure mode | Plausible but scientifically wrong decisions                  | A reproducibly wrong or outdated pipeline                       |

The useful architecture is **agent on top, workflow engine underneath**. Ask the agent to select or configure a reviewed pipeline, inspect QC, and explain exceptions; let Nextflow or Snakemake execute the computational graph. For production work, prefer a versioned community workflow such as [nf-core](https://nf-co.re/docs/guidelines/pipelines/overview), whose conventions include templates, containers, testing, and code review, over a fresh pipeline generated from scratch in every conversation. A skill can bridge the two layers by teaching the agent when and how to invoke that workflow, what parameters are safe to change, and which outputs require human review.

## Conclusion

Bioinformatics is clearly moving from asking AI for isolated code snippets to working with agents that can inspect data, run tools, and follow an analysis across many steps. That shift can remove repetitive work and leave researchers more time to think about the biological question. But the benchmarks above show the catch: an agent can finish a pipeline and still choose the wrong reference, threshold, or interpretation.

For now, the most promising future is not AI replacing bioinformaticians, but **bioinformaticians learning how to direct, constrain, and check increasingly capable agents**.
