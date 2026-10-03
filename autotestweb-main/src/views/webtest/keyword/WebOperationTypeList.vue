<template>
  <!-- 搜索表单 -->
  <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
    <el-form-item label="操作类型名称：">
      <el-input v-model="searchForm.operation_type_name" placeholder="根据名称筛选" clearable />
    </el-form-item>
    <el-row class="mb-4" type="flex" justify="end">
      <el-button type="primary" @click="loadData()">查询</el-button>
      <el-button type="warning" @click="openAddDialog">新增操作类型</el-button>
    </el-row>
  </el-form>

  <!-- 数据表格 -->
  <el-table :data="tableData" style="width: 100%" max-height="500">
    <el-table-column prop="id" label="编号" width="80" />
    <el-table-column prop="operation_type_name" label="操作类型名称" :show-overflow-tooltip="true" />
    <el-table-column prop="ex_fun_name" label="类型方法名" :show-overflow-tooltip="true" />
    <el-table-column prop="create_time" label="创建时间" width="180" />
    <el-table-column fixed="right" label="操作" width="160">
      <template #default="scope">
        <el-button link type="primary" size="small" @click="openEditDialog(scope.row)">编辑</el-button>
        <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="onDelete(scope.row.id)">
          <template #reference>
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
      @current-change="handleCurrentChange" />
  </div>

  <!-- 新增/编辑弹窗 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @close="resetForm">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="操作类型名称" prop="operation_type_name">
        <el-input v-model="form.operation_type_name" placeholder="例如：浏览器操作、元素操作" />
      </el-form-item>
      <el-form-item label="类型方法名" prop="ex_fun_name">
        <el-input v-model="form.ex_fun_name" placeholder="英文方法名（可选）" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitForm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import { ElMessage } from "element-plus";
import { queryByPage, insertData, updateData, deleteData } from "./WebOperationType.js";

const pagination = ref({
  total: 0,
  limit: 10,
  currentPage: 1
});

const handleSizeChange = (val) => {
  pagination.value.limit = val;
  loadData();
};
const handleCurrentChange = (val) => {
  pagination.value.currentPage = val;
  loadData();
};

const searchForm = reactive({
  operation_type_name: ""
});

const tableData = ref([]);

const loadData = () => {
  let data = {
    ...searchForm,
    page: pagination.value.currentPage,
    pageSize: pagination.value.limit
  };
  queryByPage(data).then((res) => {
    if (res.data.code === 200) {
      tableData.value = res.data.data;
      pagination.value.total = res.data.total;
    }
  });
};
loadData();

// 弹窗相关
const dialogVisible = ref(false);
const dialogTitle = ref("新增操作类型");
const formRef = ref(null);
const form = reactive({
  id: 0,
  operation_type_name: "",
  ex_fun_name: ""
});

const rules = {
  operation_type_name: [{ required: true, message: "必填项", trigger: "blur" }]
};

const openAddDialog = () => {
  form.id = 0;
  form.operation_type_name = "";
  form.ex_fun_name = "";
  dialogTitle.value = "新增操作类型";
  dialogVisible.value = true;
};

const openEditDialog = (row) => {
  form.id = row.id;
  form.operation_type_name = row.operation_type_name || "";
  form.ex_fun_name = row.ex_fun_name || "";
  dialogTitle.value = "编辑操作类型";
  dialogVisible.value = true;
};

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields();
};

const submitForm = () => {
  if (!formRef.value) return;
  formRef.value.validate((valid) => {
    if (!valid) return;
    if (form.id > 0) {
      updateData({ id: form.id, operation_type_name: form.operation_type_name, ex_fun_name: form.ex_fun_name }).then((res) => {
        if (res.data.code === 200) {
          ElMessage.success("修改成功");
          dialogVisible.value = false;
          loadData();
        } else {
          ElMessage.error(res.data.msg || "修改失败");
        }
      });
    } else {
      insertData({ operation_type_name: form.operation_type_name, ex_fun_name: form.ex_fun_name }).then((res) => {
        if (res.data.code === 200) {
          ElMessage.success("新增成功");
          dialogVisible.value = false;
          loadData();
        } else {
          ElMessage.error(res.data.msg || "新增失败");
        }
      });
    }
  });
};

const onDelete = (id) => {
  deleteData(id).then((res) => {
    if (res.data.code === 200) {
      ElMessage.success("删除成功");
      loadData();
    } else {
      ElMessage.error(res.data.msg || "删除失败");
    }
  });
};
</script>
