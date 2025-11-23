#!/usr/bin/env python3
"""
OpenAPI Specification Generator
Generates the OpenAPI/Swagger specification from the FastAPI application
"""

import json
import os
import sys
from pathlib import Path

# Set up environment variables for spec generation (use SQLite to avoid DB connection)
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "spec-generation-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.main import app


def generate_openapi_spec(output_path: str = "openapi.json"):
    """
    Generate OpenAPI specification and save to file
    
    Args:
        output_path: Path where the OpenAPI spec will be saved
    """
    try:
        # Generate OpenAPI schema
        openapi_schema = app.openapi()
        
        # Save to file
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"✅ OpenAPI specification generated successfully!")
        print(f"📄 File: {output_file.absolute()}")
        print(f"📌 API Title: {openapi_schema.get('info', {}).get('title', 'N/A')}")
        print(f"📌 API Version: {openapi_schema.get('info', {}).get('version', 'N/A')}")
        print(f"📌 Total Endpoints: {len(openapi_schema.get('paths', {}))}")
        print(f"📌 Total Schemas: {len(openapi_schema.get('components', {}).get('schemas', {}))}")
        
        # List all endpoints
        print("\n📋 Available Endpoints:")
        for path, methods in openapi_schema.get('paths', {}).items():
            for method in methods.keys():
                if method not in ['parameters', 'summary', 'description']:
                    print(f"  {method.upper():8} {path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating OpenAPI specification: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Generate spec in the repository root
    output_path = backend_dir.parent.parent / "openapi.json"
    success = generate_openapi_spec(str(output_path))
    sys.exit(0 if success else 1)
