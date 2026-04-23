<script setup>
import { BarChart2, Construction } from 'lucide-vue-next';
</script>

<template>
  <div class="h-full bg-[#0B0C10] flex flex-col font-sans text-slate-100 overflow-hidden">
    <!-- Header -->
    <header class="shrink-0 h-16 border-b border-white/5 bg-[#09090B] flex items-center px-6">
      <h1 class="text-xl font-bold flex items-center gap-2">
        <BarChart2 class="w-5 h-5 text-purple-400" /> Reportes
      </h1>
    </header>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto p-6 flex flex-col items-center justify-center">
      <div class="bg-[#12131A] rounded-xl border border-white/5 p-10 text-center max-w-md w-full shadow-2xl flex flex-col items-center">
        <div class="w-16 h-16 rounded-full bg-purple-500/10 flex items-center justify-center mb-4">
          <Construction class="w-8 h-8 text-purple-400" />
        </div>
        <h2 class="text-xl font-bold text-white mb-2">Próximamente</h2>
        <p class="text-slate-400 text-sm">
          El módulo de Reportes está en construcción. Aquí podrás visualizar métricas, progreso de tareas y descargar informes.
        </p>
      </div>
    </main>
  </div>
</template>
