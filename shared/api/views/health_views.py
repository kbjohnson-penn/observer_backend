"""
Health check endpoints for monitoring service availability and database connectivity.
Used by load balancers, monitoring systems, and deployment pipelines.

Security:
- Simple liveness check is public (minimal information)
- Detailed health check requires IP whitelisting (internal monitoring only)
"""

import ipaddress
import logging

from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class LivenessCheckView(APIView):
    """
    Simple liveness check - Public endpoint.

    Returns only basic "alive" status with no sensitive information.
    Used by external monitoring services and load balancers for basic availability checks.

    Returns:
        200 OK: Application is running
    """

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """Simple alive check with no sensitive information."""
        return Response({"status": "alive"}, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """
    Detailed health check - IP Whitelisted endpoint.

    Checks database connectivity and returns detailed status.
    Only accessible from whitelisted IPs (load balancers, internal monitoring).

    Configuration:
        Add to settings: HEALTH_CHECK_ALLOWED_IPS = ['127.0.0.1', '10.0.0.0/8']

    Returns:
        200 OK: Service is healthy and all databases are accessible
        403 Forbidden: Request from non-whitelisted IP
        503 Service Unavailable: Service is unhealthy (database issues)
    """

    permission_classes = []
    authentication_classes = []

    def get_client_ip(self, request):
        """Extract client IP from request, handling proxy headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Get the first IP in the chain (original client)
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def is_ip_allowed(self, client_ip, allowed_ips):
        """
        Check if client IP is in the allowed list.
        Supports both individual IPs and CIDR notation.
        """
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)

            for allowed in allowed_ips:
                try:
                    # Check if it's a network (CIDR notation)
                    if "/" in allowed:
                        network = ipaddress.ip_network(allowed, strict=False)
                        if client_ip_obj in network:
                            return True
                    else:
                        # Individual IP address
                        if client_ip_obj == ipaddress.ip_address(allowed):
                            return True
                except ValueError:
                    logger.warning(f"Invalid IP/network in whitelist: {allowed}")
                    continue

            return False
        except ValueError:
            logger.error(f"Invalid client IP address: {client_ip}")
            return False

    def get(self, request):
        """
        Perform health checks on all system components.
        Only accessible from whitelisted IPs.
        """
        # Get whitelisted IPs from settings
        allowed_ips = getattr(
            settings,
            "HEALTH_CHECK_ALLOWED_IPS",
            [
                "127.0.0.1",  # Localhost
                "::1",  # IPv6 localhost
            ],
        )

        # Check if request is from allowed IP
        client_ip = self.get_client_ip(request)
        if not self.is_ip_allowed(client_ip, allowed_ips):
            logger.warning(f"Health check access denied from IP: {client_ip}")
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

        # Perform health checks
        health_status = {"status": "healthy", "checks": {}}

        # Check each database connection
        databases_to_check = ["accounts", "clinical", "research"]

        for db_name in databases_to_check:
            try:
                # Attempt to establish connection
                conn = connections[db_name]
                conn.ensure_connection()

                # Execute a simple query to verify database is responsive
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                health_status["checks"][f"{db_name}_db"] = "healthy"

            except OperationalError as e:
                logger.error(f"Database {db_name} health check failed: {str(e)}")
                health_status["status"] = "unhealthy"
                health_status["checks"][f"{db_name}_db"] = "unhealthy"

            except Exception as e:
                logger.error(f"Unexpected error checking {db_name} database: {str(e)}")
                health_status["status"] = "unhealthy"
                health_status["checks"][f"{db_name}_db"] = "error"

        # Determine HTTP status code
        status_code = (
            status.HTTP_200_OK
            if health_status["status"] == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(health_status, status=status_code)


class ReadinessCheckView(APIView):
    """
    Readiness check - IP Whitelisted endpoint.

    Used by Kubernetes/container orchestration to determine if service
    is ready to accept traffic. Can include additional readiness criteria
    beyond just being alive.

    Security: Same IP whitelist as health check.
    """

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """
        Check if service is ready to accept traffic.
        Delegates to health check for now.
        """
        health_view = HealthCheckView()
        return health_view.get(request)
