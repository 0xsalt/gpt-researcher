"""
Debug logging utility for GPT Researcher.

Provides dual-output debug logging:
- Stdout: Emoji-enhanced messages for visual clarity
- File: Detailed timestamped logs for analysis
"""
import os
import sys
from datetime import datetime
from typing import Optional


class DebugLogger:
    """Debug logger with dual output (stdout emoji + file logging)."""

    def __init__(self, enabled: bool = False, log_file: Optional[str] = None):
        """
        Initialize debug logger.

        Args:
            enabled: Whether debug logging is enabled
            log_file: Path to log file (auto-generated if None and enabled)
        """
        self.enabled = enabled
        self.log_file = None
        self.file_handle = None

        if enabled:
            if log_file is None:
                # Auto-generate log filename with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d.%H%M.%S.%f")[:-3]  # milliseconds
                self.log_file = f"outputs/diagnostic_{timestamp}.log"
            else:
                self.log_file = log_file

            # Ensure outputs directory exists
            os.makedirs("outputs", exist_ok=True)

            # Open log file
            self.file_handle = open(self.log_file, "w", encoding="utf-8")
            self._write_header()

    def _write_header(self):
        """Write log file header."""
        if self.file_handle:
            header = f"""
{'='*80}
GPT Researcher Debug Log
Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}
{'='*80}

"""
            self.file_handle.write(header)
            self.file_handle.flush()

    def _format_timestamp(self) -> str:
        """Generate timestamp for log entries."""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

    def log(self, emoji: str, message: str, level: str = "INFO"):
        """
        Log a debug message to both stdout and file.

        Args:
            emoji: Emoji symbol for stdout display
            message: Log message content
            level: Log level (INFO, DEBUG, WARNING, ERROR)
        """
        if not self.enabled:
            return

        timestamp = self._format_timestamp()

        # Stdout: Emoji message
        stdout_msg = f"{emoji} {message}"
        print(stdout_msg, flush=True)

        # File: Detailed timestamped entry
        if self.file_handle:
            file_msg = f"[{timestamp}] {level}: {message}\n"
            self.file_handle.write(file_msg)
            self.file_handle.flush()

    def info(self, emoji: str, message: str):
        """Log info message."""
        self.log(emoji, message, "INFO")

    def debug(self, emoji: str, message: str):
        """Log debug message."""
        self.log(emoji, message, "DEBUG")

    def warning(self, emoji: str, message: str):
        """Log warning message."""
        self.log(emoji, message, "WARNING")

    def error(self, emoji: str, message: str):
        """Log error message."""
        self.log(emoji, message, "ERROR")

    def close(self):
        """Close log file handle."""
        if self.file_handle:
            footer = f"\n{'='*80}\nLog ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n{'='*80}\n"
            self.file_handle.write(footer)
            self.file_handle.close()
            self.file_handle = None

    def __del__(self):
        """Ensure file handle is closed on cleanup."""
        self.close()


# Global debug logger instance
_debug_logger: Optional[DebugLogger] = None


def initialize_debug_logger(enabled: bool = False, log_file: Optional[str] = None) -> DebugLogger:
    """
    Initialize global debug logger.

    Args:
        enabled: Whether debug logging is enabled
        log_file: Optional custom log file path

    Returns:
        DebugLogger instance
    """
    global _debug_logger
    if _debug_logger is not None:
        _debug_logger.close()
    _debug_logger = DebugLogger(enabled=enabled, log_file=log_file)
    return _debug_logger


def get_debug_logger() -> DebugLogger:
    """Get global debug logger instance."""
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = DebugLogger(enabled=False)
    return _debug_logger
