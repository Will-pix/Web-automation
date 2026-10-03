<template>
  <!-- 模块1 ： 头部的按钮和标题 -->
    <div class="form-wrapper">
        <div class="form-info">| WEB测试计划</div>
        <el-form-item class="form-buttons">
            <el-button type="primary" @click="submitForm()">保存(不包含用例维护)</el-button>
            <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
    </div>
    <!-- 模块2：主题内容信息 -->
    <el-form ref="ruleFormRef" :model="webcollection" :rules="rules" :inline="true" class="demo-form-inline">
          <!-- 模块2-1 -- 基础信息维护 -->
        <el-form-item label="测试计划名称：" prop="collection_name">
            <el-input v-model="webcollection.collection_name"  style="width: 300px"/>
        </el-form-item>
        <el-form-item label="所属项目：" prop="project_id">
            <el-select v-model="webcollection.project_id" placeholder="选择所属项目" clearable filterable>
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
            </el-select>
        </el-form-item>
        <el-form-item label="测试计划描述：" prop="collection_desc" >
            <el-input v-model="webcollection.collection_desc"  style="width: 300px"/>
        </el-form-item>
        <el-form-item label="负责人">
            <el-select  v-model="webcollection.principal" placeholder="选择负责人" clearable style="width: 150px;">
                <el-option v-for="update in update_by_list" :label="update.create_name" :value="update.create_by"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="集合所属环境" prop="collection_env_type">
            <el-select v-model="webcollection.collection_env_type" placeholder="集合所属环境"  style="width: 150px;">
                <el-option 
                        v-for="item in envTypeOptions" 
                        :key="item.value" 
                        :label="item.label" 
                        :value="item.value"
                ></el-option>
            </el-select>
        </el-form-item>
          <!-- END 模块2-1 -- 基础信息维护 -->
        <!--模块2-2 -- 用例信息\运行配置信息\其它等等维护 -->
        <el-form-item label="" class="full-width-item">
            <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 1120px">
                <el-tab-pane label="用例维护" name="用例维护">
                    <!-- 抽离到其它文件 -->
                    <WebCollectionCase v-if="webcollectionLoaded" :webcollection="webcollection"></WebCollectionCase>
                </el-tab-pane>
                <el-tab-pane label="运行环境配置" name="运行环境配置">
                    <!-- 抽离到其它文件 -->
                    <WebCollectionEnv v-if="webcollectionLoaded" :webcollection="webcollection"></WebCollectionEnv>
                </el-tab-pane>
            </el-tabs>
        </el-form-item>
    </el-form>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { queryById, insertData, updateData } from "./WebCollectionInfo.js"; // 不同页面不同的接口
import WebCollectionEnv from './WebCollectionEnv.vue';
import { ElMessage } from "element-plus";
import WebCollectionCase from "./WebCollectionCase.vue";
import { eventBus } from './event-bus.js';
import { queryAllCreateBy } from "~/views/users/user.js"

// 接收的
const router = useRouter();
// 表单实例
const ruleFormRef = ref()
// 表单数据 - 不同的页面，不同的表单字段
const webcollection = reactive({
  id: '',
  project_id: '',
  browser_id: '',
  collection_name: "",
  collection_desc: "",
  collection_env: [],
  collection_params: [],
  principal: "",
  // 新增：集合环境类型，默认值为common（通用）
  collection_env_type: 'common'
});
// 表单验证规则 - 不同的页面，不同的校验规则
const rules = reactive({
  project_id: [{ required: true, message: "必填项", trigger: "blur" }],
  collection_name: [{ required: true, message: "必填项", trigger: "blur" }],
  collection_desc: [{ required: true, message: "必填项", trigger: "blur" }],
  browser_id: [{ required: true, message: '请选择浏览器', trigger: 'change' }],
    // 新增：集合环境类型必选验证
  collection_env_type: [{ required: true, message: '请选择集合环境类型', trigger: 'change' }]
  
});
// 项目列表
const projectList = ref([])
// 获取项目列表
import { queryAll } from "../project/WebProject.js"; // 不同页面不同的接口
const getProjectList = () =>{
    queryAll().then((res)=>{
        projectList.value = res.data.data;
    })
}
// 默认跳转的页
const tabActiveName = ref("用例维护"); // tab页
// 延迟加载子组件数据
const webcollectionLoaded = ref(false); // 数据加载状态

