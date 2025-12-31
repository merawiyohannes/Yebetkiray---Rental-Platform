🏠 Yebet Kiray - Ethiopia's Premier Rental Platform v2.0


Live Production Site: https://yebetkiray.onrender.com
GitHub: https://github.com/merawiyohannes/Yebetkiray---Rental-Platform

🚀 Complete Production-Ready Platform
✨ What's New in v2.0


✅ Payment Integration – Chapa gateway for featured property upgrades
✅ Real-time Messaging – Chat with attachments between users
✅ Advanced Property Management – Full CRUD with admin verification
✅ Review & Rating System – Build trust with verified reviews
✅ Smart Search – Filter by location, price, amenities, and more
✅ Notification System – Real-time alerts for messages and updates
✅ Saved Properties – Favorites system for tenants
✅ Admin Dashboard – Property verification and user management
✅ Fully Responsive – Mobile-first design for all devices

💰 Revenue Features
Featured Listings – Weekly/Monthly payment plans (500 ETB/1500 ETB)

Property Highlighting – Priority placement in search results

Verified Badges – Trust indicators for premium properties

🛠️ Tech Stack
Backend: Django 4.2, Python 3.12

Database: PostgreSQL (Supabase)

Payments: Chapa Payment Gateway

File Storage: Cloudinary

Frontend: Tailwind CSS, Alpine.js

Deployment: Render.com

Real-time: Django Channels (Coming Soon)

⚡ Quick Start
# 1. Clone repository
git clone https://github.com/merawiyohannes/Yebetkiray---Rental-Platform.git
cd yebetkiray

# 2. Setup environment
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver

🔧 Environment Variables

# Required for production
SECRET_KEY=your_django_secret_key
DEBUG=False

# Database (Supabase)
DATABASE_URL=postgresql://...

# File Storage (Cloudinary)
CLOUDINARY_URL=cloudinary://...

# Payments (Chapa)
CHAPA_SECRET_KEY=your_chapa_live_key
CHAPA_WEBHOOK_SECRET=your_webhook_secret

📱 User Roles

👨‍💼 Landlord
Create and manage property listings

Upload multiple property images

Upgrade to featured listings

Receive inquiries from tenants

Manage property availability

👨‍💻 Tenant
Browse available properties

Save favorite listings

Message landlords directly

Submit property reviews

Advanced search with filters

👑 Admin
Verify property listings

Manage user accounts

View platform analytics

Handle payment transactions

Platform moderation

💳 Payment Plans

Plan	    Price	    Duration	Features
Weekly	    500 ETB	    7 days   	Priority placement, Featured badge
Monthly	    1500 ETB	30 days 	All weekly features + Top positioning

🔍 Search Features

🔎 Location-based – Search by city, subcity, or neighborhood

💰 Price Range – Filter by monthly rent

🏠 Property Type – Apartment, House, Villa, Condo


⭐ Featured Only – Show only promoted properties

📞 Contact & Support

Email: merawiyohannes@gmail.com

Phone: +251 921 540 245

Location: Addis Ababa, Ethiopia

📈 Coming Soon
Mobile App (React Native)

Escrow Payment System

Rental Agreement Generator

SMS Notifications

📄 License
© 2023 Yebet Kiray. All rights reserved.

🚀 Ready for Production • 🏠 Connecting Ethiopia • 💰 Making Rentals Easy
