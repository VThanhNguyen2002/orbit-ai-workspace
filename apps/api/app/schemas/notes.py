from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

NoteContentType = Literal["plain", "markdown"]
NoteSortField = Literal["created_at", "updated_at", "title"]
SortOrder = Literal["asc", "desc"]


class Note(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=50_000)
    content_type: NoteContentType
    is_archived: bool
    is_deleted: bool
    created_at: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)
    deleted_at: str | None
    version: int = Field(ge=0)


class PaginationMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    has_next: bool


class ListNotesData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[Note]
    pagination: PaginationMeta


class CreateNoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=500)
    content: str = Field(default="", max_length=50_000)
    content_type: NoteContentType = "plain"


class UpdateNoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=500)
    content: str | None = Field(default=None, max_length=50_000)
    content_type: NoteContentType | None = None
    is_archived: bool | None = None
    version: int = Field(ge=0)

    @model_validator(mode="after")
    def require_mutable_field(self) -> "UpdateNoteRequest":
        mutable_fields = {"title", "content", "content_type", "is_archived"}
        for field_name in mutable_fields & self.model_fields_set:
            if getattr(self, field_name) is None:
                msg = f"{field_name} cannot be null"
                raise ValueError(msg)

        if not mutable_fields & self.model_fields_set:
            msg = "At least one mutable note field is required"
            raise ValueError(msg)

        return self


class DeleteNoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=0)
