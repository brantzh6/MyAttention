"""
Pipeline Module - Automated information collection daemon
Runs as a background task inside the FastAPI lifespan.
"""

from .scheduler import PipelineScheduler

__all__ = ["PipelineScheduler"]
