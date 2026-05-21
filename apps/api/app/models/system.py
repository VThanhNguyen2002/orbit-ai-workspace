from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: str = Field(min_length=1)


class VersionData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service: str = Field(min_length=1)
    version: str = Field(min_length=1)
    api_version: str = Field(min_length=1)
