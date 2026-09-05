<template>
  <div class="app-shell">
    <AppSidebar :open="sidebarOpen" @close="sidebarOpen = false" />
    <button v-if="sidebarOpen" class="sidebar-backdrop" type="button" aria-label="Close navigation" @click="sidebarOpen = false"></button>
    <main class="main-content">
      <button class="mobile-menu" type="button" aria-label="Open navigation" @click="sidebarOpen = true">☰</button>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref } from "vue";
import AppSidebar from "./components/AppSidebar.vue";

const sidebarOpen = ref(false);
</script>