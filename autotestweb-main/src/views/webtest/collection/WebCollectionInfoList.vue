<template>
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="集合名称">
            <el-input v-model="searchForm.collection_name" placeholder="根据集合名称筛选" />
        </el-form-item>
        <el-form-item label="项目">
            <el-select v-model="searchForm.project_id" placeholder="项目" clearable>
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name"
                    :value="project.id" />
            </el-select>
        </el-form-item>
                <el-form-item label="创建人">
            <el-select v-model="searchForm.create_by" placeholder="根据创建人筛选" clearable style="width: 150px;">
                <el-option v-for="create in create_by_list" :label="create.create_name" :value="create.create_by"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="更新人">
            <el-select  v-model="searchForm.update_by" placeholder="根据更新人筛选" clearable style="width: 150px;">
                <el-option v-for="update in update_by_list" :label="update.create_name" :value="update.create_by"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="负责人">
            <el-select  v-model="searchForm.principal" placeholder="根据负责人筛选" clearable style="width: 150px;">
                <el-option v-for="update in update_by_list" :label="update.create_name" :value="update.create_by"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="执行环境">
            <el-select  v-model="searchForm.collection_env_type" placeholder="执行环境" clearable style="width: 150px;">
                    <el-option 
                    v-for="item in envTypeOptions" 
                    :key="item.value" 
                    :label="item.label" 
                    :value="item.value"
                ></el-option>
            </el-select>
        </el-form-item>
        <!-- 这里可以根据需要添加其他搜索条件 -->
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>
    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <!-- 数据列 -->
        <!-- 默认情况下，如果单元格内容过长，会占用多行显示。 若需要单行显示可以使用 show-overflow-tooltip，:show-overflow-tooltip="true"  -->
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop">
                <!-- 新增：对principal列进行ID转名称处理 -->
                     <template #default="scope">
                        <span v-if="col.prop === 'principal'">
                            {{ getPrincipalName(scope.row.principal) }}
                        </span>
                        <!-- 执行环境英文枚举转中文 -->
                        <span v-else-if="col.prop === 'collection_env_type'">
                            {{ getEnvTypeName(scope.row.collection_env_type) }}
                        </span>
                        <span v-else>
                            {{ scope.row[col.prop] }}
                        </span>
                    </template>
        </el-table-column>
        <!-- 操作 -->
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small" @click="onDataForm(scope.$index)">
                    编辑
                </el-button>
                <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="onDelete(scope.$index)">
                    <template #reference="scope">
                        <el-button link type="primary" size="small">删除</el-button>
                    </template>
                </el-popconfirm>
                <el-button link type="primary" size="small" @click="okExecuteTest(scope.$index)">
                    执行测试
                </el-button>
                <el-button link type="primary" size="small" @click="showWebHistorysDialog(scope.$index)">
                    执行记录
                </el-button>
             </template>
        </el-table-column>
    </el-table>
    <!-- 分页 -->
    <div class="mt-4">
            <el-pagination background layout="total,sizes,prev, pager, next, jumper" 
            :page-sizes="[10,20,30,50]"
            :total="pagination.total" 
            :page-size="pagination.limit" 
            :current-page="pagination.currentPage"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"/>
    </div>
    <!-- 报告弹窗 -->
    <WebCollectionHistoryDialog :tableDataid="tableDataid" :webHistoryDialogFormVisible="webHistoryDialogFormVisible" @close="webHistoryDialogFormVisible = false"/>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router";
import { queryByPage, deleteData} from './WebCollectionInfo.js' // 不同页面不同的接口
import { ElMessage } from "element-plus";
import { queryAllCreateBy } from "~/views/users/user.js"

// 要发送的
const router = useRouter()
// 分页参数
const pagination = ref({
    total: 0,
    limit: 10,
    currentPage: 1
  })
