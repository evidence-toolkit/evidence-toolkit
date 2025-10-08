# Quick Start Checklist - Launch in 7 Days

## ✅ DONE (Today)

- [x] Demo report #1 created (Workplace Investigation)
- [x] Branded PDF template working
- [x] Landing page copy written
- [x] Terms of Service drafted
- [x] Sanitization process documented

**Files ready**:
- `demos/workplace_investigation_001/DEMO_Report.pdf` - Portfolio piece
- `demos/landing_page_copy.md` - Web content
- `demos/TERMS_OF_SERVICE.md` - Legal foundation
- `scripts/create_branded_pdf.py` - PDF generator

---

## 📅 DAY 1-2: Landing Page (Tomorrow)

### Option A: Carrd (Fastest - 2 hours)
1. Sign up at carrd.co (£19/year for Pro)
2. Copy/paste content from `landing_page_copy.md`
3. Upload `DEMO_Report.pdf` as downloadable file
4. Add Stripe payment button:
   - First case: £150 (create discount code for £300 → £150)
   - Standard: £300
5. Collect email on submit → Mailchimp/ConvertKit
6. Publish to custom domain or carrd.co subdomain

### Option B: HTML Page (4 hours, more control)
1. Use Tailwind CSS template (free on tailwindui.com)
2. Host on Cloudflare Pages (free, fast)
3. Stripe Checkout integration
4. Form submission → webhook

**Deliverable**: Live landing page at evidencetoolkit.co.uk or similar

---

## 📅 DAY 3-4: Backend Webhook

### Minimal Python Endpoint (Flask/FastAPI)
```python
# app.py
from flask import Flask, request, jsonify
import subprocess
from pathlib import Path

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_case():
    # 1. Receive uploaded ZIP
    case_file = request.files['case_zip']
    case_type = request.form.get('case_type', 'generic')
    customer_email = request.form['email']
    
    # 2. Save to temp location
    upload_dir = Path(f'/tmp/cases/{case_id}')
    upload_dir.mkdir(parents=True)
    case_file.save(upload_dir / 'evidence.zip')
    
    # 3. Run Evidence Toolkit
    subprocess.run([
        'uv', 'run', 'evidence-toolkit', 'process-case',
        str(upload_dir), '--case-id', case_id,
        '--case-type', case_type
    ])
    
    # 4. Generate branded PDF
    subprocess.run([
        'uv', 'run', 'python', 'scripts/create_branded_pdf.py',
        f'data/packages/{case_id}*/reports/executive_summary.txt',
        f'/tmp/{case_id}_report.pdf'
    ])
    
    # 5. Email download link
    send_email(customer_email, f'/tmp/{case_id}_report.pdf')
    
    return jsonify({'status': 'success'})
```

### Deployment:
- Railway.app (£5/month, easy deploy)
- Fly.io (£3/month, more control)
- Render.com (free tier, slower)

**Deliverable**: Upload endpoint that triggers analysis

---

## 📅 DAY 5: Email Integration

### SendGrid (Free tier: 100 emails/day)
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment
import base64

