import os
import subprocess

apps = [
    'accounts', 'properties', 'bookings', 'payments', 
    'reviews', 'messaging', 'search', 'notifications',
    'analytics', 'content', 'media', 'locations',
    'support', 'api', 'core', 'tasks'
]

for app in apps:
    subprocess.run(['python', 'manage.py', 'startapp', app])
    print(f'✅ Created: {app}')

print('🎉 All 16 apps created!')