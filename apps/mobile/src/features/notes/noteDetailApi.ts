import type { NotesApi } from "@synapse/api-client";
import { NoteSchema, type Note } from "@synapse/shared";

export type NoteDetailData = Note;

export type NoteDetailApiClient = {
  readonly notes: Pick<NotesApi, "get">;
};

export type NoteDetailApi = {
  readonly getNote: (noteId: string) => Promise<NoteDetailData>;
};

export function createNoteDetailApi(
  client: NoteDetailApiClient,
): NoteDetailApi {
  return {
    getNote: async (noteId) => {
      const response = await client.notes.get(noteId);
      return NoteSchema.parse(response.data);
    },
  };
}
