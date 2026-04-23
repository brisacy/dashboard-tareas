<script setup>
import { computed } from "vue";
import { useAuth } from "../composables/useAuth.js";
import AdminPanel from "../components/AdminPanel.vue";
import EjecutorPanel from "../components/EjecutorPanel.vue";

const { user, role } = useAuth();
const isAdmin = computed(() => role.value === "ADMIN");
const isEjecutor = computed(() => role.value === "EJECUTOR");
</script>

<template>
  <div class="h-full flex flex-col bg-[#0B0C10] text-slate-100 overflow-hidden">
    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col overflow-hidden relative">
      <AdminPanel v-if="isAdmin" class="flex-1 flex flex-col overflow-hidden" />
      <EjecutorPanel v-else-if="isEjecutor" class="flex-1 flex flex-col overflow-hidden" />
      <div v-else class="flex-1 flex items-center justify-center p-6">
        <div class="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center shadow-lg">
          <svg class="w-12 h-12 text-red-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          <p class="text-red-300 text-lg font-medium">Unrecognized Role: <b>{{ user?.rol }}</b></p>
          <p class="text-red-400/70 text-sm mt-1">Please contact an administrator.</p>
        </div>
      </div>
    </main>
  </div>
</template>
