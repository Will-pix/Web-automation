<template>
  <div class="quality-dashboard">
    <!-- 顶部筛选区域 -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-item filter-badge-item">
          <el-tag type="warning" size="large" effect="plain" round>📊 定时任务监控</el-tag>
        </div>
        <div class="filter-item">
          <span class="filter-label">日期范围：</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :clearable="false"
          />
        </div>
        <div class="filter-item">
          <span class="filter-label">选择项目：</span>
          <el-select
            v-model="selectedProjects"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="请选择项目（可多选）"
            style="width: 300px;"
            clearable
          >
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </div>
        <div class="filter-item">
          <span class="filter-label">执行环境：</span>
          <el-select
            v-model="selectedEnvTypes"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="请选择环境（可多选）"
            style="width: 300px;"
            clearable
          >
            <el-option
              v-for="(label, value) in envTypeOptions"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </div>
        <el-button type="primary" :icon="Search" @click="loadData" :loading="loading">
          查询
        </el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>
    </el-card>

    <!-- AI分析区域（仅单日显示） -->
    <div v-if="isSingleDay && dashboardData" class="ai-analysis-wrapper">
      <!-- AI分析按钮 -->
      <div class="ai-analysis-header">
        <el-button 
          type="primary" 
          :icon="MagicStick"
          @click="handleAIAnalysis" 
          :loading="aiLoading"
          size="large"
          class="ai-analysis-btn"
        >
          <span v-if="!aiLoading">🤖 AI智能分析当日测试质量</span>
          <span v-else>AI分析中...</span>
        </el-button>
        <span class="ai-tip">基于AI技术深度分析测试数据，提供专业洞察与改进建议</span>
        <el-button 
          v-if="aiAnalysisContent && !aiLoading"
          type="info"
          :icon="CopyDocument"
          @click="copyAnalysis"
          class="copy-btn"
        >
          复制报告
        </el-button>
      </div>

      <!-- AI分析内容展示 -->
      <transition name="slide-fade">
        <div v-if="showAIContent" class="ai-content-container">
          <el-card shadow="hover" class="ai-result-card">
            <!-- 加载状态 -->
            <div v-if="aiLoading" class="ai-loading">
              <el-icon class="is-loading" :size="40"><Loading /></el-icon>
              <p>AI正在深度分析测试数据，请稍候...</p>
            </div>
            <!-- 分析结果 -->
            <div v-else-if="aiAnalysisContent" class="markdown-body" v-html="renderedMarkdown"></div>
          </el-card>
        </div>
      </transition>
    </div>

    <!-- 数据展示区域 -->
    <div v-if="dashboardData" class="data-container">
      <!-- 一、整体质量概览 -->
      <div class="section-block">
        <div class="section-header">
          <div class="section-title">一、整体执行质量概览<span class="section-badge">定时任务</span></div>
        </div>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-card class="overview-card" shadow="hover">
              <div class="card-content">
                <div class="card-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
                  <el-icon :size="32"><DataAnalysis /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ dashboardData.overview.total_executions }}</div>
                  <div class="card-label">测试集合执行总次数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="5">
            <el-card class="overview-card" shadow="hover">
              <div class="card-content">
                <div class="card-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
                  <el-icon :size="32"><Document /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ dashboardData.overview.total_cases }}</div>
                  <div class="card-label">集合内测试用例执行总数量</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="5">
            <el-card class="overview-card" shadow="hover">
              <div class="card-content">
                <div class="card-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
                  <el-icon :size="32"><SuccessFilled /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ dashboardData.overview.total_success }}</div>
                  <div class="card-label">测试用例执行成功总数量</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="5">
            <el-card class="overview-card" shadow="hover">
              <div class="card-content">
                <div class="card-icon" style="background: linear-gradient(135deg, #ee6666 0%, #ff8787 100%)">
                  <el-icon :size="32"><CircleCloseFilled /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ dashboardData.overview.total_failed }}</div>
                  <div class="card-label">测试用例执行失败总数量</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="5">
            <el-card class="overview-card" shadow="hover">
              <div class="card-content">
                <div class="card-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%)">
                  <el-icon :size="32"><TrendCharts /></el-icon>
                </div>
                <div class="card-info">
                  <div class="card-value">{{ dashboardData.overview.success_rate }}%</div>
                  <div class="card-label">测试用例整体执行成功率</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 二、多维度分布统计 -->
      <div class="section-block">
        <div class="section-header">
          <div class="section-title">二、多维度分布统计</div>
        </div>

        <!-- 项目维度 -->
        <div class="sub-section">
          <div class="sub-section-title">项目维度</div>
          <el-card class="chart-card" shadow="hover">
            <v-chart class="chart" :option="projectChartOption" autoresize />
          </el-card>
        </div>

        <!-- 负责人维度 -->
        <div class="sub-section">
          <div class="sub-section-title">负责人维度</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="chart-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">测试用例负责人执行情况</span>
                  </div>
                </template>
                <v-chart class="chart" :option="casePrincipalChartOption" autoresize />
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="chart-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">测试集合负责人执行情况</span>
                  </div>
                </template>
                <v-chart class="chart" :option="collectionPrincipalChartOption" autoresize />
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>

    <!-- 三、执行明细 -->
    <div class="section-block" v-if="detailData && detailData.detail_list && detailData.detail_list.length > 0">
      <div class="section-header">
        <div class="section-title">三、执行明细</div>
        <div class="section-subtitle">共 {{ detailData.total }} 条记录</div>
      </div>
      <el-card shadow="hover">
        <el-table 
          :data="detailData.detail_list" 
          style="width: 100%"
          stripe
          :default-sort="{ prop: 'execute_time', order: 'descending' }"
        >
          <el-table-column type="expand">
            <template #default="props">
              <div class="expand-content">
                <div class="expand-header">测试用例列表（共 {{ props.row.cases.length }} 个用例）</div>
                <el-table :data="props.row.cases" size="small" border>
                  <el-table-column label="用例ID" prop="case_id" width="80" align="center" />
                  <el-table-column label="用例名称" prop="case_name" min-width="200" show-overflow-tooltip />
                  <el-table-column label="用例描述" prop="case_desc" min-width="250" show-overflow-tooltip>
                    <template #default="scope">
                      <span v-if="scope.row.case_desc" class="case-desc">{{ scope.row.case_desc }}</span>
                      <span v-else style="color: #c0c4cc;">暂无描述</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="用例负责人" prop="case_principal_name" width="120" align="center">
                    <template #default="scope">
                      <el-tag 
                        :type="scope.row.case_principal_id === '无' ? 'info' : 'success'" 
                        size="small"
                      >
                        {{ scope.row.case_principal_name }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="执行结果" prop="is_pass" width="100" align="center">
                    <template #default="scope">
                      <el-tag :type="scope.row.is_pass ? 'success' : 'danger'" size="small">
                        {{ scope.row.is_pass ? '通过' : '失败' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="集合ID" prop="collection_id" width="90" align="center" sortable />
          <el-table-column label="集合名称" prop="collection_name" min-width="200" show-overflow-tooltip />
          <el-table-column label="集合描述" prop="collection_desc" min-width="180" show-overflow-tooltip>
            <template #default="scope">
              <span v-if="scope.row.collection_desc" class="collection-desc">{{ scope.row.collection_desc }}</span>
              <span v-else style="color: #c0c4cc;">暂无描述</span>
            </template>
          </el-table-column>
          <el-table-column label="集合负责人" prop="collection_principal_name" width="120" align="center">
            <template #default="scope">
              <el-tag 
                :type="scope.row.collection_principal_id === '无' ? 'info' : 'primary'" 
                size="small"
              >
                {{ scope.row.collection_principal_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="用例数量" width="100" align="center">
            <template #default="scope">
              <el-text type="primary" size="large" style="font-weight: bold;">
                {{ scope.row.cases.length }}
              </el-text>
            </template>
          </el-table-column>
          <el-table-column label="执行结果" prop="is_pass" width="100" align="center" sortable>
            <template #default="scope">
              <el-tag :type="scope.row.is_pass ? 'success' : 'danger'">
                {{ scope.row.is_pass ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="执行时间" prop="execute_time" width="180" align="center" sortable />
        </el-table>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!dashboardData && !loading" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from "element-plus"
import { Search, Refresh, DataAnalysis, Document, SuccessFilled, TrendCharts, CircleCloseFilled, MagicStick, Loading, CopyDocument } from '@element-plus/icons-vue'
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { BarChart } from "echarts/charts"
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
} from "echarts/components"
import VChart from "vue-echarts"
import { queryByPage, queryByDetail, getQualityAIData } from './WebQuality.js'
import { queryAll } from '~/views/webtest/project/WebProject.js'
import { marked } from 'marked'

// 配置 marked（使用新版本 API）
marked.use({
  breaks: true,
  gfm: true
})

// 注册 ECharts 组件
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
])

// 数据存储
const dashboardData = ref(null)
const loading = ref(false)

// 日期范围
const dateRange = ref([])

// 项目列表
const projectList = ref([])
// 选中的项目ID列表
const selectedProjects = ref([])

// 执行环境选项
const envTypeOptions = {
  'common': '通用环境',
  'test': '测试环境',
  'stage': '预发布环境',
  'online': '生产环境'
}
// 选中的环境类型列表
const selectedEnvTypes = ref([])

// AI分析相关
const aiLoading = ref(false)
const aiAnalysisContent = ref('')
const displayedContent = ref('')
const showAIContent = ref(false)

// 判断是否为单日选择
const isSingleDay = computed(() => {
  if (!dateRange.value || dateRange.value.length !== 2) return false
  return dateRange.value[0] === dateRange.value[1]
})

// 渲染Markdown
const renderedMarkdown = computed(() => {
  if (!displayedContent.value) return ''
  
  try {
    // 使用 marked.parse() 解析 Markdown
    return marked.parse(displayedContent.value)
  } catch (error) {
    console.error('Markdown 解析错误:', error)
    return displayedContent.value
  }
})

// 初始化日期为今天
const initDate = () => {
  const today = new Date()
  const dateStr = today.toISOString().split('T')[0]
  dateRange.value = [dateStr, dateStr]
}

// 加载项目列表
const loadProjectList = () => {
  queryAll().then((res) => {
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  }).catch((err) => {
    console.error("加载项目列表失败:", err)
  })
}

// 重置筛选
const handleReset = () => {
  initDate()
  selectedProjects.value = []
  selectedEnvTypes.value = []
  // 清空AI分析内容
  clearAIAnalysis()
  loadData()
}

// 加载数据
const loadData = () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning("请选择日期范围")
    return
  }

  // 清空AI分析内容
  clearAIAnalysis()
  
  loading.value = true
  const searchData = {
    start_date: dateRange.value[0],
    end_date: dateRange.value[1],
    project_ids: selectedProjects.value,
    collection_env_type: selectedEnvTypes.value
  }

  // 同时加载概览数据和明细数据
  Promise.all([
    queryByPage(searchData),
    queryByDetail(searchData)
  ]).then((results) => {
    loading.value = false
    
    // 处理概览数据
    if (results[0].data.code === 200) {
      dashboardData.value = results[0].data.data
    } else {
      ElMessage.error(results[0].data.msg || "概览数据加载失败")
    }
    
    // 处理明细数据
    if (results[1].data.code === 200) {
      detailData.value = results[1].data.data
    } else {
      console.error("明细数据加载失败:", results[1].data.msg)
    }
    
    ElMessage.success("数据加载成功")
  }).catch((err) => {
    loading.value = false
    ElMessage.error("数据加载错误")
    console.error(err)
  })
}

// 项目维度图表配置
const projectChartOption = computed(() => {
  if (!dashboardData.value) return {}
  
  const projects = dashboardData.value.distribution.project || []
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        let result = `<div style="font-weight: bold; margin-bottom: 5px;">${params[0].axisValue}</div>`
        params.forEach(item => {
          result += `${item.marker}${item.seriesName}: ${item.value}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['执行次数', '总用例数', '成功数量', '失败数量', '成功率(%)'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: projects.map(p => p.project_name),
      axisLabel: {
        interval: 0,
        rotate: projects.length > 5 ? 30 : 0,
        fontSize: 12
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '数量',
        position: 'left',
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '成功率(%)',
        position: 'right',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '执行次数',
        type: 'bar',
        data: projects.map(p => p.execution_count),
        itemStyle: { color: '#5470c6' }
      },
      {
        name: '总用例数',
        type: 'bar',
        data: projects.map(p => p.total_cases),
        itemStyle: { color: '#91cc75' }
      },
      {
        name: '成功数量',
        type: 'bar',
        data: projects.map(p => p.success_count),
        itemStyle: { color: '#fac858' }
      },
      {
        name: '失败数量',
        type: 'bar',
        data: projects.map(p => p.failed_count),
        itemStyle: { color: '#ee6666' }
      },
      {
        name: '成功率(%)',
        type: 'bar',
        yAxisIndex: 1,
        data: projects.map(p => p.success_rate),
        itemStyle: { color: '#73c0de' }
      }
    ]
  }
})

// 测试用例负责人图表配置
const casePrincipalChartOption = computed(() => {
  if (!dashboardData.value) return {}
  
  const principals = dashboardData.value.distribution.case_principal || []
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        let result = `<div style="font-weight: bold; margin-bottom: 5px;">${params[0].axisValue}</div>`
        let total = 0
        params.forEach(item => {
          result += `${item.marker}${item.seriesName}: ${item.value}<br/>`
          total += item.value
        })
        const successRate = total > 0 ? ((params[0].value / total) * 100).toFixed(2) : 0
        result += `<div style="margin-top: 5px; color: #909399;">成功率: ${successRate}%</div>`
        return result
      }
    },
    legend: {
      data: ['成功数量', '失败数量'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: principals.map(p => p.principal_name),
      axisLabel: {
        interval: 0,
        rotate: principals.length > 5 ? 30 : 0,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '用例数量'
    },
    series: [
      {
        name: '成功数量',
        type: 'bar',
        stack: 'total',
        data: principals.map(p => p.success_count),
        itemStyle: { color: '#91cc75' },
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '失败数量',
        type: 'bar',
        stack: 'total',
        data: principals.map(p => p.failed_count),
        itemStyle: { color: '#ee6666' },
        emphasis: {
          focus: 'series'
        }
      }
    ]
  }
})

// 测试集合负责人图表配置
const collectionPrincipalChartOption = computed(() => {
  if (!dashboardData.value) return {}
  
  const principals = dashboardData.value.distribution.collection_principal || []
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        let result = `<div style="font-weight: bold; margin-bottom: 5px;">${params[0].axisValue}</div>`
        let total = 0
        params.forEach(item => {
          result += `${item.marker}${item.seriesName}: ${item.value}<br/>`
          total += item.value
        })
        const successRate = total > 0 ? ((params[0].value / total) * 100).toFixed(2) : 0
        result += `<div style="margin-top: 5px; color: #909399;">成功率: ${successRate}%</div>`
        return result
      }
    },
    legend: {
      data: ['成功数量', '失败数量'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: principals.map(p => p.principal_name),
      axisLabel: {
        interval: 0,
        rotate: principals.length > 5 ? 30 : 0,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '集合数量'
    },
    series: [
      {
        name: '成功数量',
        type: 'bar',
        stack: 'total',
        data: principals.map(p => p.success_count),
        itemStyle: { color: '#91cc75' },
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '失败数量',
        type: 'bar',
        stack: 'total',
        data: principals.map(p => p.failed_count),
        itemStyle: { color: '#ee6666' },
        emphasis: {
          focus: 'series'
        }
      }
    ]
  }
})

// 明细数据
const detailData = ref(null)

// 清空AI分析内容
const clearAIAnalysis = () => {
  showAIContent.value = false
  aiAnalysisContent.value = ''
  displayedContent.value = ''
}

// AI分析方法
const handleAIAnalysis = () => {
  if (!isSingleDay.value) {
    ElMessage.warning("AI分析仅支持单日数据")
    return
  }

  aiLoading.value = true
  showAIContent.value = true
  aiAnalysisContent.value = ''
  displayedContent.value = ''

  const searchData = {
    start_date: dateRange.value[0],
    end_date: dateRange.value[1],
    project_ids: selectedProjects.value,
    collection_env_type: selectedEnvTypes.value
  }

  getQualityAIData(searchData).then((res) => {
    aiLoading.value = false
    if (res.data.code === 200) {
      let content = res.data.data.ai_analysis || ''
      
      // 检查是否包含转义的换行符
      if (content.includes('\\n')) {
        // 替换转义的换行符为真实的换行符
        content = content.replace(/\\n/g, '\n')
      }
      
      aiAnalysisContent.value = content
      // 启动打字机效果（按行渲染）
      typeWriterEffect(content)
    } else {
      ElMessage.error(res.data.msg || "AI分析失败")
      showAIContent.value = false
    }
  }).catch((err) => {
    aiLoading.value = false
    ElMessage.error("AI分析请求失败")
    showAIContent.value = false
    console.error(err)
  })
}

// 打字机效果（按行渲染）
const typeWriterEffect = (text) => {
  // 将文本按行分割
  const lines = text.split('\n')
  let currentLine = 0
  const speed = 200 // 每行的延迟时间（毫秒），可调整速度
  
  const typeNextLine = () => {
    if (currentLine < lines.length) {
      // 添加当前行和换行符
      displayedContent.value += (currentLine > 0 ? '\n' : '') + lines[currentLine]
      currentLine++
      setTimeout(typeNextLine, speed)
    }
  }
  
  typeNextLine()
}

// 复制分析报告
const copyAnalysis = () => {
  if (!aiAnalysisContent.value) {
    ElMessage.warning("暂无内容可复制")
    return
  }
  
  navigator.clipboard.writeText(aiAnalysisContent.value).then(() => {
    ElMessage.success("报告已复制到剪贴板")
  }).catch(() => {
    ElMessage.error("复制失败，请手动复制")
    })
}

// 初始化
onMounted(() => {
  initDate()
  loadProjectList()
loadData()
})
</script>

<style scoped>
.quality-dashboard {
  padding: 20px;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
}

/* 筛选区域 */
.filter-card {
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.filter-badge-item {
  margin-right: 8px;
}

/* AI分析区域 */
.ai-analysis-wrapper {
  margin: 20px 0;
}

.ai-analysis-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  flex-wrap: wrap;
}

.ai-analysis-btn {
  font-size: 16px;
  padding: 12px 32px;
  height: auto;
  border: none;
  background: white;
  color: #667eea;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-analysis-btn:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.copy-btn {
  background: white;
  color: #67c23a;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.copy-btn:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
}

.ai-tip {
  color: white;
  font-size: 14px;
  opacity: 0.9;
  flex: 1;
  text-align: center;
  min-width: 200px;
}

/* 内容容器 */
.ai-content-container {
  margin-top: 20px;
}

.ai-result-card {
  background: white;
}

.ai-result-card :deep(.el-card__body) {
  padding: 40px;
}

.ai-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
  min-height: 200px;
}

.ai-loading p {
  margin-top: 20px;
  font-size: 16px;
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.4s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* 数据展示容器 */
.data-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 区域块 */
.section-block {
  background: transparent;
}

.section-header {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  padding-left: 12px;
  border-left: 4px solid #409eff;
  line-height: 1.4;
}

.section-badge {
  display: inline-block;
  margin-left: 12px;
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 500;
  color: #e6a23c;
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 4px;
  vertical-align: middle;
}

.section-subtitle {
  font-size: 14px;
  color: #909399;
  margin-left: 20px;
}

/* 子区域 */
.sub-section {
  margin-top: 30px;
}

.sub-section:first-child {
  margin-top: 0;
}

.sub-section-title {
  font-size: 16px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #67c23a;
}

/* 概览卡片 */
.overview-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 10px;
  height: 100%;
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 6px;
  line-height: 1.2;
}

.card-label {
  font-size: 13px;
  color: #909399;
  line-height: 1.4;
  word-break: break-all;
}

/* 图表卡片 */
.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.chart {
  width: 100%;
  height: 400px;
}

/* 明细展开区域 */
.expand-content {
  padding: 20px;
  background: #f5f7fa;
}

.expand-header {
  font-size: 15px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.case-desc {
  white-space: pre-line;
  line-height: 1.5;
}

.collection-desc {
  color: #606266;
}

/* 响应式适配 */
@media (max-width: 1400px) {
  .card-value {
    font-size: 20px;
  }
  
  .card-label {
    font-size: 12px;
  }
}

@media (max-width: 768px) {
  .quality-dashboard {
    padding: 10px;
  }

  .filter-container {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    width: 100%;
  }

  .section-title {
    font-size: 18px;
  }

  .sub-section-title {
    font-size: 14px;
  }

  .chart {
    height: 300px;
  }

  .expand-content {
    padding: 10px;
  }
}
</style>

<style>
/* Markdown样式 - 不使用scoped，以便v-html插入的内容能应用样式 */
.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  word-wrap: break-word;
}

.markdown-body * {
  box-sizing: border-box;
}

.markdown-body h1 {
  font-size: 28px;
  font-weight: bold;
  margin: 30px 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #667eea;
  color: #303133;
  line-height: 1.4;
}

.markdown-body h1:first-child {
  margin-top: 0;
}

.markdown-body h2 {
  font-size: 24px;
  font-weight: bold;
  margin: 25px 0 15px 0;
  color: #409eff;
  line-height: 1.4;
}

.markdown-body h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 20px 0 12px 0;
  color: #606266;
  line-height: 1.4;
}

.markdown-body h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 15px 0 10px 0;
  color: #909399;
  line-height: 1.4;
}

.markdown-body p {
  margin: 0 0 16px 0;
  line-height: 1.8;
}

.markdown-body ul,
.markdown-body ol {
  margin: 0 0 16px 0;
  padding-left: 30px;
}

.markdown-body li {
  margin-bottom: 8px;
  line-height: 1.6;
}

/* 表格样式 */
.markdown-body table {
  display: table;
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  overflow: hidden;
}

.markdown-body thead {
  display: table-header-group;
}

.markdown-body tbody {
  display: table-row-group;
}

.markdown-body tr {
  display: table-row;
}

.markdown-body th,
.markdown-body td {
  display: table-cell;
  padding: 12px 15px;
  text-align: left;
  vertical-align: top;
  border: 1px solid #e4e7ed;
  word-break: break-word;
}

.markdown-body th {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.markdown-body td {
  background: white;
  color: #606266;
  font-size: 14px;
}

.markdown-body tbody tr:nth-child(even) td {
  background: #fafafa;
}

.markdown-body tbody tr:hover td {
  background: #ecf5ff;
  transition: background 0.2s;
}

/* 代码样式 */
.markdown-body code {
  background: #f5f7fa;
  padding: 3px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  color: #e74c3c;
  font-size: 0.9em;
}

.markdown-body pre {
  background: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 16px 0;
  border: 1px solid #e1e4e8;
}

.markdown-body pre code {
  background: transparent;
  padding: 0;
  color: #333;
}

/* 引用样式 */
.markdown-body blockquote {
  border-left: 4px solid #409eff;
  padding-left: 20px;
  margin: 16px 0;
  color: #606266;
  background: #ecf5ff;
  padding: 15px 20px;
  border-radius: 4px;
}

.markdown-body blockquote p {
  margin-bottom: 0;
}

/* 加粗 */
.markdown-body strong {
  font-weight: bold;
  color: #303133;
}

/* 分隔线 */
.markdown-body hr {
  border: none;
  border-top: 2px solid #e4e7ed;
  margin: 24px 0;
}

/* 链接 */
.markdown-body a {
  color: #409eff;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}
</style>