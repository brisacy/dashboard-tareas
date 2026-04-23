<script setup>
import { computed, onMounted, ref } from "vue";
import { useAuth } from "../composables/useAuth.js";
import { useNotifications } from "../composables/useNotifications.js";
import ChatWidget from "../components/ChatWidget.vue";
import ForcePasswordModal from "../components/ForcePasswordModal.vue";
import { 
  Bell, X, MessageSquare, RefreshCw, UserCheck, 
  LayoutDashboard, History, Users, BarChart2, 
  PanelLeftClose, PanelLeft, LogOut
} from "lucide-vue-next";
import { useRoute } from "vue-router";

const { user, role, logout, mustChangePassword } = useAuth();
const { notifications, unreadCount, markAllAsRead, initNotifications } = useNotifications();
const route = useRoute();

const isAdmin = computed(() => role.value === "ADMIN");

const showNotifications = ref(false);
const isSidebarCollapsed = ref(false);

function toggleNotifications() {
  showNotifications.value = !showNotifications.value;
  if (showNotifications.value) {
    markAllAsRead();
  }
}

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
}

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("es-AR", { hour: '2-digit', minute: '2-digit' });
}

onMounted(() => {
  initNotifications();
});

const links = computed(() => {
  const baseLinks = [
    { name: 'Tablero', to: '/dashboard', icon: LayoutDashboard }
  ];
  
  if (isAdmin.value) {
    baseLinks.push({ name: 'Auditoría', to: '/dashboard/audit', icon: History });
    baseLinks.push({ name: 'Equipo', to: '/dashboard/equipo', icon: Users });
    baseLinks.push({ name: 'Reportes', to: '/dashboard/reportes', icon: BarChart2 });
  }
  
  return baseLinks;
});
</script>

