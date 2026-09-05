<template>
  <aside class="sidebar" :class="{ open }">

    <div class="sidebar-brand">
      <div class="brand-icon">
        P
      </div>

      <div>
        <strong>Phonebook</strong>
        <span>Contact workspace</span>
      </div>
    </div>

    <nav class="sidebar-nav">

      <RouterLink class="sidebar-item" to="/contacts" @click="$emit('close')"><span class="sidebar-icon">▦</span><span>All Contacts</span></RouterLink>
      <RouterLink class="sidebar-item" to="/favorites" @click="$emit('close')"><span class="sidebar-icon">★</span><span>Favorites</span></RouterLink>
      <RouterLink class="sidebar-item" to="/recently-viewed" @click="$emit('close')"><span class="sidebar-icon">◷</span><span>Recently viewed</span></RouterLink>

    </nav>

    <div class="sidebar-section">
      <div class="sidebar-section-title">
        Labels
      </div>

      <RouterLink v-for="tag in tags" :key="tag.name" class="sidebar-item" :to="`/labels/${encodeURIComponent(tag.name)}`" @click="$emit('close')">
        <span class="label-dot"></span><span>{{ tag.name }}</span>
      </RouterLink>
    </div>

    <div class="sidebar-bottom">

      <RouterLink class="sidebar-item" to="/settings" @click="$emit('close')"><span class="sidebar-icon">⚙</span><span>Settings</span></RouterLink>

    </div>

  </aside>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useContactsStore } from "../stores/contacts";

defineProps({ open: Boolean });
defineEmits(["close"]);
const store = useContactsStore();
const tags = ref([]);

onMounted(async () => {
  try {
    tags.value = await store.fetchTags();
  } catch {
    tags.value = [];
  }
});
</script>