<template>
  <div class="crumb-wrap">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item v-for="item in currentRouteList" :key="item.path" :to="{ path: item.path }">
        {{ item.meta.title || item.path }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const currentRouteList = ref(route.matched);

watch(
  route,
  () => {
    currentRouteList.value = route.matched;
  },
  { immediate: true }
);
</script>

<style scoped>
.crumb-wrap {
  margin-bottom: 18px;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
}
</style>
