# 🎯 Payment Flow Diagram & Configuration Guide

## User Journey Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    CAFÉ PAYMENT SYSTEM                      │
└─────────────────────────────────────────────────────────────┘

                        HOME PAGE (home.html)
                              ↓
                        MENU PAGE (menu.html)
                   ┌──────────────────────────┐
                   │ • Coffee ☕              │
                   │ • Pastries 🥐           │
                   │ • Desserts 🍰           │
                   │ • Snacks 🥗             │
                   └─────────────────────────┘
                         Add to Cart ↓
                        CART PAGE (cart.html)
                   ┌──────────────────────────┐
                   │ Your Items:              │
                   │ • Item 1 × 2 = ₹XXX    │
                   │ • Item 2 × 1 = ₹XXX    │
                   │          Total = ₹XXX  │
                   └─────────────────────────┘
                    Proceed to Checkout ↓
              🆕 BILL PAGE (bill.html) 🆕
              ┌──────────────────────────┐
              │   ORDER SUMMARY          │
              │ ────────────────────     │
              │ Subtotal:    ₹X,XXX     │
              │ GST (5%):    ₹XXX       │
              │ ────────────────────     │
              │ Total:       ₹X,XXX     │
              │ ────────────────────     │
              │ [Review] [Proceed] →    │
              └──────────────────────────┘
                    Proceed to Payment ↓
              🆕 PAYMENT PAGE (payment.html) 🆕
              ┌──────────────────────────┐
              │   PAYMENT OPTIONS        │
              │                          │
              │ 📱 UPI Payment           │
              │  [QR CODE]               │
              │  ✓ Scan with App         │
              │     Payment Done! ✓      │
              │                          │
              │ 🏦 NetBanking            │
              │  [QR CODE]               │
              │  ✓ Scan with Bank App    │
              │     Payment Done! ✓      │
              │                          │
              │ 💳 Card Payment          │
              │  [Razorpay Button]       │
              │     Payment Done! ✓      │
              └──────────────────────────┘
                         ↓
                  SUCCESS PAGE ✓
```

---

## QR Code Generation Flow

```
User Clicks "Proceed to Payment"
            ↓
Request reaches views.payment()
            ↓
Session has 'grand_total' in paise
            ↓
Convert to rupees: amount_in_paise / 100
            ↓
┌─────────────────────────────────────────────────┐
│        GENERATE UPI QR CODE                     │
├─────────────────────────────────────────────────┤
│ Read from settings:                             │
│ • UPI_ID = 'yourname@bank'                      │
│ • MERCHANT_NAME = 'Café'                        │
│                                                 │
│ Create UPI String:                              │
│ upi://pay?pa={upi_id}&pn={name}&am={amt}       │
│                                                 │
│ Generate QR:                                    │
│ QRCode.add_data(upi_string)                    │
│ QRCode.make_image() → PIL Image                │
│                                                 │
│ Convert to Base64:                              │
│ Image → PNG bytes → Base64 string              │
│ (Embed directly in HTML as data:image)         │
└─────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────┐
│        GENERATE NETBANKING QR CODE              │
├─────────────────────────────────────────────────┤
│ Read from settings:                             │
│ • BANK_NAME = 'State Bank of India'            │
│ • BANK_ACCOUNT = '1234567890'                  │
│ • IFSC_CODE = 'SBIN0001234'                    │
│                                                 │
│ Create NetBanking String:                       │
│ "Bank: {name} | Account: {acc} | ..."         │
│                                                 │
│ Generate QR:                                    │
│ Same process as UPI                            │
│ QRCode.add_data(netbanking_string)             │
│ Convert to Base64                              │
└─────────────────────────────────────────────────┘
            ↓
Pass Context to payment.html:
  • upi_qr (base64)
  • netbanking_qr (base64)
  • amount
  • upi_id
  • bank details
            ↓
Display in HTML:
<img src="data:image/png;base64,{{ upi_qr }}">
            ↓
User Sees QR Code ✓
```

---

## Configuration Setup

```
┌──────────────────────────────────────────────────┐
│     EDIT: cafe_project/settings.py               │
└──────────────────────────────────────────────────┘
           ↓
  Find at the bottom:
           ↓
