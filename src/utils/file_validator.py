"""
File Validator Utility
Validates uploaded resume files before processing
"""

import os
import mimetypes
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger


class FileValidator:
    """
    Validates files for resume upload.
    Checks file extension, size, and MIME type.
    """
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    
    # Maximum file size (10 MB)
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # MIME type mappings
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/bmp',
        'image/tiff',
        'image/x-tiff'
    }
    
    @staticmethod
    def is_valid_file(file_path: str) -> bool:
        """
        Main validation method. Checks all validation rules.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return False
            
            # Check if it's a file (not directory)
            if not os.path.isfile(file_path):
                logger.error(f"Path is not a file: {file_path}")
                return False
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                logger.error(f"File is not readable: {file_path}")
                return False
            
            # Check extension
            if not FileValidator.has_valid_extension(file_path):
                logger.error(f"Invalid file extension: {file_path}")
                return False
            
            # Check file size
            if not FileValidator.is_file_size_valid(file_path):
                logger.error(f"File size exceeds limit: {file_path}")
                return False
            
            # Check MIME type
            if not FileValidator.has_valid_mime_type(file_path):
                logger.warning(f"MIME type check failed (may be false positive): {file_path}")
                # Don't return False for MIME type - can have false positives
            
            logger.info(f"File validation passed: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            return False
    
    @staticmethod
    def has_valid_extension(file_path: str) -> bool:
        """
        Check if file has a valid extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if extension is valid, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext in FileValidator.ALLOWED_EXTENSIONS
    
    @staticmethod
    def is_file_size_valid(file_path: str) -> bool:
        """
        Check if file size is within allowed limit.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if size is valid, False otherwise
        """
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= FileValidator.MAX_FILE_SIZE_BYTES
        except OSError as e:
            logger.error(f"Error getting file size: {e}")
            return False
    
    @staticmethod
    def has_valid_mime_type(file_path: str) -> bool:
        """
        Check if file MIME type matches extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if MIME type is valid, False otherwise
        """
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                # If MIME type cannot be determined, check by reading file header
                mime_type = FileValidator._detect_mime_from_header(file_path)
            
            return mime_type in FileValidator.ALLOWED_MIME_TYPES
        except Exception as e:
            logger.warning(f"Error checking MIME type: {e}")
            return False
    
    @staticmethod
    def _detect_mime_from_header(file_path: str) -> Optional[str]:
        """
        Detect MIME type by reading file header (magic numbers).
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected MIME type or None
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
            
            # PDF magic number
            if header.startswith(b'%PDF'):
                return 'application/pdf'
            
            # PNG magic number
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'image/png'
            
            # JPEG magic number
            elif header.startswith(b'\xff\xd8\xff'):
                return 'image/jpeg'
            
            # BMP magic number
            elif header.startswith(b'BM'):
                return 'image/bmp'
            
            # TIFF magic numbers
            elif header.startswith(b'II*\x00') or header.startswith(b'MM\x00*'):
                return 'image/tiff'
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting MIME from header: {e}")
            return None
    
    @staticmethod
    def is_pdf(file_path: str) -> bool:
        """
        Check if file is a PDF.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if PDF, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext == '.pdf'
    
    @staticmethod
    def is_image(file_path: str) -> bool:
        """
        Check if file is an image.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if image, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext in {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    
    @staticmethod
    def get_validation_error(file_path: str) -> str:
        """
        Get detailed validation error message.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Error message describing why file is invalid
        """
        # Check existence
        if not os.path.exists(file_path):
            return "File does not exist."
        
        if not os.path.isfile(file_path):
            return "Path is not a file."
        
        # Check readability
        if not os.access(file_path, os.R_OK):
            return "File is not readable. Check permissions."
        
        # Check extension
        if not FileValidator.has_valid_extension(file_path):
            ext = Path(file_path).suffix.lower()
            allowed = ', '.join(FileValidator.ALLOWED_EXTENSIONS)
            return f"Invalid file extension '{ext}'. Allowed: {allowed}"
        
        # Check size
        if not FileValidator.is_file_size_valid(file_path):
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return (f"File size ({file_size_mb:.2f} MB) exceeds maximum "
                   f"allowed size ({FileValidator.MAX_FILE_SIZE_MB} MB).")
        
        return "File validation passed."
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            path = Path(file_path)
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'filename': path.name,
                'extension': path.suffix.lower(),
                'size_bytes': size_bytes,
                'size_mb': round(size_mb, 2),
                'mime_type': mime_type,
                'is_valid': FileValidator.is_valid_file(file_path),
                'is_pdf': FileValidator.is_pdf(file_path),
                'is_image': FileValidator.is_image(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {'error': str(e)}


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Configure logger
    logger.add("logs/file_validator.log", rotation="10 MB")
    
    print("=" * 60)
    print("FILE VALIDATOR TEST")
    print("=" * 60)
    
    # Test with sample files (you'll need to create these for testing)
    test_files = [
        "sample_resume.pdf",  # Valid
        "sample_resume.png",  # Valid
        "sample_resume.txt",  # Invalid extension
        "large_file.pdf",     # May be too large
        "nonexistent.pdf"     # Doesn't exist
    ]
    
    for file_path in test_files:
        print(f"\nTesting: {file_path}")
        print(f"Valid: {FileValidator.is_valid_file(file_path)}")
        print(f"Error: {FileValidator.get_validation_error(file_path)}")
        
        if os.path.exists(file_path):
            info = FileValidator.get_file_info(file_path)
            print(f"Info: {info}")