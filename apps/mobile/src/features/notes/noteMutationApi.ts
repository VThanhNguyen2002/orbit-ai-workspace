import type { NotesApi } from "@synapse/api-client";
import {
  NoteSchema,
  type CreateNoteRequest,
  type DeleteNoteRequest,
  type Note,
  type UpdateNoteRequest,
} from "@synapse/shared";

export type NoteMutationData = Note;
export type CreateNoteMutationPayload = CreateNoteRequest;
export type UpdateNoteMutationPayload = UpdateNoteRequest;
export type DeleteNoteMutationPayload = DeleteNoteRequest;

export type NoteMutationApiClient = {
  readonly notes: Pick<NotesApi, "create" | "update" | "delete">;
};

export type NoteMutationApi = {
  readonly createNote: (
    payload: CreateNoteMutationPayload,
  ) => Promise<NoteMutationData>;
  readonly updateNote: (
    noteId: string,
    payload: UpdateNoteMutationPayload,
  ) => Promise<NoteMutationData>;
  readonly deleteNote: (
    noteId: string,
    payload: DeleteNoteMutationPayload,
  ) => Promise<NoteMutationData>;
};

export function createNoteMutationApi(
  client: NoteMutationApiClient,
): NoteMutationApi {
  return {
    createNote: async (payload) => {
      const response = await client.notes.create(payload);
      return NoteSchema.parse(response.data);
    },
    updateNote: async (noteId, payload) => {
      const response = await client.notes.update(noteId, payload);
      return NoteSchema.parse(response.data);
    },
    deleteNote: async (noteId, payload) => {
      const response = await client.notes.delete(noteId, payload);
      return NoteSchema.parse(response.data);
    },
  };
}
