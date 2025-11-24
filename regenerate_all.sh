#!/bin/bash

# =============================================================================
# Complete Project Regeneration Script
# =============================================================================
# This script regenerates all data, models, and figures from scratch
# Run this after modifying optimization or ML algorithms
# =============================================================================

set -e  # Exit on any error

echo "=========================================="
echo "BTP DAB TPS Project - Full Regeneration"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"

# =============================================================================
# Step 1: Clean existing generated files
# =============================================================================
echo -e "${YELLOW}Step 1: Cleaning existing generated files...${NC}"

if [ -d "data" ]; then
    echo "  Removing data/*.csv"
    rm -f data/*.csv
fi

if [ -d "models" ]; then
    echo "  Removing models/*.pkl"
    rm -f models/*.pkl
fi

if [ -d "figures" ]; then
    echo "  Removing figures/*.png (keeping manual figures)"
    rm -f figures/optimization_results.png
    rm -f figures/ml_comparison.png
    rm -f figures/rf_predictions_vs_actual.png
    rm -f figures/svr_predictions_vs_actual.png
    rm -f figures/svr_power_trends.png
    rm -f figures/mode_distribution.png
fi

echo -e "${GREEN}  ✓ Cleanup complete${NC}"
echo ""

# =============================================================================
# Step 2: Generate optimal lookup table
# =============================================================================
echo -e "${YELLOW}Step 2: Generating optimal lookup table...${NC}"
echo "  Running integrated_optimizer.py (this takes ~10 minutes)"

python3 scripts/optimization/integrated_optimizer.py

if [ ! -f "data/integrated_optimal_lookup_table.csv" ]; then
    echo -e "${RED}ERROR: Failed to generate optimal lookup table${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Optimal lookup table generated (91 points)${NC}"
echo ""

# =============================================================================
# Step 3: Train Random Forest model
# =============================================================================
echo -e "${YELLOW}Step 3: Training Random Forest model...${NC}"

python3 scripts/machine_learning/train_tps_regressor.py

if [ ! -f "models/tps_rf_model.pkl" ]; then
    echo -e "${RED}ERROR: Failed to train Random Forest model${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Random Forest model trained${NC}"
echo ""

# =============================================================================
# Step 4: Train SVR models
# =============================================================================
echo -e "${YELLOW}Step 4: Training SVR models...${NC}"

python3 scripts/machine_learning/train_tps_svr.py

if [ ! -f "models/svr_scaler.pkl" ]; then
    echo -e "${RED}ERROR: Failed to train SVR models${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ SVR models trained${NC}"
echo ""

# =============================================================================
# Step 5: Verify all required files exist
# =============================================================================
echo -e "${YELLOW}Step 5: Verifying generated files...${NC}"

REQUIRED_FILES=(
    "data/integrated_optimal_lookup_table.csv"
    "data/rf_interpolated_lookup_table.csv"
    "data/svr_interpolated_lookup_table.csv"
    "models/tps_rf_model.pkl"
    "models/svr_scaler.pkl"
    "models/svr_model_D0.pkl"
    "models/svr_model_D1.pkl"
    "models/svr_model_D2.pkl"
    "models/svr_model_Irms_A.pkl"
    "figures/rf_predictions_vs_actual.png"
    "figures/svr_predictions_vs_actual.png"
)

ALL_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (MISSING)"
        ALL_EXIST=false
    fi
done

echo ""

if [ "$ALL_EXIST" = false ]; then
    echo -e "${RED}ERROR: Some required files are missing${NC}"
    exit 1
fi

# =============================================================================
# Summary
# =============================================================================
echo "=========================================="
echo -e "${GREEN}✅ Project regeneration complete!${NC}"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  📊 Data files: $(ls -1 data/*.csv | wc -l) CSV files"
echo "  🤖 Models: $(ls -1 models/*.pkl | wc -l) model files"
echo "  📈 Figures: $(ls -1 figures/*.png 2>/dev/null | wc -l) PNG files"
echo ""
echo "Next steps:"
echo "  1. Run dashboard: cd dashboard && streamlit run dashboard.py"
echo "  2. Generate remaining figures: See docs/REQUIRED_FIGURES.md"
echo "  3. Compile report: cd docs && pdflatex final_report.tex"
echo ""
echo "Project ready for use! 🚀"
