import { defineStore } from "pinia";
import api from "../services/api";

export const useContactsStore = defineStore("contacts", {
  state: () => ({
    contacts: [],
    selectedContact: null,

    search: "",
    page: 1,
    limit: 10,
    total: 0,

    view: "all",
    favorite: null,
    tag: "",
    sort: "name_asc",
    unlabeled: false,
    recent: false,
    tags: [],
    metrics: {
      total: 0,
      favorites: 0,
      recently_added: 0,
      unlabeled: 0,
    },
    selectedIds: [],

    loading: false,
    error: null,

    deleting: false,
  }),

  getters: {
    totalPages: (state) => Math.ceil(state.total / state.limit),

    favoriteContacts: (state) =>
      state.contacts.filter((contact) => contact.is_favorite),
  },

  actions: {

    setView(view) {
      this.view = view;
      this.favorite = view === "favorites" ? true : null;
      this.tag = view.startsWith("label:") ? view.slice(6) : "";
      this.page = 1;
    },

    setSort(sort) {
      this.sort = sort;
      this.page = 1;
    },

    setTag(tag) {
      this.tag = tag;
      this.favorite = null;
      this.view = tag ? `label:${tag}` : "all";
      this.page = 1;
    },

    async fetchContacts() {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get("/contacts/", {
          params: {
            search: this.search || undefined,
            favorite: this.favorite === null ? undefined : this.favorite,
            tag: this.tag || undefined,
            unlabeled: this.unlabeled || undefined,
            recent: this.recent || undefined,
            sort: this.sort,
            page: this.page,
            limit: this.limit,
          },
        });

        this.contacts = response.data.contacts;
        this.total = response.data.total;
      } catch (error) {
        console.error(error);
        this.error = "Unable to load contacts.";
      } finally {
        this.loading = false;
      }
    },

    async fetchTags() {
      const response = await api.get("/contacts/tags");
      this.tags = response.data;
      return this.tags;
    },

    async fetchMetrics() {
      const response = await api.get("/contacts/metrics");
      this.metrics = response.data;
      return this.metrics;
    },

    async createContact(contact) {
      try {
        const response = await api.post("/contacts/", contact);

        await this.fetchContacts();

        return response.data;
      } catch (error) {
        console.error(error);
        throw error;
      }
    },

    async updateContact(id, contact) {
      try {
        const response = await api.put(`/contacts/${id}`, contact);

        await this.fetchContacts();

        return response.data;
      } catch (error) {
        console.error(error);
        throw error;
      }
    },

    async deleteContact(id) {
      this.deleting = true;

      try {
        await api.delete(`/contacts/${id}`);

        await this.fetchContacts();
      } catch (error) {
        console.error(error);
        throw error;
      } finally {
        this.deleting = false;
      }
    },

    async restoreContact(contact) {
      try {
        const response = await api.post("/contacts/", {
          name: contact.name,
          phone_number: contact.phone_number,
          email: contact.email,
          address: contact.address,
        });

        await this.fetchContacts();

        return response.data;
      } catch (error) {
        console.error(error);
        throw error;
      }
    },

    async getContact(id) {
      const response = await api.get(`/contacts/${id}`);

      this.selectedContact = response.data;

      await this.markViewed(id);

      return response.data;
    },

    async markViewed(id) {
      const response = await api.patch(`/contacts/${id}/viewed`);
      const updatedContact = response.data;
      const index = this.contacts.findIndex((item) => item.id === id);

      if (index !== -1) {
        this.contacts[index] = updatedContact;
      }

      if (this.selectedContact?.id === id) {
        this.selectedContact = updatedContact;
      }

      return updatedContact;
    },

    async toggleFavorite(contact) {
    try {
      const response = await api.patch(
        `/contacts/${contact.id}/favorite`,
        {
          is_favorite: !contact.is_favorite,
        }
      );

      const updatedContact = response.data;

      const index = this.contacts.findIndex(
        (item) => item.id === updatedContact.id
      );

      if (index !== -1) {
        this.contacts[index] = updatedContact;
      }

      if (
        this.selectedContact &&
        this.selectedContact.id === updatedContact.id
      ) {
        this.selectedContact = updatedContact;
      }

      return updatedContact;
    } catch (error) {
      console.error(error);
      throw error;
    }
  },

  },
});