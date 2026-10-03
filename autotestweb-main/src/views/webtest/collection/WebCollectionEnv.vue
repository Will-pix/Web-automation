<template>
    <!-- 运行环境配置 -->
    <el-divider content-position="left" class="custom-center">运行环境</el-divider>
    <el-form-item label="浏览器运行选择" prop="browser_id">
        <el-select v-model="webcollection.browser_id" placeholder="选择浏览器" clearable filterable>
                <el-option v-for="browser in browserList" :key="browser.id" :label="browser.name" :value="browser.id" />
        </el-select>
    </el-form-item>
    <!-- 全局变量 -->
    <el-divider content-position="left" class="custom-center">全局变量</el-divider>
    <el-table :data="webcollection.collection_env" class="table_data" max-height="250">
        <el-table-column prop="key" label="变量名" style="width: 40%" />
        <el-table-column prop="value" label="变量值" style="width: 40%" />
        <el-table-column fixed="right" label="操作" style="width: 15%">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="deleteVars(scope.$index)">删除</el-button>
            </template>
        </el-table-column>
    </el-table>
    <div class="input-group">
        <el-input v-model="vars.key" placeholder="变量名" style="width: 40%" />
        <el-input v-model="vars.value" placeholder="变量值" style="width: 40%" />
        <el-button style="width: 15%" @click="onAddVars">添加</el-button>
    </div>
</template>

<script setup>
import {ref,reactive} from 'vue'
import { ElMessage } from "element-plus";
const props = defineProps(["webcollection"]); // 接收父组件数据
// 浏览器列表
const browserList = ref([])
// 获取浏览器列表
import { queryByPage as queryByPageAllbrowser } from "../browserRemote/WebBrowser.js"; // 不同页面不同的接口
function getbrowserList() {
  let searchData = {
    "page": 1,
    "pageSize": 999
  }
  queryByPageAllbrowser(searchData).then((res) => {
    browserList.value = res.data.data;
  });
}
getbrowserList();
// 临时存储变量数据
const vars = reactive({
  key: "",
  value: "",
});
// 添加进主数据内
const onAddVars = () => {
    console.log("添加时",vars)
  // 检查 key 和 value 是否都不为空
  if (!vars.key || !vars.value) {
    ElMessage.warning('变量名和变量值不能为空'); // 提示用户
    return; // 阻止执行后续代码
  }
  // 保存起来
  props.webcollection.collection_env.push({
    key: vars.key,
    value: vars.value,
  });
  // 置空
  vars.key = "";
  vars.value = "";
  console.log("清空后",vars)

};
// 从主数据中删除
const deleteVars = (index) => {
  props.webcollection.collection_env.splice(index, 1);
};
</script>
<style scoped>
.custom-center {
  --el-divider-text-padding: 0 12px; /* 调整文字两侧的间距 */
  --el-divider-font-size: 14px; /* 调整文字大小 */
}
/* 使用 :deep() 穿透样式作用域 */
.custom-center :deep(.el-divider__text) {
  color: rgba(75, 79, 89, 0.5); /* 目标颜色 */
}
</style>