┌──────────────────────────────────────────────────┐
│ # UPI Payment Configuration                      │
│ UPI_ID = 'merchant@ybl'                          │
│ MERCHANT_NAME = 'Café'                           │
│                                                  │
│ # NetBanking Configuration                       │
│ BANK_NAME = 'State Bank of India'               │
│ BANK_ACCOUNT = '1234567890123456'               │
│ IFSC_CODE = 'SBIN0001234'                       │
│                                                  │
│ # Razorpay (Optional)                            │
│ RAZORPAY_KEY_ID = 'rzp_test_XXXXX'              │
│ RAZORPAY_KEY_SECRET = 'XXXXX'                   │
└──────────────────────────────────────────────────┘
           ↓
  Replace with YOUR information:
           ↓
┌──────────────────────────────────────────────────┐
│ # UPI Payment Configuration                      │
│ UPI_ID = 'yourname@ybl'  ← YOUR UPI ID         │
│ MERCHANT_NAME = 'Your Café'  ← YOUR NAME       │
│                                                  │
│ # NetBanking Configuration                       │
│ BANK_NAME = 'Your Bank'  ← YOUR BANK           │
│ BANK_ACCOUNT = 'YOUR_ACCOUNT_NUMBER'  ← YOURS  │
│ IFSC_CODE = 'YOUR_IFSC_CODE'  ← YOUR IFSC      │
└──────────────────────────────────────────────────┘
           ↓
   SAVE FILE (Ctrl+S)
           ↓
   RESTART DJANGO SERVER
           ↓
   Test by visiting /payment/ ✓
```

---

## UPI ID Format Reference

```
┌─────────────────────────────────────────────────┐
│          HOW TO FIND YOUR UPI ID                │
└─────────────────────────────────────────────────┘

Google Pay:
  Settings → Phone number → Copy UPI ID
  Format: phonenumber@okhdfcbank or @ybl

PhonePe:
  Profile (Bottom left) → Copy UPI ID
  Format: phonenumber@airtelpaymentsbank

BHIM:
  More → NPCI Registered Address
  Format: yourname@upi

Paytm:
  Settings → UPI
  Format: phonenumber@paytm

Your Bank's App:
  Search "UPI" in settings
  Each bank has different format
  Examples:
    • SBI: phonenumber@okhdfcbank
    • HDFC: phonenumber@hdfc
    • ICICI: phonenumber@icici
```

---

## IFSC Code & Bank Details Reference

```
┌─────────────────────────────────────────────────┐
│       HOW TO FIND IFSC CODE & ACCOUNT           │
└─────────────────────────────────────────────────┘

IFSC Code (4 letters + 0 + 4 digits):

✓ Check Bank Checkbook
  First page has: Bank name, Branch, IFSC

✓ Online Query
  Search: "Your Bank Name IFSC"
  Visit: yourbank.com → Find branch IFSC

✓ Instant Search
  Google: "HDFC IFSC Delhi" → Get all Delhi codes

Account Number:

✓ Bank Statement
  First page shows your account number

✓ Checkbook
  Printed on every check

✓ Bank App
  Account Details section

---

EXAMPLE CONFIGURATIONS:

Configuration Type 1 - SBI:
  BANK_NAME = 'State Bank of India'
  BANK_ACCOUNT = '31123456789'
  IFSC_CODE = 'SBIN0001234'

Configuration Type 2 - HDFC:
  BANK_NAME = 'HDFC Bank Limited'
  BANK_ACCOUNT = '9876543210123456'
  IFSC_CODE = 'HDFC0000123'

Configuration Type 3 - ICICI:
  BANK_NAME = 'ICICI Bank Limited'
  BANK_ACCOUNT = '1234567890'
  IFSC_CODE = 'ICIC0000001'
```

---

## QR Code Data Format

```
┌─────────────────────────────────────────────────┐
│            UPI QR CODE FORMAT                   │
└─────────────────────────────────────────────────┘

Structure:
upi://pay?pa=UPI_ID&pn=NAME&am=AMOUNT&tn=NOTE

Example:
upi://pay?pa=john@ybl&pn=JohnsCafe&am=500&tn=CafePayment

When User Scans:
1. UPI app opens
2. Shows transaction details
3. User confirms with PIN/fingerprint
4. Payment sent to merchant UPI

---

┌─────────────────────────────────────────────────┐
│       NETBANKING QR CODE FORMAT                 │
└─────────────────────────────────────────────────┘

