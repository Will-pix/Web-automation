<template>
    <div>
        <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-for-inline" >
            <el-form-item label="接口名称">
                <el-input v-model="searchForm.api_name" placeholder="根据接口名称筛选"></el-input>
            </el-form-item>
            <el-form-item label="所属项目">
                <!-- 绑定事件，如果选中projectChange才加载模块数据 change这是select的固定写法监听是否选中数据，默认情况下传递的是v-model的值-->
                <el-select v-model="searchForm.project_id" placeholder="所属项目" @change="projectChange" clearable style="width: 120px;">
                    <!-- 渲染下拉框的内容  key是下拉的主要标识，value是下拉内容的id，value作为提交参数 label是渲染显示的-->
                    <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="所属模块">
                <el-select v-model="searchForm.module_id" placeholder="所属模块" clearable style="width: 120px;">
                    <!-- 渲染下拉框的内容  key是下拉的主要标识，value是下拉内容的id，value作为提交参数 label是渲染显示的-->
                    <el-option v-for="module_info in moduleList" :key="module_info.id" :label="module_info.module_name" :value="module_info.id"></el-option>
                </el-select>
            </el-form-item>
            <!-- class="mb-4"为底部外边距（windicass）type 是 el-row 组件特有的属性（弹性布局）justify 也是 el-row 组件的属性靠右对齐（基于type=flex基础上设置）-->
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
            <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop" show-overflow-tooltip="true">
            </el-table-column>
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
    </div>
</template>

<script setup>
import {ref, reactive} from "vue"
import {useRouter,useRoute} from "vue-router"
import { ElMessage } from "element-plus";
import { queryAll } from "../project/ApiProject.js"
import {queryByPage as apiModuleQuery} from "~/views/apitest/module/ApiModule.js"
import {queryByPage,deleteData} from "~/views/apitest/apiinfo/ApiInfo.js"

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
// 搜索内容的数据
const searchForm=reactive({
    "api_name":'',
    "project_id":'',
    "module":''
})
// 表格头的展示数据
const columnList = ref([
  { prop: "id", label: '接口用例编号' },
  { prop: "api_name", label: '接口名称' },
  { prop: "request_method", label: '请求方法' },
  { prop: "request_url", label: '请求地址' }
])
// 表格数据
const tableData = ref([])
// 加载页面数据
const loadDate = ()=>{
    let searchdata = searchForm
    searchdata["page"] = pagination.value.currentPage
    searchdata["pageSize"] = pagination.value.limit
    // 请求
    queryByPage(searchdata).then((res)=>{
        tableData.value = res.data.data
        pagination.value.total = res.data.total
    })
}
// 初始化页面数据
loadDate()
// 打开新增数据页面
const onDataForm = () =>{
    router.push({
        path:"/ApiInfoForm"
    })
}
// 打开编辑页面
const ondataformedit=(index)=>{
    // 获取表单传递的index
    let id = tableData.value[index]["id"]
    console.log("传递的id",id)
    // 组装传递给编辑窗口的数据体
    let params_data = {}
    params_data={
        id: tableData.value[index]["id"],
        currentPage:pagination.value.currentPage
    }
    router.push({
        path:"/ApiInfoFormedit",
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
// 项目下拉框筛选的展示数据
const projectList = ref([])
// 请求获取下拉框筛选的数据
function getProjectList(){
    queryAll().then((res)=>{
        projectList.value = res.data.data
    })
}
// 初始化获取项目所需的列表数据
getProjectList()
// 项目筛选的监听方法，接收的是项目的id
const projectChange = (value)=>{
    // 多做一步，每次执行时先清空模块双向绑定已选的数据，防止不一致
    searchForm.module_id = ''
    // 直接调取获取模块的方法，不需要传值，因为值在searchForm的双向绑定里
    getmodulelist()
}
// 模块下拉框的数据-在内部定义数据~~~，主要是不需要全部的值（貌似不需要，可以直接全部赋值）
const moduleList = ref([])
// 请求获取模块的数据-参数从searchForm的双向绑定里取-这里复用模块的请求，用as起的别名
function getmodulelist(){
    // 需要传复用请求的请求体项目的id，页码，每页数据
    apiModuleQuery({
        "project_id":searchForm.project_id,
        "page":1,
        "pageSize":9999999
    }).then((res)=>{
        // 赋值给模块需要的下拉列表数据
        moduleList.value = res.data.data
    })
}
</script>