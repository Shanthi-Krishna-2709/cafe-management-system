# QR Code Payment Integration Guide

This guide explains how to set up and use the QR code payment feature for UPI and NetBanking payments in your Café application.

## Features Implemented

✅ **UPI Payment with QR Code** - Display a scannable QR code for UPI payments
✅ **NetBanking Payment with QR Code** - Display bank details with QR code
✅ **Beautiful Payment UI** - Modern, mobile-friendly payment interface
✅ **Razorpay Integration** - Optional card payment support
✅ **Bill/Checkout Page** - Professional order summary page
✅ **QR Code Download** - Users can download QR codes as PNG files

## Configuration

### 1. Set Your UPI Details

Edit `cafe_project/settings.py` and update:

```python
# UPI Payment Configuration
UPI_ID = 'yourupi@bank'          # Your UPI ID (e.g., name@ybl, name@okhdfcbank)
MERCHANT_NAME = 'Your Café Name'  # Your business name
```

**Where to find your UPI ID:**
- Google Pay → Settings → UPI ID
- PhonePe → Profile → UPI Address
- BHIM → Account → NPCI Registered Address
- Your Bank App → UPI section

### 2. Set Your NetBanking Details

Edit `cafe_project/settings.py` and update:

```python
# NetBanking Configuration
BANK_NAME = 'Your Bank Name'          # e.g., 'State Bank of India'
BANK_ACCOUNT = 'XXXXXXXXXXXX'         # Your account number
IFSC_CODE = 'BANK0001234'             # Your bank's IFSC code
```

**How to find IFSC Code:**
- Check your checkbook
- Visit your bank's website
- Call your bank's customer service

### 3. (Optional) Set Razorpay for Card Payments

Edit `cafe_project/settings.py` and update:

```python
RAZORPAY_KEY_ID = 'rzp_test_XXXXX'
RAZORPAY_KEY_SECRET = 'XXXXX'
```

Get your keys from: https://dashboard.razorpay.com

## Required Python Packages

Make sure these packages are installed:

```bash
pip install django
pip install qrcode[pil]
pip install razorpay
pip install pillow
```

## How It Works

### User Journey

1. **Menu Page** → Add items to cart
2. **Cart Page** → Review items
3. **Checkout (Bill) Page** → See order summary
4. **Payment Page** → Choose payment method and scan QR code

### Payment Methods

#### 1. UPI Payment
- User scans the QR code with their UPI app
- Apps: Google Pay, PhonePe, BHIM, Paytm, WhatsApp Pay
- Instant payment confirmation

#### 2. NetBanking Payment
- User scans the QR code with their bank's app
- Enter account details in bank app
- Verify with OTP
- Payment confirmed

#### 3. Card Payment (Optional, via Razorpay)
- User clicks "Pay with Card"
- Enters card details in Razorpay modal
- Payment processed securely

## File Structure

```
cafe_project/
├── cafe_app/
│   ├── templates/
│   │   ├── payment.html          # NEW: Payment page with QR codes
│   │   └── bill.html             # NEW: Checkout/Order summary page
│   ├── views.py                  # UPDATED: Added QR code generation
│   └── urls.py                   # UPDATED: Added QR code endpoints
├── cafe_project/
│   └── settings.py               # UPDATED: Added payment configuration
└── manage.py
```

## New Views Added

### 1. `generate_qr_code_for_payment(upi_string)`
Helper function to generate QR code from a string

### 2. `get_qr_code_image_base64(image)`
Helper function to convert PIL image to base64 for embedding in HTML

### 3. `generate_upi_qr(request)`
View to generate and download UPI QR code

### 4. `generate_netbanking_qr(request)`
View to generate and download NetBanking QR code

### 5. `payment(request)` - UPDATED
Updated to generate all three payment options with QR codes

## New URLs

- `/payment/` - Payment page with all options
- `/qr/upi/` - Download UPI QR code as PNG
- `/qr/netbanking/` - Download NetBanking QR code as PNG

## Testing

### Test with Sample Data

1. Update settings.py with test UPI and Bank details
2. Run migrations: `python manage.py migrate`
3. Start server: `python manage.py runserver`
4. Visit: http://127.0.0.1:8000/menu/
5. Add items → Checkout → See QR codes

### Testing Different Payment Methods

**Test UPI:**
- Scan QR code with actual UPI app
- Or use any QR code scanner to verify the code

**Test NetBanking:**
- The QR code contains bank details
- In production, you'd integrate actual NetBanking API

**Test Card Payment:**
- Use Razorpay test keys from dashboard
- Test card numbers available in Razorpay docs

## Security Notes

⚠️ **Important for Production:**

1. **Never commit sensitive data** to git:
   - Use environment variables for keys
   - Use `.env` files with python-decouple

2. **Use environment variables:**
   ```python
   import os
   from decouple import config
   
   UPI_ID = config('UPI_ID', default='test@ybl')
   RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID')
   RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET')
   ```

3. **Enable HTTPS** in production
4. **Never expose SECRET_KEY** in production
5. **Use Live keys** only when ready for real transactions

## Customization Tips

### Custom QR Code Size
Edit `views.py` in `generate_qr_code_for_payment()`:
```python
qr = qrcode.QRCode(
    version=2,  # Larger size (1-40)
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # More error correction
    box_size=15,  # Larger boxes
    border=5,
)
```

### Custom Payment Page Styling
Edit `payment.html` CSS variables:
```css
:root {
    --btn: #7c3f5e;  /* Primary button color */
    --accent2: #a0522d;  /* Accent color */
    /* etc... */
}
```

### Add Additional Payment Methods
In `views.py` payment view, add more QR code generation methods and display in `payment.html`

## Troubleshooting

### QR Code Not Showing
- ✅ Install required packages: `pip install qrcode[pil]`
- ✅ Verify settings.py has payment configuration
- ✅ Check browser console for errors

### QR Code Not Scanning
- Settings might have invalid format
- Test with different QR code scanner app
- Verify UPI/Bank details in settings

### Page Not Loading
- Clear browser cache
- Check Django logs: `python manage.py runserver`
- Verify all templates exist

## Support & Integration

For real payment processing:
1. **Razorpay Integration**: https://razorpay.com/docs/
2. **UPI Integration**: Contact your bank's developer program
3. **Custom NetBanking**: Your bank's API documentation

---

**Ready to go live?** Update settings.py with real credentials and test thoroughly!
