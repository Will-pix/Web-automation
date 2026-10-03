<template>
  <div class="workspace-shell">
    <aside class="shell-aside">
      <FMenu />
    </aside>
    <div class="shell-main">
      <FHeader />
      <main class="main-content">
        <FTafList />
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import FHeader from "./componemts/FHeader.vue";
import FTafList from "./componemts/FTafList.vue";
import FMenu from "./componemts/FMenu.vue";
import { useLayout } from "~/composables/useLayout.js";

const { isCollapse } = useLayout();
</script>

<style scoped>
.workspace-shell {
  display: grid;
  grid-template-columns: v-bind("isCollapse ? '64px' : '280px'") 1fr;
  min-height: 100vh;
  background: transparent;
  transition: grid-template-columns 0.3s ease;
}

.shell-aside {
  position: relative;
  border-right: 1px solid #e5e7eb;
  background: #ffffff;
  overflow: hidden;
}

.shell-main {
  min-width: 0;
}

.main-content {
  padding: 108px 24px 28px;
}

@media (max-width: 1080px) {
  .workspace-shell {
    grid-template-columns: 1fr;
  }

  .shell-aside {
    display: none;
  }

  .main-content {
    padding: 96px 16px 24px;
  }
}
</style>
