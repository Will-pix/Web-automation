<template>
    <!-- 表单横向展示 -->
    <el-form ref = "searchFormRef" :inline="true" :model="searchForm" class="demo-for-inline">
        <el-form-item label="集合名称">
            <!-- 集合的搜索输入 -->
             <el-input v-model="searchForm.collection_name" placeholder="根据集合名称筛选"></el-input>
        </el-form-item>
        <el-form-item label="项目">
            <!-- 项目的搜索下拉 clearable为删除功能-->
             <el-select v-model="searchForm.project_id" placeholder="所属项目" clearable style="width: 120px;">
                <el-option v-for="project in projectlist" :key="project.id" :value="project.id" :label="project.project_name"></el-option>
             </el-select>
        </el-form-item>
        <!-- 搜索操作 -->
            <!-- 主要是将这两个按钮进行排列方式-靠右 -->
            <el-row class="mb-4" type="flex" justify="end">
                <el-button type="primary" @click="loadData">查询</el-button>
                <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
            </el-row>
    </el-form>
    <!-- 表格-->
     <el-table :data="tableData" style="width: 100%;" max-height="500">
        <!-- 表头 -->
         <el-table-column v-for="col in columnlist" :prop="col.prop" :label="col.label" :key="col.prop" show-overflow-tooltip="true"></el-table-column>
         <!-- 操作栏 -->
          <el-table-column fixed="right" label="操作">
                <template #default="scope">
                    <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">编辑</el-button>
                    <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="onDelete(scope.$index)">
                        <template #reference="scope">
                            <el-button link type="primary" size="small">删除</el-button>
                        </template>
                    </el-popconfirm>
                    <el-button link type="primary" size="small" @click.prevent="onExecuteTest(scope.$index)">执行测试</el-button>
                    <el-button link type="primary" size="small" @click.prevent="showApiHistoryDialog(scope.$index)">执行记录</el-button>
                </template>
          </el-table-column>
     </el-table>
        <!-- 分页 total总数，currentPage页码，pageSize每页展示数量 handleSizeChange切换每页展示数量，handleCurrentChange切换页码-->
        <div class="demo-pagination-block">
            <div class="demonstration"></div>
            <el-pagination v-model:current-page="pagination.currentPage" v-model:page-size="pagination.limit" :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper" :total="pagination.total" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />
        </div>
    <!-- 报告弹窗 -->
     <el-dialog v-model="apiHistoryDialogFormVisible" title="执行记录">
        <el-form-item>
            <el-table :data="apiHistoryList" style="width: 100%;">
                <el-table-column prop="id" label="报告编号" min-width="20%" show-overflow-tooltip="true"></el-table-column>
            <el-table-column prop="history_desc" label="执行情况简述" min-width="30%" show-overflow-tooltip="true"></el-table-column>
            <el-table-column prop="create_time" label="执行时间" min-width="30%" show-overflow-tooltip="true"></el-table-column>
            <el-table-column fixed="right" label="操作" min-width="20%">
                <template #default="scope">
                    <el-button type="primary" size="small" @click.prevent="showApiHistory(scope.$index)">
                        查看报告
                    </el-button>
                </template>
            </el-table-column>
            </el-table>
        </el-form-item>
        <el-form-item>
            <el-pagination :current-page="currentApiHistoryPage" :page-size="apiHistoryPageSize" :total="apiHistoryTotal"
                @current-change="handleApiHistoryCurrentChange"></el-pagination>
        </el-form-item>
     </el-dialog>
