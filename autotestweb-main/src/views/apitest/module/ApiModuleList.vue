<template>
    <!-- 查询-新增 筛选  searchFormRef为表单的对象，主要是提取数据及表单的验证
      :inline="true"主要是控制 el - form - item 的横向布局
      :model="searchForm"表单的渲染数据-->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-for-inline" >
        <!-- 搜索 -->
        <el-form-item label="模块名称">
            <el-input v-model="searchForm.module_name" placeholder="根据模块名称筛选"></el-input>
        </el-form-item>
        <el-form-item label="所属项目">
            <el-select v-model="searchForm.project_id" placeholder="所属项目" clearable style="width: 120px;">
                <!-- 渲染下拉框的内容  key是下拉的主要标识，value是下拉内容的id，value作为提交参数 label是渲染显示的-->
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
            </el-select>
        </el-form-item>
        <!-- class="mb-4"为底部外边距（windicass）type 是 el-row 组件特有的属性（弹性布局）justify 也是 el-row 组件的属性靠右对齐（基于type=flex基础上设置）
         el-row一般代表行，el-col一般代表列-->
            <el-row class="mb-4" type="flex" justify="end">
                <el-button type="primary" @click="loadDate">查询</el-button>
                <el-button type="warning" @click="onDataForm">新增数据</el-button>
            </el-row>
    </el-form>
    <!-- 表单数据 
     data是表单的数据，宽度100%，高度500-->
     <el-table :data="tableData" style="width: 100%;" max-height="500">
    <!-- 默认情况下，如果单元格内容过长，会占用多行显示。 若需要单行显示可以使用 show-overflow-tooltip 
    columnList是表格列的数据，label是列的表头，key是资源id,prop是列的数据指向，通过prop与data的数据对应渲染 -->
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop" show-overflow-tooltip="true"></el-table-column>
    <!-- 操作  fixed样式靠右，label表头名-->
         <el-table-column fixed="right" label="操作">
                  <!-- default 相当于给这个template传递表格的数据信息 索引 -->
            <template #default="scope">
                        <!-- link是可跳转的样式，size是样式大小，type是展示样式，这里的点击操作传入表的数据信息 -->
                <el-button link type="primary" size="small" @click.prevent="ondataformedit(scope.$index)">编辑</el-button>
                <!-- 二次确认删除逻辑 -->
                <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="onDelete(scope.$index)">
                    <template #reference="scope">
                        <el-button link type="primary" size="small">删除</el-button>
                     </template>
                </el-popconfirm>
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
</template>
<script setup>
import {ref, reactive} from "vue"
import {useRouter,useRoute} from "vue-router"
import { queryAll } from "../project/ApiProject.js"
import {queryByPage,deleteData} from "~/views/apitest/module/ApiModule.js"
import { ElMessage } from "element-plus";
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
    loadDate()
}
// 分页数据大小变更
const handleSizeChange =(val)=>{
    pagination.value.limit = val
    loadDate()
}
// 查询和筛选的表单数据-因为数据类型是字典用reactive
const searchForm = reactive({
    module_name :'',
    project_id :'',
})
// 下拉框筛选的展示数据
const projectList = ref([])
// 请求获取下拉框项目的数据
function getProjectList(){
    queryAll().then((res)=>{
        projectList.value = res.data.data
    })
}
// 每次进入页面获取项目列表
getProjectList()
// 表头的展示数据
const columnList = ref([
  { prop: "id", label: '模块编号' },
  { prop: "module_name", label: '模块名称' },
  { prop: "module_desc", label: '模块介绍' },
  { prop: "create_time", label: '创建时间' }
])
// 表单的展示数据
const tableData = ref([])
// 查询数据-接收input的参数与筛选的数据+分页数据
const loadDate = () =>{
    const pageParam = route.query.currentPage
    if (pageParam){
        pagination.value.currentPage = parseInt(pageParam)
        // 清空url参数
        router.replace({
            path:route.path,
            query:Object.fromEntries(
                Object.entries(route.query).filter(([key]) => key!== 'currentPage')
            )
        })
    }
    let searchdata = searchForm
    searchdata["page"] = pagination.value.currentPage
    searchdata["pageSize"] = pagination.value.limit
    // 发起请求
    queryByPage(searchdata).then((res)=>{
        tableData.value = res.data.data
        pagination.value.total = res.data.total
    })
}
loadDate()
// 打开新增数据页面
const onDataForm = () =>{
    router.push({
        path:"/ApiModuleForm"
    })
}
// 打开编辑页面
const ondataformedit=(index)=>{
    // 获取表单传递的index
    const id = tableData.value[index]["id"]
    console.log("传递的id",id)
    // 组装传递给编辑窗口的数据体
    let params_data = {}
    params_data={
        id: tableData.value[index]["id"],
        currentPage:pagination.value.currentPage
    }
    router.push({
        path:"/ApiModuleFormedit",
        query:params_data

    })
}
// 删除操作
const onDelete= (index)=>{
 // 调用删除函数
    console.log(tableData.value[index]["id"])
    deleteData(tableData.value[index]["id"]).then((res)=>{
        ElMessage.success("删除成功");
        loadDate()
    })
}
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
  margin-top: 10px;
}

.demo-pagination-block .demonstration {
  margin-bottom: 16px;
}
</style>