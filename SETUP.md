# Quick Setup Guide

## Installation & Migration

1. **Install Pillow (for image uploads)**:
   ```bash
   pip install Pillow
   ```

2. **Apply Database Migrations**:
   ```bash
   python manage.py migrate core
   ```

3. **Create Media Directory**:
   ```bash
   mkdir -p media/products
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

Visit: `http://localhost:8000/`

---

## Feature Access

### Admin Features
- **Admin Panel**: `/admin-panel/` - Dashboard with charts
- **User Management**: `/users/` - Create/edit users
- **Audit Logs**: `/audit-logs/` - View system activity
- **Products**: `/products/` - Search, filter, view images
- **Orders**: `/orders/` - Filter by status/date, view timeline

### Customer Features
- **Dashboard**: `/` - View your orders and stats
- **Products**: `/products/` - Browse products with search
- **Orders**: `/orders/` - Place and track orders
- **Order Details**: `/orders/<id>/` - View timeline & leave review
- **Settings**: `/settings/` - Account and security preferences

---

## Key New Fields in Admin

**Products Admin**:
- Image upload field (replaces text field)
- Viewing uploaded images

**Orders Admin**:
- View order timeline history
- Status change tracking

**Users Admin**:
- Two-factor authentication toggle
- Email notification preferences

---

## Using New Features

### 1. Upload Product Images
- Go to `/products/add/` or edit existing product
- Select image file from your computer
- Saved to `media/products/`

### 2. Search Products
- `/products/` page
- Search by name or SKU
- Filter by category or low stock status

### 3. Track Orders
- Click "View" on any order
- See complete status timeline with timestamps
- Leave review if order is completed

### 4. Manage Users (Admin)
- `/users/` - List all users
- `/users/new/` - Create new user
- Click "Edit" to modify user details/role

### 5. View Audit Logs (Admin)
- `/audit-logs/`
- Filter by model, user, or action
- See who changed what and when

### 6. View Customer History (Admin)
- Go to `/users/` 
- Click "History" on any customer
- See all their orders and spending

### 7. Dashboard Charts (Admin)
- `/admin-panel/`
- See 30-day sales trend
- View top 10 products ordered

---

## Configuration

### Email Notifications (Optional)
Edit `xama_system/settings.py`:

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@xamatrading.com'
```

For Gmail:
1. Enable 2-Step Verification
2. Create an App Password
3. Use the App Password above

### Media Files
- Images stored in: `media/products/`
- Ensure directory is writable: `chmod 755 media/products`
- In production, use cloud storage (S3, Azure, etc.)

---

## Troubleshooting

**Issue**: "No module named 'PIL'"
- **Fix**: `pip install Pillow`

**Issue**: Image not uploading
- **Fix**: Ensure `media/` directory exists and is writable

**Issue**: Pagination not showing
- **Fix**: Add 20+ items to see pagination controls

**Issue**: Charts not displaying
- **Fix**: Charts require Chart.js (loaded from CDN). Check internet connection.

**Issue**: Audit logs empty
- **Fix**: Create/edit items to generate log entries

---

## Next Steps

1. ✅ Run migrations
2. ✅ Create admin user: `python manage.py createsuperuser`
3. ✅ Upload some product images
4. ✅ Create test orders
5. ✅ Try search, filtering, and pagination
6. ✅ Review charts on admin panel
7. ✅ Test order cancellation
8. ✅ Check audit logs

---

## File Structure

```
xama_system/
├── core/
│   ├── migrations/
│   │   └── 0003_add_features.py        # New features migration
│   ├── models.py                        # +5 new models, 2 updated
│   ├── views.py                         # +8 new views, 4 updated
│   ├── forms.py                         # +6 new forms
│   ├── urls.py                          # +8 new routes
│   ├── admin.py                         # All models registered
│   └── ...
├── templates/core/
│   ├── order_detail.html                # NEW: Order timeline & reviews
│   ├── customer_history.html            # NEW: Customer order history
│   ├── audit_logs.html                  # NEW: Audit log viewer
│   ├── user_list.html                   # NEW: User management
│   ├── user_create.html                 # NEW: Create user
│   ├── user_edit.html                   # NEW: Edit user
│   ├── user_settings.html               # NEW: Account settings
│   ├── product_list.html                # UPDATED: Search, pagination, images
│   ├── order_list.html                  # UPDATED: Filtering, pagination
│   ├── admin_panel.html                 # UPDATED: Charts, new quick actions
│   └── ...
├── media/products/                      # NEW: Product image directory
├── manage.py
├── FEATURES.md                          # NEW: This feature documentation
├── SETUP.md                             # NEW: This quick setup guide
└── ...
```

---

**Version**: 2.0.0 (Full Feature Set)
**Last Updated**: May 27, 2026