<template>
  <div class="h-screen flex bg-[#0B0C10] text-slate-100 font-sans overflow-hidden">
    
    <!-- Sidebar -->
    <aside 
      class="shrink-0 bg-[#12131A] border-r border-white/5 flex flex-col transition-all duration-300 z-20"
      :class="isSidebarCollapsed ? 'w-20' : 'w-64'"
    >
      <!-- Logo Area -->
      <div class="h-16 flex items-center px-4 border-b border-white/5 shrink-0" :class="isSidebarCollapsed ? 'justify-center' : 'justify-between'">
        <div v-if="!isSidebarCollapsed" class="flex items-center gap-2 overflow-hidden">
          <div class="w-8 h-8 shrink-0 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold text-lg ring-1 ring-blue-500/30 shadow-[0_0_15px_rgba(37,99,235,0.2)]">
            WE
          </div>
          <h1 class="text-lg font-semibold tracking-wide truncate">WorkSpace</h1>
        </div>
        <div v-else class="w-8 h-8 shrink-0 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold text-lg ring-1 ring-blue-500/30 shadow-[0_0_15px_rgba(37,99,235,0.2)]">
          WE
        </div>
        
        <!-- Toggle button -->
        <button v-if="!isSidebarCollapsed" @click="toggleSidebar" class="p-1.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
          <PanelLeftClose class="w-5 h-5" />
        </button>
      </div>
      
      <!-- Nav Links -->
      <nav class="flex-1 py-4 flex flex-col gap-1 px-3 overflow-y-auto">
        <div v-if="isSidebarCollapsed" class="flex justify-center mb-2">
          <button @click="toggleSidebar" class="p-1.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors" title="Expandir menú">
            <PanelLeft class="w-5 h-5" />
          </button>
        </div>
        
        <router-link 
          v-for="link in links" :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group relative"
          :class="route.path === link.to ? 'bg-blue-600/10 text-blue-400 ring-1 ring-blue-500/20' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'"
          :title="isSidebarCollapsed ? link.name : ''"
        >
          <component :is="link.icon" class="w-5 h-5 shrink-0" :class="route.path === link.to ? 'text-blue-400' : 'text-slate-400 group-hover:text-slate-200'" />
          <span v-if="!isSidebarCollapsed" class="font-medium text-sm truncate">{{ link.name }}</span>
          
          <!-- Tooltip for collapsed mode -->
          <div v-if="isSidebarCollapsed" class="absolute left-full ml-4 px-2 py-1 bg-[#1E2028] text-white text-xs rounded border border-white/10 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
            {{ link.name }}
          </div>
        </router-link>
      </nav>

      <!-- User Profile (Bottom) -->
      <div class="shrink-0 border-t border-white/5 p-4 flex flex-col gap-3">
        <div class="flex items-center gap-3" :class="isSidebarCollapsed ? 'justify-center' : ''">
          <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center shrink-0 uppercase font-bold text-slate-300 text-sm border border-white/10">
            {{ user?.username?.charAt(0) || 'U' }}
          </div>
          <div v-if="!isSidebarCollapsed" class="flex flex-col min-w-0">
            <span class="text-xs font-medium text-slate-200 truncate">@{{ user?.username }}</span>
            <span class="text-[10px] text-slate-500 uppercase tracking-wider truncate">{{ user?.rol }}</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0">
      
      <!-- Top Header -->
      <header class="h-16 shrink-0 flex items-center justify-end px-6 border-b border-white/5 bg-[#09090B] z-10 relative">
        <div class="flex items-center gap-4">
          
          <!-- Notification Bell -->
          <button 
            @click="toggleNotifications"
            class="relative p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors focus:outline-none"
            title="Notificaciones"
          >
            <Bell class="w-5 h-5" />
            <span 
              v-if="unreadCount > 0" 
              class="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[9px] font-bold flex items-center justify-center rounded-full ring-2 ring-[#09090B]"
            >
              {{ unreadCount > 9 ? '9+' : unreadCount }}
            </span>
          </button>

          <!-- Logout Button -->
          <button 
            class="flex items-center gap-2 rounded-lg bg-[#1E2028] px-3 py-1.5 text-sm font-medium hover:bg-[#252832] transition-colors ring-1 ring-white/5 shadow-sm text-slate-300 hover:text-red-400" 
            @click="logout"
            title="Cerrar Sesión"
          >
            <LogOut class="w-4 h-4" />
            <span class="hidden sm:inline">Salir</span>
          </button>
        </div>
      </header>

      <!-- Router View Container -->
      <main class="flex-1 overflow-hidden relative">
        <router-view />
      </main>
      
    </div>

    <!-- Notifications Drawer -->
    <div 
      v-if="showNotifications" 
      class="absolute top-0 right-0 h-full w-80 bg-[#12131A] border-l border-white/5 shadow-2xl flex flex-col z-40 transform transition-transform animate-in slide-in-from-right duration-200"
    >
      <div class="shrink-0 p-4 border-b border-white/5 flex items-center justify-between bg-[#15161A]">
        <h2 class="font-semibold text-white flex items-center gap-2">
          <Bell class="w-4 h-4 text-slate-400" /> Notificaciones
        </h2>
        <button @click="toggleNotifications" class="p-1 text-slate-400 hover:text-white rounded-md hover:bg-white/5">
          <X class="w-4 h-4" />
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-3 space-y-2">
        <div v-if="notifications.length === 0" class="text-center p-6 text-sm text-slate-500">
          No tienes notificaciones recientes.
        </div>
        
        <div 
          v-for="(n, i) in notifications" :key="i"
          class="p-3 rounded-lg border text-sm"
          :class="n.type === 'DIRECT' ? 'bg-[#1E2028] border-blue-500/30' : 'bg-[#15161A] border-white/5 opacity-80'"
        >
          <div class="flex gap-3">
            <div class="shrink-0 mt-0.5">
              <MessageSquare v-if="n.action === 'NEW_COMMENT'" class="w-4 h-4 text-blue-400" />
              <RefreshCw v-else-if="n.action === 'STATUS_CHANGE'" class="w-4 h-4 text-yellow-400" />
              <UserCheck v-else-if="n.action === 'ASSIGNMENT'" class="w-4 h-4 text-emerald-400" />
              <Bell v-else class="w-4 h-4 text-slate-400" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-slate-200 text-[13px] leading-snug">{{ n.message }}</p>
              <div class="mt-1 flex items-center justify-between">
                <span class="text-[10px] font-medium px-1.5 py-0.5 rounded-full"
                  :class="n.type === 'DIRECT' ? 'bg-blue-500/10 text-blue-400' : 'bg-white/5 text-slate-400'"
                >
                  {{ n.type === 'DIRECT' ? 'Para ti' : 'General' }}
                </span>
                <span class="text-[10px] text-slate-500">{{ formatDate(n.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Global Chat Widget -->
    <ChatWidget />
    
    <!-- Force Password Change Modal -->
    <ForcePasswordModal v-if="mustChangePassword" />
    
  </div>
</template>
