<template>
    <!-- 查询新增 -->
    <el-form :model="searchFrom" :inline="true">
        <el-form-item label="wen用例名称">
            <el-input v-model="searchForm.case_name" placeholder="web用例名称筛选" clearable></el-input>
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
        <el-form-item label="负责人">
            <el-select  v-model="searchForm.principal" placeholder="根据负责人筛选" clearable style="width: 150px;">
                <el-option v-for="update in update_by_list" :label="update.create_name" :value="update.create_by"></el-option>
            </el-select>
        </el-form-item>
        <!-- class="mb-4"为底部外边距（windicass）type 是 el-row 组件特有的属性（弹性布局）justify 也是 el-row 组件的属性靠右对齐（基于type=flex基础上设置）
         el-row一般代表行，el-col一般代表列-->
        <el-row class="mb-4" type="flex" justify="end">       
            <el-button type="primary" @click="loadDate">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增用例</el-button>
        </el-row>
     </el-form>
     <!-- 表格 -->
     <el-table :data="tableData">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop">
            <template #default="scope">
                <span v-if="col.prop==='is_pre'">
                    <!-- scope.row：当前行的完整数据对象（即tableData中的一个元素） -->
                    {{ scope.row.is_pre === "0" ? '否' : scope.row.is_pre === "1" ? '是':'-'}}
                </span>
                    <!-- 新增：处理负责人ID转名称 -->
                <span v-else-if="col.prop === 'principal'">
                    {{ getPrincipalName(scope.row.principal) }}
                </span>
                    <!-- 其他列保持默认显示 -->
                <span v-else>
                    {{ scope.row[col.prop] }}
                </span>
            </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="dialog_copy(scope.$index)">复制</el-button>
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">编辑</el-button>
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
    <!-- 弹窗 -->
       <el-dialog  v-model="dialogVisible" title="复制用例" >
        <el-form-item label="用例名称">
                <el-input  v-model="newCaseName" placeholder="请输入新的用例名称"></el-input>
        </el-form-item>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="copy_onsubmit">确认</el-button>
                </span>
            </template>
       </el-dialog>
</template>

<script setup>
import {ref,reactive} from 'vue'
import { queryByPage,deleteData,copyCase} from './WebInfo.js'
import {queryAll} from '~/views/webtest/project/WebProject.js'
import { ElMessage } from "element-plus";
import {useRouter,useRoute} from "vue-router"
import { queryAllCreateBy } from "~/views/users/user.js"

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
// 表格列 
const columnList = ref([
  { prop: "id", label: "用例编号" },
  { prop: "case_name", label: "用例名称" },
  { prop: "case_desc", label: "用例描述" },
  { prop: "is_pre", label: "是否前置" },
    { prop: "update_time", label: '更新时间' },
    { prop: "update_name", label: '更新人' },
    { prop: "create_time", label: '创建时间' },
    { prop: "create_name", label: '创建人' },
    { prop: "principal", label: '负责人' }
])
// 表格数据
const tableData = ref([]);
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
        path:"/WebInfoForm",
        query:param_data
    })
}
// 删除
const ondel = (index) =>{
    let id = tableData.value[index]["id"]
    console.log(id)
    deleteData(id).then((res)=>{
        if(res.data.code===200){
            ElMessage.success("删除成功")
            loadDate()
        }else{
            ElMessage.error(`删除失败-检查是否为已存在集合中或被引用为前置用例：${res.data.msg || '服务器异常-检查是否存在前置依赖用例'}`);
        }

    })
}
// 复制弹窗
const dialog_copy = (index) =>{
    newCaseName.value = ""
    console.log("拿到的index是", index)
    // 通过下标获取用例id
    let id = tableData.value[index]["id"]
    console.log("拿到的webinfoid是",id)
    dialogVisible_id.value = id
    // 唤起弹窗
    dialogVisible.value = true
}
// 弹窗开关状态
const dialogVisible = ref(false)
// 弹窗拿到的临时id
const dialogVisible_id = ref("")
// 新名称
const newCaseName = ref("")
// 弹窗确定事件
const copy_onsubmit = () =>{
        // 准备要传出的name与id
    let id = dialogVisible_id.value
    let newname = newCaseName.value
    if (newCaseName.value===""){
        ElMessage.error("名称不能为空")
        console.log("为空无法保存")
        return
    }
    let data = {}
    data["caseid"] = id
    data["newcasename"] = newname
    console.log("传出值")
    console.log(data)
    copyCase(data).then((res)=>{
        if(res.data.code===200){
            ElMessage.success("已复制")
            loadDate()
            dialogVisible.value = false
        }else{
            console.log("出错")
            ElMessage.error("复制出错，请联系管理员")
        }
    }).catch((error)=>{
            console.error("网络错误:", error);
            ElMessage.error(`网络错误: ${error.message}`);
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
// 根据负责人ID获取名称
const getPrincipalName = (principalId) => {
  // 若ID为空，直接返回默认值
  if (!principalId) return '-';
  // 在update_by_list中查找匹配的条目
  const matchItem = update_by_list.value?.find(item => item.create_by === principalId);
  // 找到则返回名称，未找到返回原ID
  return matchItem ? matchItem.create_name : principalId;
};
</script>