<template>
  <div class="f-menu">
    <div class="menu-brand" :class="{ 'is-collapsed': isCollapse }">
      <div class="section-title" v-show="!isCollapse">工作台</div>
      
    </div>
    <el-menu
      :default-active="activePath"
      class="menu-surface"
      background-color="transparent"
      text-color="#4b5563"
      active-text-color="#4080ff"
      :collapse="isCollapse"
      :collapse-transition="false"
      @select="handleSelect"
    >
      <template v-for="item in asideMenus" :key="item.name">
        <el-sub-menu v-if="item.child && item.child.length" :index="item.name">
          <template #title>
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.name }}</span>
          </template>

          <el-menu-item v-for="child in item.child" :key="child.frontpath" :index="child.frontpath">
            <el-icon><component :is="child.icon" /></el-icon>
            <span>{{ child.name }}</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item v-else :index="item.frontpath">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.name }}</span>
        </el-menu-item>
      </template>
    </el-menu>
    <div class="collapse-trigger" @click="toggleCollapse" :class="{ 'is-collapsed-trigger': isCollapse }">
      <el-icon><component :is="isCollapse ? 'Expand' : 'Fold'" /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useLayout } from "~/composables/useLayout.js";
import { Fold, Expand } from "@element-plus/icons-vue";
import { useCookies } from "@vueuse/integrations/useCookies";

const route = useRoute();
const router = useRouter();
const cookie = useCookies();
// 表单/编辑页 → 对应列表页的映射，保持侧边栏高亮
const formToListMap = {
  "/ApiProjectForm": "/ApiProjectList",
  "/ApiProjectFormedit": "/ApiProjectList",
  "/ApiModuleForm": "/ApiModuleList",
  "/ApiModuleFormedit": "/ApiModuleList",
  "/ApiInfoForm": "/ApiInfoList",
  "/ApiInfoFormedit": "/ApiInfoList",
  "/ApiCollectionForm": "/ApiCollectionList",
  "/WebProjectForm": "/WebProjectList",
  "/WebBrowserForm": "/WebBrowserList",
  "/WebKeyWordForm": "/WebKeyWordList",
  "/WebInfoForm": "/WebInfoList",
  "/WebCollectionInfoForm": "/WebCollectionInfoList",
};
const activePath = computed(() => formToListMap[route.path] || route.path);
const { isCollapse, toggleCollapse } = useLayout();

const handleSelect = (path) => {
  router.push(path);
};

const baseMenus = [
  {
    name: "工作台",
    icon: "House",
    child: [
      { name: "仪表盘", icon: "DataBoard", frontpath: "/" },
      { name: "平台设置", icon: "Setting", frontpath: "/platform-settings" },
      { name: "用户管理", icon: "User", frontpath: "/users" },
    ],
  },
  {
    name: "接口自动化",
    icon: "Connection",
    child: [
      { name: "项目管理", icon: "FolderOpened", frontpath: "/ApiProjectList" },
      { name: "模块管理", icon: "Grid", frontpath: "/ApiModuleList" },
      { name: "用例管理", icon: "Document", frontpath: "/ApiInfoList" },
      { name: "集合管理", icon: "Collection", frontpath: "/ApiCollectionList" },
      { name: "定时任务", icon: "Clock", frontpath: "/Apitimetasklist" },
    ],
  },
  {
    name: "Web自动化",
    icon: "Monitor",
    child: [
      { name: "项目管理", icon: "Folder", frontpath: "/WebProjectList" },
      { name: "文件中心", icon: "Files", frontpath: "/WebFileList" },
      { name: "浏览器池", icon: "Monitor", frontpath: "/WebBrowserList" },
      { name: "操作类型", icon: "CollectionTag", frontpath: "/WebOperationTypeList" },
      { name: "关键字管理", icon: "Tickets", frontpath: "/WebKeyWordList" },
      { name: "用例管理", icon: "Reading", frontpath: "/WebInfoList" },
      { name: "集合管理", icon: "CopyDocument", frontpath: "/WebCollectionInfoList" },
      { name: "定时任务", icon: "Timer", frontpath: "/WebTimeTaskList" },
      { name: "质量看板", icon: "TrendCharts", frontpath: "/WebQualityList" },
    ],
  },
];

const asideMenus = computed(() => {
  const role = cookie.get("l-role") || "user";
  if (role === "admin") {
    return baseMenus;
  }

  return baseMenus.map((menu) => {
    if (!menu.child) {
      return menu;
    }
    return {
      ...menu,
      child: menu.child.filter((child) => !["/platform-settings", "/users"].includes(child.frontpath)),
    };
  });
});
</script>

<style scoped>
.f-menu {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.menu-brand {
  padding: 22px 16px 18px;
  flex-shrink: 0;
}

.menu-surface {
  flex: 1;
  overflow-y: auto;
  border-right: none;
}

.collapse-trigger {
  flex-shrink: 0;
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  color: #6b7280;
  font-size: 20px;
  cursor: pointer;
  border-top: 1px solid #f3f4f6;
  transition: all 0.3s ease;
}

.collapse-trigger:hover {
  color: #4080ff;
  background-color: #f9fafb;
}

.is-collapsed-trigger {
  justify-content: center;
  padding: 16px 0;
}

.is-collapsed {
  display: none;
}
</style>
