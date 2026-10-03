<template>
  <div class="users-page">
    <section class="content-panel page-head">
      <div>
        <div class="section-title">用户管理</div>
        <div class="section-subtitle">可搜索、可编辑的用户列表。</div>
      </div>
      <div class="head-actions">
        <el-input v-model="searchText" placeholder="搜索用户名" clearable class="search-box" />
        <el-button type="primary" @click="openCreate">新增用户</el-button>
      </div>
    </section>

    <section class="metric-grid">
      <div class="metric-card">
        <span class="metric-label">用户总数</span>
        <strong>{{ filteredData.length }}</strong>
        <div class="soft-text">当前可见记录</div>
      </div>
      <div class="metric-card">
        <span class="metric-label">最近新增</span>
        <strong>{{ recentUsers }}</strong>
        <div class="soft-text">最新的7条记录</div>
      </div>
      <div class="metric-card">
        <span class="metric-label">可操作</span>
        <strong>{{ filteredData.length }}</strong>
        <div class="soft-text">编辑和删除已启用</div>
      </div>
    </section>

    <section class="content-panel table-panel">
      <el-table :data="pagedData" v-loading="loading">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="username" label="用户名" min-width="220" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : scope.row.role === 'pending' ? 'warning' : 'success'">
              {{ scope.row.role || 'user' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" min-width="180" />
        <el-table-column label="状态" width="120">
          <template #default>
            <el-tag type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button>
            <el-popconfirm v-if="isAdmin" title="确认删除该用户？" @confirm="handleDelete(scope.row.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        background
        layout="prev, pager, next"
        :page-size="pagination.limit"
        :current-page="pagination.currentPage"
        :total="filteredData.length"
        @current-change="handlePageChange"
      />
    </section>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增用户' : '编辑用户'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="conPassword">
          <el-input v-model="form.conPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option label="待审批" value="pending" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useCookies } from "@vueuse/integrations/useCookies";
import { addUser, delUser, editUser, getUserBypage } from "~/views/users/user.js";

const cookie = useCookies();
const isAdmin = computed(() => cookie.get("l-role") === "admin");

const loading = ref(false);
const dialogVisible = ref(false);
const dialogMode = ref("create");
const editingId = ref(null);
const searchText = ref("");
const tableData = ref([]);
const formRef = ref(null);

const form = reactive({
  username: "",
  password: "",
  conPassword: "",
  role: "user",
});

const pagination = reactive({
  limit: 10,
  currentPage: 1,
});

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
  conPassword: [
    {
      validator: (_, value, callback) => {
        if (value !== form.password) {
          callback(new Error("两次密码不一致"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
};

const filteredData = computed(() => {
  const keyword = searchText.value.trim().toLowerCase();
  if (!keyword) {
    return tableData.value;
  }
  return tableData.value.filter((item) => (item.username || "").toLowerCase().includes(keyword));
});

const pagedData = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.limit;
  return filteredData.value.slice(start, start + pagination.limit);
});

const recentUsers = computed(() => tableData.value.slice(0, 7).length);

function resetForm() {
  form.username = "";
  form.password = "";
  form.conPassword = "";
  form.role = "user";
  editingId.value = null;
}

function loadData() {
  loading.value = true;
  getUserBypage(1)
    .then((res) => {
      tableData.value = res.data.data || [];
    })
    .finally(() => {
      loading.value = false;
    });
}

function handlePageChange(page) {
  pagination.currentPage = page;
}

function openCreate() {
  dialogMode.value = "create";
  resetForm();
  dialogVisible.value = true;
}

function openEdit(row) {
  dialogMode.value = "edit";
  editingId.value = row.id;
  form.username = row.username || "";
  form.password = row.password || "";
  form.conPassword = row.password || "";
  form.role = row.role || "user";
  dialogVisible.value = true;
}

function submitForm() {
  formRef.value.validate((valid) => {
    if (!valid) {
      return;
    }

    const request = dialogMode.value === "create"
      ? addUser(form.username, form.password, form.role)
      : editUser(editingId.value, form.username, form.password, form.role);

    request.then((res) => {
      if (res.data.code === 200) {
        ElMessage.success(dialogMode.value === "create" ? "用户创建成功" : "用户更新成功");
        dialogVisible.value = false;
        resetForm();
        loadData();
        return;
      }
      ElMessage.error(res.data.msg || "操作失败");
    });
  });
}

function handleDelete(id) {
  delUser(id).then((res) => {
    if (res.data.code === 200) {
      ElMessage.success("用户已删除");
      loadData();
      return;
    }
    ElMessage.error(res.data.msg || "删除失败");
  });
}

loadData();
</script>

<style scoped>
.users-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
}

.head-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.search-box {
  width: 260px;
}

.table-panel {
  padding: 20px;
}

@media (max-width: 900px) {
  .page-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-box {
    width: 100%;
  }
}
</style>
