<template>
    <!-- 查询新增 -->
     <el-form :model="searchFrom" :inline="true">
        <el-form-item label="浏览器名称">
            <el-input v-model="searchForm.name" placeholder="浏览器名称筛选" clearable></el-input>
        </el-form-item>
        <el-form-item label="所属项目">
            <el-select v-model="searchForm.project_id" placeholder="所属项目" clearable style="width: 120px;">
                <!-- 渲染下拉框的内容  key是下拉的主要标识，value是下拉内容的id，value作为提交参数 label是渲染显示的-->
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
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
        <!-- class="mb-4"为底部外边距（windicass）type 是 el-row 组件特有的属性（弹性布局）justify 也是 el-row 组件的属性靠右对齐（基于type=flex基础上设置）
         el-row一般代表行，el-col一般代表列-->
        <el-row class="mb-4" type="flex" justify="end">       
            <el-button type="primary" @click="loadDate">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
     </el-form>
     <el-table :data="tableData">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop">
            <template #default="scope">
                <span v-if="col.prop==='is_enabled'">
                    <!-- scope.row：当前行的完整数据对象（即tableData中的一个元素） -->
                    {{ scope.row.is_enabled === "0" ? '否' : scope.row.is_enabled === "1" ? '是':'-'}}
                </span>
            </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">编辑</el-button>
                <el-button link type="success" size="small" @click.prevent="onTestConnection(scope.$index)">测试连接</el-button>
                <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="ondel(scope.$index)">
                    <template #reference="scope">
                        <el-button link type="primary" size="small">删除</el-button>
                    </template>
                </el-popconfirm>
            </template>
        </el-table-column>
     </el-table>
     <div class="mt-4">
            <el-pagination background layout="total,sizes,prev, pager, next, jumper" 
            :page-sizes="[10,20,30,50]"
            :total="pagination.total" 
            :page-size="pagination.limit" 
            :current-page="pagination.currentPage"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"/>
    </div>
    <el-dialog v-model="testDialogVisible" title="浏览器池连接测试" width="620px">
        <el-alert
            v-for="(item, index) in testResultItems"
            :key="index"
            :type="item.status === 'fail' ? 'error' : item.status === 'pass' ? 'success' : 'warning'"
            :title="`${item.name}：${item.status}`"
            :description="item.detail"
            show-icon
            :closable="false"
            class="test-alert"
        />
    </el-dialog>
</template>

<script setup>
import {ref,reactive} from 'vue'
import { queryByPage,deleteData,testBrowserConnection} from './WebBrowser.js'
import {queryAll} from '~/views/webtest/project/WebProject.js'
import { ElMessage } from "element-plus";
import {useRouter,useRoute} from "vue-router"
import { queryAllCreateBy } from "~/views/users/user.js"


// 要发送的
const router = useRouter()
// 要接收的
const route = useRoute()
const testDialogVisible = ref(false)
const testResultItems = ref([])
// 分页参数
const pagination = ref({
    total: 0,
    limit: 10,
    currentPage: 1
  })
// 分页数据大小变更
const handleSizeChange =(val)=>{
    pagination.value.limit = val
    loadDate()
}
// 页码变更
const handleCurrentChange =(val)=>{
    pagination.value.currentPage = val
    loadDate()
}
// 搜索的双向绑定值
const searchForm = reactive({
    name :'',
    project_id :'',
})
// 项目的列表
const projectList = ref()
// 获取项目列表
const getprojectList = () =>{
    queryAll().then((res)=>{
        console.log("获取的列表为",res.data.data)
        projectList.value = res.data.data
    })
}
getprojectList()
// 查询数据
const loadDate = () =>{
    let searchdata = searchForm
    searchdata["page"] = pagination.value.currentPage
    searchdata["pageSize"] = pagination.value.limit
    queryByPage(searchdata).then((res)=>{
        if(res.data.code===200){
            tableData.value = res.data.data
            pagination.value.total = res.data.total
            // ElMessage.success("查询成功")
        }
    })
}
loadDate()
// 新增/编辑数据
const onDataForm = (index) =>{
    let param_data = {}
    if(index>=0){
        // 编辑
        param_data = {
            id:tableData.value[index]["id"]
        }
    }
    router.push({       // 新增
        path:"/WebBrowserForm",
        query:param_data
    })
}
// =============
// table数据
const tableData = ref([])
// 表格列
const columnList = ref([
    {prop:"id",label:"编号"},
    {prop:"name",label:"浏览器名称"},
    {prop:"enName",label:"浏览器英文名"},
    {prop:"remote_url",label:"Grid地址"},
    {prop:"browser_debug",label:"浏览器调试参数"},
    {prop:"is_enabled",label:"是否启动"},
    { prop: "update_time", label: '更新时间' },
    { prop: "update_name", label: '更新人' },
    { prop: "create_time", label: '创建时间' },
    { prop: "create_name", label: '创建人' }
])
// 删除
const ondel = (index) =>{
    let id = tableData.value[index]["id"]
    console.log(id)
    deleteData(id).then((res)=>{
        ElMessage.success("删除成功")
        loadDate()
    })
}
const onTestConnection = (index) =>{
    const id = tableData.value[index]["id"]
    ElMessage.info("正在测试浏览器连接...")
    testBrowserConnection(id).then((res)=>{
        testResultItems.value = res.data.data.items || []
        testDialogVisible.value = true
    }).catch(()=>{
        ElMessage.error("测试连接失败")
    })
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
</script>

<style scoped>
.test-alert + .test-alert {
    margin-top: 12px;
}
</style>
