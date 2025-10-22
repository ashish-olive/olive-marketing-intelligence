#!/bin/bash

# Local Testing Script for Olive Marketing Intelligence
# Tests with a small dataset to verify everything works

echo "======================================================================"
echo "OLIVE MARKETING INTELLIGENCE - LOCAL TEST"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo "Step 1: Checking Python..."
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python3 found: $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

# Step 2: Install backend dependencies
echo ""
echo "Step 2: Installing backend dependencies..."
cd data-pipeline
pip3 install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
cd ..

# Step 3: Generate small test dataset
echo ""
echo "Step 3: Generating test dataset..."
echo -e "${YELLOW}Using small dataset: 7 days, 1000 users, 2 campaigns per channel${NC}"
python3 data-pipeline/scripts/generate_data.py --days 7 --users 1000 --campaigns 2

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test data generated successfully${NC}"
else
    echo -e "${RED}✗ Data generation failed${NC}"
    exit 1
fi

# Step 4: Check database
echo ""
echo "Step 4: Verifying database..."
if [ -f "instance/marketing.db" ]; then
    DB_SIZE=$(du -h instance/marketing.db | cut -f1)
    echo -e "${GREEN}✓ Database created: $DB_SIZE${NC}"
else
    echo -e "${RED}✗ Database not found${NC}"
    exit 1
fi

# Step 5: Test backend
echo ""
echo "Step 5: Testing backend API..."
echo -e "${YELLOW}Starting backend server (will run for 5 seconds)...${NC}"

# Start backend in background
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait for server to start
sleep 3

# Test health endpoint
HEALTH_CHECK=$(curl -s http://localhost:5000/api/health)
if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Backend API is healthy${NC}"
    echo "  Response: $HEALTH_CHECK"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Test executive summary endpoint
SUMMARY=$(curl -s http://localhost:5000/api/executive/summary?days=7)
if [[ $SUMMARY == *"total_spend"* ]]; then
    echo -e "${GREEN}✓ Executive summary endpoint working${NC}"
else
    echo -e "${RED}✗ Executive summary endpoint failed${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Stop backend
kill $BACKEND_PID 2>/dev/null
echo -e "${GREEN}✓ Backend tests passed${NC}"

# Step 6: Summary
echo ""
echo "======================================================================"
echo -e "${GREEN}ALL TESTS PASSED!${NC}"
echo "======================================================================"
echo ""
echo "Your local setup is working correctly!"
echo ""
echo "Next steps:"
echo "  1. To run with full dataset:"
echo "     python3 data-pipeline/scripts/generate_data.py --days 90 --users 500000"
echo ""
echo "  2. Start backend:"
echo "     cd backend && python3 app.py"
echo ""
echo "  3. Start frontend (in new terminal):"
echo "     cd frontend && npm install && npm start"
echo ""
echo "  4. Access app at: http://localhost:3000"
echo ""
echo "======================================================================"
