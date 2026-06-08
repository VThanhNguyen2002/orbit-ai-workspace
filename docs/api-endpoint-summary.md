# API Endpoint Summary

## 1. Purpose

This document lists the currently implemented local/demo API endpoints for the Synapse backend. It serves as a direct reference for portfolio review, CV preparation, and interview support, ensuring all claims about backend capabilities remain honest, accurate, and fully aligned with the project's intent.

---

## 2. Implemented Endpoint Table

| Method | Path | Capability | Demo Status | Notes / Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/health` | Service health status check | ✅ Fully tested | Returns standard health status `{"status": "ok"}` |
| **GET** | `/version` | Service and API version check | ✅ Fully tested | Returns app version and API contract version info |
| **POST** | `/v1/notes` | Create a new note | ✅ Fully tested | Accepts JSON payload; initializes version to `1`; user isolated |
| **GET** | `/v1/notes` | List user notes | ✅ Fully tested | Supports pagination, sorting (`updated_at`, `created_at`, `title`), order (`asc`, `desc`), archive filtering, and soft-delete inclusion |
| **GET** | `/v1/notes/{note_id}` | Retrieve note details | ✅ Fully tested | Returns note data; soft-deleted notes return `404`; user isolated |
| **PATCH** | `/v1/notes/{note_id}` | Update note details | ✅ Fully tested | Requires JSON payload & matching `version` to prevent write-conflict; returns `409 Conflict` on stale version |
| **DELETE** | `/v1/notes/{note_id}` | Soft-delete a note | ✅ Fully tested | Marks `is_deleted=true` and sets `deleted_at`; checks version conflict; soft-deleted note returns `404` on subsequent detail retrieval |
| **POST** | `/v1/ai/notes/{note_id}/summarize` | Summarize a note | ✅ Gated | Returns deterministic mock summary using `FakeProvider`; enabled only via env flag `SYNAPSE_AI_SUMMARIZATION_ENABLED=true` |
| **GET** | `/v1/ai/notes/{note_id}/summaries` | Retrieve summary history | ✅ Fully tested | Returns in-memory fake summary history sorted newest-first; memory-only state (resets on backend restart) |

---

## 3. What the Project Can Currently Demonstrate

*   **Health and Version Checks**: Service discovery/readiness checking routes returning structured JSON envelopes.
*   **Versioned Conflict Detection**: Lockless optimistic concurrency checking using a `version` field (rejects updates/deletes with `HTTP 409 Conflict` if the client version is stale).
*   **Soft-Delete Isolation**: Note deletion changes note metadata without data destruction, immediately hiding it from listing and detail requests (`HTTP 404 Not Found`).
*   **User Ownership Isolation**: Multi-tenant isolation where notes are scoped by `user_id`. Access to other users' note IDs returns `HTTP 404 Not Found` (rather than `HTTP 403 Forbidden`) to prevent resource enumeration.
*   **Fake-Provider Boundary**: Deterministic mock AI summarization showing safe boundary integration without introducing external dependencies, provider SDKs, or credentials.
*   **Summary History Ordering**: Retrieve previous summaries ordered newest-first (descending by timestamp).
*   **Zero-Dependency Local API Demo**: Run the 13-step bash/curl script (`scripts/demo-api.sh`) end-to-end to verify all backend paths, conflict detection, and isolation safeguards.

---

## 4. Deferred / Not Implemented API Surfaces

*   **Search**: The `/search` router is mounted as a placeholder only (Notes search/filter is deferred).
*   **Auth / Sync / Tasks / Voice Memos**: Mounted stubs exist as structural routers, but lack implementation.
*   **Live AI Provider**: The OpenAI SDK is **NOT APPROVED / DENIED**; no live API calls are implemented.
*   **Supabase / PostgreSQL / RLS**: The backend state is in-memory only; no database persistence or RLS policies are active.
*   **Rendered Mobile UI**: The `apps/mobile` package contains pure TypeScript view-state and Vitest tests; rendering/Expo UI is deferred.

---

## 5. Resume-Safe Endpoint Summary

### Vietnamese Version (Vietnamese CV / Interview)
> Thiết kế và phát triển RESTful API backend sử dụng **FastAPI (Python 3.11)** với các tính năng: CRUD ghi chú (Notes), phân quyền và cô lập tài nguyên theo người dùng, cơ chế soft-delete (ẩn ghi chú khỏi danh sách, trả về **HTTP 404** khi truy cập), và cơ chế phát hiện xung đột ghi đè dữ liệu (optimistic locking) trả về **HTTP 409 Conflict** khi version bị cũ. Hệ thống tích hợp module tóm tắt nội dung ghi chú thông qua một lớp fake-provider AI boundary để kiểm thử an toàn, cùng tính năng lưu trữ lịch sử tóm tắt theo thứ tự mới nhất. Toàn bộ API được kiểm thử tự động (pytest) và tích hợp kịch bản demo chạy local (`scripts/demo-api.sh`).

### English Version (English CV / LinkedIn / GitHub / Interview)
> Designed and built a versioned REST API with **FastAPI (Python 3.11)** featuring full Notes CRUD, multi-tenant user isolation, soft-delete isolation (returning **HTTP 404**), and optimistic concurrency control (returning **HTTP 409 Conflict** on version mismatch). Integrated a dependency-free, mock-provider AI summarization boundary with a newest-first summary history listing. The API surface is fully verified via automated tests (pytest) and a credential-free, 13-step local shell demo script (`scripts/demo-api.sh`).

---

## 6. Do-Not-Claim Reminders

When presenting this project:
*   **Do not claim** production AI or live OpenAI integration.
*   **Do not claim** a rendered mobile application (it is view-state TypeScript logic only).
*   **Do not claim** Supabase, Docker, or RLS database runtime usage.
*   **Do not claim** persistent database-backed notes or summary histories (everything is memory-only).
*   **Do not claim** a deployed production app or live URL.
