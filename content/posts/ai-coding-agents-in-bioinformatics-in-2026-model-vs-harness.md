---
title: "AI coding agents in bioinformatics in 2026: harness"
date: 2026-08-24
---

I've been running a local benchmark pilot test these past few days, and it's got me thinking about the [[posts/ai-coding-agents-in-bioinformatics-in-2026|previous post]] in a different way.

The last post was more of an intro, discussing the common fear that AI will replace bioinformaticians, and using two papers to show why we can't be replaced (maybe it will be just a matter of time though) along with the current limitations of these AI coding agents.

A benchmark study shows AI coding agents have drawbacks in different ways and reminds us to pay attention to those common errors and think about how to improve them. But there's more to look at in these benchmark studies, since the benchmark itself can also be imperfect or biased, and that's fine, nothing is, or should be, perfect. That imperfection still contributes valuable knowledge to the AI-for-science community, and the room for improvement in those methods and studies is even more interesting.

Reading three of these benchmark papers back to back, one thing kept surfacing that I hadn't paid attention to before, and it's what this post is actually about: **when we say "this model scored X%", we're quietly reporting the score of two things at once.** There's the model, and there's the software wrapper it runs inside — the harness. Swap the wrapper, keep everything else identical, and the number moves. Sometimes it moves more than switching to a whole new model generation does.

So this post walks through it in that order: the models, then the harnesses, then what happens when we cross the two.

## The three papers

