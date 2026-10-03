<template>
  <!-- 搜索表单 --> 
  <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
    
    <el-form-item label="关键字名称：">
      <el-input  v-model="searchForm.name"  placeholder="根据关键字名称筛选"/>
    </el-form-item>

    <el-form-item label="操作类型ID：">
      <el-select v-model="searchForm.operation_type_id"  placeholder="选择所属类型" clearable style="width: 120px;">
        <!-- 需要对应的操作类型的下拉数据 -->
      <el-option v-for="operationType in operationTypeList" :key="operationType.id" :label="operationType.operation_type_name" :value="operationType.id"/>     
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

    <el-row class="mb-4" type="flex" justify="end">
      <el-button type="primary" @click="loadData()">查询</el-button>
      <el-button type="warning" @click="onDataForm(-1)" >新增关键字方法</el-button>
    </el-row>
  </el-form>
    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%" max-height="500">
    <!-- 数据列 -->
    <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop" :show-overflow-tooltip="true">
    <!-- 自定义某个列的数据 -->
      <template #default="scope">
        <span v-if="col.prop === 'is_enabled'">
          {{
              scope.row.is_enabled === "false" ? "否" : scope.row.is_enabled === "true" ? "是" : "-"
          }}
        </span>
      </template>

    </el-table-column>
  <!-- END 数据表格  -->

    <!-- 操作 -->
    <el-table-column fixed="right" label="操作">
      <template #default="scope">
        <el-button link type="primary" size="small"  @click.prevent="onDataForm(scope.$index)">
          编辑
        </el-button>
          
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
</template>

<script setup>
import { ref, reactive } from "vue";
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
// 搜索功能 - 筛选表单
const searchForm = reactive({
    "name": "", 
    "operation_type_id": "" 
});
// 加载元素操作类型
import { queryAll } from "./WebOperationType.js"; // 不同页面不同的接口
import { useRouter } from "vue-router";
import { queryByPage, deleteData } from "./WebKeyWord.js"; // 不同页面不同的接口
import { queryAllCreateBy } from "~/views/users/user.js"


const router = useRouter();
// 操作的获取
const operationTypeList = ref([{
  id: 0,
  operation_type_name: '',
  create_time: ''
}]);
const getOperationTypeList = () =>{
    queryAll().then((res) => {
    operationTypeList.value = res.data.data;
  });
}
getOperationTypeList();
// 表格
// 表头
const columnList = ref([
  { prop: "id", label: "关键字编号" },
  { prop: "name", label: "关键字名称" },
  { prop: "keyword_fun_name", label: "关键字函数名" },
  { prop: "is_enabled", label: "是否启动" },
  { prop: "update_time", label: '更新时间' },
  { prop: "update_name", label: '更新人' },
  { prop: "create_time", label: '创建时间' },
  { prop: "create_name", label: '创建人' }
]);
// 表格数据
const tableData = ref([]);
// 查询数据
const loadData = () =>{
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
loadData()
// 打开表单 （编辑/新增）
const onDataForm = (index) => {
  let params_data = {};
  if (index >= 0) {
    params_data = {
      id: tableData.value[index]["id"],
    };
  }
  router.push({
    path: "/WebKeyWordForm", // 不同页面不同的表单路径
    query: params_data,
  });
};
// 删除
const ondel = (index) => {
  deleteData(tableData.value[index]["id"]).then((res) => {
    loadData();
  });
};
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