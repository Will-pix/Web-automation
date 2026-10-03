<template>
  <div class="platform-settings">
    <div class="hero content-panel">
      <div>
        <div class="section-title">平台设置</div>
        <div class="section-subtitle">
          集中管理部署、AI模型路由、关键字导入和仪表盘浏览器窗口。
        </div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="onSave">保存设置</el-button>
        <el-button type="success" @click="onGenerateDeploy">生成快速部署包</el-button>
      </div>
    </div>

    <div class="settings-grid">
      <section class="content-panel pane">
        <div class="pane-header">
          <div class="section-title">品牌信息</div>
          <div class="section-subtitle">替换旧版名称和外部引用。</div>
        </div>
        <el-form label-position="top" :model="form.branding">
          <el-row :gutter="16">
            <el-col :md="12">
              <el-form-item label="平台名称">
                <el-input v-model="form.branding.platform_name" />
              </el-form-item>
            </el-col>
            <el-col :md="12">
              <el-form-item label="帮助文档URL">
                <el-input v-model="form.branding.support_url" placeholder="可选的知识库或文档链接" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-divider>系统登录配置</el-divider>
          <el-row :gutter="16">
            <el-col :md="12">
              <el-form-item label="登录方式" prop="login.mode">
                <el-select v-model="form.login.mode" style="width: 100%">
                  <el-option label="仅账号密码登录" value="password_only" />
                  <el-option label="仅飞书授权登录" value="feishu_only" />
                  <el-option label="密码与飞书混合登录" value="mixed" />
                </el-select>
              </el-form-item>
              <div style="color: #6b7280; font-size: 13px; margin-top: -8px;">
                若选择包含飞书登录的模式，请确保后端已配置正确的 FEISHU_APP_ID 和 FEISHU_APP_SECRET
              </div>
            </el-col>
          </el-row>
        </el-form>
        <div class="pane-footer">
          <el-button type="primary" size="small" @click="onSaveSection('branding')">保存品牌信息</el-button>
        </div>
      </section>

      <section class="content-panel pane">
        <div class="pane-header">
          <div class="section-title">飞书登录配置</div>
          <div class="section-subtitle">配置企业自建应用凭证，同事可通过飞书授权登录平台。</div>
        </div>
        <el-form label-position="top" :model="form.feishu">
          <el-row :gutter="16">
            <el-col :md="12">
              <el-form-item label="FEISHU_APP_ID">
                <el-input v-model="form.feishu.app_id" placeholder="cli_xxxxxxxxxxxxxxxx" />
              </el-form-item>
            </el-col>
            <el-col :md="12">
              <el-form-item label="FEISHU_APP_SECRET">
                <el-input v-model="form.feishu.app_secret" type="password" show-password placeholder="飞书应用密钥" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="登录回调地址">
            <el-input v-model="form.feishu.redirect_uri" placeholder="例如 http://localhost:5173/login 或 https://autotest.company.com/login" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :md="8">
              <el-form-item label="允许自动注册">
                <el-switch v-model="form.feishu.auto_register" />
              </el-form-item>
            </el-col>
            <el-col :md="8">
              <el-form-item label="新用户默认角色">
                <el-select v-model="form.feishu.default_role" style="width: 100%">
                  <el-option label="普通用户" value="user" />
                  <el-option label="管理员" value="admin" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :md="8">
              <el-form-item label="需要管理员审批">
                <el-switch v-model="form.feishu.require_approval" />
              </el-form-item>
            </el-col>
          </el-row>
          <div class="settings-note">
            该回调地址需要同步填写到飞书开放平台。开启审批后，新用户会先创建为 pending 角色，管理员需在用户管理中改为 user 或 admin。
          </div>
        </el-form>
        <div class="pane-footer">
          <el-button type="primary" size="small" @click="onSaveSection('feishu')">保存飞书配置</el-button>
        </div>
      </section>

      <section class="content-panel pane">
        <div class="pane-header">
          <div class="section-title">通知群配置</div>
          <div class="section-subtitle">配置自动化用例执行完成后的群通知，支持飞书、钉钉、企业微信。</div>
        </div>
        <el-form label-position="top" :model="form.notification">
          <el-row :gutter="16">
            <el-col :md="8">
              <el-form-item label="通知平台">
                <el-select v-model="form.notification.platform" style="width: 100%">
                  <el-option label="飞书" value="feishu" />
                  <el-option label="钉钉" value="dingtalk" disabled />
                  <el-option label="企业微信" value="wecom" disabled />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :md="4">
              <el-form-item label="启用通知">
                <el-switch v-model="form.notification.enabled" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="Webhook URL">
            <el-input v-model="form.notification.webhook_url" placeholder="粘贴飞书/钉钉/企微机器人 Webhook 地址" />
          </el-form-item>
          <div class="pane-footer">
            <el-button type="primary" plain @click="onTestNotification" :loading="testingNotification">发送测试通知</el-button>
            <el-button type="primary" size="small" @click="onSaveSection('notification')">保存通知配置</el-button>
          </div>
        </el-form>
      </section>

      <section class="content-panel pane">
        <div class="pane-header">
          <div class="section-title">AI模型配置</div>
          <div class="section-subtitle">支持豆包及任何OpenAI兼容模型服务。</div>
        </div>
        <el-form label-position="top" :model="form.ai" autocomplete="off">
          <el-row :gutter="16">
            <el-col :md="12">
              <el-form-item label="服务商名称">
                <el-input v-model="form.ai.provider_name" />
              </el-form-item>
            </el-col>
            <el-col :md="12">
              <el-form-item label="模型名称">
                <el-input v-model="form.ai.model_name" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="API基础URL">
            <el-input v-model="form.ai.api_base" autocomplete="off" name="ai-api-base" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :md="14">
              <el-form-item label="API密钥">
                <el-input v-model="form.ai.api_key" type="password" show-password autocomplete="off" name="ai-api-key" />
              </el-form-item>
            </el-col>
            <el-col :md="10">
              <el-form-item label="请求路径">
                <el-input v-model="form.ai.request_path" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        <div class="pane-footer">
          <el-button type="primary" size="small" @click="onSaveSection('ai')">保存AI配置</el-button>
        </div>
      </section>

      <section class="content-panel pane">
        <div class="pane-header">
          <div class="section-title">快速部署</div>
          <div class="section-subtitle">生成可直接运行的Docker和环境配置文件。</div>
        </div>
        <el-form label-position="top" :model="form.deployment">
          <el-row :gutter="16">
            <el-col :md="12">
              <el-form-item label="前端端口">
                <el-input-number v-model="form.deployment.frontend_port" :min="1" :max="65535" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :md="12">
              <el-form-item label="后端端口">
                <el-input-number v-model="form.deployment.backend_port" :min="1" :max="65535" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :md="12">
              <el-form-item label="MySQL主机">
                <el-input v-model="form.deployment.mysql_host" />
              </el-form-item>
            </el-col>
            <el-col :md="12">
              <el-form-item label="MySQL数据库">
                <el-input v-model="form.deployment.mysql_db" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :md="12">
              <el-form-item label="MySQL用户名">
                <el-input v-model="form.deployment.mysql_user" />
              </el-form-item>
            </el-col>
            <el-col :md="12">
              <el-form-item label="MySQL密码">
                <el-input v-model="form.deployment.mysql_password" type="password" show-password />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="公网访问URL">
            <el-input v-model="form.deployment.public_base_url" placeholder="可选的外部访问地址" />
          </el-form-item>
        </el-form>
        <div class="pane-footer">
          <el-button type="primary" size="small" @click="onSaveSection('deployment')">保存部署配置</el-button>
        </div>
      </section>

      <section class="content-panel pane">
        <div class="pane-header">
          <div class="section-title">仪表盘浏览器窗口设置</div>
          <div class="section-subtitle">配置仪表盘预览墙上展示的 noVNC 浏览器实时画面地址。</div>
        </div>
        <div class="browser-grid">
          <div v-for="(item, index) in form.browser_previews" :key="index" class="browser-item">
            <el-form label-position="top">
              <el-form-item :label="`窗口名称 ${index + 1}`">
                <el-input v-model="item.name" placeholder="例如：Chrome执行机1" />
              </el-form-item>
              <el-form-item label="noVNC预览URL">
                <el-input v-model="item.url" placeholder="请输入 noVNC 浏览器画面地址，例如：http://192.168.1.100:7900" />
              </el-form-item>
            </el-form>
            <el-button type="danger" size="small" plain @click="removeBrowserPreview(index)">删除此窗口</el-button>
          </div>
          <div v-if="form.browser_previews.length === 0" class="browser-empty">
            暂无浏览器窗口，请点击下方按钮新增。
          </div>
        </div>
        <div class="pane-footer">
          <el-button type="success" size="small" @click="addBrowserPreview">新增窗口</el-button>
          <el-button type="primary" size="small" @click="onSaveSection('browser_previews')">保存窗口设置</el-button>
        </div>
      </section>

      <section class="content-panel pane">
        <div class="pane-header">
          <div class="section-title">关键字导入</div>
          <div class="section-subtitle">从平台直接导入关键字代码文件或批量步骤文本。</div>
        </div>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="关键字代码" name="keyword_code">
            <el-form label-position="top" :model="keywordImport">
              <el-row :gutter="16">
                <el-col :md="12">
                  <el-form-item label="关键字名称">
                    <el-input v-model="keywordImport.name" />
                  </el-form-item>
                </el-col>
                <el-col :md="12">
                  <el-form-item label="函数名">
                    <el-input v-model="keywordImport.keyword_fun_name" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :md="12">
                  <el-form-item label="操作类型ID">
                    <el-input-number v-model="keywordImport.operation_type_id" :min="1" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :md="12">
                  <el-form-item label="是否启用">
                    <el-select v-model="keywordImport.is_enabled">
                      <el-option label="是" value="true" />
                      <el-option label="否" value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="关键字文件">
                <el-upload :auto-upload="false" :show-file-list="true" :limit="1" :on-change="onKeywordFileChange" :on-remove="onKeywordFileRemove">
                  <el-button>选择文件</el-button>
                </el-upload>
              </el-form-item>
              <el-button type="primary" @click="submitKeywordImport">导入关键字</el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="批量步骤" name="step_lines">
            <el-form label-position="top" :model="stepImport">
              <el-row :gutter="16">
                <el-col :md="12">
                  <el-form-item label="目标用例ID">
                    <el-input-number v-model="stepImport.web_info_id" :min="1" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :md="12">
                  <el-form-item label="关键字ID">
                    <el-input-number v-model="stepImport.key_word_id" :min="1" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="步骤文本文件">
                <el-upload :auto-upload="false" :show-file-list="true" :limit="1" :on-change="onStepFileChange" :on-remove="onStepFileRemove">
                  <el-button>选择文件</el-button>
                </el-upload>
              </el-form-item>
              <el-button type="primary" @click="submitStepImport">导入步骤</el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </section>

      <section class="content-panel pane diagnostics">
        <div class="pane-header">
          <div class="section-title">兼容性诊断</div>
          <div class="section-subtitle">检查MySQL迁移后的PostgreSQL残留和配置缺失。</div>
        </div>
        <div class="pane-footer diagnostics-actions">
          <el-button type="primary" plain @click="onRunDiagnostics" :loading="diagnosticsRunning">运行配置检测</el-button>
        </div>
        <el-empty v-if="!diagnostics.length" description="未发现兼容性问题" />
        <el-alert
          v-for="(item, index) in diagnostics"
          :key="index"
          :type="item.level === 'warning' ? 'warning' : item.level === 'success' ? 'success' : 'info'"
          :title="item.title"
          :description="item.detail"
          show-icon
          :closable="false"
          class="diag-alert"
        />
      </section>
    </div>

    <el-dialog v-model="deployDialogVisible" title="生成快速部署包" width="480px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="输出目录">
          <el-input v-model="deployOutputDir" placeholder="请输入生成目录的绝对路径" />
        </el-form-item>
        <div style="color: #6b7280; font-size: 13px; margin-top: -8px;">
          留空则使用服务器默认目录（项目下 easy_deploy 文件夹）
        </div>
      </el-form>
      <template #footer>
        <el-button @click="deployDialogVisible = false">取消</el-button>
        <el-button type="success" @click="doGenerateDeploy" :loading="deployGenerating">开始生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import {
  fetchPlatformSettings,
  generateDeployBundle,
  importPlatformKeywords,
  runPlatformDiagnostics,
  savePlatformSettings,
  testNotification,
} from "./platform.js";

