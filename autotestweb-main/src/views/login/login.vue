<template>
  <div class="login-page">
    <section class="login-hero">
      <div class="hero-badge">WEB 自动化测试平台</div>
      <h1>浏览器AI驱动、用例管理、关键字编排，一站式自动化工作台。</h1>
    
    </section>

    <section class="login-panel content-panel">
      <div v-if="isFeishuLoggingIn" class="feishu-loading">
        <el-icon class="is-loading" :size="48" color="#4080ff"><Loading /></el-icon>
        <h2 style="margin-top: 16px;">正在通过飞书授权登录...</h2>
      </div>
      <template v-else>
        <div class="panel-title">登录</div>
        <div class="panel-subtitle">请使用平台账号登录工作台。</div>

        <el-form v-if="loginMode === 'password_only' || loginMode === 'mixed'" ref="formref" :model="form" :rules="rules" label-position="top" @keyup.enter="onSubmit">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="admin" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
          </el-form-item>
          <el-button class="submit-btn" type="primary" @click="onSubmit" :loading="isSubmitting">账号密码登录</el-button>
        </el-form>

        <template v-if="loginMode === 'feishu_only' || loginMode === 'mixed'">
          <el-divider v-if="loginMode === 'mixed'">或使用以下方式</el-divider>
          <el-button class="submit-btn feishu-btn" @click="onFeishuLogin" :loading="isFetchingAppId" :style="loginMode === 'feishu_only' ? 'margin-top: 20px; padding: 24px 0; font-size: 16px;' : ''">
            <svg viewBox="0 0 1024 1024" width="20" height="20" style="margin-right: 8px;"><path d="M439.466667 601.6c4.266667 55.466667 46.933333 102.4 102.4 102.4h320A102.4 102.4 0 0 0 964.266667 601.6v-320c-4.266667-55.466667-46.933333-102.4-102.4-102.4H541.866667A102.4 102.4 0 0 0 439.466667 281.6v320z m-320 0c0-55.466667 46.933333-102.4 102.4-102.4h115.2A102.4 102.4 0 0 1 439.466667 601.6V716.8c0 55.466667-46.933333 102.4-102.4 102.4h-115.2a102.4 102.4 0 0 1-102.4-102.4v-115.2z" fill="#00D6B9"></path><path d="M439.466667 499.2A102.4 102.4 0 0 0 337.066667 396.8h-115.2a102.4 102.4 0 0 0-102.4 102.4v115.2c0 55.466667 46.933333 102.4 102.4 102.4h115.2A102.4 102.4 0 0 0 439.466667 601.6v-102.4z m524.8 102.4A102.4 102.4 0 0 0 861.866667 503.466667H541.866667A102.4 102.4 0 0 0 439.466667 605.866667v102.4c0 55.466667 46.933333 102.4 102.4 102.4h320c55.466667 0 102.4-46.933333 102.4-102.4v-104.533334z m-102.4-320c55.466667 0 102.4 46.933333 102.4 102.4v42.666667a51.2 51.2 0 0 1-51.2 51.2h-371.2a51.2 51.2 0 0 1-51.2-51.2v-42.666667c0-55.466667 46.933333-102.4 102.4-102.4h268.8z" fill="#00B69D"></path></svg>
            飞书身份授权登录
          </el-button>
        </template>
      </template>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElNotification } from "element-plus";
import { Loading } from "@element-plus/icons-vue";
import { useCookies } from "@vueuse/integrations/useCookies";
import { login, getFeishuConfig, doFeishuLogin, getLoginConfig } from "~/views/login/login.js";

const router = useRouter();
const route = useRoute();
const cookie = useCookies();
const formref = ref(null);
const isSubmitting = ref(false);
const isFetchingAppId = ref(false);
const isFeishuLoggingIn = ref(false);
const loginMode = ref("password_only"); // default

const form = reactive({
  username: "",
  password: "",
});

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const onSubmit = () => {
  formref.value.validate((valid) => {
    if (!valid) {
      return;
    }
    isSubmitting.value = true;
    login(form.username, form.password).then((res) => {
      isSubmitting.value = false;
      if (res.data.code === 200 && res.data.data.token) {
        cookie.set("l-token", res.data.data.token);
        cookie.set("l-username", res.data.data.username || form.username);
        cookie.set("l-name", res.data.data.access_name || res.data.data.username || form.username);
        cookie.set("l-access_user_id", res.data.data.access_user_id || "");
        cookie.set("l-role", res.data.data.role || "user");
        ElNotification({
          title: "成功",
          message: "登录成功",
          type: "success",
        });
        router.push("/");
        return;
      }

      ElNotification({
        title: "登录失败",
        message: res.data.msg || "请检查用户名和密码",
        type: "error",
      });
    }).catch(() => {
      isSubmitting.value = false;
      ElNotification({
        title: "登录异常",
        message: "服务器无响应或网络错误",
        type: "error",
      });
    });
  });
};

