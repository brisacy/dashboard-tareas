<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../Api.js';
import { ArrowLeft, History, RefreshCw, MessageSquare, CheckCircle2, UserCheck } from 'lucide-vue-next';
import { useRouter } from 'vue-router';

const router = useRouter();
const logs = ref([]);
const cargando = ref(true);

const cargarAuditoria = async () => {
  cargando.value = true;
  try {
    const { data } = await api.get('audit/');
    logs.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("Error al cargar auditoría:", error);
  } finally {
    cargando.value = false;
  }
};

const formatDate = (iso) => {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-AR", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"
  });
};

onMounted(() => {
  cargarAuditoria();
});
</script>

<template>
  <div class="h-full bg-[#0B0C10] flex flex-col font-sans text-slate-100 overflow-hidden">
    <!-- Header -->
    <header class="shrink-0 h-16 border-b border-white/5 bg-[#09090B] flex items-center justify-between px-6">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold flex items-center gap-2">
          <History class="w-5 h-5 text-blue-500" /> Registro de Auditoría
        </h1>
      </div>
      <button 
        @click="cargarAuditoria" 
        class="flex items-center gap-2 text-sm text-slate-400 hover:text-white bg-[#1E2028] px-3 py-1.5 rounded-lg border border-white/5 transition-colors"
      >
        <RefreshCw class="w-4 h-4" :class="{'animate-spin': cargando}" /> Actualizar
      </button>
    </header>

    <!-- Tabla -->
    <main class="flex-1 overflow-y-auto p-6">
      <div class="bg-[#12131A] rounded-xl border border-white/5 overflow-hidden shadow-xl max-w-6xl mx-auto">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="bg-[#1A1C23] border-b border-white/5 uppercase text-xs font-semibold text-slate-500 tracking-wider">
            <tr>
              <th class="px-6 py-4">Fecha y Hora</th>
              <th class="px-6 py-4">Usuario</th>
              <th class="px-6 py-4">Acción</th>
              <th class="px-6 py-4 w-full">Detalles (Tarea)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5 text-slate-300">
            <tr v-if="cargando && logs.length === 0">
              <td colspan="4" class="px-6 py-8 text-center text-slate-500">Cargando registros...</td>
            </tr>
            <tr v-else-if="logs.length === 0">
              <td colspan="4" class="px-6 py-8 text-center text-slate-500">No hay registros de auditoría.</td>
            </tr>
            <tr 
              v-for="log in logs" :key="log.id"
              class="hover:bg-white/[0.02] transition-colors"
            >
              <td class="px-6 py-4 text-xs text-slate-500">{{ formatDate(log.timestamp) }}</td>
              <td class="px-6 py-4 font-medium text-slate-200">@{{ log.actor_username }}</td>
              <td class="px-6 py-4">
                <span 
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wide uppercase border"
                  :class="{
                    'bg-blue-500/10 text-blue-400 border-blue-500/20': log.action === 'NEW_COMMENT',
                    'bg-yellow-500/10 text-yellow-500 border-yellow-500/20': log.action === 'STATUS_CHANGE',
                    'bg-emerald-500/10 text-emerald-400 border-emerald-500/20': log.action === 'ASSIGNMENT',
                    'bg-slate-500/10 text-slate-400 border-slate-500/20': !['NEW_COMMENT', 'STATUS_CHANGE', 'ASSIGNMENT'].includes(log.action)
                  }"
                >
                  <MessageSquare v-if="log.action === 'NEW_COMMENT'" class="w-3 h-3" />
                  <RefreshCw v-else-if="log.action === 'STATUS_CHANGE'" class="w-3 h-3" />
                  <UserCheck v-else-if="log.action === 'ASSIGNMENT'" class="w-3 h-3" />
                  {{ log.action.replace('_', ' ') }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-col gap-0.5">
                  <span class="text-white font-medium text-[13px] truncate max-w-lg">{{ log.task_title || 'Tarea Eliminada/Desconocida' }}</span>
                  <span class="text-xs text-slate-500 truncate max-w-lg">
                    <template v-if="log.action === 'STATUS_CHANGE'">
                      Cambió de <b class="text-slate-300">{{ log.details.old }}</b> a <b class="text-slate-300">{{ log.details.new }}</b>
                    </template>
                    <template v-else-if="log.action === 'ASSIGNMENT'">
                      Asignó la tarea a <b class="text-slate-300">@{{ log.details.new_user || 'nadie' }}</b>
                    </template>
                    <template v-else-if="log.action === 'NEW_COMMENT'">
                      "{{ log.details.texto }}"
                    </template>
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>
