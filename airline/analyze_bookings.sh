#!/bin/bash
#
# Quick Booking Analysis Script for TvlSim
# Provides quick stats and exports from simulation logs
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
LOG_FILE="simulate.log"
OUTPUT_DIR="booking_data_$(date +%Y%m%d_%H%M%S)"

# Print banner
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  TvlSim Booking Data Analysis Tool${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo -e "${RED}❌ Error: Log file '$LOG_FILE' not found!${NC}"
    echo -e "${YELLOW}💡 Make sure you've run the simulation first:${NC}"
    echo -e "   $ simulate"
    echo -e "   $ ./tvlsim/tvlsim -b"
    exit 1
fi

echo -e "${GREEN}✅ Found log file: $LOG_FILE${NC}"
echo -e "   Size: $(du -h "$LOG_FILE" | cut -f1)"
echo -e "   Lines: $(wc -l < "$LOG_FILE" | tr -d ' ')\n"

# Create output directory
mkdir -p "$OUTPUT_DIR"
echo -e "${GREEN}📁 Created output directory: $OUTPUT_DIR${NC}\n"

# Quick log analysis
echo -e "${BLUE}🔍 Quick Log Analysis:${NC}"
echo -e "   Booking requests: $(grep -ci 'booking request' "$LOG_FILE" || echo '0')"
echo -e "   Notifications: $(grep -c 'NOTIFICATION' "$LOG_FILE" || echo '0')"
echo -e "   Cancellations: $(grep -ci 'cancellation' "$LOG_FILE" || echo '0')"
echo -e "   Errors: $(grep -ci 'error' "$LOG_FILE" || echo '0')\n"

# Extract sample booking lines
echo -e "${BLUE}📋 Sample booking entries:${NC}"
grep -i 'booking request' "$LOG_FILE" | head -3
echo ""

# Run Python extraction script
echo -e "${BLUE}🐍 Running booking extraction script...${NC}\n"

if command -v python3 &> /dev/null; then
    # Extract to all formats
    python3 extract_bookings.py \
        --log "$LOG_FILE" \
        --csv "$OUTPUT_DIR/bookings_raw.csv" \
        --json "$OUTPUT_DIR/bookings_full.json" \
        --demand "$OUTPUT_DIR/demand_forecast.csv"
    
    echo -e "\n${GREEN}✅ Extraction complete!${NC}\n"
    
    # Show output files
    echo -e "${BLUE}📦 Generated files:${NC}"
    ls -lh "$OUTPUT_DIR"
    
    echo -e "\n${YELLOW}💡 Quick view of demand forecast data:${NC}"
    head -20 "$OUTPUT_DIR/demand_forecast.csv" | column -t -s,
    
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✨ Success! Booking data extracted to: $OUTPUT_DIR${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo -e "\n${YELLOW}📊 To analyze in Python/pandas:${NC}"
    echo -e "   import pandas as pd"
    echo -e "   df = pd.read_csv('$OUTPUT_DIR/bookings_raw.csv')"
    echo -e "   df.head()"
    
    echo -e "\n${YELLOW}📈 For demand forecasting:${NC}"
    echo -e "   Use: $OUTPUT_DIR/demand_forecast.csv"
    
else
    echo -e "${RED}❌ Error: python3 not found!${NC}"
    echo -e "${YELLOW}💡 Please install Python 3 to use the extraction script${NC}"
    exit 1
fi
