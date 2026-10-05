"""ActionOutput dataclass for action return values."""

from dataclasses import dataclass
from typing import Optional, Any, Dict, List

from utility.output_formatter import OutputFormatter


@dataclass
class ActionOutput:
    """Output from action functions.

    Holds result data for both List Objects and Upload File actions.
    print_output() renders STDOUT; to_dict() builds the Extension Output JSON
    result object.  There are no stdout_options / output_options control fields
    in the template, so both methods always include all available data.
    """

    # Shared field
    bucket: Optional[str] = None

    # List Objects result fields
    total_count: Optional[int] = None
    displayed_count: Optional[int] = None
    objects: Optional[List[Dict[str, Any]]] = None

    # Upload File result fields
    key: Optional[str] = None
    s3_uri: Optional[str] = None
    size_bytes: Optional[int] = None
    local_file: Optional[str] = None

    # Control fields — not present in template; default empty list means
    # print / include everything (per action_output.md fallback behaviour)
    stdout_options: Optional[List[str]] = None
    output_options: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Initialise control fields with empty-list defaults."""
        if self.stdout_options is None:
            self.stdout_options = []
        if self.output_options is None:
            self.output_options = []

    def print_output(self) -> None:
        """Print action results to STDOUT.

        Delegates formatting to OutputFormatter utilities.  The branch that
        executes is determined by which fields are populated:
        - objects is not None  → List Objects output
        - s3_uri is not None   → Upload File output
        """
        if self.objects is not None:
            # List Objects: render ASCII table
            table = OutputFormatter.format_objects_table(self.objects)
            print(table)

            if (
                self.displayed_count is not None
                and self.total_count is not None
                and self.displayed_count < self.total_count
            ):
                notice = OutputFormatter.format_truncation_notice(
                    self.displayed_count, self.total_count
                )
                print(notice)

        elif self.s3_uri is not None and self.local_file is not None:
            # Upload File: render upload confirmation
            confirmation = OutputFormatter.format_upload_confirmation(
                local_file=self.local_file,
                s3_uri=self.s3_uri,
                file_size_bytes=self.size_bytes or 0,
            )
            print(confirmation)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for Extension Output (unv_output result object).

        No output_options control field exists in the template, so all
        available data is always included.

        Returns:
            Dict matching the Extension Output JSON result structure defined in
            the analysis document.
        """
        if self.objects is not None:
            # List Objects result structure
            return OutputFormatter.build_list_objects_result(
                bucket=self.bucket or "",
                total_count=self.total_count or 0,
                displayed_count=self.displayed_count or 0,
                objects=self.objects,
            )

        if self.s3_uri is not None:
            # Upload File result structure
            return OutputFormatter.build_upload_result(
                bucket=self.bucket or "",
                key=self.key or "",
                s3_uri=self.s3_uri,
                size_bytes=self.size_bytes or 0,
            )

        return {}
