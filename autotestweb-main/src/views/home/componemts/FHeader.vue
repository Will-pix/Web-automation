<template>
  <header class="f-header">
    <div class="header-title">
      <div class="brand-mark">自动</div>
      <div>
        <div class="brand-name">Web自动化测试平台</div>
       
      </div>
    </div>

    <div class="header-actions">
      <router-link to="/platform-settings" class="header-link">平台设置</router-link>
      <div class="avatar-wrap">
        <div class="text-avatar">{{ usernameLastTwoChars }}</div>
        <el-dropdown>
          <span class="dropdown-trigger">
            {{ username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="outlogin">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";
import { useCookies } from "@vueuse/integrations/useCookies";
import { useRouter } from "vue-router";
import { ArrowDown } from "@element-plus/icons-vue";
import { useLayout } from "~/composables/useLayout.js";

const cookie = useCookies();
const router = useRouter();
const { isCollapse } = useLayout();

const username = computed(() => {
  return decodeURIComponent(cookie.get("l-name") || cookie.get("l-username") || "Admin");
});

const usernameLastTwoChars = computed(() => {
  return username.value.slice(-2) || "管理";
});

const outlogin = () => {
  cookie.remove("l-token");
  cookie.remove("l-name");
  cookie.remove("l-username");
  cookie.remove("l-access_user_id");
  router.push("/login");
};
</script>

<style scoped>
.f-header {
  position: fixed;
  top: 0;
  right: 0;
  left: v-bind("isCollapse ? '64px' : '280px'");
  transition: left 0.3s ease;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18px);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4080ff, #16a34a);
  color: white;
  font-weight: 700;
  font-size: 14px;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: #1d2129;
}

.brand-subtitle {
  margin-top: 4px;
  color: #6b7280;
  font-size: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

.header-link {
  color: #4b5563;
  font-size: 14px;
}

.avatar-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.text-avatar {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: rgba(64, 128, 255, 0.12);
  color: #4080ff;
  font-size: 13px;
  font-weight: 700;
}

.dropdown-trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #1d2129;
  cursor: pointer;
}

@media (max-width: 1080px) {
  .f-header {
    left: 0;
    padding: 16px;
  }

  .brand-subtitle,
  .header-link {
    display: none;
  }
}
</style>
