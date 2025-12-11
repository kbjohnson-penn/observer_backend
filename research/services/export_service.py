"""
Export Service for generating CSV and ZIP exports.

This service handles server-side generation of data exports,
ensuring consistent formatting and enabling audit logging.
"""

import csv
import io
import zipfile
from datetime import datetime
from typing import Any


class ExportService:
    """Service for generating CSV/ZIP exports of research data."""

    def generate_csv(
        self,
        table_id: str,
        data: list[dict[str, Any]],
        fieldnames: list[str] | None = None,
    ) -> str:
        """
        Generate CSV string from data.

        Args:
            table_id: Identifier for the table (used for logging/context)
            data: List of dictionaries representing rows
            fieldnames: Optional list of column names (used for empty tables)

        Returns:
            CSV formatted string
        """
        output = io.StringIO()

        # Determine fieldnames: from data, or from provided fieldnames
        if data:
            fields = list(data[0].keys())
        elif fieldnames:
            fields = fieldnames
        else:
            return ""

        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        if data:
            writer.writerows(data)
        return output.getvalue()

    def generate_zip(
        self,
        tables_data: dict[str, list[dict[str, Any]]],
        include_docs: bool = False,
        table_headers: dict[str, list[str]] | None = None,
    ) -> bytes:
        """
        Generate ZIP file with multiple CSV files.

        Args:
            tables_data: Dictionary mapping table_id to list of row dicts
            include_docs: Whether to include documentation README
            table_headers: Optional dict mapping table_id to list of column names
                          (used to generate headers for empty tables)

        Returns:
            ZIP file as bytes
        """
        buffer = io.BytesIO()
        table_headers = table_headers or {}

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for table_id, data in tables_data.items():
                # Get headers for this table (used if data is empty)
                fieldnames = table_headers.get(table_id)
                csv_content = self.generate_csv(table_id, data, fieldnames)
                zf.writestr(f"{table_id}.csv", csv_content)

            if include_docs:
                readme_content = self._generate_readme(tables_data)
                zf.writestr("README.txt", readme_content)

        buffer.seek(0)
        return buffer.getvalue()

    def _generate_readme(self, tables_data: dict[str, list[dict[str, Any]]]) -> str:
        """
        Generate documentation README for export.

        Args:
            tables_data: Dictionary mapping table_id to list of row dicts

        Returns:
            README content as string
        """
        lines = [
            "OBSERVER DATA EXPORT",
            "=" * 40,
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "CONTENTS",
            "-" * 40,
        ]

        total_records = 0
        for table_id, data in tables_data.items():
            record_count = len(data) if data else 0
            total_records += record_count
            lines.append(f"  {table_id}.csv: {record_count} records")

        lines.extend(
            [
                "",
                "-" * 40,
                f"Total records: {total_records}",
                f"Total tables: {len(tables_data)}",
                "",
                "NOTICE",
                "-" * 40,
                "This export contains Protected Health Information (PHI).",
                "Handle in accordance with HIPAA regulations.",
                "Do not share without proper authorization.",
            ]
        )

        return "\n".join(lines)
