from pathlib import Path


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}


class InputClassifierError(Exception):
    """Raised when file type is unsupported or invalid."""
    pass


def classify(file_path: str) -> str:
    """
    Classify input file type based on extension.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: "pdf" or "image"

    Raises:
        InputClassifierError: If file type is unsupported or file does not exist.
    """
    path = Path(file_path)

    if not path.exists():
        raise InputClassifierError(f"File does not exist: {file_path}")

    ext = path.suffix.lower()

    if ext in SUPPORTED_PDF_EXTENSIONS:
        return "pdf"

    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"

    raise InputClassifierError(f"Unsupported file type: {ext}")