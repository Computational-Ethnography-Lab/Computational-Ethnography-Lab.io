# Code for Arteaga, I., Hernández de Jesús, A., Ginn, B., Abramson, C., & Dohan, D. Forthcoming. Understanding How Social Context Shapes Decisions to Seek Institutional Care: A Qualitative Study of Latinx Families 
# Navigating Progressive Cognitive Decline. The Gerontologist.”
# C.M. Abramson - https://github.com/Computational-Ethnography-Lab/Computational-Ethnography-Lab

# 1. Load Required Packages
# ========================
if (!require(pheatmap)) install.packages("pheatmap", dependencies = TRUE)
if (!require(lsa)) install.packages("lsa", dependencies = TRUE)
if (!require(viridisLite)) install.packages("viridisLite", dependencies = TRUE)
if (!require(colorspace)) install.packages("colorspace", dependencies = TRUE)

library(pheatmap)
library(lsa)
library(grid)
library(viridisLite) # For the Viridis palette, colorblind version
library(colorspace)  # For desaturating colors, to produce B&W visual


# 2. Define Data Matrix
# =====================
data <- matrix(c(
  1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
  1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1,
  1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
  1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0,
  1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0,
  1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1,
  1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0
), nrow = 8, byrow = TRUE)

rownames(data) <- c(
  "Moved to long term care facility",
  "Mentioned seeking a diagnosis",
  "Has medical insurance",
  "Owns a property",
  "Private financial resources",
  "History of full employment",
  "Has a support network",
  "Second generation in the USA"
)

colnames(data) <- c(
  "Caregiver 49 (F)", "Older adult 07 (M)", "Older adult 13 (F)",
  "Older adult 03 (F)", "Older adult 39 (F)", "Caregiver 29 (M)",
  "Caregiver 24 (M)", "Caregiver 39 (F)", "Caregiver 09 (M)",
  "Caregiver 31 (F)", "Older adult 20 (M)", "Older adult 14 (F)",
  "Caregiver 42 (F)", "Caregiver 46 (F)", "Older adult 17 (F)",
  "Older adult 34 (F)", "Older adult 16 (M)"
)


# 3. Prepare Data for Plotting
# =======================================
# Remap rows to substantive analytical domains
data_colored <- data
data_colored[2:5, ][data_colored[2:5, ] != 0] <- 1 # Resources (Middle rows)
data_colored[1, data_colored[1, ] != 0] <- 2     # Decisions (Top row)
data_colored[6:8, ][data_colored[6:8, ] != 0] <- 3 # Sociodemographics (Bottom rows)


# Define Palettes (Colorblind and Grayscale-readable)
# =========================================================
# Standardized Order: Darkest -> Lightest -> Medium
viridis_samples <- viridis(20)
darkest_color  <- viridis_samples[1]   # Darkest (deep purple)
lightest_color <- viridis_samples[20]  # Lightest (bright yellow)
medium_color   <- viridis_samples[10]  # Medium (blue-green)

# Palette for Color Version using Viridis samples
custom_colors_color <- c("white",          # Value 0 (No data)
                         lightest_color,   # Value 1: Resources (Lightest)
                         darkest_color,    # Value 2: Decisions (Darkest)
                         medium_color)     # Value 3: Sociodemographics (Medium)

# Palette for B&W Version (desaturated color palette)
custom_colors_bw <- desaturate(custom_colors_color)


# 4. Perform Clustering
# ==========================================
# Calculate cosine similarity distance for column clustering
cosine_sim <- cosine(as.matrix(data))
cosine_dist <- as.dist(1 - cosine_sim)
column_clustering <- hclust(cosine_dist)


# 5. Generate and Draw Heatmaps (Color and Black & White)
# =====================================================

# --- COLOR VERSION ---
p_color <- pheatmap(
  mat = data_colored,
  color = custom_colors_color,
  cluster_rows = FALSE,
  cluster_cols = column_clustering,
  show_rownames = TRUE,
  show_colnames = TRUE,
  angle_col = 45,
  border_color = "black",
  main = "Characterization of LatinX Households:\nCaregiving Decisions, Resources, and Sociodemographics",
  fontsize_row = 12,
  fontsize_col = 12,
  cellwidth = 20,
  cellheight = 15,
  treeheight_col = 50,
  legend = FALSE
)

grid.newpage()
grid.draw(p_color$gtable)

