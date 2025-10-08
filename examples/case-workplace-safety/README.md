# Workplace Safety Escalation - Example Case

**Case Type**: Employment Law / Workplace Safety
**Evidence Count**: 6 pieces
**Demonstrates**: Safety concern escalation, retaliation detection, power dynamics analysis

---

## Case Overview

This example demonstrates a typical workplace safety investigation scenario where an employee raises legitimate safety concerns, and the response shifts focus to individual productivity rather than addressing systemic issues.

**Timeline**: February - March 2025

**Key Participants**:
- **James Wilson** - Warehouse Associate (complainant)
- **Sarah Chen** - Warehouse Manager
- **Michael Torres** - Shift Supervisor
- **Lisa Rodriguez** - Safety Compliance Officer
- **Rachel Martinez** - HR Specialist

---

## Evidence Files

### Documents (4 files)

1. **2025-02-02-LETTER-SafetyConcerns-JWilson-Management.txt**
   - Initial formal complaint about warehouse safety issues
   - Documents specific hazards in Warehouse Area 3
   - Requests management action and policy review

2. **2025-03-06-EMAIL-ProductivityMeeting-SChen-JWilson.txt**
   - Management response focusing on productivity metrics
   - Proposes individual workaround rather than systemic solution

3. **2025-03-07-EMAIL-MeetingResponse-JWilson-SChen.txt**
   - Employee response expressing concerns about approach
   - Highlights conflict between safety compliance and productivity metrics
   - Escalates to broader systemic issues

4. **2025-03-10-MEMO-InvestigationNotice-HR-JWilson.txt**
   - Formal HR investigation notice
   - Outlines investigation scope and process
   - Professional, neutral tone

### Emails (1 .eml file)

5. **2025-02-09-EMAIL-SafetyMeeting-MTorres-JWilson.eml**
   - Shift supervisor response about photography policy
   - Shows management concern about documentation methods
   - Demonstrates email thread analysis capabilities

### Personal Notes (1 file)

6. **employee-timeline-notes.txt**
   - Employee's personal timeline of events
   - Documents informal and formal communications
   - Shows progression from concern to investigation

---

## What This Case Demonstrates

### Evidence Toolkit Features

**Entity Correlation**:
- 5 named individuals across multiple documents
- Demonstrates cross-document entity tracking
- Shows relationship mapping (employee → supervisor → manager → HR)

**Timeline Reconstruction**:
- Events spanning 2 months (Jan 15 - Mar 10)
- Multiple date formats handled
- Correlation of formal and informal communications

**Sentiment Analysis**:
- Initial professional complaint (neutral/professional)
- Escalating concern in follow-up (professional but assertive)
- Management responses (professional but dismissive undertones)

**Legal Pattern Detection**:
- **Potential retaliation indicators**: Focus shift from safety to productivity
- **Evidence gaps**: No response to initial Feb 2 complaint until Mar 6 meeting
- **Power dynamics**: Employee vs. management hierarchy
- **Corroboration opportunities**: Multiple people copied on emails

**Communication Patterns**:
- Professional email threads
- Escalation sequence (informal → formal → investigation)
- Authority levels (employee → supervisor → manager → HR)

---

## Usage

### Quick Test
```bash
# Process this example case
uv run evidence-toolkit process-case examples/case-workplace-safety \
  --case-id example-workplace-safety

# View results
cat data/packages/example-workplace-safety_*/reports/executive_summary.txt
```

### With Case Type Support (v3.2+)
```bash
# Process as workplace/employment case
uv run evidence-toolkit process-case examples/case-workplace-safety \
  --case-id example-workplace-safety \
  --case-type workplace

# With AI entity resolution
uv run evidence-toolkit process-case examples/case-workplace-safety \
  --case-id example-workplace-safety \
  --case-type workplace \
  --ai-resolve
```

---

## Expected Analysis Results

### Entities Extracted
- **People**: James Wilson, Sarah Chen, Michael Torres, Lisa Rodriguez, Rachel Martinez
- **Organizations**: RetailCorp, HR Department, Safety Compliance
- **Dates**: Feb 2, Feb 9, Feb 20, Mar 5, Mar 6, Mar 7, Mar 10
- **Locations**: Warehouse Area 3, Distribution Center

### Timeline Events
- Jan 15: Initial safety concerns observed
- Feb 2: Formal complaint submitted
- Feb 9: Photography policy meeting (early AM, outside shift)
- Mar 6: Productivity metrics meeting (after shift)
- Mar 7: Escalation response from employee
- Mar 10: HR investigation initiated

### Legal Patterns
- **Potential retaliation**: Meetings outside work hours, productivity focus after safety complaint
- **Evidence gaps**: No management response for 1 month (Feb 2 - Mar 6)
- **Corroboration**: Multiple parties copied on emails, consistent timeline across documents

### Risk Flags
- Workplace safety compliance issues
- Potential retaliation against complainant
- Productivity metrics conflicting with safety procedures
- Meetings held outside regular work hours

---

## Privacy Notice

This is a **completely anonymized** example case:
- ✅ No real people, companies, or events
- ✅ Generic workplace safety scenario
- ✅ Safe for public demonstrations and training
- ✅ Based on common legal patterns in employment law

All names, companies, dates, and specific details are fictional.

---

## Customization

To create your own workplace safety case:

1. Copy this directory structure
2. Replace names, company details, and specific issues
3. Maintain the file naming convention: `YYYY-MM-DD-TYPE-Subject-From-To.ext`
4. Ensure dates follow chronological progression
5. Include a mix of formal (letters, memos) and informal (emails, notes) evidence

**See**: `examples/templates/` for blank templates

---

**Case Created**: 2025-10-08 for Evidence Toolkit v3.3.0 launch
**Purpose**: Demonstrate workplace safety escalation analysis and legal pattern detection
