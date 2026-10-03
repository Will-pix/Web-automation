<template>
    <!-- 查询/新增 -->
     <el-form ref="searchFormRef" :model="searchForm" :inline="true">
        <el-form-item label="模块名称">
            <el-input v-model="searchForm.project_name" placeholder="根据项目名称筛选"></el-input>
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
        <el-row type="flex" justify="end" class="mb-4">
            <el-button type="primary" @click="loadDate()">查询</el-button>
            <el-button type="warning" @click="ondataform(-1)">新增数据</el-button>
        </el-row>
    </el-form>
    <!-- 表格展示区 -->
    <el-table :data="tableData" :stripe="false">
        <el-table-column v-for="col in columnList" :key="col.prop" :label="col.label" :prop="col.prop"></el-table-column>
        <el-table-column label="操作" fixed="right">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="ondataform(scope.$index)">编辑</el-button>
                <el-button link type="primary" size="small" @click.prevent="ondbbase(scope.$index)">数据库配置</el-button>
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
    <!-- 数据库弹窗 -->
     <el-dialog v-model="DbBaseShow">
        <el-form-item>
            <el-table :data="dbbaselist">
                <el-table-column prop="name" label="连接名" style="width: 10%" />
                <el-table-column prop="ref_name" label="引用变量" style="width: 20%" show-overflow-tooltip="true" />
                <el-table-column prop="db_info" label="数据库连接信息" style="width: 40%" show-overflow-tooltip="true" />
                <el-table-column prop="is_enabled" label="是否启用" style="width: 10%" show-overflow-tooltip="true" >
                <template #default="scope">
                    {{ scope.row.is_enabled === "0"?'否' : scope.row.is_enabled === "1"?'是':'-' }}
                </template>
                </el-table-column>
                <el-table-column prop="db_type" label="数据库类型" style="width: 10%" show-overflow-tooltip="true" />
                <el-table-column label="操作" fixed="right"  style="width: 10%">
                    <template #default="scope">
                        <el-button link type="primary" size="small" @click.prevent="dbedit(scope.$index)">修改是否启用</el-button>
                        <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="dbondel(scope.$index)">
                            <template #reference="scope">
                                <el-button link type="primary" size="small">删除</el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>
            <el-input v-model="ruleForm.name" placeholder="连接名" style="width: 15%"/>
            <el-input v-model="ruleForm.ref_name" placeholder="引用变量" style="width: 15%"/>
            <el-input v-model="ruleForm.db_info" placeholder="数据库连接信息，如：{host: 主机IP/服务器, port: 端口号, username: 用户名, password: 密码, database: 数据库名}" style="width: 20%"/>
            <el-select v-model="ruleForm.is_enabled"  placeholder="是否启用"  style="width: 15%">
                <el-option v-for="item in options"  :key="item.value" :label="item.label"  :value="item.value" />
            </el-select>
            <el-select v-model="ruleForm.db_type" placeholder="数据库类型" style="width: 20%">
                <el-option v-for="item in optionsDbType"  :key="item.value" :label="item.label"  :value="item.value" />
            </el-select>
            <el-button style="width: 10%" type="primary" @click="onAddDbinfo">添加</el-button>
        </el-form-item>
        <div>
            数据库连接信息，如：{host: 主机IP/服务器, port: 端口号, username: 用户名, password: 密码, database: 数据库名}
        </div>
     </el-dialog>
</template>

<script setup>
import {ref,reactive} from 'vue'
import {queryByPage,deleteData} from '~/views/webtest/project/WebProject.js'
import { ElMessage } from "element-plus";
import {useRouter,useRoute} from "vue-router"
import {queryByPage as dbqueryByPage,uptateData as dbuptateData,insertData,deleteData as dbdeleteData} from '~/views/webtest/project/DbBaseManage.js'
import { queryAllCreateBy } from "~/views/users/user.js"
// import { getUserBypage } from "~/views/users/user.js"

