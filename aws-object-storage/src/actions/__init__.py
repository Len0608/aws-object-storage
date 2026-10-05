"""Actions module — business logic implementations for the AWS Object Storage extension."""

from actions.output import ActionOutput
from actions.list_objects import list_objects
from actions.upload_file import upload_file
from manager import ExtensionManager

extension_manager = ExtensionManager()

# Maps the action.value string (as sent by UAC) to the implementing function.
# Keys must match the option values defined in the template.json choice field.
ACTION_MAPPER = {
    "List Objects": list_objects,
    "Upload File": upload_file,
}
