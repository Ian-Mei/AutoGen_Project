# Example Google Sheets Data Structure for Event Planning

This document shows example data structures you can use in your Google Sheets for testing the event planning tool.

## Example Sheet 1: Event Planning Data

**Sheet Name:** Event_Planning
**Range:** A1:E10

| Event Name | Theme | Date | Budget | Activities |
|------------|-------|------|--------|------------|
| Mid Autumn Festival | Traditional | 2024-09-15 | 5000 | Lantern making, Moon cake tasting |
| Spring Mixer | Social | 2024-03-20 | 3000 | Games, Music, Dancing |
| Cultural Night | Multicultural | 2024-05-10 | 4500 | Performances, Food booths |
| Study Break | Academic | 2024-04-15 | 2000 | Snacks, Relaxation activities |
| End of Year Party | Celebration | 2024-05-30 | 6000 | Awards, Dinner, Entertainment |

## Example Sheet 2: Fundraising Data

**Sheet Name:** Fundraising
**Range:** A1:D8

| Campaign | Goal Amount | Current Amount | Activities |
|----------|-------------|----------------|------------|
| Mid Autumn Festival | 5000 | 2500 | Ticket sales, Sponsorships |
| Spring Mixer | 3000 | 1800 | Entry fees, Merchandise |
| Cultural Night | 4500 | 3200 | Vendor fees, Donations |
| Study Break | 2000 | 2000 | Student fees |

## Example Sheet 3: Quality Checklist

**Sheet Name:** Quality_Check
**Range:** A1:C10

| Item | Status | Notes |
|------|--------|-------|
| Venue booking | Complete | Confirmed for 2024-09-15 |
| Catering | In Progress | Quotes received |
| Decorations | Pending | Waiting for theme approval |
| Entertainment | Complete | Band booked |
| Registration | In Progress | Online form created |
| Safety measures | Pending | Need fire safety approval |
| Cleanup plan | Pending | Volunteers needed |

## How to Use These Examples

1. **Create a new Google Sheet** in your Google Drive
2. **Copy one of the data structures** above into your sheet
3. **Get the Sheet ID** from the URL (the long string of characters)
4. **Note the range** you want to read (e.g., "Event_Planning!A1:E10")
5. **Update the test file** with your Sheet ID and range
6. **Run the test** to see the data integration in action

## Test Sheet ID (Public Example)

For initial testing, you can use this public Google Sheet:
- **Sheet ID:** `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
- **Range:** `Class Data!A2:E`

This is Google's public example sheet for API testing.

## Environment Variables

You can also add these to your `.env` file for easier testing:

```env
# Google Sheets Configuration
GOOGLE_SHEETS_TEST_ID=your_sheet_id_here
GOOGLE_SHEETS_TEST_RANGE=Sheet1!A1:E10
```

## Testing Commands

Run the test with:
```bash
python test_google_sheets.py
```

Or test individual components:
```python
# Test basic functionality
python -c "import asyncio; from test_google_sheets import test_basic_functionality; asyncio.run(test_basic_functionality())"

# Test credentials
python -c "import asyncio; from test_google_sheets import test_google_sheets_credentials; asyncio.run(test_google_sheets_credentials())"
```
