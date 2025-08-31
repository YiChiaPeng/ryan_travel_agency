"""Package initializer for backend.app

This module intentionally does not create a Flask app. The project
was migrated to FastAPI; the ASGI application lives in `app.main`.
"""

__all__ = ["main", "routes", "models", "services", "utils"]