const activeTab = ref("keyword_code");
const diagnostics = ref([]);
const keywordFile = ref(null);
const stepFile = ref(null);
const testingNotification = ref(false);
const deployDialogVisible = ref(false);
const deployOutputDir = ref("");
const deployGenerating = ref(false);
const diagnosticsRunning = ref(false);

const form = reactive({
  login: {
    mode: "password_only"
  },
  branding: {
    platform_name: "",
    support_url: "",
  },
  feishu: {
    app_id: "",
    app_secret: "",
    redirect_uri: "",
    auto_register: true,
    default_role: "user",
    require_approval: false,
  },
  ai: {
    provider_name: "",
    api_base: "",
    api_key: "",
    model_name: "",
    request_path: "",
  },
  deployment: {
    frontend_port: 8080,
    backend_port: 8000,
    mysql_host: "mysql",
    mysql_db: "hcdb",
    mysql_user: "root",
    mysql_password: "123456",
    public_base_url: "",
  },
  browser_previews: [],
  notification: {
    platform: "feishu",
    webhook_url: "",
    enabled: false,
  },
});

const keywordImport = reactive({
  name: "",
  keyword_fun_name: "",
  operation_type_id: 1,
  is_enabled: "true",
});

const stepImport = reactive({
  web_info_id: 0,
  key_word_id: 0,
});

