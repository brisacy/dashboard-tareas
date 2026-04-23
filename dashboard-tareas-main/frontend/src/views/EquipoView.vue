<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../Api.js';
import { Users, Plus, X, UserPlus, Mail, Shield, CheckCircle2, User as UserIcon } from 'lucide-vue-next';

const users = ref([]);
const loading = ref(true);

const showSlideover = ref(false);
const submitting = ref(false);
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  rol: 'EJECUTOR'
});

const formError = ref('');
const successMessage = ref('');

const fetchUsers = async () => {
  loading.value = true;
  try {
    const { data } = await api.get('users/executors/');
    users.value = data;
  } catch (error) {
    console.error("Error cargando equipo:", error);
  } finally {
    loading.value = false;
  }
};

const openSlideover = () => {
  form.value = { first_name: '', last_name: '', email: '', rol: 'EJECUTOR' };
  formError.value = '';
  successMessage.value = '';
  showSlideover.value = true;
};

const closeSlideover = () => {
  showSlideover.value = false;
};

const submitForm = async () => {
  submitting.value = true;
  formError.value = '';
  try {
    await api.post('users/create/', form.value);
    successMessage.value = 'Usuario creado exitosamente. Se ha enviado un correo con la contraseña temporal.';
    fetchUsers(); // Refresh list
    setTimeout(() => {
      closeSlideover();
    }, 3000);
  } catch (error) {
    if (error.response?.data) {
      const msgs = [];
      for (const [key, value] of Object.entries(error.response.data)) {
        msgs.push(`${key}: ${Array.isArray(value) ? value.join(' ') : value}`);
      }
      formError.value = msgs.join(' | ');
    } else {
      formError.value = 'Error al crear el usuario. Intente nuevamente.';
    }
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<template>
  <div class="h-full bg-[#0B0C10] flex flex-col font-sans text-slate-100 overflow-hidden relative">
    <!-- Header -->
    <header class="shrink-0 h-16 border-b border-white/5 bg-[#09090B] flex items-center justify-between px-6">
      <h1 class="text-xl font-bold flex items-center gap-2">
        <Users class="w-5 h-5 text-emerald-400" /> Miembros del Equipo
      </h1>
      <button 
        @click="openSlideover"
        class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-emerald-500/20"
      >
        <Plus class="w-4 h-4" /> Nuevo Miembro
      </button>
    </header>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto p-6">
      <div class="bg-[#12131A] rounded-xl border border-white/5 overflow-hidden shadow-xl max-w-6xl mx-auto">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="bg-[#1A1C23] border-b border-white/5 uppercase text-xs font-semibold text-slate-500 tracking-wider">
            <tr>
              <th class="px-6 py-4">Usuario</th>
              <th class="px-6 py-4">Email</th>
              <th class="px-6 py-4">Rol</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5 text-slate-300">
            <tr v-if="loading && users.length === 0">
              <td colspan="3" class="px-6 py-8 text-center text-slate-500">Cargando equipo...</td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="3" class="px-6 py-8 text-center text-slate-500">No hay miembros en el equipo.</td>
            </tr>
            <tr 
              v-for="user in users" :key="user.id"
              class="hover:bg-white/[0.02] transition-colors"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center uppercase font-bold text-slate-300 text-xs border border-white/10">
                    {{ user.username.charAt(0) }}
                  </div>
                  <div class="flex flex-col">
                    <span class="font-medium text-slate-200">@{{ user.username }}</span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-slate-400">{{ user.email }}</td>
              <td class="px-6 py-4">
                <span 
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wide uppercase border"
                  :class="user.rol === 'ADMIN' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'"
                >
                  {{ user.rol }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- Overlay -->
    <div 
      v-if="showSlideover"
      class="absolute inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
      @click="closeSlideover"
    ></div>

    <!-- Slide-over panel -->
    <div 
      v-if="showSlideover"
      class="absolute top-0 right-0 h-full w-full max-w-md bg-[#12131A] border-l border-white/5 shadow-2xl z-50 transform transition-transform duration-300 flex flex-col animate-in slide-in-from-right"
    >
      <div class="shrink-0 px-6 py-5 border-b border-white/5 flex items-center justify-between bg-[#15161A]">
        <h2 class="text-lg font-bold text-white flex items-center gap-2">
          <UserPlus class="w-5 h-5 text-emerald-400" /> Crear Usuario
        </h2>
        <button @click="closeSlideover" class="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="successMessage" class="mb-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm flex gap-3 items-start">
          <CheckCircle2 class="w-5 h-5 shrink-0" />
          <p>{{ successMessage }}</p>
        </div>

        <form v-else @submit.prevent="submitForm" class="space-y-5">
          <div v-if="formError" class="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {{ formError }}
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Nombre</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <UserIcon class="h-4 w-4 text-slate-500" />
                </div>
                <input 
                  v-model="form.first_name" 
                  type="text" 
                  required
                  class="w-full bg-[#0B0C10] border border-white/10 text-slate-200 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                  placeholder="Ej. Juan"
                />
              </div>
            </div>
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Apellido</label>
              <input 
                v-model="form.last_name" 
                type="text" 
                required
                class="w-full bg-[#0B0C10] border border-white/10 text-slate-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                placeholder="Ej. Pérez"
              />
            </div>
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Correo Electrónico</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail class="h-4 w-4 text-slate-500" />
              </div>
              <input 
                v-model="form.email" 
                type="email" 
                required
                class="w-full bg-[#0B0C10] border border-white/10 text-slate-200 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm"
                placeholder="juan@empresa.com"
              />
            </div>
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Rol de Acceso</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Shield class="h-4 w-4 text-slate-500" />
              </div>
              <select 
                v-model="form.rol"
                class="w-full bg-[#0B0C10] border border-white/10 text-slate-200 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all text-sm appearance-none"
              >
                <option value="EJECUTOR">Ejecutor</option>
                <option value="ADMIN">Superadmin</option>
              </select>
            </div>
          </div>

          <div class="pt-4 border-t border-white/5">
            <button 
              type="submit" 
              :disabled="submitting"
              class="w-full bg-emerald-500 hover:bg-emerald-600 text-white py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 flex justify-center items-center gap-2"
            >
              <span v-if="submitting" class="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
              {{ submitting ? 'Creando Usuario...' : 'Crear Usuario Seguro' }}
            </button>
            <p class="text-[11px] text-slate-500 text-center mt-3">
              El sistema generará una contraseña segura aleatoria y la enviará por correo electrónico automáticamente.
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
