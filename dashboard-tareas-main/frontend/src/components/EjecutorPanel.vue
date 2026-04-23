<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { api } from "../Api.js";
import { useAuth } from "../composables/useAuth.js";
import draggable from "vuedraggable";
import { 
  MessageSquare, Clock, RotateCw, X, 
  CircleDashed, CircleDot, CheckCircle2, ChevronRight, Paperclip
} from "lucide-vue-next";

const { user } = useAuth();

const cargando = ref(false);
const err = ref("");

const tareas = ref([]);

// Kanban Columns State
const columns = ref({
  PENDIENTE: [],
  EN_PROGRESO: [],
  COMPLETADA: []
});

// For executor, the API already returns only their tasks.
const tareasFiltradas = computed(() => tareas.value);

// Update columns when tareas change
watch(tareasFiltradas, (newVal) => {
  columns.value.PENDIENTE = newVal.filter(t => t.estado === "PENDIENTE");
  columns.value.EN_PROGRESO = newVal.filter(t => t.estado === "EN_PROGRESO");
  columns.value.COMPLETADA = newVal.filter(t => t.estado === "COMPLETADA");
}, { immediate: true, deep: true });

const stats = computed(() => {
  return {
    total: tareasFiltradas.value.length,
    PENDIENTE: columns.value.PENDIENTE.length,
    EN_PROGRESO: columns.value.EN_PROGRESO.length,
    COMPLETADA: columns.value.COMPLETADA.length
  };
});

async function cargarMisTareas() {
  err.value = "";
  cargando.value = true;
  try {
    const { data } = await api.get("tasks/");
    tareas.value = Array.isArray(data) ? data : [];
  } catch (e) {
    err.value = "No se pudieron cargar tus tareas.";
  } finally {
    cargando.value = false;
  }
}

// Drag & Drop Handler
function onDragChange(event, newEstado) {
  if (event.added) {
    const tarea = event.added.element;
    cambiarEstado(tarea, newEstado);
  }
}

async function cambiarEstado(tarea, nuevoEstado) {
  const tareaLocal = tareas.value.find(t => t.id === tarea.id);
  if (tareaLocal) tareaLocal.estado = nuevoEstado; // Optimistic update
  
  if (tareaDetalle.value?.id === tarea.id) {
    tareaDetalle.value.estado = nuevoEstado;
  }

  try {
    await api.patch(`tasks/${tarea.id}/`, { estado: nuevoEstado });
  } catch (e) {
    if (tareaLocal) tareaLocal.estado = tarea.estado; // Revert
    err.value = "Error al actualizar estado.";
  }
}

// Drawer Detalles
const showDrawer = ref(false);
const tareaDetalle = ref(null);
const comentarios = ref([]);
const cargandoComentarios = ref(false);
const nuevoComentario = ref("");
const enviandoComentario = ref(false);

async function abrirDetalles(t) {
  tareaDetalle.value = { ...t };
  showDrawer.value = true;
  await cargarComentarios(t.id);
}

function cerrarDetalles() {
  showDrawer.value = false;
  tareaDetalle.value = null;
}

async function cargarComentarios(id) {
  cargandoComentarios.value = true;
  try {
    const { data } = await api.get(`tasks/${id}/comments/`);
    comentarios.value = Array.isArray(data) ? data : [];
  } catch (e) {
    comentarios.value = [];
  } finally {
    cargandoComentarios.value = false;
  }
}

const nuevoArchivo = ref(null);
const archivoInput = ref(null);

const handleFileUpload = (event) => {
  const selected = event.target.files[0];
  if (!selected) return;
  if (selected.size > 4 * 1024 * 1024) {
    alert("El archivo no puede pesar más de 4MB.");
    if (archivoInput.value) archivoInput.value.value = "";
    return;
  }
  nuevoArchivo.value = selected;
};

