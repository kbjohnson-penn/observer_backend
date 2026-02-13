# Observer Backend - Production Deployment Guide

## Server Information
- **Server**: observer-dev.pmacs.upenn.edu
- **OS**: RedHat Enterprise Linux
- **Location**: `/home/s_observerdev/observer_backend/`
- **User**: `s_observerdev`
- **Web Server**: Apache (managed by IT)
- **Database**: MariaDB (3 databases)
- **URL**: https://observer-dev.pmacs.upenn.edu/

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Deployment Steps](#deployment-steps)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Updating the Application](#updating-the-application)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## Prerequisites

### Server Access
- SSH access to observer-dev.pmacs.upenn.edu
- User account: `s_observerdev`
- Sudo privileges (for service restarts via IT)

### Required Software (should be pre-installed)
- Python 3.10 or higher
- MariaDB client libraries
- Apache with mod_wsgi
- Git

### Required Services
- **MariaDB Databases** (3 databases must be created):
  - `observer_accounts` - User authentication and accounts
  - `observer_clinical` - Clinical data
  - `observer_research` - Research data

- **Azure Storage Account** - For encounter file storage
  - Storage account name
  - Filesystem name
  - SAS token with read/write permissions

### Required Credentials
- Database username and password
- Azure Storage credentials
- Email SMTP credentials (for notifications)
- Django SECRET_KEY (generate new for production)

---

## Initial Setup

### 1. Connect to Server
```bash
ssh s_observerdev@observer-dev.pmacs.upenn.edu
```

### 2. Deploy Application Code
```bash
# Navigate to home directory
cd /home/s_observerdev/

# Clone repository (or copy files)
git clone <repository-url> observer_backend
# OR
# Use scp/rsync to copy files from development machine
```

### 3. Verify Directory Structure
```bash
cd /home/s_observerdev/observer_backend
ls -la
```

Expected structure:
```
observer_backend/
├── backend/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prd.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
├── clinical/
├── research/
├── shared/
├── deployment/
│   ├── deploy_simple.sh
│   ├── apache_observer.conf (reference only)
│   └── health_check.sh
├── scripts/
│   ├── server_side_cleandb.sh
│   └── server_side_import_data.sh
├── requirements.txt
├── manage.py
└── .env.production.template
```

---

## Deployment Steps

### Step 1: Configure Environment Variables

```bash
cd /home/s_observerdev/observer_backend

# Copy template to .env
cp .env.production.template .env

# Edit with your values
nano .env
```

**Important variables to configure:**
- `SECRET_KEY` - Generate using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `ALLOWED_HOSTS` - Set to `observer-dev.pmacs.upenn.edu`
- Database credentials (all 3 databases)
- Azure Storage credentials
- Email SMTP settings
- `FRONTEND_URL` and `CORS_ALLOWED_ORIGINS`

### Step 2: Run Deployment Script

For **first-time installation**:
```bash
cd /home/s_observerdev/observer_backend/deployment
chmod +x deploy_simple.sh
./deploy_simple.sh --fresh-install
```

The script will:
1. Create necessary directories
2. Set up Python virtual environment
3. Install dependencies from requirements.txt
4. Verify .env configuration
5. Run database migrations (all 3 databases)
6. Collect static files
7. Prompt to create superuser
8. Set proper file permissions

### Step 3: Verify Installation

Check that everything was created:
```bash
# Virtual environment exists
ls -la /home/s_observerdev/observer_backend/venv/

# Static files collected
ls -la /home/s_observerdev/observer_backend/static/

# Log directory exists
ls -la /home/s_observerdev/logs/
```

### Step 4: Restart Backend Service

**Contact IT** to restart the backend service, or if you have permission:
```bash
sudo systemctl restart observer-backend
sudo systemctl status observer-backend
```

### Step 5: Verify Deployment

Run the health check script:
```bash
cd /home/s_observerdev/observer_backend/deployment
./health_check.sh
```

Or manually test endpoints:
```bash
# Liveness check
curl https://observer-dev.pmacs.upenn.edu/health/liveness/

# Readiness check
curl https://observer-dev.pmacs.upenn.edu/health/readiness/

# API root
curl https://observer-dev.pmacs.upenn.edu/api/v1/
```

---

## Configuration

### Environment Variables Reference

See [.env.production.template](/.env.production.template) for complete list.

**Critical Production Settings:**
```bash
# Security
DEBUG=False
SECRET_KEY=<50+ character random string>
ALLOWED_HOSTS=observer-dev.pmacs.upenn.edu

# SSL/Security Headers
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Database credentials for all 3 databases
ACCOUNTS_DB_NAME=observer_accounts
ACCOUNTS_DB_USER=...
ACCOUNTS_DB_PASSWORD=...
# (repeat for CLINICAL and RESEARCH)

# Azure Storage
AZURE_STORAGE_ACCOUNT_NAME=...
AZURE_SAS_TOKEN=...

# Frontend Integration (IMPORTANT: Backend and Frontend are on different subdomains)
# Backend:  observer-dev.pmacs.upenn.edu
# Frontend: observer-dev-d.pmacs.upenn.edu
FRONTEND_URL=https://observer-dev-d.pmacs.upenn.edu
CSRF_TRUSTED_ORIGINS=https://observer-dev.pmacs.upenn.edu,https://observer-dev-d.pmacs.upenn.edu
CORS_ALLOWED_ORIGINS=https://observer-dev-d.pmacs.upenn.edu
```

### Django Settings

The application uses different settings modules:
- **Development**: `backend.settings.dev`
- **Production**: `backend.settings.prd`

Production settings location: [backend/settings/prd.py](/backend/settings/prd.py)

The `DJANGO_SETTINGS_MODULE` environment variable controls which settings are used.

---

## Database Setup

### Database Schema

The application uses **3 separate MariaDB databases**:

1. **observer_accounts** (port 3306)
   - Django auth models
   - User accounts
   - Sessions
   - Admin logs

2. **observer_clinical** (port 3306)
   - Clinical data
   - Patient records
   - Provider information
   - Encounters

3. **observer_research** (port 3306)
   - Research data
   - Analytics

### Creating Databases

**IT should create these databases:**
```sql
CREATE DATABASE observer_accounts CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE observer_clinical CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE observer_research CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user and grant permissions
CREATE USER 'observer_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON observer_accounts.* TO 'observer_user'@'localhost';
GRANT ALL PRIVILEGES ON observer_clinical.* TO 'observer_user'@'localhost';
GRANT ALL PRIVILEGES ON observer_research.* TO 'observer_user'@'localhost';
FLUSH PRIVILEGES;
```

### Running Migrations

Migrations are automatically run by the deployment script, but can be run manually:

```bash
cd /home/s_observerdev/observer_backend
source venv/bin/activate

# Migrate accounts database
python manage.py migrate --database=accounts

# Migrate clinical database
python manage.py migrate --database=clinical

# Migrate research database
python manage.py migrate --database=research
```

### Creating Superuser

```bash
cd /home/s_observerdev/observer_backend
source venv/bin/activate
python manage.py createsuperuser --database=accounts
```

### Importing Sample Data (Optional)

```bash
cd /home/s_observerdev/observer_backend
bash scripts/server_side_import_data.sh
```

### Database Backup

**Recommendation**: Set up automated daily backups via cron:
```bash
# Add to crontab
0 2 * * * /usr/bin/mysqldump -u observer_user -p'password' observer_accounts > /home/s_observerdev/backups/accounts_$(date +\%Y\%m\%d).sql
0 2 * * * /usr/bin/mysqldump -u observer_user -p'password' observer_clinical > /home/s_observerdev/backups/clinical_$(date +\%Y\%m\%d).sql
0 2 * * * /usr/bin/mysqldump -u observer_user -p'password' observer_research > /home/s_observerdev/backups/research_$(date +\%Y\%m\%d).sql
```

---

## Updating the Application

### Regular Updates (Code Changes)

```bash
cd /home/s_observerdev/observer_backend

# Pull latest changes (if using git)
git pull origin main

# Run update script
cd deployment
./deploy_simple.sh --update
```

The update script will:
1. Backup .env file (timestamped)
2. Update Python dependencies
3. Run new migrations
4. Collect static files
5. Set permissions

**Then contact IT to restart the service.**

### Updating Dependencies Only

```bash
cd /home/s_observerdev/observer_backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Running Migrations Only

```bash
cd /home/s_observerdev/observer_backend/deployment
./deploy_simple.sh --migrate
```

### Collecting Static Files Only

```bash
cd /home/s_observerdev/observer_backend/deployment
./deploy_simple.sh --static
```

---

## Troubleshooting

### 1. Application Not Starting

**Check service status:**
```bash
sudo systemctl status observer-backend
```

**Check application logs:**
```bash
tail -f /home/s_observerdev/logs/django_prd.log
tail -f /home/s_observerdev/logs/django_error.log
```

**Check Apache logs:**
```bash
sudo tail -f /var/log/httpd/error_log
sudo tail -f /var/log/httpd/access_log
```

### 2. Database Connection Errors

**Verify database credentials in .env:**
```bash
cd /home/s_observerdev/observer_backend
grep DB_ .env
```

**Test database connectivity:**
```bash
mysql -u observer_user -p -h localhost observer_accounts -e "SELECT 1;"
```

**Check database router:**
The application uses a custom database router in `shared/db_router.py`. Ensure migrations are run for each database.

### 3. Static Files Not Loading

**Verify static files were collected:**
```bash
ls -la /home/s_observerdev/observer_backend/static/
```

**Recollect static files:**
```bash
cd /home/s_observerdev/observer_backend
source venv/bin/activate
python manage.py collectstatic --noinput
```

**Check Apache configuration** (via IT):
- Verify `Alias /static/` directive points to correct path
- Check file permissions

### 4. Backend Admin Redirects to 127.0.0.1:8000

**Symptom:** When accessing `https://observer-dev.pmacs.upenn.edu/admin`, it redirects to `https://127.0.0.1:8000/admin`

**Root Cause:** The backend domain is missing from `CSRF_TRUSTED_ORIGINS` in your `.env` file.

**Solution:**

The application has backend and frontend on **different subdomains**:
- Backend: `observer-dev.pmacs.upenn.edu`
- Frontend: `observer-dev-d.pmacs.upenn.edu`

Your `.env` file **MUST** include the backend domain in `CSRF_TRUSTED_ORIGINS`:

```bash
# CORRECT Configuration (includes BOTH domains)
CSRF_TRUSTED_ORIGINS=https://observer-dev.pmacs.upenn.edu,https://observer-dev-d.pmacs.upenn.edu
```

**Why this happens:**
- `CSRF_TRUSTED_ORIGINS` validates the Origin/Referer headers in requests
- When you access `/admin` directly on the backend, Django checks if `observer-dev.pmacs.upenn.edu` is in `CSRF_TRUSTED_ORIGINS`
- If only the frontend domain is listed, Django rejects the request and redirects
- Including both domains allows both direct backend access and frontend API calls

**Complete cross-subdomain configuration:**
```bash
# Backend domain (where Django runs)
ALLOWED_HOSTS=observer-dev.pmacs.upenn.edu,localhost,127.0.0.1

# Frontend domain (where Next.js runs)
FRONTEND_URL=https://observer-dev-d.pmacs.upenn.edu

# BOTH domains for CSRF (critical!)
CSRF_TRUSTED_ORIGINS=https://observer-dev.pmacs.upenn.edu,https://observer-dev-d.pmacs.upenn.edu

# Only frontend for CORS (so frontend can call backend APIs)
CORS_ALLOWED_ORIGINS=https://observer-dev-d.pmacs.upenn.edu

# Backend documentation URL
DOCUMENTATION_URL=https://observer-dev.pmacs.upenn.edu/docs/
```

After updating `.env`, restart the backend service.

### 5. CORS/CSRF Errors

**Common issues:**
- Frontend and backend must use same domain scheme (both https)
- Cannot mix localhost and 127.0.0.1
- Check `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` in .env
- For cross-subdomain setups, ensure both domains are in `CSRF_TRUSTED_ORIGINS`

**Cross-subdomain authentication issues:**

If authentication cookies aren't working between frontend and backend, you may need to enable cookie domain sharing in `.env`:

```bash
# Allows cookies to be shared across *.pmacs.upenn.edu subdomains
SESSION_COOKIE_DOMAIN=.pmacs.upenn.edu
CSRF_COOKIE_DOMAIN=.pmacs.upenn.edu
```

**Warning:** This allows ALL `*.pmacs.upenn.edu` subdomains to access the cookies. Only enable if acceptable in your security policy.

### 6. Permission Errors

**Reset permissions:**
```bash
cd /home/s_observerdev/observer_backend
sudo chown -R s_observerdev:s_observerdev .
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;
chmod 775 media/
```

### 7. Azure Storage Errors

**Verify Azure credentials:**
```bash
cd /home/s_observerdev/observer_backend
source venv/bin/activate
python manage.py shell

# In Python shell:
from django.conf import settings
print(settings.AZURE_STORAGE_ACCOUNT_NAME)
print(settings.AZURE_STORAGE_FILE_SYSTEM_NAME)
# Don't print the SAS token!
```

**Check SAS token expiration:**
- SAS tokens expire and need to be regenerated
- Contact Azure admin for new token

### 8. Email Not Sending

**Test SMTP connection:**
```bash
cd /home/s_observerdev/observer_backend
source venv/bin/activate
python manage.py shell

# In Python shell:
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@email.com', ['to@email.com'])
```

**Common issues:**
- Gmail requires "App Passwords" (not regular password)
- Check firewall rules for outbound port 587

---

## Maintenance

### Log Rotation

Create logrotate configuration (see `deployment/logrotate.conf`):
```bash
sudo cp deployment/logrotate.conf /etc/logrotate.d/observer
```

### Monitoring

**Health Check Endpoints:**
- `/health/liveness/` - Basic application health
- `/health/readiness/` - Database and dependency checks
- `/health/` - Detailed health info (IP restricted)

**Set up monitoring service** to ping health endpoints every 5 minutes.

### Regular Maintenance Tasks

**Weekly:**
- Check log files for errors
- Verify backups are running
- Monitor disk space

**Monthly:**
- Review and rotate logs
- Update dependencies (security patches)
- Test backup restoration

**Quarterly:**
- Review Azure Storage usage
- Audit user accounts
- Update documentation

### Performance Optimization

**Database:**
- Review slow query logs
- Add indexes as needed
- Optimize frequently-run queries

**Application:**
- Consider adding Redis for caching
- Monitor memory usage
- Adjust worker processes if needed

### Security Updates

**Keep dependencies updated:**
```bash
cd /home/s_observerdev/observer_backend
source venv/bin/activate

# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt
```

---

## Important Files and Locations

| File/Directory | Location | Purpose |
|----------------|----------|---------|
| Application root | `/home/s_observerdev/observer_backend/` | Main application |
| Virtual environment | `/home/s_observerdev/observer_backend/venv/` | Python dependencies |
| Environment config | `/home/s_observerdev/observer_backend/.env` | Production settings |
| Static files | `/home/s_observerdev/observer_backend/static/` | CSS, JS, images |
| Media files | `/home/s_observerdev/observer_backend/media/` | User uploads |
| Application logs | `/home/s_observerdev/logs/` | Django logs |
| Apache logs | `/var/log/httpd/` | Web server logs |
| Deployment scripts | `/home/s_observerdev/observer_backend/deployment/` | Deployment automation |

---

## Quick Reference Commands

```bash
# Activate virtual environment
cd /home/s_observerdev/observer_backend
source venv/bin/activate

# Run management commands
python manage.py <command>

# Check Django configuration
python manage.py check --deploy

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate --database=accounts
python manage.py migrate --database=clinical
python manage.py migrate --database=research

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser --database=accounts

# Django shell
python manage.py shell

# Check deployment
./deployment/health_check.sh

# View logs
tail -f /home/s_observerdev/logs/django_prd.log
tail -f /home/s_observerdev/logs/django_error.log
```

---

## Support and Contact

**For deployment issues:**
- Check this documentation first
- Review application logs
- Contact IT for Apache/service issues

**For application bugs:**
- Check GitHub issues
- Review development documentation
- Contact development team

**Emergency contacts:**
- IT Support: [contact info]
- Database Admin: [contact info]
- Development Team: [contact info]

---

## Additional Resources

- [Development Guide](DEVELOPMENT.md)
- [Project README](README.md)
- [API Documentation](https://observer-dev.pmacs.upenn.edu/docs/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
