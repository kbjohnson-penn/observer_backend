"""
Management command to cleanup expired JWT tokens from the blacklist.

Usage:
    python manage.py cleanup_tokens
    python manage.py cleanup_tokens --days 30  # Delete tokens older than 30 days

Schedule with cron:
    0 2 * * * cd /path/to/project && python manage.py cleanup_tokens
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class Command(BaseCommand):
    help = 'Cleanup expired JWT tokens from blacklist to prevent database bloat'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete tokens that expired more than N days ago (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        # Find expired tokens
        expired_tokens = OutstandingToken.objects.using('accounts').filter(
            expires_at__lt=cutoff_date
        )

        count = expired_tokens.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would delete {count} tokens expired before {cutoff_date}'
                )
            )
            return

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No expired tokens to cleanup')
            )
            return

        # Delete the tokens
        expired_tokens.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {count} expired tokens (older than {days} days)'
            )
        )
