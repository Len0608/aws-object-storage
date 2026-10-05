"""
OutputFormatter — formats List Objects and Upload File results for STDOUT and
Extension Output JSON.

Responsibilities
----------------
- Render object metadata as an ASCII table (``tabulate`` rounded_outline style).
- Produce a truncation notice when the displayed count is below the total.
- Build the ``result`` dicts consumed by the Extension Output JSON for both actions.
- Build the human-readable upload confirmation string for STDOUT.
"""
import logging

from tabulate import tabulate

logger = logging.getLogger("UNV")

_EMPTY_BUCKET_MESSAGE: str = "The bucket contains no objects."


class OutputFormatter:
    """
    Static helper class for formatting extension output.

    All methods are static — no instance state is required.
    """

    @staticmethod
    def format_objects_table(objects: list[dict]) -> str:
        """
        Render a list of S3 object metadata dicts as a ``rounded_outline`` ASCII table.

        Args:
            objects: List of dicts with keys ``key``, ``size``, and
                     ``last_modified``.

        Returns:
            A formatted ASCII table string, or a human-readable message when
            ``objects`` is empty.
        """
        if not objects:
            logger.debug("No objects to display; returning empty bucket message")
            return _EMPTY_BUCKET_MESSAGE

        rows: list[list] = [
            [obj["key"], obj["size"], obj["last_modified"]]
            for obj in objects
        ]
        logger.debug("Rendering object table with %d rows", len(rows))
        return tabulate(
            rows,
            headers=["Object Key", "Size (bytes)", "Last Modified"],
            tablefmt="rounded_outline",
        )

    @staticmethod
    def format_truncation_notice(displayed_count: int, total_count: int) -> str:
        """
        Return the truncation notice shown when STDOUT output is capped.

        Args:
            displayed_count: Number of objects included in the table.
            total_count:     Total number of objects in the bucket.

        Returns:
            A notice string; intended to be printed immediately after the table.
        """
        return (
            "Showing %d of %d objects. "
            "Set UE_MAX_OUTPUT_RECORDS to display more." % (displayed_count, total_count)
        )

    @staticmethod
    def build_list_objects_result(
        bucket: str,
        total_count: int,
        displayed_count: int,
        objects: list[dict],
    ) -> dict:
        """
        Build the Extension Output JSON ``result`` dict for the List Objects action.

        Args:
            bucket:          S3 bucket name.
            total_count:     Actual total number of objects in the bucket.
            displayed_count: Number of objects included in the ``objects`` array
                             (after applying the output cap).
            objects:         Capped list of object metadata dicts.

        Returns:
            A dict with keys ``bucket``, ``total_count``, ``displayed_count``,
            and ``objects``.
        """
        logger.debug(
            "Building list_objects result: bucket=%s total=%d displayed=%d",
            bucket,
            total_count,
            displayed_count,
        )
        return {
            "bucket": bucket,
            "total_count": total_count,
            "displayed_count": displayed_count,
            "objects": objects,
        }

    @staticmethod
    def build_upload_result(
        bucket: str,
        key: str,
        s3_uri: str,
        size_bytes: int,
    ) -> dict:
        """
        Build the Extension Output JSON ``result`` dict for the Upload File action.

        Args:
            bucket:     S3 bucket name.
            key:        S3 object key of the uploaded file.
            s3_uri:     Full S3 URI (``s3://bucket/key``).
            size_bytes: Size of the uploaded file in bytes.

        Returns:
            A dict with keys ``bucket``, ``key``, ``s3_uri``, and ``size_bytes``.
        """
        logger.debug(
            "Building upload result: s3_uri=%s size_bytes=%d",
            s3_uri,
            size_bytes,
        )
        return {
            "bucket": bucket,
            "key": key,
            "s3_uri": s3_uri,
            "size_bytes": size_bytes,
        }

    @staticmethod
    def format_upload_confirmation(
        local_file: str,
        s3_uri: str,
        file_size_bytes: int,
    ) -> str:
        """
        Build the human-readable upload confirmation string for STDOUT.

        Args:
            local_file:      Absolute path of the uploaded file on the agent host.
            s3_uri:          Full S3 URI of the uploaded object.
            file_size_bytes: Size of the uploaded file in bytes.

        Returns:
            A multi-line confirmation string.
        """
        return (
            "Upload successful.\n"
            "  Local file : %s\n"
            "  S3 URI     : %s\n"
            "  File size  : %d bytes" % (local_file, s3_uri, file_size_bytes)
        )
