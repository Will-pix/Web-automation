<template>
    <!-- inline代表form的元素行级显示 -->
    <el-form ref="searchFormRef" :model="searchForm" :inline="true">
        <el-form-item label="任务名称">
            <el-input v-model="searchForm.task_name" placeholder="输入任务名称"></el-input>
        </el-form-item>
        <el-form-item label="所属项目" style="width: 200px;">
            <el-select v-model="searchForm.project_id" placeholder="集合所属项目" clearable @change="projectChange">
                <el-option v-for="project in projectlist" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="所属集合"  style="width: 200px;">
            <el-select v-model="searchForm.collection_id" placeholder="项目筛选集合" clearable multiple>
                <el-option v-for="collection in collectionlist" :key="collection.id" :label="collection.collection_name" :value="collection.id"></el-option>
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
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData(-1)">查询</el-button>
            <el-button type="warning" @click="onDataForm">新增任务</el-button>
        </el-row>
    </el-form>
    <!-- 数据表格 -->
    <el-table :data="tableData">
        <el-table-column v-for="task in tasklist" :prop="task.prop" :label="task.label" :key="task.prop">
            <!-- 特殊列使用自定义模板 -->
            <template #default="scope" v-if="task.prop === 'is_state' || task.prop === 'task_type' || task.prop === 'collection_name' || task.prop === 'inform' || task.prop === 'collection_env_type'">
                <span v-if="task.prop === 'is_state'">
                    {{ scope.row.is_state ? '通过' : '未通过' }}
                </span>
                <span v-else-if="task.prop === 'collection_env_type'">
                    {{ getEnvTypeName(scope.row.collection_env_type) }}
                </span>
                <span v-else-if="task.prop === 'task_type'">
                    {{ formatTaskType(scope.row.task_type) }}
                </span>
                <span v-else-if="task.prop === 'collection_name'">
                    {{ getCollectionName(scope.row.collection_id) }}
                </span>
                  <!-- 免打扰状态开关 -->
                <span v-else-if="task.prop === 'inform'">
                    <el-switch 
                        v-model="scope.row.inform" 
                        class="ml-2" 
                        style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" 
                        @change="handleInformSwitchChange(scope.row)"
                    />
                </span>
            </template>
        </el-table-column>
        <!-- 操作 -->
         <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small"  @click.prevent="editDataForm(scope.$index)">编辑</el-button>
                <el-button link type="primary" size="small"  @click.prevent="showWebHistorysDialog(scope.$index)">执行记录</el-button>
                <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="onDelete(scope.$index)">
                        <template #reference="scope">
                            <el-button link type="primary" size="small">删除</el-button>
                        </template>
                </el-popconfirm>
            </template>
         </el-table-column>
     </el-table>
     <div>
        <!-- 分页 total总数，currentPage页码，pageSize每页展示数量 handleSizeChange切换每页展示数量，handleCurrentChange切换页码-->
        <el-pagination v-model:current-page="pagination.currentPage" v-model:page-size="pagination.limit" :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper" :total="pagination.total" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />
    </div>
    <!-- 编辑弹窗 -->
    <WebTimeTaskForm :create_edit="create_edit" @close="create_edit = false" :edit="edit" @updatelist="loadData"/>
    <!-- 报告弹窗 -->
    <WebCollectionHistoryTimeDialog :tableDataid="tableDataid" :taskId="taskId" :webHistoryDialogFormVisible="webHistoryDialogFormVisible" @close="webHistoryDialogFormVisible = false"/>
</template>

<script setup>
import {ref,reactive, watch} from "vue"
import { ElMessage } from "element-plus";
import { queryAll as projectqueryall} from "../project/WebProject";
import { queryByPage as collectionqueryall} from "../collection/WebCollectionInfo.js";
import WebTimeTaskForm from "./WebTimeTaskForm.vue";
import { queryAllCreateBy } from "~/views/users/user.js"


