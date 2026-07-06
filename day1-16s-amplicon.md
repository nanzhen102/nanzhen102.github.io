---
title: day 1 - 16S amplicon sequencing
layout: default
nav_order: 2
---
# Sara/Sarah Assignment - Nanzhen explores
## Basic info.
- Shared folder: `/global/project/hpcg1554/`
- My person folder: `/global/teaching-home/sa3240009`
## Step 1. Check what you have
- In R interactive

```R
# Check which R, which library paths
R.version.string
.libPaths()

# Are phyloseq and microbiome installed?
installed <- rownames(installed.packages())
c(phyloseq = "phyloseq" %in% installed, microbiome = "microbiome" %in% installed)
```
## Step 2. Install datasets
- in R interactive

```R
# Install packages.
install.packages("igraph")
install.packages("BiocManager")
BiocManager::install(c("phyloseq", "microbiome))

# Confirm they are installed.

```

Step 1. Load dataset

- `dietswap`
- `GlobalPatterns`
Step 2. Load packages

Step 3. Explore the dataset
Step 4. Check absolute and relative abundances
Step 5. Data filtering
Step 6. Data normalization
Step 6. Check microbial diversity 
- Alpha diversity
- Beta diversity