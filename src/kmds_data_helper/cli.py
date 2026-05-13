"""Backward-compatible CLI shim.

The canonical implementation lives in helper_output_adapter.py.
"""

from .helper_output_adapter import ingest_helper_output, main

__all__ = ["ingest_helper_output", "main"]


if __name__ == "__main__":
	raise SystemExit(main())