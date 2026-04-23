import { ref, computed } from "vue";
import { api, setAuthToken } from "../Api.js";

const accessToken = ref(localStorage.getItem("access") || "");
const user = ref(null);
const loadingUser = ref(false);

const isAuthenticated = computed(() => !!accessToken.value);
const role = computed(() => user.value?.rol || null);
const mustChangePassword = computed(() => user.value?.force_password_change || false);

if (accessToken.value) setAuthToken(accessToken.value);

async function fetchMe() {
  if (!accessToken.value) {
    user.value = null;
    return null;
  }

  loadingUser.value = true;
  try {
    const { data } = await api.get("auth/me/");
    user.value = data;
    return data;
  } catch (e) {
    // token inválido/expirado
    accessToken.value = "";
    user.value = null;
    localStorage.removeItem("access");
    setAuthToken(null);
    return null;
  } finally {
    loadingUser.value = false;
  }
}

async function login(username, password) {
  const { data } = await api.post("auth/login/", { username, password });

  accessToken.value = data.access;
  localStorage.setItem("access", data.access);
  setAuthToken(data.access);

  await fetchMe();
  return user.value;
}

function logout() {
  accessToken.value = "";
  user.value = null;
  localStorage.removeItem("access");
  setAuthToken(null);
}

export function useAuth() {
  return {
    accessToken,
    user,
    role,
    isAuthenticated,
    loadingUser,
    mustChangePassword,
    login,
    fetchMe,
    logout,
  };
}