// 加载表单数据
const loadData = (id) => {
    queryById(id).then((res)=>{
        webcollection.id = res.data.data.id;
        webcollection.project_id = res.data.data.project_id;
        webcollection.browser_id = res.data.data.browser_id;
        webcollection.collection_name = res.data.data.collection_name;
        webcollection.collection_desc = res.data.data.collection_desc;
        webcollection.collection_env = JSON.parse(res.data.data.collection_env);
        webcollectionLoaded.value = true;
        webcollection.principal = res.data.data.principal; // 关键行，将后端返回的principal绑定到webInfo
        // 新增：回显集合环境类型（兼容编辑场景）
        webcollection.collection_env_type = res.data.data.collection_env_type || 'common';
    })
}
// 如果有id参数，说明是编辑，需要获取数据
onMounted(()=>{
    getProjectList();
    let query_id = router.currentRoute.value.query.id;
    console.log("query_id",query_id)
    if (Number(query_id) > 0) {
        loadData(query_id);
            }
            else{
                webcollectionLoaded.value=true
            }
})
// 取消订阅
// onUnmounted(() => {
//   eventBus.value.off('refreshList');
// });
// 保存
const submitForm = () =>{
    if(!ruleFormRef.value){
        ElMessage.error("表单未初始化，请刷新页面后重试")
        return
    }
    ruleFormRef.value.validate((valid, invalidFields)=>{
        if(!valid){
            const fieldNames = Object.keys(invalidFields || {}).map(k => {
                const map = { project_id: '所属项目', collection_name: '测试计划名称', collection_desc: '测试计划描述', browser_id: '浏览器运行选择', collection_env_type: '集合所属环境' }
                return map[k] || k
            }).join('、')
            ElMessage.warning(`请完善必填信息：${fieldNames}`)
            return
        }
        let collection_data = {
            id: webcollection.id,
            project_id: webcollection.project_id,
            browser_id: webcollection.browser_id,
            collection_name: webcollection.collection_name,
            collection_desc: webcollection.collection_desc,
            collection_env: JSON.stringify(webcollection.collection_env || []),
            principal:webcollection.principal ?? null ,
            collection_env_type: webcollection.collection_env_type
        }
        if(webcollection.id>0){
            updateData(collection_data).then((res)=>{
                if(res.data.code===200){
                    ElMessage.success("修改成功")
                    loadData(webcollection.id)
                }else{
                    ElMessage.error("修改失败")
                }
            })
        }else{
            insertData(collection_data).then((res)=>{
                if(res.data.code===200){
                    ElMessage.success("保存成功")
                    webcollection.id = res.data.data.id
                    loadData(webcollection.id)
                    console.log("zuihou", webcollection.id)
                }else{
                    ElMessage.error("保存失败")
                }
            })
        }
    })
}
// 关闭表单 - 回到数据列表页 - 不同的页面，不同的路径
const closeForm = () => {
  router.push("/WebCollectionInfoList");
};
// 负责人列表
const update_by_list = ref()
// 获取负责人列表
const get_update_by_list = () =>{
    queryAllCreateBy().then((res)=>{
        console.log("获取到的负责人列表为:", res.data)
        update_by_list.value = res.data.data
    })
}
get_update_by_list()

// 新增：集合环境类型选项列表
const envTypeOptions = ref([
  { label: '通用环境', value: 'common' },
  { label: '测试环境', value: 'test' },
  { label: '预发布环境', value: 'stage' },
  { label: '生产环境', value: 'online' }
])

</script>

<style scoped>


.el-divider__text{
  background-color: unset;
}

/* 控制保存和取消按钮右对齐 */
.form-wrapper {
  margin-bottom: 20px;
  /* 根据需要调整间隔大小 */
  border-bottom: 1px solid #ccc;
  /* 添加横线，颜色和粗细可以根据需要调整 */
  display: flex;
  align-items: center;
  /* 垂直居中 */
  justify-content: space-between;
  /* 水平分布，使得两端元素靠边 */
}

.demo-form-inline .el-select {
  --el-select-width: 145px;
  margin-right: 10px;
  /* 设置右边距 */
  margin-left: 5px;
  /* 设置右边距 */
}

/* ---分页相关的样式--- */

.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}

.el-collapse-item__header{
  background-color: beige;
}

.full-width-item {
  display: block !important; /* 强制独占一行 */
  clear: both; /* 清除行内浮动，和上面的基础信息分隔 */
  width: 100%; /* 占满宽度 */
  margin-top: 20px !important; /* 加个间距，视觉更清晰 */
}
</style>