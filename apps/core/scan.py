import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class ResumeScanProvider(Protocol):
    def scan(self, file_path: str) -> None: ...


class NoOpScanProvider:
    def scan(self, file_path: str) -> None:
        logger.debug("NoOpScanProvider: skipping scan for %s", file_path)