const onFeishuLogin = () => {
  isFetchingAppId.value = true;
  getFeishuConfig().then(res => {
    if (res.data.code === 200 && res.data.data.app_id) {
      const appId = res.data.data.app_id;
      const configuredRedirectUri = res.data.data.redirect_uri || "";
      const redirectUri = encodeURIComponent(configuredRedirectUri || window.location.origin + "/login");
      window.location.href = `https://passport.feishu.cn/suite/passport/oauth/authorize?client_id=${appId}&redirect_uri=${redirectUri}&response_type=code`;
    } else {
      ElNotification.error(res.data.msg || "获取飞书配置失败，请检查后端是否配置了APP ID");
      isFetchingAppId.value = false;
    }
  }).catch(() => {
    ElNotification.error("请求后端飞书配置异常");
    isFetchingAppId.value = false;
  });
};

onMounted(() => {
  // Check if we just returned from feishu oauth
  const code = route.query.code;
  if (code) {
    isFeishuLoggingIn.value = true;
    doFeishuLogin(code).then(res => {
      if (res.data.code === 200 && res.data.data.token) {
        cookie.set("l-token", res.data.data.token);
        cookie.set("l-username", res.data.data.username);
        cookie.set("l-name", res.data.data.access_name || res.data.data.username);
        cookie.set("l-access_user_id", res.data.data.access_user_id || "");
        cookie.set("l-role", res.data.data.role || "user");
        ElNotification.success("飞书登录成功");
        router.push("/");
      } else {
        isFeishuLoggingIn.value = false;
        ElNotification.error(res.data.msg || "飞书登录失败");
        // router.replace('/login') to clear query params
        router.replace("/login");
      }
    }).catch(err => {
      isFeishuLoggingIn.value = false;
      ElNotification.error("飞书登录请求异常: " + err.message);
      router.replace("/login");
    });
  }

  // Fetch login configuration
  getLoginConfig().then(res => {
    if (res.data.code === 200 && res.data.data.mode) {
      loginMode.value = res.data.data.mode;
    }
  }).catch(() => {
    console.error("Failed to fetch login configuration.");
  });
});
</script>

<style scoped>
.login-page {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  min-height: 100vh;
  padding: 32px;
  gap: 28px;
}

.login-hero {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
  border-radius: 24px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e6f0fa 100%);
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(64, 128, 255, 0.08);
}

.login-hero::before {
  content: "";
  position: absolute;
  top: -10%;
  left: -10%;
  width: 450px;
  height: 450px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4080ff 0%, #8ca8f9 100%);
  filter: blur(100px);
  opacity: 0.15;
  z-index: 0;
}

.login-hero::after {
  content: "";
  position: absolute;
  bottom: -10%;
  right: -10%;
  width: 350px;
  height: 350px;
  border-radius: 50%;
  background: linear-gradient(135deg, #16a34a 0%, #86efac 100%);
  filter: blur(90px);
  opacity: 0.12;
  z-index: 0;
}

.hero-badge {
  position: relative;
  z-index: 1;
  display: inline-flex;
  width: fit-content;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(64, 128, 255, 0.2);
  color: #4080ff;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(64, 128, 255, 0.05);
}

.login-hero h1 {
  position: relative;
  z-index: 1;
  max-width: 580px;
  margin: 24px 0 16px;
  font-size: 52px;
  line-height: 1.1;
  font-weight: 700;
  color: #1d2129;
  letter-spacing: -0.5px;
}

.login-hero p {
  max-width: 520px;
  color: #6b7280;
  font-size: 15px;
}

.login-panel {
  align-self: center;
  padding: 32px;
}

.panel-title {
  font-size: 28px;
  font-weight: 700;
  color: #1d2129;
}

.panel-subtitle {
  margin: 8px 0 24px;
  color: #6b7280;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
}

.feishu-btn {
  background-color: #f2f3f5;
  color: #1d2129;
  border-color: #e5e6eb;
}

.feishu-btn:hover {
  background-color: #e5e6eb;
  border-color: #e5e6eb;
  color: #1d2129;
}

.feishu-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 0;
  color: #1d2129;
}

@media (max-width: 980px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 20px;
  }

  .login-hero {
    padding: 8px 4px 0;
  }

  .login-hero h1 {
    font-size: 34px;
  }
}
</style>