async function agregarComentario() {
  const texto = nuevoComentario.value.trim();
  if (!texto && !nuevoArchivo.value) return;
  if (!tareaDetalle.value) return;
  enviandoComentario.value = true;
  try {
    const formData = new FormData();
    if (texto) formData.append("texto", texto);
    if (nuevoArchivo.value) formData.append("archivo", nuevoArchivo.value);

    const { data } = await api.post(`tasks/${tareaDetalle.value.id}/comments/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    comentarios.value = Array.isArray(data) ? data : comentarios.value;
    nuevoComentario.value = "";
    nuevoArchivo.value = null;
    if (archivoInput.value) archivoInput.value.value = "";
  } catch (e) {
    // Error
  } finally {
    enviandoComentario.value = false;
  }
}

function formatFecha(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-AR", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

onMounted(cargarMisTareas);
</script>

<template>
  <div class="flex-1 flex flex-col h-full overflow-hidden">
    <!-- Top Bar -->
    <div class="shrink-0 flex flex-col md:flex-row justify-between items-center bg-[#09090B] border-b border-white/5 px-6 py-4">
      <div class="flex items-center gap-6">
        <div class="flex gap-4">
          <div class="text-center">
            <div class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Tus Tareas</div>
            <div class="text-lg font-semibold text-white">{{ stats.total }}</div>
          </div>
          <div class="w-px h-8 bg-white/10"></div>
          <div class="text-center">
            <div class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Pendiente</div>
            <div class="text-lg font-semibold text-yellow-500">{{ stats.PENDIENTE }}</div>
          </div>
          <div class="text-center">
            <div class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Progreso</div>
            <div class="text-lg font-semibold text-blue-500">{{ stats.EN_PROGRESO }}</div>
          </div>
          <div class="text-center">
            <div class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Lista</div>
            <div class="text-lg font-semibold text-emerald-500">{{ stats.COMPLETADA }}</div>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3 mt-4 md:mt-0">
        <button @click="cargarMisTareas" class="p-2 text-slate-400 hover:text-white bg-[#1E2028] rounded-lg border border-white/5 transition-colors" title="Refrescar">
          <RotateCw class="w-4 h-4" :class="{ 'animate-spin': cargando }" />
        </button>
      </div>
    </div>

    <!-- Kanban Board -->
    <div class="flex-1 overflow-x-auto overflow-y-hidden p-6">
      <div class="flex gap-6 h-full items-start min-w-[900px]">
        
        <!-- PENDIENTE COLUMN -->
        <div class="flex-1 flex flex-col max-h-full bg-[#12131A] rounded-xl border border-white/5 overflow-hidden">
          <div class="shrink-0 p-4 border-b border-white/5 flex items-center gap-2 bg-[#0d0e14]">
            <CircleDashed class="w-4 h-4 text-yellow-500" />
            <h3 class="font-semibold text-sm text-slate-200">Pendiente</h3>
            <span class="ml-auto bg-yellow-500/10 text-yellow-500 text-[10px] font-bold px-2 py-0.5 rounded-full">{{ stats.PENDIENTE }}</span>
          </div>
          <draggable 
            v-model="columns.PENDIENTE" 
            group="tareas" 
            item-key="id"
            class="flex-1 p-3 overflow-y-auto space-y-3 min-h-[150px]"
            ghost-class="opacity-40"
            @change="(e) => onDragChange(e, 'PENDIENTE')"
          >
            <template #item="{ element }">
              <div @click="abrirDetalles(element)" class="bg-[#1E2028] border border-white/5 p-4 rounded-lg cursor-pointer hover:border-slate-600 transition-colors shadow-sm group">
                <h4 class="font-medium text-sm text-slate-100 group-hover:text-blue-400 transition-colors">{{ element.titulo }}</h4>
                <p class="text-xs text-slate-500 mt-1 line-clamp-2">{{ element.descripcion || 'Sin descripción' }}</p>
                <div class="mt-4 flex items-center justify-between">
                  <span class="text-[10px] text-slate-500">De: {{ element.creada_por_username || 'Admin' }}</span>
                  <div class="flex items-center gap-1 text-slate-500">
                    <MessageSquare class="w-3 h-3" />
                  </div>
                </div>
              </div>
            </template>
          </draggable>
        </div>

        <!-- EN PROGRESO COLUMN -->
        <div class="flex-1 flex flex-col max-h-full bg-[#12131A] rounded-xl border border-white/5 overflow-hidden">
          <div class="shrink-0 p-4 border-b border-white/5 flex items-center gap-2 bg-[#0d0e14]">
            <CircleDot class="w-4 h-4 text-blue-500" />
            <h3 class="font-semibold text-sm text-slate-200">En Progreso</h3>
            <span class="ml-auto bg-blue-500/10 text-blue-500 text-[10px] font-bold px-2 py-0.5 rounded-full">{{ stats.EN_PROGRESO }}</span>
          </div>
          <draggable 
            v-model="columns.EN_PROGRESO" 
            group="tareas" 
            item-key="id"
            class="flex-1 p-3 overflow-y-auto space-y-3 min-h-[150px]"
            ghost-class="opacity-40"
            @change="(e) => onDragChange(e, 'EN_PROGRESO')"
          >
            <template #item="{ element }">
              <div @click="abrirDetalles(element)" class="bg-[#1E2028] border border-blue-500/20 p-4 rounded-lg cursor-pointer hover:border-blue-500/50 transition-colors shadow-sm group">
                <h4 class="font-medium text-sm text-slate-100 group-hover:text-blue-400 transition-colors">{{ element.titulo }}</h4>
                <p class="text-xs text-slate-500 mt-1 line-clamp-2">{{ element.descripcion || 'Sin descripción' }}</p>
                <div class="mt-4 flex items-center justify-between">
                  <span class="text-[10px] text-slate-500">De: {{ element.creada_por_username || 'Admin' }}</span>
                  <div class="flex items-center gap-1 text-slate-500">
                    <MessageSquare class="w-3 h-3" />
                  </div>
                </div>
              </div>
            </template>
          </draggable>
        </div>

        <!-- COMPLETADA COLUMN -->
        <div class="flex-1 flex flex-col max-h-full bg-[#12131A] rounded-xl border border-white/5 overflow-hidden">
          <div class="shrink-0 p-4 border-b border-white/5 flex items-center gap-2 bg-[#0d0e14]">
            <CheckCircle2 class="w-4 h-4 text-emerald-500" />
            <h3 class="font-semibold text-sm text-slate-200">Completada</h3>
            <span class="ml-auto bg-emerald-500/10 text-emerald-500 text-[10px] font-bold px-2 py-0.5 rounded-full">{{ stats.COMPLETADA }}</span>
          </div>
          <draggable 
            v-model="columns.COMPLETADA" 
            group="tareas" 
            item-key="id"
            class="flex-1 p-3 overflow-y-auto space-y-3 min-h-[150px]"
            ghost-class="opacity-40"
            @change="(e) => onDragChange(e, 'COMPLETADA')"
          >
            <template #item="{ element }">
              <div @click="abrirDetalles(element)" class="bg-[#1E2028] border border-emerald-500/20 opacity-80 p-4 rounded-lg cursor-pointer hover:opacity-100 hover:border-emerald-500/40 transition-all shadow-sm group">
                <h4 class="font-medium text-sm text-slate-100 line-through decoration-slate-600">{{ element.titulo }}</h4>
                <p class="text-xs text-slate-500 mt-1 line-clamp-2">{{ element.descripcion || 'Sin descripción' }}</p>
                <div class="mt-4 flex items-center justify-between">
                  <span class="text-[10px] text-slate-500">De: {{ element.creada_por_username || 'Admin' }}</span>
                  <div class="text-[10px] text-emerald-500/70 font-medium flex items-center gap-1">
                    <CheckCircle2 class="w-3 h-3" /> Hecho
                  </div>
                </div>
              </div>
            </template>
          </draggable>
        </div>

      </div>
    </div>

    <!-- Side Drawer (Task Details) -->
    <div v-if="showDrawer" class="fixed inset-0 z-50 overflow-hidden flex justify-end">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="cerrarDetalles"></div>
      
      <!-- Panel -->
      <div class="relative w-full max-w-md bg-[#0B0C10] border-l border-white/5 h-full flex flex-col shadow-2xl transform transition-transform animate-in slide-in-from-right duration-200">
        
        <!-- Drawer Header -->
        <div class="shrink-0 p-5 border-b border-white/5 flex items-start justify-between bg-[#15161A]">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="text-[10px] uppercase font-bold tracking-wider text-slate-500">Task Details</span>
              <span class="bg-blue-500/10 text-blue-400 text-[10px] px-2 py-0.5 rounded-full border border-blue-500/20">
                {{ tareaDetalle.estado }}
              </span>
            </div>
            <h2 class="text-xl font-bold text-white leading-tight">{{ tareaDetalle.titulo }}</h2>
          </div>
          <button @click="cerrarDetalles" class="p-2 bg-[#1E2028] hover:bg-slate-800 rounded-lg text-slate-400 transition-colors">
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Drawer Body -->
        <div class="flex-1 overflow-y-auto p-5 space-y-6">
          
          <!-- Properties -->
          <div class="bg-[#15161A] border border-white/5 rounded-xl p-4 space-y-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-sm text-slate-400">
                <Clock class="w-4 h-4" /> Actualizada
              </div>
              <span class="text-sm text-slate-200">{{ formatFecha(tareaDetalle.actualizada_en) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-sm text-slate-400">
                <CircleDashed class="w-4 h-4" /> Creador
              </div>
              <span class="text-sm text-slate-200">{{ tareaDetalle.creada_por_username || 'Admin' }}</span>
            </div>
          </div>

          <!-- Description -->
          <div>
            <h4 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Descripción</h4>
            <div class="bg-[#1E2028] border border-white/5 rounded-xl p-4 text-sm text-slate-300 whitespace-pre-wrap min-h-[100px]">
              {{ tareaDetalle.descripcion || 'Sin descripción provista.' }}
            </div>
          </div>

          <!-- Comments -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Comentarios</h4>
              <button @click="cargarComentarios(tareaDetalle.id)" class="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                <RotateCw class="w-3 h-3" :class="{'animate-spin': cargandoComentarios}" /> Actualizar
              </button>
            </div>
            
            <div class="space-y-3">
              <div v-if="comentarios.length === 0" class="text-sm text-slate-500 italic text-center py-4 bg-[#15161A] rounded-xl border border-white/5">
                No hay comentarios todavía.
              </div>
              <div 
                v-for="c in comentarios" :key="c.id" 
                class="bg-[#1E2028] border rounded-xl p-3"
                :class="c.author_rol === 'ADMIN' ? 'border-blue-500/20' : 'border-white/5'"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-semibold text-slate-200">{{ c.author_username }}</span>
                    <span v-if="c.author_rol === 'ADMIN'" class="text-[9px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-1.5 py-0.5 rounded-full uppercase font-bold">Admin</span>
                  </div>
                  <span class="text-[10px] text-slate-500">{{ formatFecha(c.creada_en) }}</span>
                </div>
                <p v-if="c.texto" class="text-sm text-slate-300">{{ c.texto }}</p>
                <!-- Archivo Adjunto -->
                <div v-if="c.archivo" class="mt-2">
                  <img 
                    v-if="c.archivo.match(/\.(jpeg|jpg|gif|png)$/i)" 
                    :src="c.archivo" 
                    class="rounded-lg max-h-32 object-cover cursor-pointer hover:opacity-90"
                    @click="window.open(c.archivo, '_blank')"
                  />
                  <a 
                    v-else 
                    :href="c.archivo" 
                    target="_blank" 
                    class="flex items-center gap-2 w-max p-2 rounded bg-black/20 hover:bg-black/40 text-xs font-medium text-slate-300"
                  >
                    <Paperclip class="w-3 h-3" /> Ver Archivo Adjunto
                  </a>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Drawer Footer (Add Comment) -->
        <div class="shrink-0 p-5 border-t border-white/5 bg-[#15161A] flex flex-col gap-2">
          <div v-if="nuevoArchivo" class="px-3 py-1.5 bg-[#1E2028] border border-white/10 rounded-lg flex items-center justify-between">
            <span class="text-xs text-slate-300 truncate max-w-[200px]">{{ nuevoArchivo.name }}</span>
            <button @click="nuevoArchivo = null; archivoInput.value = ''" class="text-slate-500 hover:text-red-400">
              <X class="w-4 h-4" />
            </button>
          </div>
          <div class="flex gap-2">
            <button @click="$refs.archivoInput.click()" class="p-2 text-slate-400 hover:text-blue-400 rounded-lg hover:bg-blue-500/10 shrink-0">
              <Paperclip class="w-5 h-5" />
            </button>
            <input type="file" ref="archivoInput" class="hidden" @change="handleFileUpload" accept="image/*,.pdf" />

            <input 
              v-model="nuevoComentario"
              @keyup.enter="agregarComentario"
              type="text" 
              placeholder="Escribe un comentario..." 
              class="flex-1 bg-[#1E2028] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500/50"
            />
            <button 
              @click="agregarComentario"
              :disabled="(!nuevoComentario.trim() && !nuevoArchivo) || enviandoComentario"
              class="bg-blue-600 hover:bg-blue-500 text-white rounded-lg p-2 disabled:opacity-50 transition-colors"
            >
              <ChevronRight class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
