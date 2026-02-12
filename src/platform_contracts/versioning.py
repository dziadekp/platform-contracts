"""Schema versioning helpers."""

from pydantic import BaseModel, field_validator


class VersionedSchema(BaseModel):
    """Base schema with version validation."""

    schema_version: str = "1.0"

    @field_validator("schema_version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Invalid schema version format: {v}. Expected 'major.minor'.")
        return v

    def is_compatible(self, other_version: str) -> bool:
        """Check if major version matches (backward-compatible within major)."""
        my_major = self.schema_version.split(".")[0]
        other_major = other_version.split(".")[0]
        return my_major == other_major