def send_email(to_email, pdf_path):
    message = Mail(
        from_email='hello@evidencetoolkit.ai',
        to_emails=to_email,
        subject='Your Evidence Analysis Report is Ready',
        html_content='''
        <h2>Analysis Complete</h2>
        <p>Your case has been analyzed. Download your report attached.</p>
        <p>Questions? Reply to this email.</p>
        '''
    )
    
    with open(pdf_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
        message.attachment = Attachment(
            file_content=data,
            file_name='Evidence_Analysis_Report.pdf'
        )
    
    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    sg.send(message)
```

**Deliverable**: Automated email delivery of PDF reports

---

## 📅 DAY 6: End-to-End Testing

### Test Scenarios:
1. **Happy path**: Upload ZIP → Receive PDF in 30 min ✅
2. **Payment flow**: Stripe → Webhook → Analysis trigger ✅
3. **Error handling**: Invalid ZIP → User-friendly error message ✅
4. **Email delivery**: PDF attached, links work ✅
5. **Refund flow**: Request refund → Stripe refund processed ✅

### Load test:
- 5 concurrent uploads (simulate busy day)
- Verify queue doesn't break
- Check processing time stays <60 min

**Deliverable**: Tested, working end-to-end flow

---

## 📅 DAY 7: Soft Launch

### LinkedIn Post (Reach: 500-1000)
```
After analyzing 1,295 pieces of evidence in a workplace case, 
I built an AI tool that does it in 30 minutes.

Employment solicitors: Stop spending 6 hours manually reviewing evidence.

✅ Upload case files (emails, photos, docs)
✅ Get AI analysis in 30 minutes
✅ Timeline, contradictions, risk assessment

First case: £150

Demo report: [link to PDF]

Built for: Unfair dismissal, whistleblowing, workplace investigations

Early access: DM me or visit [link] 🚀
```

### Direct Outreach (10 people)
- 5 employment solicitors (LinkedIn connections or Law Society directory)
- 3 HR consultants (Upwork, LinkedIn)
- 2 tribunal representatives (Google search local)

**Template**:
```
Hi [Name],

I've built an AI tool that analyzes employment case evidence 
in 30 minutes (vs 6 hours manually).

Upload: Photos, emails, documents
Get: Timeline, contradictions, risk assessment, PDF report

Here's a real demo: [link]

First case: £150

Worth a quick look?

Paul
```

**Deliverable**: 10 targeted messages sent, 2-3 responses expected

---

## 🎯 Success Metrics - Week 1

### Traffic:
- 50-100 landing page visitors
- 10-20 demo downloads
- 5-10 inquiry emails/DMs

### Revenue:
- 1-2 paying customers × £150 = **£150-300**
- Validate: People will pay for this

### Feedback:
- Collect: What questions do they ask?
- Note: What objections come up?
- Adjust: Improve copy based on responses

---

## 🚨 Blockers to Watch For

### Technical:
- OpenAI API limits (upgrade to paid tier if needed)
- Processing timeout on large cases (set 10 min limit, fail gracefully)
- PDF generation errors (test with various content types)

### Business:
- "How do I know it's accurate?" → Show confidence scores in report
- "Is this legal advice?" → Clear disclaimer in ToS + report footer
- "Can I get a refund?" → 30-day money-back, no questions asked

### Operations:
- Manual QA required for each case (budget 15 min/case)
- Customer support load (aim for FAQ to handle 80%)
- Payment disputes (Stripe handles, respond within 24h)

---

## 💰 Revenue Target - Month 1

**Conservative (10 customers)**:
- 10 × £150 first case = £1,500
- 5 × £300 second case = £1,500
- 2 × £30 Tidy sub = £60/mo
- **Total: £3,060**

**Optimistic (20 customers)**:
- 20 × £150 = £3,000
- 10 × £300 = £3,000
- 5 × £30 = £150/mo
- **Total: £6,150**

**Break-even**: 2 customers covers hosting costs (~£300/mo)

---

## 📝 Next Actions (Priority Order)

1. **TODAY**: Deploy landing page (Carrd - 2 hours)
2. **TOMORROW**: Set up Stripe payment (1 hour)
3. **DAY 3**: Build webhook endpoint (4 hours)
4. **DAY 4**: Email integration (2 hours)
5. **DAY 5**: End-to-end test (3 hours)
6. **DAY 6**: Soft launch LinkedIn (30 min)
7. **DAY 7**: Direct outreach (2 hours)

**First customer by**: Friday (Day 5-7)
**First £500 revenue by**: End of Week 2

---

## ✅ You Have Everything You Need

- [x] Working tech (Evidence Toolkit v3.2)
- [x] Demo report (proves value)
- [x] Landing page copy (converts visitors)
- [x] Pricing strategy (£150/£300/£30)
- [x] Legal foundation (ToS)
- [x] PDF branding (professional output)

**The gap**: Web implementation (7 days of focused work)

**The prize**: £3-6K revenue in Month 1, validated business model

**Your move**: Start with landing page deployment. Everything else follows from there.

Want help with any specific step?