function loadSettings() {
  fetchPlatformSettings().then((res) => {
    const data = res.data.data;
    Object.assign(form.login, data.login || { mode: 'password_only' });
    Object.assign(form.branding, data.branding || {});
    Object.assign(form.feishu, data.feishu || {});
    Object.assign(form.ai, data.ai || {});
    Object.assign(form.deployment, data.deployment || {});
    Object.assign(form.notification, data.notification || {});
    form.browser_previews = (data.browser_previews || []).map((item) => ({ ...item }));
    diagnostics.value = data.diagnostics || [];
  });
}

function onSave() {
  savePlatformSettings({
    branding: form.branding,
    login: form.login,
    feishu: form.feishu,
    ai: form.ai,
    deployment: form.deployment,
    browser_previews: form.browser_previews,
    notification: form.notification,
  }).then(() => {
    ElMessage.success("平台设置已保存");
    loadSettings();
  });
}

function onSaveSection(section) {
  const payload = {};
  if (section === 'browser_previews') {
    payload.browser_previews = form.browser_previews;
  } else if (section === 'branding') {
    // Also save login config together with branding
    payload.branding = form.branding;
    payload.login = form.login;
  } else {
    payload[section] = form[section];
  }
  savePlatformSettings(payload).then(() => {
    ElMessage.success("已保存");
    loadSettings();
  });
}

