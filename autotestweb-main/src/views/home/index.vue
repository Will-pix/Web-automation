<template>
  <div class="dashboard">
    <section class="hero content-panel">
      <div>
        <div class="section-title">{{ branding.platform_name || "Web自动化测试平台" }}</div>
        <div class="hero-copy">{{ branding.platform_subtitle || "部署、浏览器自动化与AI执行，一站式管理。" }}</div>
      </div>
      <div class="hero-side">
        <div class="status-pill">环境就绪</div>
        <router-link to="/platform-settings">
          <el-button type="primary">打开平台设置</el-button>
        </router-link>
      </div>
    </section>

    <!-- 执行记录概览卡片 -->
    <section class="content-panel">
      <div class="section-title">执行记录概览（今日）</div>
      <div class="summary-grid">
        <div class="summary-card">
          <div class="summary-value">{{ summary.today_executions }}</div>
          <div class="summary-label">今日执行次数</div>
        </div>
        <div class="summary-card passed">
          <div class="summary-value">{{ summary.today_passed }}</div>
          <div class="summary-label">通过</div>
        </div>
        <div class="summary-card failed">
          <div class="summary-value">{{ summary.today_failed }}</div>
          <div class="summary-label">失败</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ summary.today_cases }}</div>
          <div class="summary-label">今日执行用例数</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ summary.total_executions }}</div>
          <div class="summary-label">历史总执行次数</div>
        </div>
      </div>
    </section>

    <!-- 近期执行记录表格 -->
    <section class="content-panel">
      <div class="preview-header">
        <div class="section-title">近期执行记录</div>
        <div class="preview-header-right">
          <el-select v-model="selectedTriggerType" placeholder="触发方式筛选" size="small" style="width: 140px; margin-right: 12px;" @change="loadRecords" clearable>
            <el-option label="全部记录" value="" />
            <el-option label="手动执行" value="手动执行" />
            <el-option label="集合执行" value="手动执行" />
            <el-option label="定时执行" value="定时任务" />
          </el-select>
          <el-button size="small" @click="loadRecords">刷新</el-button>
        </div>
      </div>
      <el-table :data="records" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="collection_name" label="集合名称" min-width="15%" show-overflow-tooltip />
        <el-table-column prop="project_name" label="所属项目" min-width="12%" show-overflow-tooltip />
        <el-table-column prop="collection_env_type" label="环境" min-width="8%" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ envLabel(row.collection_env_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" label="触发方式" min-width="9%" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.trigger_type === '定时任务' ? 'warning' : 'primary'">
              {{ row.trigger_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用例统计" min-width="14%" align="center">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: 600;">{{ row.passed_count }}</span>
            <span style="margin: 0 4px;">/</span>
            <span style="color: #f56c6c; font-weight: 600;">{{ row.failed_count }}</span>
            <span style="margin: 0 4px;">/</span>
            <span>{{ row.total_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="run_time" label="耗时" min-width="9%" align="center" />
        <el-table-column label="状态" min-width="8%" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'passed' ? 'success' : 'danger'">
              {{ row.status === 'passed' ? '通过' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="12%" align="center" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.history_detail" type="primary" size="small" link
              @click="openReport(row.history_detail)">
              查看报告
            </el-button>
            <span v-else style="color: #c0c4cc;">-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 30]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="loadRecords"
          @current-change="loadRecords"
        />
      </div>
    </section>

    <section class="content-panel preview-panel">
      <div class="preview-header">
        <div>
          <div class="section-title">浏览器预览墙</div>
          <div class="section-subtitle">硬编码的第三方预览链接已替换为可编辑端点。</div>
        </div>
      </div>

      <div class="preview-grid">
        <div v-for="(item, index) in previews" :key="index" class="preview-card">
          <div class="preview-title">
            <span>{{ item.name || `浏览器 ${index + 1}` }}</span>
            <div class="preview-actions">
              <el-button size="small" type="primary" plain @click="openPreview(item)">点击放大</el-button>
              <a v-if="item.url" :href="item.url" target="_blank" rel="noreferrer">新窗口打开</a>
            </div>
          </div>
          <div v-if="item.url" class="frame-shell">
            <iframe :src="item.url" class="preview-frame" />
          </div>
          <div v-else class="preview-empty">
            请前往平台设置配置预览URL。
          </div>
        </div>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="currentName" width="85%" top="3vh" :close-on-click-modal="false">
      <iframe :src="currentUrl" frameborder="0" style="width: 100%; height: 75vh; border: none;" />
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { fetchPlatformSettings } from "~/views/platform/platform.js";
import { getExecutionRecords } from "./workbench.js";
import { apiBaseURL } from "../../../config.js";

const branding = reactive({});
const previews = reactive([]);

const defaultPreviews = [
  { name: "browser-driver", url: "https://auto-browser-driver-test.yc345.tv/vnc.html?password=secret&autoconnect=true" },
  { name: "browser-driver2", url: "https://auto-browser-driver-test2.yc345.tv/vnc.html?password=secret&autoconnect=true" },
  { name: "browser-driver3", url: "https://auto-browser-driver-test3.yc345.tv/vnc.html?password=secret&autoconnect=true" },
  { name: "browser-driver4", url: "https://auto-browser-driver-test4.yc345.tv/vnc.html?password=secret&autoconnect=true" },
];

const dialogVisible = ref(false);
const currentUrl = ref("");
const currentName = ref("");
const openPreview = (item) => {
  currentUrl.value = item.url;
  currentName.value = item.name;
  dialogVisible.value = true;
};

// 执行记录
const records = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedTriggerType = ref("");
const summary = reactive({
  today_executions: 0,
  today_passed: 0,
  today_failed: 0,
  today_cases: 0,
  total_executions: 0,
});

const envLabel = (type) => {
  const map = { common: "通用", test: "测试", stage: "预发", online: "线上" };
  return map[type] || type || "通用";
};

const loadRecords = () => {
  loading.value = true;
  getExecutionRecords({ page: currentPage.value, pageSize: pageSize.value, trigger_type: selectedTriggerType.value }).then((res) => {
    const data = res.data.data;
    if (data) {
      records.value = data.records || [];
      total.value = res.data.total || 0;
      if (data.summary) {
        Object.assign(summary, data.summary);
      }
    }
  }).finally(() => {
    loading.value = false;
  });
};

const openReport = (historyDetail) => {
  window.open(apiBaseURL + "/WebHistory/" + historyDetail + "/index.html", "_blank");
};

fetchPlatformSettings().then((res) => {
  const data = res.data.data;
  Object.assign(branding, data.branding || {});
  const configured = (data.browser_previews || []).filter(item => item.url);
  previews.splice(0, previews.length, ...(configured.length > 0 ? configured : defaultPreviews));
});

onMounted(() => {
  loadRecords();
});
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 26px 28px;
}

.hero-copy {
  margin-top: 10px;
  max-width: 680px;
  color: #6b7280;
  font-size: 14px;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: flex-end;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
  margin-top: 14px;
}

.summary-card {
  text-align: center;
  padding: 18px 12px;
  border-radius: 8px;
  background: #f5f7fa;
  border: 1px solid #e5e7eb;
}

.summary-card.passed {
  background: #f0f9eb;
  border-color: #c2e7b0;
}

.summary-card.failed {
  background: #fef0f0;
  border-color: #fbc4c4;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.summary-card.passed .summary-value {
  color: #67c23a;
}

.summary-card.failed .summary-value {
  color: #f56c6c;
}

.summary-label {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}

.preview-panel {
  padding: 22px;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.preview-header-right {
  display: flex;
  align-items: center;
}

.preview-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.preview-card {
  display: flex;
  flex-direction: column;
  min-height: 320px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
}

.preview-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-weight: 600;
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-title a {
  color: #4080ff;
  font-size: 13px;
  text-decoration: none;
}

.preview-title a:hover {
  text-decoration: underline;
}

.frame-shell {
  flex: 1;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.preview-frame {
  width: 100%;
  height: 100%;
  min-height: 240px;
  border: none;
  background: #ffffff;
}

.preview-empty {
  display: grid;
  place-items: center;
  flex: 1;
  min-height: 240px;
  padding: 18px;
  text-align: center;
  border-radius: 8px;
  color: #6b7280;
  border: 1px dashed #d1d5db;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 1080px) {
  .hero,
  .hero-side {
    align-items: flex-start;
  }

  .hero {
    flex-direction: column;
  }

  .preview-grid {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
