import logging
import time
from functools import wraps
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Registry for lazy-loaded ML services to avoid reinitializing models."""

    def __init__(self):
        self._services: dict[str, Any] = {}
        self._initialized: dict[str, bool] = {}

    def register(self, name: str, factory_fn):
        self._services[name] = factory_fn
        self._initialized[name] = False

    def get(self, name: str) -> Any:
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered")
        if not self._initialized[name]:
            logger.info(f"Initializing service: {name}")
            start = time.time()
            self._services[name] = self._services[name]()
            self._initialized[name] = True
            logger.info(f"Service '{name}' initialized in {time.time() - start:.2f}s")
        return self._services[name]


registry = ServiceRegistry()