function addBrowserPreview() {
  form.browser_previews.push({ name: "", url: "" });
}

function removeBrowserPreview(index) {
  form.browser_previews.splice(index, 1);
}

function onGenerateDeploy() {
  deployOutputDir.value = "";
  deployDialogVisible.value = true;
}

function doGenerateDeploy() {
  deployGenerating.value = true;
  generateDeployBundle(deployOutputDir.value || undefined)
    .then((res) => {
      const files = res.data.data.files || {};
      const summary = Object.keys(files).join("\u3001");
      ElMessage.success(`部署包已生成: ${summary}`);
      deployDialogVisible.value = false;
    })
    .catch(() => {
      ElMessage.error("生成失败，请检查目录路径是否正确");
    })
    .finally(() => {
      deployGenerating.value = false;
    });
}

function onKeywordFileChange(file) {
  keywordFile.value = file.raw;
}

function onKeywordFileRemove() {
  keywordFile.value = null;
}

function onStepFileChange(file) {
  stepFile.value = file.raw;
}

function onStepFileRemove() {
  stepFile.value = null;
}

function submitKeywordImport() {
  if (!keywordFile.value) {
    ElMessage.warning("请先选择关键字文件");
    return;
  }

  const formData = new FormData();
  formData.append("import_type", "keyword_code");
  formData.append("file", keywordFile.value);
  formData.append("name", keywordImport.name);
  formData.append("keyword_fun_name", keywordImport.keyword_fun_name);
  formData.append("operation_type_id", keywordImport.operation_type_id);
  formData.append("is_enabled", keywordImport.is_enabled);
  formData.append("keyword_desc", "[]");

  importPlatformKeywords(formData).then((res) => {
    ElMessage.success(`关键字已${res.data.data.action}`);
  });
}

