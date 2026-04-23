<script setup>
import { ref } from 'vue';
import { ShieldAlert, Lock, ArrowRight } from 'lucide-vue-next';
import { api } from '../Api.js';
import { useAuth } from '../composables/useAuth.js';

const { fetchMe } = useAuth();

const newPassword = ref('');
const confirmPassword = ref('');
const error = ref('');
const submitting = ref(false);
const success = ref(false);

const submitForm = async () => {
  error.value = '';
  
  if (newPassword.value.length < 6) {
    error.value = 'La contraseña debe tener al menos 6 caracteres.';
    return;
  }
  
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden.';
    return;
  }
  
  submitting.value = true;
  
  try {
    await api.post('auth/change-password/', { new_password: newPassword.value });
    success.value = true;
    
    // Refresh user data so force_password_change becomes false
    await fetchMe();
  } catch (err) {
    error.value = 'Ocurrió un error al cambiar la contraseña. Intente nuevamente.';
  } finally {
    submitting.value = false;
  }
};
</script>

<template>
  <div class="fixed inset-0 bg-[#09090B]/90 backdrop-blur-md z-[100] flex items-center justify-center p-4 animate-in fade-in duration-300">
    <div class="bg-[#12131A] border border-red-500/20 shadow-2xl shadow-red-500/10 rounded-2xl w-full max-w-md overflow-hidden transform transition-all">
      
      <!-- Header -->
      <div class="px-6 py-8 text-center bg-red-500/5 border-b border-red-500/10">
        <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4 ring-4 ring-red-500/5">
          <ShieldAlert class="w-8 h-8 text-red-500" />
        </div>
        <h2 class="text-xl font-bold text-white mb-2">Acción Requerida</h2>
        <p class="text-slate-400 text-sm px-4">
          Por razones de seguridad, debes cambiar la contraseña temporal asignada a tu cuenta antes de poder acceder al sistema.
        </p>
      </div>
      
      <!-- Form Area -->
      <div class="p-6">
        <div v-if="success" class="text-center py-4">
          <div class="w-12 h-12 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-3">
            <ShieldAlert class="w-6 h-6 text-emerald-400" />
          </div>
          <h3 class="text-emerald-400 font-bold mb-1">¡Contraseña Actualizada!</h3>
          <p class="text-slate-400 text-sm mb-6">Iniciando sesión segura...</p>
        </div>
        
        <form v-else @submit.prevent="submitForm" class="space-y-4">
          <div v-if="error" class="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
            {{ error }}
          </div>
          
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Nueva Contraseña</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock class="h-4 w-4 text-slate-500" />
              </div>
              <input 
                v-model="newPassword" 
                type="password" 
                required
                placeholder="••••••••"
                class="w-full bg-[#0B0C10] border border-white/10 text-slate-200 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500 transition-all"
              />
            </div>
          </div>
          
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Confirmar Contraseña</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock class="h-4 w-4 text-slate-500" />
              </div>
              <input 
                v-model="confirmPassword" 
                type="password" 
                required
                placeholder="••••••••"
                class="w-full bg-[#0B0C10] border border-white/10 text-slate-200 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500 transition-all"
              />
            </div>
          </div>
          
          <button 
            type="submit" 
            :disabled="submitting"
            class="w-full mt-2 bg-red-500 hover:bg-red-600 text-white py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2 group"
          >
            <span v-if="submitting" class="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
            <span v-else>{{ 'Establecer Contraseña' }}</span>
            <ArrowRight v-if="!submitting" class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>
      </div>
      
    </div>
  </div>
</template>
