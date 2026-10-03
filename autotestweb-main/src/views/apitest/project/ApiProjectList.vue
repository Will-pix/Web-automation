<template>
    <!-- 查询-新增 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-for-inline">
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadDate()">查询</el-button>
            <el-button type="warning" @click="onDataForm">新增数据</el-button>
        </el-row>
    </el-form>
    <!-- 数据表格 -->
     <el-table :data="tableData" style="width: 100%" max-height="500">
        <!-- --数据列-- -->
         <el-table-column
         v-for="col in columnList"
         :prop="col.prop"
         :label="col.label"
         :key="col.prop"
         show-coverflow-rooltip = true
         ></el-table-column>
         <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small" @click="openedit(scope.$index)">编辑</el-button>
                <el-popconfirm
                title="是否删除"
                confirm-button-text="确认"
                cancel-button-text="取消"
                @confirm="ondel(scope.$index)">
                <template #reference="scope">
                    <el-button link type="primary" size="small">删除</el-button>
                </template>
            </el-popconfirm>
                
            </template>
        </el-table-column>
     </el-table>
     <!-- 分页 -->
     <div class="demo-pagination-block">
        <div class="demonstration"></div>
            <el-pagination
            background
            layout="total,sizes,prev, pager, next, jumper" 
            :page-sizes="[10,20,30,50]"
            :total="pagination.total" 
            :page-size="pagination.limit" 
            :current-page="pagination.currentPage"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"/>
      </div>
</template>

<script setup>
import {ref,reactive} from "vue"
import {useRouter,useRoute} from "vue-router"
import {queryByPage,deleteData} from "./ApiProject.js"
import { ElMessage } from "element-plus";
const route = useRoute();
const router = useRouter()
// 表格列
const columnList = ref([
    {prop:"id",label:"项目编号"},
    {prop:"project_name",label:"项目名称"},
    {prop:"project_desc",label:"项目描述"},
    {prop:"create_time",label:"创建时间"}
])
// 分页
const pagination = ref({
    total: 0,
    limit: 10,
    currentPage: 1
  })
// 搜索功能-表单中的筛选
const searchForm = reactive({})
// 表格数据
const tableData = ref([
])
// 查询数据
const loadDate = ()=>{
    // 先获取从编辑页面传过来的页码并设置
    const pageParam = route.query.currentPage;
    // console.log('duoshao',pageParam)
    if (pageParam) {
        // 使用parseInt将字符串转换为数字
        pagination.value.currentPage = parseInt(pageParam)
        // 清空URL的参数
        router.replace({
            path: route.path,
            query: Object.fromEntries(
                Object.entries(route.query).filter(([key]) => key!== 'currentPage'))
        })
    }
    let searchData = searchForm
    searchData["page"] = pagination.value.currentPage
    searchData["pageSize"] = pagination.value.limit
    queryByPage(searchData).then((res)=>{
        tableData.value = res.data.data
        pagination.value.total = res.data.total
    })

}
// 初始化数据
loadDate()
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
// 打开新增窗口
const onDataForm=()=>{
    router.push({
        path:"/ApiProjectForm"
    })
}
// 编辑窗口
const openedit=(index)=>{
    const id = tableData.value[index].id;
    console.log("传递的id", id);
    // 传递参数，通过重新请求获取编辑数据、携带当前的页码
    let params_data = {}
    params_data={
        id:tableData.value[index]["id"],
        currentPage:pagination.value.currentPage
    }
    router.push({
        path:"/ApiProjectFormedit",
        query:params_data
    })
}
// 删除
const ondel=(index)=>{
    // 调用删除函数
    console.log(tableData.value[index]["id"])
    deleteData(tableData.value[index]["id"]).then((res)=>{
        if(res.data.code==200){
            ElMessage.success("删除成功");
            loadDate()
        }else{
            ElMessage.error(res.data.msg)
        }
    })
}
</script>

<style scoped>
.demo-pagination-block + .demo-pagination-block {
  margin-top: 10px;
}

.demo-pagination-block .demonstration {
  margin-bottom: 16px;
}
</style>