// 要发送的
const router = useRouter()
// 要接收的
const route = useRoute()
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
// 搜索表单
const searchForm = reactive({
    project_name:'',
    create_by:'',
    update_by:''
})
// 搜索事件
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
// 表格数据的加载
const tableData = ref([])
// 表格表头的数据
const columnList = ref([
  { prop: "id", label: '项目编号' },
  { prop: "project_name", label: '项目名称' },
  { prop: "project_desc", label: '项目描述' },
  { prop: "update_time", label: '更新时间' },
  { prop: "update_name", label: '更新人' },
  { prop: "create_time", label: '创建时间' },
  { prop: "create_name", label: '创建人' }
])
// 新增/编辑项目
const ondataform = (index) =>{
    // 判断是新增还是修改的临时参数
    let params_data = {}
    if(index >=0){
        // 是编辑将id传进去
        params_data = {
            id:tableData.value[index]["id"]
        }
    }
    router.push({
        path:"/WebProjectForm",
        query:params_data
    })
}
// 删除
const ondel= (index) =>{
    let id = tableData.value[index]["id"]
    deleteData(id).then((res)=>{
        ElMessage.success("删除成功")
        loadDate()
    })
}
// 打开配置数据库数据
const ondbbase = (index) =>{
    clearnadd()
    dbbasevalue.value = tableData.value[index]["id"]
    ruleForm.project_id=dbbasevalue.value
    loaddbbase()
    console.log("此时存储的项目id为:", dbbasevalue.value)
    DbBaseShow.value = true
}
// =========
// 弹窗
const DbBaseShow = ref(false)
// 存储打开的配置得项目id
const dbbasevalue = ref(0)
// 表格的数据
const dbbaselist = ref([])
// 弹窗添加区
const ruleForm = reactive(
    {
        id:0,
        project_id:0,
        name:'',
        ref_name:'',
        db_info:'',
        db_type:'',
        is_enabled:'1',
    }
)
// 11-4 下拉列表的值-是否启动
const options = [
  {
    value: '1',
    label: '是',
  },
  {
    value: '0',
    label: '否',
  }
]
// 11-5 下拉列表的值-数据库类型
const optionsDbType = [
  {
    value: 'Mysql',
    label: 'Mysql',
  },
  {
    value: 'Oracle',
    label: 'Oracle',
  }
]
// 新增-弹窗添加
const onAddDbinfo  = () =>{
    // 将ruleForm的值保存
    insertData(ruleForm).then((res)=>{
        if(res.data.code===200){
            ElMessage.success("添加成功")
            clearnadd()
            loaddbbase()
        }else{
            ElMessage.error(res.data.msg)
        }
    })
}
// 清理添加区
const clearnadd = () =>{
    ruleForm.name='',
    ruleForm.ref_name='',
    ruleForm.db_info='',
    ruleForm.db_type='',
    ruleForm.is_enabled='1'
}
// 加载弹窗数据
const loaddbbase = () =>{
    let searchForm = {}
    searchForm["project_id"] = ruleForm.project_id
    searchForm["page"] = 1
    searchForm["pageSize"] = 9999
    dbqueryByPage(searchForm).then((res)=>{
        console.log("弹窗的数据为:",res.data.data)
        dbbaselist.value = res.data.data
    })
}
// 删除
const dbondel = (index) =>{
    let id = dbbaselist.value[index]["id"]
    console.log("应该删除的是",id)
    dbdeleteData(id).then((res)=>{
        ElMessage.success("删除成功")
        loaddbbase()
    })
}
// 修改暂存
const UpDataruleForm = reactive({
        id:0,
        project_id:0,
        name:'',
        ref_name:'',
        db_info:'',
        db_type:'',
        is_enabled:'1',
})
// 修改是否可用
const dbedit = (index) =>{
    let id = dbbaselist.value[index]["id"]
    UpDataruleForm.id = dbbaselist.value[index].id
    UpDataruleForm.project_id = dbbaselist.value[index].project_id
    UpDataruleForm.name = dbbaselist.value[index].name
    UpDataruleForm.ref_name = dbbaselist.value[index].ref_name
    UpDataruleForm.db_info = dbbaselist.value[index].db_info
    UpDataruleForm.db_type = dbbaselist.value[index].db_type
    UpDataruleForm.is_enabled = dbbaselist.value[index].is_enabled === '1' ? '0' : '1'; //三元表达式，是否等于1，成立赋值第一个。不成立赋值第二个
    console.log("应该删除的是",id)
    dbuptateData(UpDataruleForm).then((res)=>{
        loaddbbase()
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