vp_color <- viewport(x = unit(0.1, "npc"), y = unit(0.2, "npc"), width = unit(0.2, "npc"), height = unit(0.15, "npc"))
pushViewport(vp_color)
grid.text("Key", x = unit(0.05, "npc"), y = unit(0.9, "npc"), gp = gpar(fontsize = 12, fontface = "bold"), just = "left")

grid.rect(x = unit(0.05, "npc"), y = unit(0.7, "npc"), width = unit(0.15, "npc"), height = unit(0.1, "npc"), gp = gpar(fill = custom_colors_color[3]), just = "left")
grid.text("Decisions", x = unit(0.25, "npc"), y = unit(0.7, "npc"), just = "left")

grid.rect(x = unit(0.05, "npc"), y = unit(0.5, "npc"), width = unit(0.15, "npc"), height = unit(0.1, "npc"), gp = gpar(fill = custom_colors_color[2]), just = "left")
grid.text("Resources", x = unit(0.25, "npc"), y = unit(0.5, "npc"), just = "left")

grid.rect(x = unit(0.05, "npc"), y = unit(0.3, "npc"), width = unit(0.15, "npc"), height = unit(0.1, "npc"), gp = gpar(fill = custom_colors_color[4]), just = "left")
grid.text("Sociodemographics", x = unit(0.25, "npc"), y = unit(0.3, "npc"), just = "left")
upViewport()


# --- 0 SATURATION (B&W) VERSION ---
p_bw <- pheatmap(
  mat = data_colored,
  color = custom_colors_bw,
  cluster_rows = FALSE,
  cluster_cols = column_clustering,
  show_rownames = TRUE,
  show_colnames = TRUE,
  angle_col = 45,
  border_color = "black",
  main = "Characterization of LatinX Households:\nCaregiving Decisions, Resources, and Sociodemographics",
  fontsize_row = 12,
  fontsize_col = 12,
  cellwidth = 20,
  cellheight = 15,
  treeheight_col = 50,
  legend = FALSE
)

grid.newpage()
grid.draw(p_bw$gtable)

vp_bw <- viewport(x = unit(0.1, "npc"), y = unit(0.2, "npc"), width = unit(0.2, "npc"), height = unit(0.15, "npc"))
pushViewport(vp_bw)
grid.text("Key", x = unit(0.05, "npc"), y = unit(0.9, "npc"), gp = gpar(fontsize = 12, fontface = "bold"), just = "left")

grid.rect(x = unit(0.05, "npc"), y = unit(0.7, "npc"), width = unit(0.15, "npc"), height = unit(0.1, "npc"), gp = gpar(fill = custom_colors_bw[3]), just = "left")
grid.text("Decisions", x = unit(0.25, "npc"), y = unit(0.7, "npc"), just = "left")

grid.rect(x = unit(0.05, "npc"), y = unit(0.5, "npc"), width = unit(0.15, "npc"), height = unit(0.1, "npc"), gp = gpar(fill = custom_colors_bw[2]), just = "left")
grid.text("Resources", x = unit(0.25, "npc"), y = unit(0.5, "npc"), just = "left")

grid.rect(x = unit(0.05, "npc"), y = unit(0.3, "npc"), width = unit(0.15, "npc"), height = unit(0.1, "npc"), gp = gpar(fill = custom_colors_bw[4]), just = "left")
grid.text("Sociodemographics", x = unit(0.25, "npc"), y = unit(0.3, "npc"), just = "left")
upViewport()


# 6. Citations
# ============
# R Core Team (2025). R: A language and environment for statistical
#   computing. R Foundation for Statistical Computing, Vienna, Austria.
#   URL https://www.R-project.org/.
#
# Kolde, R. (2019). pheatmap: Pretty Heatmaps. R package version 1.0.12.
#   URL https://cran.r-project.org/web/packages/pheatmap/
#
# Wild, F. (2015). lsa: Latent Semantic Analysis. R package version 0.73.1.
#   URL https://cran.r-project.org/web/packages/lsa/
#
# Green, M. (2023). viridisLite: Colorblind-Friendly Color Maps (R package).
#   URL: https://CRAN.R-project.org/package=viridisLite
#
# Zeileis, A., et al. (2020). colorspace: A Tool for Developing Effective
#   Color Palettes. Journal of Statistical Software, 96(1), 1-48.
#   URL: https://www.jstatsoft.org/v96/i01/
