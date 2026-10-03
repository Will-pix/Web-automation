<template>
  <!-- 筛选（完全保留你的原始逻辑） -->
  <el-form :model="searchForm" :inline="true">
    <el-form-item label="文件名称">
      <el-input v-model="searchForm.file_name" placeholder="根据文件名称筛选"></el-input>
    </el-form-item>
    <el-row type="flex" justify="end" class="mb-4">
      <el-button type="primary" @click="loadDate()">查询</el-button>
      <!-- 点击按钮打开上传弹窗 -->
      <el-button type="warning" @click="uploadDialogVisible = true">上传文件</el-button>
    </el-row>
  </el-form>

  <!-- 表格展示区（完全保留你的原始逻辑） -->
  <el-table :data="tableData">
    <el-table-column v-for="col in columnList" :label="col.label" :prop="col.prop" :key="col.prop"></el-table-column>
    <el-table-column label="操作" fixed="right">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="ondataform(scope.$index)">生成正则表达式</el-button>
                <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="ondel(scope.$index)">
                    <template #reference="scope">
                        <el-button link type="primary" size="small">删除</el-button>
                    </template>
                </el-popconfirm>
            </template>
    </el-table-column>
    
  </el-table>

  <!-- 分页（完全保留你的原始逻辑） -->
  <div class="mt-4">
    <el-pagination 
      background 
      layout="total,sizes,prev, pager, next, jumper" 
      :page-sizes="[10,20,30,50]"
      :total="pagination.total" 
      :page-size="pagination.limit" 
      :current-page="pagination.currentPage"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
  <!-- 弹窗 -->
   <el-dialog v-model="uploadDialogVisible">
        <!-- <el-form-item label="文件描述">
            <el-input v-model="filevalue.project_name" placeholder="描述"></el-input>
        </el-form-item> -->
        <el-upload
            class="upload-demo"
            drag
            :http-request="customUpload"
            multiple>
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <div class="el-upload__tip" slot="tip">不限制文件格式，但不超过100mb</div>
        </el-upload>
   </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { queryByPage, deleteData, upload as uploadFile ,get_regular_expression} from '~/views/webtest/webfile/WebFile.js'
import { ElMessage } from "element-plus";
// 修复：补充分页页码变更函数
const handleCurrentChange = (val) => {
  pagination.value.currentPage = val
  loadDate()
}
// 分页参数（完全保留你的原始逻辑）
const pagination = ref({
  total: 0,
  limit: 10,
  currentPage: 1
})

// 分页事件（完全保留你的原始逻辑）
const handleSizeChange = (val) => {
  pagination.value.limit = val
  loadDate()
}
// 搜索表单（完全保留你的原始逻辑）
const searchForm = reactive({
  file_name: ''
})

// 表格数据（完全保留你的原始逻辑）
const tableData = ref([])
const columnList = ref([
//   { prop: "id", label: '文件编号' },
  { prop: "file_name", label: '文件名称' },
//   { prop: "file_desc", label: '文件描述' },
//   { prop: "update_time", label: '更新时间' },
//   { prop: "update_name", label: '更新人' },
//   { prop: "create_time", label: '创建时间' },
//   { prop: "create_name", label: '创建人' }
])

// 加载表格数据（完全保留你的原始逻辑）
const loadDate = () => {
  const searchdata = { ...searchForm }  // 复制对象避免污染原数据
  searchdata.page = pagination.value.currentPage
  searchdata.pageSize = pagination.value.limit
  queryByPage(searchdata).then((res) => {
    tableData.value = res.data.data
    pagination.value.total = res.data.total
  }).catch(err => {
    ElMessage.error('加载数据失败')
    console.error(err)
  })
}
loadDate()

// 弹窗状态
const uploadDialogVisible = ref(false)

// 自定义上传函数
const customUpload = (params) =>{
  const formData = new FormData()
  formData.append('file', params.file)  // 单个文件
  uploadFile(formData).then((res)=>{
    if (res.data.code===200){
    params.onSuccess(res)  // 通知el-upload上传成功
    ElMessage.success('上传成功')
    loadDate()  // 刷新表格
    }else{
    ElMessage.error('上传失败')
    ElMessage.error(res.data.msg)
    }
  })
}
// 生成正则表达式
const ondataform = (index) => {
    let file_name = tableData.value[index]["file_name"]
    file_name = { "file_name": file_name },
    console.log("正则id",file_name)
    get_regular_expression(file_name).then((res)=>{
        console.log(res.data)
        console.log("正则id",res.data.data.regex_pattern)
        ElMessage.success("生成成功↓，复制使用")
        ElMessage.success(res.data.data.regex_pattern)
    })

}
// 删除
const ondel = (index) =>{
    let id = tableData.value[index]["id"]
    deleteData(id).then((res)=>{
        if (res.data.code === 200){
        ElMessage.success("删除成功"+res.data.msg)
        loadDate()
        }else{
        ElMessage.error("删除失败")
        }
    })
}
</script>