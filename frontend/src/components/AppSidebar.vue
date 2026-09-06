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
      <div class="sidebar-section-title">Tags</div>

        <RouterLink
          v-for="tag in tags"
          :key="tag.name"
          class="sidebar-item"
          :class="{ 'tag-active': currentTag === tag.name }"
          :to="tagLink(tag.name)"
          @click.prevent="selectTag(tag.name)"
        >
        <span class="label-dot"></span><span>{{ tag.name }}</span>
      </RouterLink>
    </div>

    <div class="sidebar-bottom">

      <RouterLink class="sidebar-item" to="/settings" @click="$emit('close')"><span class="sidebar-icon">⚙</span><span>Settings</span></RouterLink>

    </div>

  </aside>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useContactsStore } from "../stores/contacts";

defineProps({ open: Boolean });
const emit = defineEmits(["close"]);
const store = useContactsStore();
const tags = ref([]);
const route = useRoute();
const router = useRouter();

onMounted(async () => {
  try {
    tags.value = await store.fetchTags();
  } catch {
    tags.value = [];
  }
});

const currentTag = computed(() => typeof route.query.tag === "string" ? route.query.tag : "");

function tagLink(tag) {
  return {
    path: "/contacts",
    query: { ...route.query, tag },
  };
}

function selectTag(tag) {
  router.push({
    path: "/contacts",
    query: {
      ...route.query,
      tag: currentTag.value === tag ? undefined : tag,
      page: undefined,
    },
  });
  emit("close");
}
</script>