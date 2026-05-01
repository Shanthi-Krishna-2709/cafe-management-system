# 🎯 QR Code Payment Setup - Quick Start Guide

## ✅ What Has Been Implemented

### Files Created:
1. **payment.html** - Beautiful payment page with UPI & NetBanking QR codes
2. **bill.html** - Professional checkout/order summary page
3. **QR_PAYMENT_README.md** - Complete documentation

### Files Modified:
1. **views.py** - Added QR code generation functions
2. **urls.py** - Added payment endpoints
3. **settings.py** - Added payment configuration

### New Payment Methods:
- ✅ UPI Payment with QR Code
- ✅ NetBanking Payment with QR Code
- ✅ Optional Razorpay Card Payment

---

## 📋 Step 1: Install Required Packages

Run this command in your terminal:

```bash
pip install qrcode[pil] pillow razorpay
```

If you're in a virtual environment:
```bash
cd C:\Users\sivap\OneDrive\Desktop\Desktop\cafe_project\cafe_project
venv\Scripts\pip install qrcode[pil] pillow razorpay
```

---

## ⚙️ Step 2: Configure Payment Settings

Edit: `cafe_project/settings.py`

Find the section at the bottom with:
```python
# UPI Payment Configuration
UPI_ID = 'merchant@ybl'
MERCHANT_NAME = 'Café'

# NetBanking Configuration
BANK_NAME = 'State Bank of India'
BANK_ACCOUNT = '1234567890123456'
IFSC_CODE = 'SBIN0001234'
```

### Update with Your Details:

**For UPI:**
- Replace `merchant@ybl` with your actual UPI ID
  - Open any UPI app (Google Pay, PhonePe, etc.)
  - Go to Settings/Profile
  - Copy your UPI ID (format: name@bank)

**For NetBanking:**
- Replace `State Bank of India` with your bank name
- Replace account and IFSC with yours
- Find IFSC in your checkbook or bank website

---

## 🚀 Step 3: Test It Out

1. Start your Django server:
```bash
python manage.py runserver
```

2. Go to: `http://127.0.0.1:8000/`

3. Click "Menu" and follow this path:
   - Add items to cart → Click "View Cart" → Click "Proceed to Checkout"
   - Review order → Click "Proceed to Payment"
   - See your UPI and NetBanking QR codes! 🎉

---

## 📱 User Flow

```
Menu Page
   ↓ (Add items)
Cart Page
   ↓ (View Cart)
Checkout/Bill Page (bill.html)
   ↓ (Shows order summary with GST)
Payment Page (payment.html)
   ↓ (Choose payment method)
UPI / NetBanking / Card (with QR codes)
```

---

## 🔍 What Each QR Code Does

### 1️⃣ UPI QR Code
- Scanned with: Google Pay, PhonePe, BHIM, Paytm
- Format: `upi://pay?pa=YOUR_UPI_ID&pn=YourName&am=AMOUNT&tn=CafePayment`
- User scans → Opens their UPI app → Completes payment instantly

### 2️⃣ NetBanking QR Code
- Scanned with: Bank's app or generic QR scanner
- Contains: Bank name, account number, IFSC, amount
- User scans → Opens bank app → Enters credentials → Confirms

### 3️⃣ Card Payment (Optional)
- If Razorpay keys are set, users can pay with credit/debit card
- Iframe payment gateway

---

## 📸 Preview

### Payment Page Shows:
```
💳 Payment Options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Amount to Pay: ₹XXXX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────┬─────────────────┐
│  📱 UPI Payment │ 🏦 NetBanking  │
│  [QR Code]      │  [QR Code]      │
│  Scan to pay    │  Scan to pay    │
│  ↓ Download     │  ↓ Download     │
└─────────────────┴─────────────────┘
```

---

## 🔒 Security Notes

✅ All QR codes are generated fresh for each order
✅ Amount is tied to the order total
✅ User can download QR code as backup

⚠️ For Production:
- Never commit your real UPI ID or bank details to Git
- Use environment variables for sensitive data
- Enable HTTPS
- Use Razorpay LIVE keys only when ready

---

## 🐛 Troubleshooting

### QR Code Not Showing?
```
Error: Module 'qrcode' not installed
→ Run: pip install qrcode[pil]
```

### Payment Page Shows Error?
```
Error: 'qrcode' not imported
→ Restart Django: Ctrl+C, then python manage.py runserver
```

### QR Code Not Scanning?
```
→ Verify your UPI ID format is correct (name@bank)
→ Try with different QR code scanner
→ Check if amount shows in QR code details
```

### Templates Not Found?
```
→ Make sure payment.html and bill.html are in:
   cafe_app/templates/
```

---

## 📲 Quick Test with Phone

1. Add items to your cart
2. Go to Checkout page
3. On Payment page, take screenshot of UPI QR code
4. Open Google Pay/PhonePe on phone
5. Tap "Scan QR Code"
6. Scan the QR from your screen
7. You'll see the payment popup! ✓

---

## 🎨 Customize Payment Page

Edit `templates/payment.html` to:
- Change colors (--btn, --accent2)
- Add your logo
- Add payment instructions
- Change text

Edit `templates/bill.html` to:
- Customize checkout layout
- Add company info
- Modify tax calculation

---

## 📞 Need Help?

Check the full documentation: `QR_PAYMENT_README.md`

Common issues:
- ✅ Update settings.py with your credentials
- ✅ Install required packages
- ✅ Restart Django server after settings change
- ✅ Clear browser cache if styles don't load

---

## 🎉 You're All Set!

Your Café app now has professional QR code payment integration!

Next steps:
1. Test with real UPI
2. Configure NetBanking details
3. (Optional) Add Razorpay for card payments
4. Deploy to production

Happy payments! 💰
