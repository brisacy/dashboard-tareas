import { api } from "../Api.js";

export const TaskApi = {
  async getExecutors() {
    const { data } = await api.get("users/executors/");
    return data;
  },

  async getTasks() {
    const { data } = await api.get("tasks/");
    return data;
  },

  async createTask(payload) {
    const { data } = await api.post("tasks/", payload);
    return data;
  },

  async updateTask(id, payload) {
    const { data } = await api.patch(`tasks/${id}/`, payload);
    return data;
  },
};