function submitStepImport() {
  if (!stepFile.value) {
    ElMessage.warning("请先选择步骤文本文件");
    return;
  }

  const formData = new FormData();
  formData.append("import_type", "step_lines");
  formData.append("file", stepFile.value);
  formData.append("web_info_id", stepImport.web_info_id);
  formData.append("key_word_id", stepImport.key_word_id);

  importPlatformKeywords(formData).then((res) => {
    ElMessage.success(`已导入 ${res.data.data.created_count} 个步骤`);
  });
}

loadSettings();

function onTestNotification() {
  if (!form.notification.webhook_url) {
    ElMessage.warning("请先填写 Webhook URL");
    return;
  }
  testingNotification.value = true;
  testNotification({
    platform: form.notification.platform,
    webhook_url: form.notification.webhook_url,
  })
    .then(() => {
      ElMessage.success("测试通知已发送，请检查群消息");
    })
    .catch(() => {
      ElMessage.error("发送失败，请检查 Webhook URL 是否正确");
    })
    .finally(() => {
      testingNotification.value = false;
    });
}

function onRunDiagnostics() {
  diagnosticsRunning.value = true;
  runPlatformDiagnostics()
    .then((res) => {
      diagnostics.value = (res.data.data.items || []).map((item) => ({
        level: item.status === "fail" ? "warning" : item.status === "pass" ? "success" : "info",
        title: `${item.name}：${item.status}`,
        detail: item.detail,
      }));
      ElMessage.success("配置检测完成");
    })
    .catch(() => {
      ElMessage.error("配置检测失败");
    })
    .finally(() => {
      diagnosticsRunning.value = false;
    });
}
</script>

<style scoped>
.platform-settings {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.pane {
  padding: 22px;
}

.pane-header {
  margin-bottom: 18px;
}

.pane-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #f0f0f0;
}

.browser-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.browser-item {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.browser-empty {
  grid-column: 1 / -1;
  padding: 40px;
  text-align: center;
  color: #9ca3af;
  border: 1px dashed #d1d5db;
  border-radius: 8px;
}

.diagnostics {
  grid-column: 1 / -1;
}

.diag-alert + .diag-alert {
  margin-top: 12px;
}

.diagnostics-actions {
  justify-content: flex-start;
  margin-top: 0;
  margin-bottom: 14px;
}

.settings-note {
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
  margin-top: -8px;
}

@media (max-width: 1080px) {
  .settings-grid,
  .browser-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
