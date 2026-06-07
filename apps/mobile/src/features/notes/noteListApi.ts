import type { NotesApi } from "@synapse/api-client";
import {
  ListNotesDataSchema,
  type ListNotesRequest,
  type Note,
  type PaginationMeta,
} from "@synapse/shared";

export type NoteListData = {
  readonly items: readonly Note[];
  readonly pagination: PaginationMeta;
};
export type NoteListItemData = NoteListData["items"][number];
export type NoteListPaginationData = NoteListData["pagination"];
export type NoteListQuery = Partial<ListNotesRequest>;

export type NoteListApiClient = {
  readonly notes: Pick<NotesApi, "list">;
};

export type NoteListApi = {
  readonly listNotes: (query?: NoteListQuery) => Promise<NoteListData>;
};

export function createNoteListApi(client: NoteListApiClient): NoteListApi {
  return {
    listNotes: async (query) => {
      const response = await client.notes.list(query);
      return ListNotesDataSchema.parse(response.data);
    },
  };
}
