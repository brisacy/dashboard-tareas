<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { api } from '../Api.js';
import { MessageCircle, X, Send, Paperclip, Smile } from 'lucide-vue-next';
import { useAuth } from '../composables/useAuth.js';

const { user } = useAuth();
const isOpen = ref(false);
const messages = ref([]);
const newMessage = ref("");
const file = ref(null);
const fileInput = ref(null);
const messagesContainer = ref(null);
const isTypingUsers = ref(new Set());
const hasUnread = ref(false);
const showEmojis = ref(false);
let typingTimeout = null;
let ws = null;

const toggleChat = async () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    hasUnread.value = false;
    await loadMessages();
    scrollToBottom();
    if (!ws) connectWebSocket();
  } else {
    showEmojis.value = false;
  }
};

const loadMessages = async () => {
  try {
    const { data } = await api.get('chat/');
    messages.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("Error cargando mensajes", error);
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const connectWebSocket = () => {
  const token = localStorage.getItem('access');
  if (!token) return;

  ws = new WebSocket(`ws://localhost:8000/ws/chat/?token=${token}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === "chat_message") {
      messages.value.push(data.message);
      if (!isOpen.value) {
        hasUnread.value = true;
      } else {
        scrollToBottom();
      }
      
      // Si el que mandó el mensaje estaba escribiendo, quitarlo
      if (isTypingUsers.value.has(data.message.sender_username)) {
        isTypingUsers.value.delete(data.message.sender_username);
      }
    } 
    else if (data.type === "typing_status") {
      if (data.username !== user.value?.username) {
        if (data.is_typing) {
          isTypingUsers.value.add(data.username);
        } else {
          isTypingUsers.value.delete(data.username);
        }
      }
    }
  };

  ws.onclose = () => {
    ws = null;
    if (isOpen.value) setTimeout(connectWebSocket, 3000);
  };
};

const handleTyping = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "typing_status", is_typing: true }));
    
    if (typingTimeout) clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
      ws.send(JSON.stringify({ type: "typing_status", is_typing: false }));
    }, 2000);
  }
};

const handleFileUpload = (event) => {
  const selected = event.target.files[0];
  if (!selected) return;
  
  if (selected.size > 4 * 1024 * 1024) {
    alert("El archivo no puede pesar más de 4MB.");
    fileInput.value.value = "";
    return;
  }
  file.value = selected;
};

const sendMessage = async () => {
  if (!newMessage.value.trim() && !file.value) return;

  const formData = new FormData();
  if (newMessage.value.trim()) formData.append("texto", newMessage.value.trim());
  if (file.value) formData.append("archivo", file.value);

  showEmojis.value = false;

  try {
    await api.post('chat/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    newMessage.value = "";
    file.value = null;
    if (fileInput.value) fileInput.value.value = "";
    
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "typing_status", is_typing: false }));
    }
  } catch (error) {
    console.error("Error enviando mensaje", error);
  }
};

const addEmoji = (emoji) => {
  newMessage.value += emoji;
  showEmojis.value = false;
  handleTyping();
};

const formatTime = (iso) => {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("es-AR", { hour: '2-digit', minute: '2-digit' });
};

onMounted(() => {
  // Conectar silenciosamente al iniciar para recibir notificaciones
  connectWebSocket();
});

onUnmounted(() => {
  if (ws) ws.close();
});
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
    <!-- Ventana del Chat -->
    <div 
      v-if="isOpen" 
      class="mb-4 w-80 sm:w-96 bg-[#12131A] border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 duration-200"
      style="height: 500px; max-height: calc(100vh - 120px);"
    >
      <!-- Header -->
      <div class="shrink-0 bg-[#1A1C23] border-b border-white/5 p-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center">
            <MessageCircle class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-slate-100 font-semibold text-sm">Chat de Equipo</h3>
            <p class="text-emerald-400 text-[11px] font-medium flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Online
            </p>
          </div>
        </div>
        <button @click="toggleChat" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/5">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Messages -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-[#0B0C10]" ref="messagesContainer">
        <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
          <MessageCircle class="w-8 h-8 opacity-50" />
          <p class="text-sm">Aún no hay mensajes.</p>
        </div>

        <div 
          v-for="msg in messages" :key="msg.id"
          class="flex flex-col max-w-[85%]"
          :class="msg.sender_username === user?.username ? 'ml-auto items-end' : 'mr-auto items-start'"
        >
          <span class="text-[10px] text-slate-500 mb-1 px-1">
            {{ msg.sender_username === user?.username ? 'Tú' : '@' + msg.sender_username }}
          </span>
          <div 
            class="px-4 py-2 rounded-2xl relative group"
            :class="msg.sender_username === user?.username ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-[#1E2028] text-slate-200 border border-white/5 rounded-tl-sm'"
          >
            <p v-if="msg.texto" class="text-sm break-words whitespace-pre-wrap">{{ msg.texto }}</p>
            
            <!-- Archivo Adjunto -->
            <div v-if="msg.archivo" class="mt-2">
              <img 
                v-if="msg.archivo.match(/\.(jpeg|jpg|gif|png|webp)$/i)" 
                :src="msg.archivo" 
                class="rounded-lg max-h-40 object-cover cursor-pointer hover:opacity-90 transition-opacity"
                @click="window.open(msg.archivo, '_blank')"
              />
              <a 
                v-else 
                :href="msg.archivo" 
                target="_blank" 
                class="flex items-center gap-2 p-2 rounded bg-black/20 hover:bg-black/40 transition-colors text-xs font-medium"
              >
                <Paperclip class="w-3 h-3" /> Ver Adjunto
              </a>
            </div>

            <span class="text-[9px] opacity-60 mt-1 block text-right" :class="msg.sender_username === user?.username ? 'text-blue-100' : 'text-slate-400'">
              {{ formatTime(msg.timestamp) }}
            </span>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isTypingUsers.size > 0" class="mr-auto items-start flex flex-col">
          <div class="bg-[#1E2028] border border-white/5 px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-1 w-16">
            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
          </div>
          <span class="text-[10px] text-slate-500 mt-1 px-1">Alguien está escribiendo...</span>
        </div>
      </div>

      <!-- Input Area -->
      <div class="shrink-0 p-3 bg-[#1A1C23] border-t border-white/5">
        <div v-if="file" class="mb-2 px-3 py-1.5 bg-[#1E2028] border border-white/10 rounded-lg flex items-center justify-between">
          <span class="text-xs text-slate-300 truncate max-w-[200px]">{{ file.name }}</span>
          <button @click="file = null; fileInput.value = ''" class="text-slate-500 hover:text-red-400">
            <X class="w-4 h-4" />
          </button>
        </div>

        <form @submit.prevent="sendMessage" class="flex items-end gap-2">
          <!-- Adjuntar -->
          <button type="button" @click="$refs.fileInput.click()" class="p-2 text-slate-400 hover:text-blue-400 rounded-lg hover:bg-blue-500/10 transition-colors shrink-0">
            <Paperclip class="w-5 h-5" />
          </button>
          <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" accept="image/*,.pdf" />

          <!-- Input Text -->
          <div class="flex-1 bg-[#0B0C10] border border-white/10 rounded-xl relative flex items-center">
            <input 
              v-model="newMessage"
              @input="handleTyping"
              type="text" 
              placeholder="Escribe un mensaje..." 
              class="w-full bg-transparent text-sm text-white px-4 py-2.5 focus:outline-none rounded-xl placeholder-slate-500"
            />
            
            <!-- Emojis (Click toggle) -->
            <div class="relative px-2">
              <button type="button" @click.prevent="showEmojis = !showEmojis" class="text-slate-400 hover:text-yellow-400 p-1">
                <Smile class="w-4 h-4" />
              </button>
              <div v-show="showEmojis" class="absolute bottom-[120%] right-0 mb-2 flex bg-[#1E2028] border border-white/10 rounded-lg p-3 gap-3 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                <button type="button" @click="addEmoji('👍')" class="text-xl hover:scale-125 transition-transform">👍</button>
                <button type="button" @click="addEmoji('🔥')" class="text-xl hover:scale-125 transition-transform">🔥</button>
                <button type="button" @click="addEmoji('✅')" class="text-xl hover:scale-125 transition-transform">✅</button>
                <button type="button" @click="addEmoji('😅')" class="text-xl hover:scale-125 transition-transform">😅</button>
                <button type="button" @click="addEmoji('🚀')" class="text-xl hover:scale-125 transition-transform">🚀</button>
              </div>
            </div>
          </div>

          <!-- Enviar -->
          <button 
            type="submit" 
            :disabled="!newMessage.trim() && !file"
            class="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0"
          >
            <Send class="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>

    <!-- Burbuja Flotante -->
    <button 
      v-if="!isOpen"
      @click="toggleChat"
      class="w-14 h-14 bg-blue-600 rounded-full flex items-center justify-center text-white shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:bg-blue-500 hover:scale-105 transition-all relative"
      :class="{'animate-bounce-slow': !hasUnread, 'animate-bounce': hasUnread}"
    >
      <MessageCircle class="w-6 h-6" />
      <!-- Unread Badge -->
      <span v-if="hasUnread" class="absolute top-0 right-0 w-3.5 h-3.5 bg-red-500 border-2 border-[#0B0C10] rounded-full animate-pulse"></span>
    </button>
  </div>
</template>

<style scoped>
.animate-bounce-slow {
  animation: bounce 3s infinite;
}
@keyframes bounce {
  0%, 100% {
    transform: translateY(-5%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}
</style>