</template>
<script setup>
import {ref,reactive} from "vue"
import {useRouter,useRoute} from "vue-router"
import { ElMessage } from "element-plus";
import { queryAll } from "../project/ApiProject.js"
import {queryByPage,deleteData,excuteTest} from '~/views/apitest/collection/ApiCollection.js'
// 要获取的路由
const route = useRoute()
// 要发送的路由
const router = useRouter()
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
// 搜索表单数据
const searchForm = reactive({
    collection_name:'',
    project_id:'',
})
// 项目的列表数据
const projectlist = ref([])
// 请求获取下拉框筛选的数据
function getProjectList(){
    queryAll().then((res)=>{
        projectlist.value = res.data.data
    })
}
// 初始化获取项目所需的列表数据
getProjectList()
// 查询的提交方法
const loadData = () =>{
    let searchdata = searchForm
    searchdata["page"] = pagination.value.currentPage
    searchdata["pageSize"] = pagination.value.limit
    // 请求
    queryByPage(searchdata).then((res)=>{
        tableData.value = res.data.data
        pagination.value.total = res.data.total
    })
}
// 初始化获取列表数据
loadData()
// 新增数据的提交方法-加上编辑
const onDataForm = (index) =>{
    console.log("要发送的值为",index)
    console.log("tableData的值为",tableData)
    let param_data = {}
    if (index >= 0){
        param_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path:"/ApiCollectionForm",
        query: param_data
    })
}
// 表头的数据
const columnlist = ref([
    {prop:"id",label:"测试集编号"},
    {prop:"collection_name",label:"测试集名称"}
])
// 表格数据
const tableData = ref([])
// 编辑事件
const onDataFormedit = (index)=>{

}
// 删除事件
const onDelete = (index)=>{
    deleteData(tableData.value[index]["id"]).then((res)=>{
        ElMessage.success("删除成功")
        loadData()
    })
}
// 执行事件
const onExecuteTest = (index)=>{
    console.log("获取到的执行事件id是:",index)
    console.log("执行事件:",tableData.value[index]["id"])
    excuteTest(tableData.value[index]["id"]).then((res)=>{
        ElMessage.success(res.data.msg)
    })
}
// ============
import {queryByPage as queryApiHistoryByPage} from '~/views/apitest/collection/ApiHistory.js'
// 执行记录弹窗的状态
const apiHistoryDialogFormVisible = ref(false)
// 当前展示的执行记录关联的 collectionId-临时存储
const currentCollectionId = ref(0) 
// 报告事件-执行记录
const showApiHistoryDialog = (index)=>{
    // 打开弹窗
    apiHistoryDialogFormVisible.value=true
    // 清空弹窗的全部信息
    apiHistoryTotal.value = 0
    apiHistoryPageSize.value = 10
    currentApiHistoryPage.value = 1
    apiHistoryList.value = []
    // 通过传入的index，获取表单的测试集id
    currentCollectionId.value = tableData.value[index]["id"]
    // 并且发送请求获取该集合id下的所有报告信息
    loadApiHistorys()
}
// 获取集合下的所有报告信息
const loadApiHistorys = () =>{
    let searchData = {}
    searchData["collection_id"] = currentCollectionId.value
    searchData["page"] = currentApiHistoryPage.value
    searchData["pageSize"] = apiHistoryPageSize.value
    queryApiHistoryByPage(searchData).then((res)=>{
        apiHistoryList.value = res.data.data
        apiHistoryTotal.value = res.data.total
        console.log("此时的apiHistoryList为:",apiHistoryList.value)
    })
}
// 分页数据
const currentApiHistoryPage = ref(1) // 页码
const apiHistoryPageSize = ref(10) // 每页大小
const apiHistoryTotal = ref(0) //总数
// 翻页
const handleApiHistoryCurrentChange = (val) => {
    currentApiHistoryPage.value = val
    loadApiHistorys()
}
// 单独打开某个报告的详情
const showApiHistory = (index) =>{
    // 注意： 这个地方的测试报告服务器地址，是需要根据后端服务器修改的，这里写死了，后面要改成配置文件
    var report_id = apiHistoryList.value[index]["history_detail"]
    window.open("http://127.0.0.1:5000/api/ApiHistory/"+report_id+"/index.html", '_blank');

}
// 弹窗的数据
const apiHistoryList = ref([])
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}
</style>