| Benchmark | Year | Group | Models | Harness(es) | Test size |
| --- | --- | --- | --- | --- | --- |
| BixBench | 2025 | [FutureHouse](https://www.futurehouse.org/) and [ScienceMachine](https://sciencemachine.ai/) | GPT‑4o, Claude 3.5 Sonnet | custom Aviary framework | 61 analytical scenarios (capsules), 205 open‑answer questions |
| BioAgent Bench | 2026 | [Entropic](https://www.entropic.ltd/) and the University of Zagreb's [TakeLab](https://takelab.fer.hr/) | Claude Opus 4.5, Claude Sonnet 4.5, GPT‑5.2, Gemini 3 Pro, GLM‑4.7, Kimi K2 Thinking, MiniMax M2.1, Qwen3 Coder, Devstral 2512 | Codex‑CLI / Claude‑Code / OpenCode | 10 manually‑curated end‑to‑end bioinformatics pipeline tasks |
| BioSecBench‑Surveillance | 2026 | [LatchBio](https://latch.bio/) | Claude Opus 4.8/4.7/4.6, Claude Sonnet 4.6, GPT‑5.5/5.4, Gemini 3.5 Flash/3.1 Pro, Grok 4.3/4.20 | PI / Codex‑CLI / Claude‑Code | 100 evaluations, 7 pathogen genomic‑surveillance task categories |

They also don't score the same thing:

| Benchmark                | What it actually asks                                                     | Metric                 | Graded by                    |
| ------------------------ | --------------------------------------------------------------------------- | ---------------------- | ---------------------------- |
| BixBench                 | did the final answer match the ground truth?                              | accuracy (%)           | LLM judge                    |
| BioAgent Bench           | how many required pipeline steps got done, and did the final file appear? | completion rate (%)    | LLM judge (GPT‑5.1)          |
| BioSecBench‑Surveillance | did the structured JSON answer survive typed field checks?                | endpoint pass rate (%) | deterministic grader, no LLM |

A 92% on BioAgent Bench and a 45% on BioSecBench‑Surveillance don't mean one model is twice as good, as one is to see if the task is done and the other to see how much answers were correct.

## Axis 1: the models

All three papers used multiple models, and no two of them share a single model in common.

Ranked by release date, the Claude versions that show up across the three papers go Opus 4.8 > Opus 4.7 > Sonnet 4.6 > Opus 4.6 > Sonnet 4.5 > Claude 3.5 Sonnet. BixBench only tested 1 Claude model (3.5 Sonnet), BioAgent Bench tested 2 (Opus 4.5 and Sonnet 4.5), and BioSecBench‑Surveillance tested 4 (Opus 4.8, 4.7, 4.6, and Sonnet 4.6). Same story for the other model families.

To better visualize which models overlap across benchmarks (spoiler: none do), I made another table including model name, release date, org, model type (open‑source weights vs. closed‑source API), and which benchmark evaluated it.

| Models              | Release Date | Org         | Country | Model type             | Evaluated in Benchmark   |
| ------------------- | ------------ | ----------- | ------- | ---------------------- | ------------------------ |
| Claude Opus 4.8     | May 28, 2026 | Anthropic   | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| Claude Opus 4.7     | Apr 16, 2026 | Anthropic   | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| Claude Sonnet 4.6   | Feb 17, 2026 | Anthropic   | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| Claude Opus 4.6     | Feb 05, 2026 | Anthropic   | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| Claude Opus 4.5     | Nov 24, 2025 | Anthropic   | US      | Proprietary (API‑only) | BioAgent Bench           |
| Claude Sonnet 4.5   | Sep 29, 2025 | Anthropic   | US      | Proprietary (API‑only) | BioAgent Bench           |
| Claude 3.5 Sonnet   | Oct 22, 2025 | Anthropic   | US      | Proprietary (API‑only) | BixBench                 |
| GPT‑5.5             | Apr 23, 2026 | OpenAI      | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| GPT‑5.4             | Mar 18, 2026 | OpenAI      | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| GPT‑5.2             | Dec 08, 2025 | OpenAI      | US      | Proprietary (API‑only) | BioAgent Bench           |
| GPT‑4o              | May 13, 2025 | OpenAI      | US      | Proprietary (API‑only) | BixBench                 |
| Gemini 3.5 Flash    | May 19, 2026 | Google      | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| Gemini 3.1 Pro      | Feb 19, 2026 | Google      | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| Gemini 3 Pro        | Feb 12, 2026 | Google      | US      | Proprietary (API‑only) | BioAgent Bench           |
| Grok 4.3            | Jun 11, 2026 | xAI         | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| Grok 4.20 Reasoning | May 27, 2026 | xAI         | US      | Proprietary (API‑only) | BioSecBench‑Surveillance |
| GLM‑4.7             | Dec 22, 2025 | Zhipu AI    | China   | Open‑weight            | BioAgent Bench           |
| Qwen3 Coder         | Oct 10, 2025 | Alibaba     | China   | Open‑weight            | BioAgent Bench           |
| MiniMax M2.1        | Sep 05, 2025 | MiniMax     | China   | Open‑weight            | BioAgent Bench           |
| Kimi K2 Thinking    | Jul 15, 2025 | Moonshot AI | China   | Open‑weight            | BioAgent Bench           |
| Devstral‑2512       | Dec 12, 2025 | Mistral AI  | France  | Open‑weight            | BioAgent Bench           |

Both published in 2026, BioSecBench‑Surveillance leaned on noticeably newer models. Most of its lineup released between February and June 2026, versus BioAgent Bench's mostly mid-to-late-2025 vintage (Gemini 3 Pro, from February 2026, is the one exception).

BioSecBench‑Surveillance picked a narrower set of companies, all US-based: Anthropic, OpenAI, Google, and xAI. BioAgent Bench cast a wider net, alongside Claude, GPT, and Gemini, it included four Chinese open-weight models (GLM‑4.7 from Zhipu AI, Kimi K2 Thinking from Moonshot AI, MiniMax M2.1, and Qwen3 Coder from Alibaba) plus one French one (Devstral‑2512 from Mistral AI).

### What the model axis alone looks like

If we only ever looked at models, here's roughly the picture:

**BioAgent Bench**. The paper's overall model ranking, on end-to-end pipeline completion.

| Rank | Model             | Completion rate | Model type  |
| ---- | ----------------- | --------------- | ----------- |
| 1    | Claude Opus 4.5   | 100.0%          | closed      |
| 2    | Gemini 3 Pro      | 96.6%           | closed      |
| 3    | GPT‑5.2           | 92.5%           | closed      |
| 4    | Claude Sonnet 4.5 | 92.5%           | closed      |
| 5    | GLM‑4.7           | 82.5%           | open‑weight |
| 6    | GPT‑5.1‑Codex‑Max | 81.7%           | closed      |
| 7    | Kimi K2 Thinking  | 80.5%           | open‑weight |
| 8    | MiniMax M2.1      | 73.6%           | open‑weight |
| 9    | Qwen3 Coder       | 68.8%           | open‑weight |
| 10   | Devstral 2512     | 67.9%           | open‑weight |

Every closed model clears 90%, every open-weight model sits below 83%. Though the ordering has a wrinkle I like: GLM‑4.7 (82.5%) edges out GPT‑5.1‑Codex‑Max (81.7%), so the best open-weight model beats a closed, coding-tuned OpenAI model. The real split should be "frontier vs everything else", not "closed vs open".

Two findings from that paper matter more to me than the ranking:

- **Planning quality only partly explains completion.** Plan ratings correlate with completion at Pearson r = 0.61 — real, but far from deterministic. Some open-weight models write visibly worse plans and still finish.
- **Completion ≠ correctness.** Under deliberate perturbation, GPT‑5.2 flagged corrupted inputs in 7/10 tasks but still swallowed decoy files in 2/10, and padding the prompt with irrelevant background text cut completion by 28 points.

✍️ Note: ***A pipeline that runs to the end is not a pipeline you'd trust.***

**BixBench**. The agent gets an empty Jupyter notebook, a raw dataset, and a research question, then has to write and run its own analysis code:

| Evaluation mode | Claude 3.5 Sonnet | GPT‑4o | What it tells us |
| --- | --- | --- | --- |
| Open-answer | **21%** | **15%** | the real task; no-notebook baseline ≈ 0% |
| MCQ, refusal allowed | ~25% | ~20% | both barely above random |
| MCQ, no refusal option | ~40% | ~33% | both clear random once forced to commit |

MCQ here just means the same question re-served as multiple choice, with the agent's own notebook attached — an easier format, and not one a real bioinformatician ever gets, but the paper includes it as a diagnostic. Claude 3.5 Sonnet beats GPT‑4o in every row; the more interesting comparison runs down the column. Open-answer --> MCQ roughly doubles both scores, and adding a refusal option ("insufficient information") drags them back to near-random. When the models are allowed to opt out, they opt out a lot, which reads to me as a calibration problem more than a knowledge problem.

The models here are from 2025 and no longer frontier, so 21% is only a floor.

The questions here *are* precisely specified, with exact ground truths ("what is the lower bound of the 95% CI for peak swarming area?"). What's unspecified is the *method* — no prescribed pipeline, tool, or parameters. So it's more like a precise exam question with no lecture notes, free choice of statistical approach, and only the final number marked. A defensible analysis with different normalization scores zero. That's a benchmark design choice.

**BioSecBench‑Surveillance**. Each of the 100 evaluations freezes a real pathogen-surveillance workflow at the moment of a decision, hands the agent only what a human analyst would have, and grades the structured answer deterministically. Difficulty tracks the task, not the model:

| Task category | Pass rate | n |
| --- | --- | --- |
| Source tracking | 50% | 12 |
| Taxonomic classification | 46% | 16 |
| AMR characterization | 42% | 15 |
| Variant detection | 42% | 23 |
| Toxin & virulence characterization | 39% | 12 |
| Genetic-engineering characterization | 35% | 12 |
| Anomaly detection | 20% | 10 |

Read length mattered, as long-read datasets (26%) were much harder than short-read (41%) , while sample type barely moved the needle (clinical 45%, isolate 44%, wastewater 37%).

Agents almost always reached for the *right* tool, calling validated aligners and classifiers instead of reinventing them, then undercut themselves on the choices around the tool: which reference, which threshold, which filter, which normalization. On anomaly detection they were systematically too conservative, dismissing a low-abundance but high-consequence organism as environmental background. That's judgment of chosen models.

## Axis 2: the harnesses

A harness (or agent scaffold) is **the software layer wrapped around the model**. It handles ***tool-calling, the multi-step agent loop, context compression, sandboxed execution, and trajectory logging***. The model decides what to do; the harness determines what it can see, touch, retry, and how much of its own history it still remembers by step 40.

✍️ Note: **The harness is a separate product from the model, built by a separate team, and often by a different company entirely.**

| Harness                                                                               | Built by                            | Vendor-aligned?                  | Used in                                  |
| ------------------------------------------------------------------------------------- | ------------------------------------ | --------------------------------- | ----------------------------------------- |
| [Claude Code](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Anthropic                           | yes — Anthropic's own            | BioAgent Bench, BioSecBench‑Surveillance |
| [Codex‑CLI](https://developers.openai.com/blog/codex-as-a-platform)                   | OpenAI                              | yes — OpenAI's own               | BioAgent Bench, BioSecBench‑Surveillance |
| [OpenCode](https://github.com/anomalyco/opencode)                                     | AnomalyInnovations                  | no — independent, model-agnostic | BioAgent Bench                           |
| [PI (Pi Agent)](https://github.com/earendil-works/pi)                                 | Earendil Works                      | no — independent, model-agnostic | BioSecBench‑Surveillance                 |
| Aviary                                                                                | FutureHouse (the benchmark authors) | no — research scaffold           | BixBench                                 |

Two of these are vendor harnesses: Anthropic built Claude Code, OpenAI built Codex‑CLI. Three are vendor-neutral, written by people who don't sell a model.

This means every evaluation makes a pairing choice, and the pairing can be **native** (Anthropic model in Anthropic's harness) or **foreign** (Anthropic model in OpenAI's harness, or in a neutral one). Nothing stops you doing either. Both 2026 papers do both.

## Model × harness = agent

Both papers converge on the same definition, and it's the one sentence I'd keep from all three: **an agent is model + harness** ([BioAgent Bench, arXiv:2601.21800](https://arxiv.org/abs/2601.21800)).

✍️ Note: **Treating the model alone as "the agent" is a category error. The model on its own can't open a file.**

BioSecBench‑Surveillance is explicit that it treats the two as independent axes, on the grounds that the same model behaves very differently across harnesses in both capability and refusal, thus, 10 models BioSecBench-Surveillance used became **16 model–harness configurations**:

| Model | Claude Code | PI | Codex |
| --- | --- | --- | --- |
| Claude Opus 4.8 | ✅ | ✅ | – |
| Claude Opus 4.7 | ✅ | ✅ | – |
| Claude Opus 4.6 | ✅ | ✅ | – |
| Claude Sonnet 4.6 | ✅ | ✅ | – |
| GPT‑5.5 | – | ✅ | ✅ |
| GPT‑5.4 | – | ✅ | ✅ |
| Gemini 3.5 Flash | – | ✅ | – |
| Gemini 3.1 Pro | – | ✅ | – |
| Grok 4.3 | – | ✅ | – |
| Grok 4.20 Reasoning | – | ✅ | – |

As summarized in the table, Anthropic models get their native harness plus a neutral one. OpenAI models get their native harness plus the same neutral one. Google and xAI models only get the neutral one, as no vendor harness exists for them in this study. PI is the common denominator, which is exactly what makes cross-vendor comparison possible at all.

Once you accept model and harness as two axes, there are four different comparisons you can make, and they answer four different questions.

| Cut | What's held fixed | What varies              | Question it answers               |
| --- | ----------------- | ------------------------- | ---------------------------------- |
| 1   | model             | harness                  | how much does the wrapper matter? |
| 2   | harness           | model                    | which model is actually better?   |
| 3   | model             | native vs foreign vendor | does matching brands help?        |
| 4   | harness           | model generation         | is the newer model an upgrade?    |

## Cut 1 — same model, different harness

BioAgent Bench ran its models across up to three harnesses. Completion rates:

| Model             | Codex‑CLI | Claude‑Code | OpenCode | Best      |
| ----------------- | --------- | ----------- | -------- | --------- |
| Claude Opus 4.5   | 100.0%    | 96.0%       | 93.3%    | Codex‑CLI |
| Gemini 3 Pro      | 96.6%     | –           | 68.0%    | Codex‑CLI |
| GPT‑5.2           | 92.5%     | –           | 87.5%    | Codex‑CLI |
| Claude Sonnet 4.5 | 92.5%     | 90.0%       | 83.3%    | Codex‑CLI |
| GLM‑4.7           | 82.5%     | –           | 75.0%    | Codex‑CLI |
| Kimi K2 Thinking  | 65.7%     | –           | 80.5%    | OpenCode  |
| Devstral 2512     | 47.9%     | –           | 65.0%    | OpenCode  |
| MiniMax M2.1      | 12.5%     | –           | 73.6%    | OpenCode  |
| Qwen3 Coder       | 0.0%      | –           | 62.9%    | OpenCode  |

Sorted by how far the same weights travel:

| Model           | Worst harness     | Best harness       | Swing     |
| --------------- | ------------------ | -------------------- | --------- |
| Qwen3 Coder     | 0.0% (Codex‑CLI)  | 62.9% (OpenCode)   | **+62.9** |
| MiniMax M2.1    | 12.5% (Codex‑CLI) | 73.6% (OpenCode)   | **+61.1** |
| Gemini 3 Pro    | 68.0% (OpenCode)  | 96.6% (Codex‑CLI)  | +28.6     |
| Devstral 2512   | 47.9% (Codex‑CLI) | 65.0% (OpenCode)   | +17.1     |
| Claude Opus 4.5 | 93.3% (OpenCode)  | 100.0% (Codex‑CLI) | +6.7      |

Qwen3 Coder scores a literal zero under one harness and a respectable 62.9% under another. Same weights, same ten tasks, same prompts. If you'd only run the Codex‑CLI column you'd have written that model off entirely, and reported it as a fact about the model.

Robustness to harness turns out to be its own model property, and nobody reports it. Claude Opus 4.5 spans ~7 points across all three harnesses; Qwen3 Coder spans 63. That difference tells us something real about deployment risk, and it's invisible in any single-number leaderboard.

## Cut 2 — same harness, different models

This is the comparison a benchmark *should* be making, and it's why PI matters so much in BioSecBench‑Surveillance: it's the one harness nearly every model ran under.

| Model (all on PI)   | Pass rate |
| ------------------- | --------- |
| **Opus 4.8**            | **50.2%**     |
| **Opus 4.7**            | **49.6%**     |
| **Sonnet 4.6**          | **48.6%**     |
| Gemini 3.5 Flash    | 47%       |
| Opus 4.6            | 46%       |
| Gemini 3.1 Pro      | 45%       |
| GPT‑5.5             | 45%       |
| GPT‑5.4             | 38%       |
| Grok 4.3            | 16%       |
| Grok 4.20 Reasoning | 14%       |

Across all 16 configurations and 3,962 gradable attempts, pass rates run 14% to 50%, averaging 41%. The best agent anyone fielded gets about half of these right. And the two xAI configurations are the only ones that clearly separate from the pack at the bottom; everyone else lives between 38% and 50%.

## Cut 3 — same company, or not?

This is the cut I found genuinely surprising, and it's only visible because both papers ran models in foreign harnesses.

**OpenAI models prefer OpenAI's harness.** Every time:

| Model | Native (Codex‑CLI) | Foreign | Native advantage |
| --- | --- | --- | --- |
| GPT‑5.5 | 50.2% | 45% (PI) | +5.2 |
| GPT‑5.4 | 41% | 38% (PI) | +3 |
| GPT‑5.2 | 92.5% | 87.5% (OpenCode) | +5 |

**Anthropic models mostly prefer somebody else's.** Five times out of six:

| Model             | Native (Claude Code) | Foreign                | Native advantage |
| ----------------- | ---------------------- | ------------------------- | ------------------ |
| Claude Opus 4.8   | 39%                    | **50.2%** (PI)         | **−11.2**         |
| Claude Opus 4.7   | 44%                    | 49.6% (PI)             | −5.6              |
| Claude Sonnet 4.6 | 44%                    | 48.6% (PI)             | −4.6              |
| Claude Opus 4.5   | 96.0%                  | **100.0%** (Codex‑CLI) | −4.0              |
| Claude Sonnet 4.5 | 90.0%                  | 92.5% (Codex‑CLI)      | −2.5              |
| Claude Opus 4.6   | 47%                    | 46% (PI)               | +1.0              |

Five of six Anthropic pairings did better outside Anthropic's own harness, including two where the Claude model scored higher inside *OpenAI's* harness than inside Claude Code. Three of three OpenAI pairings did better inside OpenAI's.

I want to be careful about what this does and doesn't mean. It is not "Claude Code is a bad harness." The most plausible reading is that Claude Code is built for interactive software engineering, including a human in the loop, iterative edits, a repo, while these benchmarks are headless, long-running, batch bioinformatics jobs. PI and Codex‑CLI are leaner and more execution-oriented, which is closer to the task shape here. A harness is optimized for a workload, and this workload isn't Claude Code's home turf.

There's also a matching effect running the other direction, from the model side. On that *same* Codex‑CLI harness, OpenAI's own family climbs:

| Model on Codex‑CLI | Completion |
| --- | --- |
| `gpt‑5‑1` (base) | 38.5% |
| `gpt‑5‑1‑codex` | 74.7% |
| `gpt‑5‑1‑codex‑max` | 81.7% |

A 43-point climb from tuning the model *for* the harness. Models and harnesses get co-designed, and a model evaluated outside the scaffold it was tuned for will look worse than it is. Which cuts both ways: it's a reason to be suspicious of any leaderboard that runs everything in one vendor's harness, and a reason to be suspicious of "vendor-neutral" leaderboards too, since neutral isn't the same as equally-favourable.

## Cut 4 — same harness, newer model

Fix the harness, walk up a model family, and you'd expect a clean upward trend. On PI, you get one. On Claude Code, it reverses:

| Model     | on PI                          | on Claude Code               |
| --------- | ------------------------------- | ------------------------------- |
| Opus 4.6  | 46%                             | 47%                             |
| Opus 4.7  | 49.6%                           | 44%                             |
| Opus 4.8  | 50.2%                           | 39%                             |
| **Trend** | **46 --> 50.2, improving ✅** | **47 --> 39, declining ❌** |

Same three models, same 100 tasks, opposite answers to "is the newer model better?"

I'd resist over-reading a single benchmark, and the confidence intervals in that paper are wide (Opus 4.8/PI is 50.2% with a 95% CI of 40.1–60.3). But the direction of the effect is hard to explain away, and the size comparison is the part that stuck with me: two full model generations bought about 4 points on a fixed harness, while switching harness moved a single model 11.

## Why the harness moves the number this much

None of the papers fully answers this, but between them we can see the mechanism.

The harness controls:

- **What the model can see.** File listings, directory trees, tool output formatting, how errors get surfaced. A harness that truncates a stack trace hides the information needed to recover from it.
- **How much it still remembers.** Context compression policy over a 40-step, six-hour run determines whether step 38 still knows what step 4 decided.
- **How many attempts it gets.** Retry logic, error handling, whether a failed subprocess kills the run or gets caught.
- **What it's allowed to do.** Sandbox permissions, internet access, which tools are even registered. BioSecBench‑Surveillance gave every run 6 CPU cores, 34 GiB RAM, a 512 GiB disk, a six-hour wall clock, and internet access — generous, and identical across configurations, which is what makes its harness comparison fair.
- **Whether it declines.** Refusal behaviour is shaped by the harness's system prompt and turn structure, not only the model's training. Which turns out to matter more than I'd have guessed.

BioAgent Bench's failure-mode notes line up with this: the models that collapsed under a bad harness didn't fail on biology, they got stuck in repeated error-correction loops or terminated early. That's a loop-and-recovery problem, which is squarely the harness's job.

## A wrinkle in the metric: refusals

One more harness effect, and it bends the scoreboard itself.

BioSecBench‑Surveillance scores every run as **correct, incorrect, or refused**, and pass rate is correct ÷ (correct + incorrect) — refusals are dropped from the denominator entirely. Refusal rates vary enormously, and mostly by harness rather than by model:

| Provider | Refusal rate | Note |
| --- | --- | --- |
| OpenAI under PI | 27–29% | same models, same tasks |
| OpenAI under Codex | 8–9% | |
| Anthropic | 18–31% | varies by configuration |
| Google | 7–15% | |
| xAI | 0% | never refused |

GPT‑5.5 declining ~28% of tasks under PI and ~8% under Codex is a threefold swing driven by the scaffold, not the weights.

The paper is admirably upfront that this is a hole in its own metric: because refused tasks vanish from the denominator, a model could inflate its pass rate by declining exactly the tasks it would have failed. They checked, and none of the frontier models showed that pattern — but the vulnerability is real, and the configurations that refuse most end up scored on the fewest and least comparable tasks. Which loops back to where I started: the benchmark is a measuring instrument, and measuring instruments have their own failure modes.

## What I'm taking away

Putting the four cuts side by side, with the model-generation effect included for scale:

| Cut                                             | Comparison                              | Effect               |
| ------------------------------------------------- | ------------------------------------------ | ----------------------- |
| 1. Same model, different harness                | Qwen3 Coder, Codex‑CLI vs OpenCode      | 0% --> 62.9%         |
| 1. Same model, different harness                | MiniMax M2.1, Codex‑CLI vs OpenCode     | 12.5% --> 73.6%      |
| 3. Native vs foreign vendor                     | Opus 4.8, Claude Code vs PI             | 39% --> 50.2%        |
| 3. Model tuned for harness                      | `gpt‑5‑1` --> `codex‑max`, same harness | 38.5% --> 81.7%      |
| Refusal side-effect                             | GPT‑5.5, PI vs Codex                    | ~28% --> ~8% refused |
| *(for scale)* **4. Newer model, fixed harness** | Opus 4.6 --> 4.8 on PI                  | 46% --> 50.2%        |

🤔 **The harness is a first-class variable, not plumbing.**
- A two-generation model upgrade bought ~4 points. Switching harness moved the same model 11, and moved other models 60+. If I'm tuning my own setup, the model may not be the highest-leverage knob.

🌉 **Vendor matching is not a shortcut.**
- Same-company pairing helped OpenAI models consistently and hurt Anthropic models consistently, in both papers. "Use the official harness" is not reliable advice; it's an empirical question per workload.

🔧 **Any score without a named harness is half a result.**
- "Model X scored Y%" is underspecified in the same way "the assay gave 40%" is underspecified without the protocol. Both 2026 papers report the pairing, and BioSecBench‑Surveillance goes further by treating model and harness as independent axes from the start. I'd like to see that become the default.
