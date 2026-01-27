#!/bin/bash
# 🚀 Quick Start Deployment Script
# Run this to deploy Phase 6-8 bot to production

set -e

echo "================================"
echo "🚀 TRENCH ALERT BOT - DEPLOYMENT"
echo "================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}[1/6]${NC} Checking Python version..."
python3 --version
if ! python3 --version 2>&1 | grep -q "3.9"; then
    echo -e "${YELLOW}⚠️  Recommended Python 3.9+${NC}"
fi
echo -e "${GREEN}✅ Python version OK${NC}\n"

# Check required files
echo -e "${BLUE}[2/6]${NC} Checking required files..."
files=("app.py" "onchain.py" "meta.py" "subscriptions.py" "requirements.txt")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        exit 1
    fi
done
echo -e "${GREEN}✅ All required files present${NC}\n"

# Activate virtual environment
echo -e "${BLUE}[3/6]${NC} Setting up environment..."
if [ ! -d ".venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv .venv
fi

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}\n"
else
    echo -e "${YELLOW}⚠️  Virtual environment activation may have failed${NC}\n"
fi

# Install/update requirements
echo -e "${BLUE}[4/6]${NC} Installing requirements..."
pip install -q -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Requirements installed${NC}\n"

# Run verification tests
echo -e "${BLUE}[5/6]${NC} Running verification tests..."
python3 verify_deployment.py
echo ""

# Ready to deploy
echo -e "${BLUE}[6/6]${NC} Deployment preparation complete!"
echo ""
echo "================================"
echo -e "${GREEN}✅ READY FOR DEPLOYMENT${NC}"
echo "================================"
echo ""
echo "To start the bot:"
echo ""
echo "  export BOT_TOKEN='your_bot_token_here'"
echo "  export CHECK_INTERVAL=30  # Optional"
echo "  python3 app.py"
echo ""
echo "Features deployed:"
echo "  ✅ Phase 6: Wallet buy detection (Pro/Premium)"
echo "  ✅ Phase 7: List heating analysis (Pro/Premium)"
echo "  ✅ Phase 8: Three-tier monetization"
echo ""
echo "Test commands in Telegram:"
echo "  /start    - Show main menu"
echo "  /pricing  - Display pricing tiers"
echo "  /help     - Show available commands"
echo ""
echo "For detailed info, see:"
echo "  - DEPLOYMENT_GUIDE.md"
echo "  - PHASE_678_COMPLETE.md"
echo "  - FEATURE_SUMMARY.md"
echo ""
