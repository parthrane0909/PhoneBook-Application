<template>
  <div class="pagination">

    <span class="pagination-info">
      Showing {{ startItem }}–{{ endItem }} of {{ total }}
    </span>

    <div class="pagination-controls">
      <button
        :disabled="page === 1"
        @click="$emit('change', page - 1)"
      >
        ←
      </button>

      <span class="page-number">
        {{ page }}
      </span>

      <button
        :disabled="page >= totalPages"
        @click="$emit('change', page + 1)"
      >
        →
      </button>
    </div>

  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  page: Number,
  limit: Number,
  total: Number,
  totalPages: Number,
});

defineEmits(["change"]);

const startItem = computed(() => {
  if (props.total === 0) return 0;

  return (props.page - 1) * props.limit + 1;
});

const endItem = computed(() => {
  return Math.min(
    props.page * props.limit,
    props.total
  );
});
</script>