// 搜索的双向绑定数据
const searchForm = reactive({
    "task_name":"",
    "project_id":"",
    "collection_id":[],
    "collection_env_type":""
})
// 项目的列表值
const projectlist = ref([])
// 项目的获取
const getprojectlist = () =>{
    projectqueryall().then((res)=>{
        console.log("项目的列表值为:",res.data.data)
        projectlist.value= res.data.data
    })
}
getprojectlist()
// 触发集合查询
const projectChange = () =>{
    // 先清空集合列表
    searchForm.collection_id = []
    // 复用-清理弹窗表单
    // taskForm.collection_id = ''
    getcollectionlist()
}
// 集合的列表值
const collectionlist = ref([])
// 集合的获取
const getcollectionlist = () =>{
    collectionqueryall({
        "page":1,
        "pageSize":9999999,
        "project_id":searchForm.project_id
    }).then((res)=>{
        console.log("集合的列表值为:",res.data.data)
        collectionlist.value = res.data.data
    })
}
// 表格数据
const tableData = ref([])
// 表格列
const tasklist = ref([
    {prop:"id",label:"任务id"},
    {prop:"task_name",label:"任务名称"},
    {prop:"task_type",label:"执行类型"},
    {prop:"collection_id",label:"测试集id"},
    {prop:"collection_name",label:"测试集名称"},
    { prop: "collection_env_type", label: '执行环境' },
    {prop:"last_time",label:"最近执行时间"},
    {prop:"is_state",label:"最近执行状态"},
    {prop:"task_num",label:"执行总次数"},
    { prop: "update_time", label: '更新时间' },
    { prop: "update_name", label: '更新人' },
    { prop: "create_time", label: '创建时间' },
    { prop: "create_name", label: '创建人' },
    { prop: "inform", label: '免打扰状态' }
])
// 分页参数
const pagination = ref({
    total: 0,
    limit: 10,
    currentPage: 1
  })
// 页码变更
const handleCurrentChange =(val)=>{
    pagination.value.currentPage = val
    loadData()
}
// 分页数据大小变更
const handleSizeChange =(val)=>{
    pagination.value.limit = val
    loadData()
}
import {queryByPage,insertData,queryById,uptateData,deleteData} from '~/views/webtest/webtimetask/Webtimetask.js'
// 获取所有数据
const loadData = () =>{
    let searchdata = searchForm
    searchdata["page"] = pagination.value.currentPage //这是页码
    searchdata["pageSize"] = pagination.value.limit  //这是每页多少条数据
    // 传出的数据为
    console.log("传出的数据为",searchdata)
    // 请求
    // getcollectionlist()
    queryByPage(searchdata).then((res)=>{
        tableData.value = res.data.data
        pagination.value.total = res.data.total
        get_collection_name_list()
})}
loadData()
// 格式化任务类型
const formatTaskType = (type) => {
    return type === 'interval_task' ? '间隔任务' : 
           type === 'fixed_task' ? '定时任务' : 
           type === 'cron_task' ? 'cron自定义时间' : 
           type
           ;
};
// 渲染需要的集合全量映射
const collection_name_list = ref([])
// 获取渲染需要的集合全量映射
const get_collection_name_list = ()=>{
    collectionqueryall({
        "page":1,
        "pageSize":9999999,
    }).then((res)=>{
        collection_name_list.value = res.data.data
        console.log("渲染需要集合的列表值为:",collection_name_list.value)

    })
}
// 通过id查找name的方法
const getCollectionName = (id) =>{
    // 从全局集合列表中找到对应ID的项，并返回其名称
    const collectionItem = collection_name_list.value.find(item => item.id === id);
    return collectionItem?.collection_name || '未找到'
}
// 弹窗的状态-编辑
const create_edit = ref(false)
// 编辑的临时存储
const edit = ref(0)
// 新增查询按钮
const onDataForm = () =>{
    edit.value = 0
    create_edit.value = true
}
// 编辑
const editDataForm = (index) =>{
    let id = tableData.value[index].id
    edit.value = id
    console.log("临时的id",edit.value)
    create_edit.value = true
}
// 删除
const onDelete  = (index) =>{
    deleteData(tableData.value[index]["id"]).then((res)=>{
        ElMessage.success("删除成功")
        loadData()
    })
}
import WebCollectionHistoryTimeDialog from "../collection/WebCollectionHistoryTimeDialog.vue";
// 报告弹窗状态
const webHistoryDialogFormVisible = ref(false) // 是否展示弹窗
// 临时存储的点击id--集合id
const tableDataid = ref()
// 临时存储主表id
const taskId = ref() // 临时存储的点击行的任务id
// 点击触发报告弹窗
const showWebHistorysDialog = (index) => {
    webHistoryDialogFormVisible.value =true
    // 点击后获取id并传递
    console.log("传递的id",tableData.value[index].collection_id)
    tableDataid.value = tableData.value[index].collection_id
    console.log("实际的集合id",tableDataid.value)
    console.log("实际的主表id",tableData.value[index].id)
    taskId.value = tableData.value[index].id

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

// 免打扰开关状态变更处理
const handleInformSwitchChange = (row) => {
    const originalValue = !row.inform; // 保存原始值用于回滚
    const updateData = {
        id: row.id,
        inform: row.inform
    };
    
    uptateData(updateData).then((res) => {
        if (res.data.code === 200) {
            ElMessage.success(`免打扰已${row.inform ? '开启' : '关闭'}`);
            loadData()
        } else {
            // 接口返回失败时回滚状态
            row.inform = originalValue;
            ElMessage.error(`更新失败：${res.data.msg || '服务器异常'}`);
        }
    }).catch((err) => {
        // 网络错误时回滚状态
        row.inform = originalValue;
        ElMessage.error('网络错误，更新失败');
    });
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