// 分页数据大小变更
const handleSizeChange =(val)=>{
    pagination.value.limit = val
    loadData()
}
// 页码变更
const handleCurrentChange =(val)=>{
    pagination.value.currentPage = val
    loadData()
}
// 表单实例
const searchFormRef = ref()
// 提交数据
const searchForm = reactive({
    collection_name:'',
    project_id:'',
    create_by: '', // 已有的其他筛选字段
    update_by: '', // 已有的其他筛选字段
    principal: '', // 新增：初始化负责人筛选字段
    collection_env_type: ''
})
// 项目列表
const projectList = ref([])
// 获取项目列表
import { queryAll } from "../project/WebProject.js"; // 不同页面不同的接口
const getProjectList = () =>{
    queryAll().then((res)=>{
        projectList.value = res.data.data;
    })
}
getProjectList();
// 表格数据
const tableData = ref([])
// 表格列 - 不同页面不同的列
const columnList = ref([
    { prop: "id", label: '集合编号' },
    { prop: "collection_name", label: '集合名称' },
    { prop: "collection_env_type", label: '执行环境' },
    { prop: "update_time", label: '更新时间' },
    { prop: "update_name", label: '更新人' },
    { prop: "create_time", label: '创建时间' },
    { prop: "create_name", label: '创建人' },
    { prop: "principal", label: '负责人' }
    // 其他列
])
// 加载页面数据
const loadData = () => {
    let searchData = searchForm
    searchData["page"] = pagination.value.currentPage
    searchData["pageSize"] = pagination.value.limit

    queryByPage(searchData).then((res) => {
        tableData.value = res.data.data
        pagination.value.total = res.data.total
    })
}
loadData()
// 打开表单 （编辑/新增）
const onDataForm = (index) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path: '/WebCollectionInfoForm', // 不同页面不同的表单路径
        query: params_data
    });
}
// 删除数据
const onDelete = (index) => {
    deleteData(tableData.value[index]["id"]).then((res) => {
        loadData()
    })
}
// -----------------------------扩展功能1-执行测试用例 --------------------------------
import { excuteTest } from "./WebCollectionInfo.js"; // 不同页面不同的接口
const okExecuteTest = (index) => {
  console.log("------开始执行测试用例计划集合编号------:",tableData.value[index].id);
 // 确定当前执行的ID
   let searchData = reactive({}); 
   searchData["id"] =  tableData.value[index].id;
// 调用执行的接口，并且把需要执行的ID传递过去
   excuteTest(searchData).then((res) => {
   console.log(res);
   if(res.data.code===200){
    ElMessage.success("执行成功，请去查看报告")
   }else{
    ElMessage.error("执行失败，联系管理员")
   }
  });
};
import WebCollectionHistoryDialog from "./WebCollectionHistoryDialog.vue";
// 报告弹窗状态
const webHistoryDialogFormVisible = ref(false) // 是否展示弹窗
// 临时存储的点击id
const tableDataid = ref()
// 点击触发报告弹窗
const showWebHistorysDialog = (index) => {
    webHistoryDialogFormVisible.value =true
    // 点击后获取id并传递
    console.log("传递的id",tableData.value[index].id)
    tableDataid.value = tableData.value[index].id
    console.log("实际的id",tableDataid.value)

}
// 创建人列表
const create_by_list = ref()
// 获取创建人列表
const get_create_by_list = () =>{
    queryAllCreateBy().then((res)=>{
        console.log("获取到的更新人列表为:", res.data)
        create_by_list.value = res.data.data
    })
}
get_create_by_list()
// 更新人列表
const update_by_list = ref()
// 获取更新人列表
const get_update_by_list = () =>{
    queryAllCreateBy().then((res)=>{
        console.log("获取到的更新人列表为:", res.data)
        update_by_list.value = res.data.data
    })
}
get_update_by_list()
// 根据负责人ID获取名称
const getPrincipalName = (principalId) => {
  // 若ID为空，直接返回默认值
  if (!principalId) return '-';
  // 在update_by_list中查找匹配的条目
  const matchItem = update_by_list.value?.find(item => item.create_by === principalId);
  // 找到则返回名称，未找到返回原ID
  return matchItem ? matchItem.create_name : principalId;
};
// 新增：集合环境类型选项列表（用于转换枚举值）
const envTypeOptions = ref([
  { label: '通用环境', value: 'common' },
  { label: '测试环境', value: 'test' },
  { label: '预发布环境', value: 'stage' },
  { label: '生产环境', value: 'online' }
])
// 新增：根据执行环境英文值获取中文标签
const getEnvTypeName = (envValue) => {
  // 若值为空，返回默认值
  if (!envValue) return '通用环境';
  // 在envTypeOptions中查找匹配的条目
  const matchItem = envTypeOptions.value?.find(item => item.value === envValue);
  // 找到则返回中文标签，未找到返回原值（兼容异常情况）
  return matchItem ? matchItem.label : envValue;
};
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}
</style>