Structure:
Bank: {NAME} | Account: {ACCOUNT} | IFSC: {IFSC} | Amount: ₹{AMOUNT}

Example:
Bank: State Bank of India | Account: 31123456789 | IFSC: SBIN0001234 | Amount: ₹500

When User Scans:
1. Opens bank app (if installed) or generic QR reader
2. Shows bank transfer details
3. User enters their UPI PIN or net banking credentials
4. Payment transferred to merchant account
```

---

## File Locations

```
your_cafe_project/
│
├── cafe_project/          (Django project settings)
│   ├── settings.py        ← EDIT THIS (Add your payment details)
│   ├── urls.py
│   └── wsgi.py
│
├── cafe_app/              (Django app)
│   ├── views.py           ← MODIFIED (New QR functions)
│   ├── urls.py            ← MODIFIED (New endpoints)
│   └── templates/
│       ├── payment.html   ← NEW (Payment page with QR)
│       ├── bill.html      ← NEW (Checkout summary)
│       ├── menu.html      (Existing)
│       ├── cart.html      (Existing)
│       └── ... other templates
│
├── db.sqlite3
├── manage.py
│
├── SETUP_GUIDE.md         ← READ THIS (How to install)
├── QR_PAYMENT_README.md   ← FULL DOCUMENTATION
└── IMPLEMENTATION_SUMMARY.md ← TECHNICAL DETAILS
```

---

## Testing Checklist

```
Phase 1: Installation
  ☐ Run: pip install qrcode[pil] pillow razorpay
  ☐ Verify packages installed
  ☐ Restart Django server

Phase 2: Configuration
  ☐ Open cafe_project/settings.py
  ☐ Find UPI/Bank configuration
  ☐ Update with your real UPI ID
  ☐ Update with your bank details
  ☐ Save file
  ☐ Restart Django server

Phase 3: Testing Flow
  ☐ Go to http://127.0.0.1:8000/menu/
  ☐ Add 1-2 items to cart
  ☐ Click "View Cart"
  ☐ Review items
  ☐ Click "Proceed to Checkout"
  ☐ See bill.html with items and GST
  ☐ Click "Proceed to Payment"
  ☐ See payment.html with QR codes ✓

Phase 4: QR Testing
  ☐ See UPI QR Code displayed
  ☐ See NetBanking QR Code displayed
  ☐ Click "Download" buttons
  ☐ Save QR codes to phone
  ☐ Open Google Pay / PhonePe
  ☐ Scan UPI QR code
  ☐ Verify amount shows correctly in app ✓

Phase 5: Mobile Test (Optional)
  ☐ Access from mobile phone
  ☐ Verify page layout responsive
  ☐ Tap QR download button
  ☐ Scan QR code with actual UPI app
  ☐ See transaction details appear ✓
```

---

## Quick Troubleshooting

```
❌ "No module named 'qrcode'"
✓ Fix: pip install qrcode[pil]

❌ "AttributeError: 'NoneType' object has no attribute 'add_data'"
✓ Fix: Restart Django server after installing qrcode

❌ "QR code not showing on payment page"
✓ Check:
  • Is qrcode package installed?
  • Did you update settings.py?
  • Are UPI_ID and BANK_ACCOUNT configured?
  • Did you restart Django?

❌ "QR code not scanning"
✓ Check:
  • UPI ID format: is it valid? (name@bank)
  • Bank details complete and correct?
  • Try different QR scanner app

❌ "payment.html or bill.html not found"
✓ Check:
  • Files exist in cafe_app/templates/
  • No typos in file names
  • Folder structure is correct
```

---

## Success Indicators

```
✅ All Systems Go When:
  1. QR codes display on payment page
  2. QR codes contain correct amount
  3. QR codes are scannable
  4. Bank/UPI details appear below QR
  5. Download buttons work
  6. Mobile layout is responsive
  7. Cart → Bill → Payment flow works
  8. GST calculated correctly (5%)

You're Ready for Production When:
  1. Real UPI ID configured and tested
  2. Real bank details configured and tested
  3. QR codes scan with real apps
  4. Amount calculations verified
  5. HTTPS enabled (if public)
  6. Error messages tested
```

---

**Everything is set up! Follow the SETUP_GUIDE.md to complete configuration.** 🚀
