"""
Management command to cleanup expired tokens from the database.

Cleans up:
- JWT tokens from the blacklist
- Password reset tokens (expired or used)
- Email verification tokens (expired or used)

Usage:
    python manage.py cleanup_tokens
    python manage.py cleanup_tokens --days 30  # Delete tokens older than 30 days

Schedule with cron:
    0 2 * * * cd /path/to/project && python manage.py cleanup_tokens
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from accounts.models.user_models import EmailVerificationToken, PasswordResetToken


class Command(BaseCommand):
    help = "Cleanup expired tokens from database to prevent bloat"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Delete tokens that expired more than N days ago (default: 7)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        total_deleted = 0

        # 1. Cleanup JWT tokens
        jwt_count = self._cleanup_jwt_tokens(cutoff_date, dry_run)
        total_deleted += jwt_count

        # 2. Cleanup password reset tokens
        password_reset_count = self._cleanup_password_reset_tokens(cutoff_date, dry_run)
        total_deleted += password_reset_count

        # 3. Cleanup email verification tokens
        email_verification_count = self._cleanup_email_verification_tokens(cutoff_date, dry_run)
        total_deleted += email_verification_count

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Total tokens that would be deleted: {total_deleted}"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"\nTotal tokens deleted: {total_deleted}"))

    def _cleanup_jwt_tokens(self, cutoff_date, dry_run):
        """Cleanup expired JWT tokens from blacklist."""
        expired_tokens = OutstandingToken.objects.using("accounts").filter(
            expires_at__lt=cutoff_date
        )
        count = expired_tokens.count()

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY RUN] JWT tokens: Would delete {count}"))
        elif count > 0:
            expired_tokens.delete()
            self.stdout.write(self.style.SUCCESS(f"JWT tokens: Deleted {count}"))
        else:
            self.stdout.write("JWT tokens: None to cleanup")

        return count

    def _cleanup_password_reset_tokens(self, cutoff_date, dry_run):
        """Cleanup expired or used password reset tokens."""
        # Delete tokens that are used OR expired
        expired_or_used = PasswordResetToken.objects.using("accounts").filter(
            expires_at__lt=cutoff_date
        ) | PasswordResetToken.objects.using("accounts").filter(is_used=True)

        count = expired_or_used.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] Password reset tokens: Would delete {count}")
            )
        elif count > 0:
            expired_or_used.delete()
            self.stdout.write(self.style.SUCCESS(f"Password reset tokens: Deleted {count}"))
        else:
            self.stdout.write("Password reset tokens: None to cleanup")

        return count

    def _cleanup_email_verification_tokens(self, cutoff_date, dry_run):
        """Cleanup expired or used email verification tokens."""
        # Delete tokens that are used OR expired
        expired_or_used = EmailVerificationToken.objects.using("accounts").filter(
            expires_at__lt=cutoff_date
        ) | EmailVerificationToken.objects.using("accounts").filter(is_used=True)

        count = expired_or_used.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] Email verification tokens: Would delete {count}")
            )
        elif count > 0:
            expired_or_used.delete()
            self.stdout.write(self.style.SUCCESS(f"Email verification tokens: Deleted {count}"))
        else:
            self.stdout.write("Email verification tokens: None to cleanup")

        return count
