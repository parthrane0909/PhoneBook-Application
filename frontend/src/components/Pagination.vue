<template>
  <div class="pagination">

    <span class="pagination-info">
      Showing {{ startItem }}–{{ endItem }} of {{ total }}
    </span>

    <div class="pagination-controls">
      <button
        class="pagination-arrow"
        type="button"
        :disabled="page === 1"
        @click="$emit('change', page - 1)"
        aria-label="Previous page"
      >
        ←
      </button>

      <button
        v-for="pageNumber in visiblePages"
        :key="pageNumber"
        type="button"
        class="page-number"
        :class="{ active: pageNumber === page }"
        :aria-current="pageNumber === page ? 'page' : undefined"
        @click="$emit('change', pageNumber)"
      >{{ pageNumber }}</button>

      <button
        class="pagination-arrow"
        type="button"
        :disabled="page >= totalPages"
        @click="$emit('change', page + 1)"
        aria-label="Next page"
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

const visiblePages = computed(() => {
  const pageCount = props.totalPages || 0;
  if (pageCount <= 5) {
    return Array.from({ length: pageCount }, (_, index) => index + 1);
  }

  let start = Math.max(1, props.page - 2);
  let end = Math.min(pageCount, props.page + 2);

  if (props.page <= 3) {
    start = 1;
    end = 5;
  } else if (props.page >= pageCount - 2) {
    start = pageCount - 4;
    end = pageCount;
  }

  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
});
</script>