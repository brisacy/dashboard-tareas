<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../composables/useAuth.js";

const router = useRouter();
const { login, loadingUser } = useAuth();

const username = ref("");
const password = ref("");
const err = ref("");

async function onLogin() {
  err.value = "";
  try {
    await login(username.value, password.value);
    router.push("/dashboard"); // ✅ redirige
  } catch (e) {
    console.log("LOGIN ERROR:", e?.response?.data || e);
    err.value = e?.response?.data?.detail || "Login falló";
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-6 bg-[#12131A] relative overflow-hidden">
    <!-- Decoración de fondo sutil (opcional, imitando el borde angular de la imagen) -->
    <div class="absolute top-0 left-0 w-64 h-64 bg-white opacity-[0.02] transform -skew-x-12 -translate-x-32 -translate-y-32"></div>
    <div class="absolute bottom-0 right-0 w-64 h-64 bg-white opacity-[0.02] transform skew-x-12 translate-x-32 translate-y-32"></div>

    <div class="w-full max-w-[420px] bg-[#09090B] rounded-2xl p-10 shadow-2xl relative z-10 border border-white/5">
      <div class="mb-10">
        <h1 class="text-3xl font-bold text-white mb-2">Welcome Back</h1>
        <p class="text-sm text-gray-400">Log into your account</p>
      </div>

      <div class="space-y-6">
        <!-- E-mail / Username -->
        <div class="relative">
          <label class="block text-xs font-medium text-gray-500 mb-2">Username</label>
          <div class="relative flex items-center">
            <input 
              v-model="username"
              type="text" 
              class="w-full bg-transparent border-b border-gray-700 text-white pb-2 focus:outline-none focus:border-gray-500 transition-colors"
              placeholder="Your username"
            />
            <svg class="w-4 h-4 text-gray-500 absolute right-0 bottom-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"></path>
            </svg>
          </div>
        </div>

        <!-- Password -->
        <div class="relative">
          <label class="block text-xs font-medium text-gray-500 mb-2">Password</label>
          <div class="relative flex items-center">
            <input 
              v-model="password"
              type="password" 
              class="w-full bg-transparent border-b border-gray-700 text-white pb-2 focus:outline-none focus:border-gray-500 transition-colors"
              placeholder="Your password"
            />
            <button type="button" class="absolute right-0 bottom-3 focus:outline-none text-gray-500 hover:text-gray-300">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Extra options -->
        <div class="flex items-center justify-between mt-4">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input type="checkbox" class="w-4 h-4 rounded border-gray-700 bg-gray-900 text-yellow-500 focus:ring-yellow-500/20 focus:ring-offset-gray-900" />
            <span class="text-xs text-gray-400">Remember for 30 days</span>
          </label>
          <a href="#" class="text-xs text-[#E9C46A] hover:text-[#f4d17b] transition-colors">Forgot password</a>
        </div>

        <!-- Error Message -->
        <p v-if="err" class="text-red-400 text-xs mt-2">{{ err }}</p>

        <!-- Submit Button -->
        <button 
          @click="onLogin"
          :disabled="loadingUser"
          class="w-full mt-6 bg-[#1E2028] text-[#E9C46A] py-3 rounded-lg font-medium hover:bg-[#252832] transition-colors disabled:opacity-60 flex justify-center items-center"
        >
          {{ loadingUser ? "Ingresando..." : "Log In" }}
        </button>

        <!-- Social Login -->
        <div class="mt-8">
          <div class="flex items-center space-x-4">
            <span class="text-xs text-gray-500 whitespace-nowrap">Log in with</span>
            <div class="flex space-x-3 w-full">
              <button type="button" class="flex-1 flex justify-center items-center py-2 bg-[#1E2028] rounded-lg hover:bg-[#252832] transition-colors">
                <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.477 2 2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12c0-5.523-4.477-10-10-10z"></path>
                </svg>
              </button>
              <button type="button" class="flex-1 flex justify-center items-center py-2 bg-[#1E2028] rounded-lg hover:bg-[#252832] transition-colors">
                <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
              </button>
              <button type="button" class="flex-1 flex justify-center items-center py-2 bg-[#1E2028] rounded-lg hover:bg-[#252832] transition-colors">
                <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                  <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                  <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Footer link -->
        <div class="mt-8 text-xs text-gray-500">
          Don't have an account? 
          <router-link to="/register" class="text-[#E9C46A] hover:text-[#f4d17b] transition-colors ml-1 font-medium">Sign Up</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
