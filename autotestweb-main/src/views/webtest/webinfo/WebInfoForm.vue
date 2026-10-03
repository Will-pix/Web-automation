<template>
      <el-form ref="ruleFormRef" :inline="true" :model="webInfo" :rules="rules" class="demo-form-inline">
        <div class="form-wrapper">
            <div class="form-info">| 基础信息</div>
            <el-form-item class="form-buttons">
                <el-button type="primary" @click="onSubmit()">保存(不包含用例步骤)</el-button>
                <el-button type="warning" @click="saveinfo">调试执行测试</el-button>
                <el-button type="info" @click="onCancel">关闭</el-button>
            </el-form-item>
        </div>
        <el-form-item label="用例编号：">
            <el-input v-model="webInfo.id" placeholder="用例编号" clearable disabled />
        </el-form-item>
        <el-form-item label="用例名称："prop="case_name">
            <el-input v-model="webInfo.case_name" placeholder="输入用例名称" clearable />
        </el-form-item>
        <el-form-item label="所属项目ID：" prop="project_id">
            <el-select v-model="webInfo.project_id" placeholder="选择所属项目" filterable clearable>
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
            </el-select>
        </el-form-item>
        <el-form-item label="前置用例：" prop="is_pre">
            <el-select v-model="webInfo.is_pre" placeholder="是否前置用例" clearable>
                <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
        </el-form-item>
        <el-form-item label="负责人">
            <el-select  v-model="webInfo.principal" placeholder="选择负责人" clearable style="width: 150px;">
                <el-option v-for="update in update_by_list" :label="update.create_name" :value="update.create_by"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="用例描述：">
            <el-input v-model="webInfo.case_desc" style="width: 600px" :rows="3" type="textarea" placeholder="请输入用例描述" />
        </el-form-item>
        <div class="form-wrapper">
            <div class="form-info">| 用例信息</div>
        </div>
        <el-form-item style="width: 1300px;">
            <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 100%">
                <!-- 功能1：测试用例步骤 -->
                <el-tab-pane label="当前用例步骤" name="当前用例步骤">
                    <!-- 功能1-1 显示已经添加的所有步骤-->
                    <el-table :data="tableDataCaseStep" row-key="id" class="table_data" max-height="500" :expand-row-keys="expandedRowIds" :row-class-name="getRowClassName">
                        <el-table-column fixed="right" label="操作" width="80">
                            <template #default="scope">
                                <el-button link type="primary" size="small" @click="updateWebCaseStep(scope.row)">确认修改</el-button><br />
                                <el-button link type="primary" size="small" @click="onDelete(scope.row.id)">删除</el-button>
                            </template>
                        </el-table-column>
                        <el-table-column prop="run_order" label="执行顺序" width="120">
                            <template #default="scope">
                             <!-- <el-input style="width: 50px" v-model="scope.row.run_order" placeholder="顺序-数字类型"></el-input> -->
                                <el-input-number v-model="scope.row.run_order" :min="1" style="width: 110px" placeholder="顺序"/>
                            </template>
                        </el-table-column>
                        <el-table-column prop="step_desc" label="步骤描述" width="310">
                            <template #default="scope">
                                <el-input style="max-width: 280px; width: 280px" v-model="scope.row.step_desc"
                                placeholder="输入步骤描述"></el-input>
                            </template>
                        </el-table-column>
                        <el-table-column prop="key_word_id" label="关键字操作" width="320">
                            <template #default="scope">
                                <el-cascader v-model="scope.row.key_word_id" :options="keyWordAllList" @change="onStepKeyModifyChange(scope.$index)"style="width: 250px;" />
                            </template>
                        </el-table-column>
                        <el-table-column prop="ref_variable" label="关键字参数" type="expand" width="120" style="background-color: antiquewhite;">
                            <template #default="scope">
                                <!-- 循环遍历出所有的参数数据 -->
                                <span style="margin-left: 10px;" v-for="(key,value) in scope.row.ref_variable" >
                                    <span style="margin-right: 10px;">{{value}}</span >
                                    <!-- 普通参数就是一个输入框 -->
                                    <el-input style="width: 240px; margin: left 20px ;" v-model="scope.row.ref_variable[value]"
                                        :placeholder="value"
                                        :type="value === 'ai_step' ? 'textarea' : ''"
                                        :style="value === 'ai_step' ? 'width: 600px' : ''"
                                        :rows="value === 'ai_step' ? 3 : ''"
                                        ></el-input>
                                </span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="is_enabled" label="是否执行" width="80">
                            <template #default="scope">
                                    <!-- 绑定当前行数据的 is_enabled 字段 -->
                                  <el-switch v-model="scope.row.is_enabled" class="ml-2" style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" @change="handleSwitchChange(scope.row)"/>
                            </template>                        
                        </el-table-column>
                    </el-table>
                    <!-- 功能1-2 添加对应的测试用例步骤-->
                    <div class="input-group">
                        <el-input-number v-model="tmp_webCaseStep.run_order" placeholder="顺序-数字类型" :min="1"/>
                        <el-input v-model="tmp_webCaseStep.step_desc" placeholder="输入步骤描述"/>
                        <!-- 1. 以级联的方式去进行数据的显示 -->
                        <el-cascader  v-model="cascaderValue" :options="keyWordAllList" @change="onStepAddKeyHandleChange"/> 
                        <!-- 1-1 根据关键字参数生成对应的输入框 -->
                        <span v-if="tmp_webCaseStep.keyword != undefined && keydesclist.length > 0"  v-for="variable in keydesclist">
                        <!-- 1-2 普通参数就是一个输入框 -->
                        <el-input  v-model="tmp_webCaseStep.ref_variable[variable.name]" :placeholder="variable.placeholder" 
                            :type="variable.name === 'ai_step' ? 'textarea' : ''"
                            :style="variable.name === 'ai_step' ? 'width: 600px' : ''"
                            :rows="variable.name === 'ai_step' ? 3 : ''"
                            />
                        </span>
                        <!-- 2. 根据关键字参数生成对应的输入框 -->
                        <el-button style="width: 10%" @click="addWebCaseStep">添加</el-button>
                    </div>
                </el-tab-pane>
                <!-- 功能2：变量定义 -->
                <el-tab-pane label="变量定义" name="变量定义">
                    <!-- 2-1 变量描述的数据显示部分 -->
                    <el-table  :data="webInfo.param_data"   class="table_data"   max-height="250" >
                        <el-table-column prop="key" label="变量名" style="width: 40%" />
                        <el-table-column prop="value" label="变量值" style="width: 40%" />
                        <el-table-column fixed="right" label="删除" style="width: 15%">
                            <template #default="scope">
                                <el-button link  type="primary"   size="small"  @click.prevent="deleteVars(scope.$index)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                    <!-- 2-2 添加变量描述位置 -->
                    <div class="input-group">
                        <el-input v-model="vars.key" placeholder="变量名" style="width: 30%"  />
                        <el-input v-model="vars.value" placeholder="变量描述" style="width: 30%"  />
                        <el-button style="width: 20%" @click="onAddVars">添加</el-button>
                    </div>
                </el-tab-pane>
                <!-- 功能3：前置脚本 -->
                <el-tab-pane label="执行前事件(pre)" name="执行前事件(pre)">
                    <el-input v-model="webInfo.pre_request" type="textarea" :rows="15" placeholder="执行前事件" />
                </el-tab-pane>
                <!-- 功能4：后置脚本 -->
                <el-tab-pane label="执行后事件(post)" name="执行后事件(post)">
                    <el-input v-model="webInfo.post_request" type="textarea" :rows="15" placeholder="执行后事件" />
                </el-tab-pane>
               <!-- 功能5: 添加前置用例复用 -->
               <el-tab-pane label="前置用例复用" name="前置用例复用">
                    <el-table :data = "tableDataCaseInfoPre">
                            <el-table-column fixed="right" label="操作" width="80">
                                <template #default="scope">
                                    <el-button link type="primary" size="small" @click="updateWebCaseStepPre(scope.row)">确认修改</el-button><br />
                                    <el-popconfirm title="请检查变量定义并自行手动删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="onDeletePre(scope.row)">
                                        <template #reference>
                                            <el-button link type="primary" size="small">删除</el-button>
                                        </template>
                                    </el-popconfirm>
                                </template>
                            </el-table-column>
                            <el-table-column prop="run_order" label="执行顺序" width="130" >
                                    <template #default="scope">
                                    <el-input-number style="width: 100px" v-model="scope.row.run_order" placeholder="顺序-数字类型" :min="1"></el-input-number>
                                    </template>
                            </el-table-column>
                            <el-table-column prop="pre_info_id" label="用例id" :show-overflow-tooltip="true"  width="130"/>
                            <el-table-column prop="pre_case_name" label="用例名称" :show-overflow-tooltip="true"  width="330"/>
                            <el-table-column prop="pre_param_data" label="变量依赖(已同步到此用例变量定义中，注意更改，相同则覆盖)" :show-overflow-tooltip="true" />
                            
                    </el-table>
                    <el-button type="primary" @click="preCaseDialogVisible = true">+添加前置用例</el-button>
                    <!-- 子组件弹窗 -->
                    <WebInfoFormPreCase 
                        :visible="preCaseDialogVisible" 
                        :webinfo_id="webInfo.id"   
                        @close="preCaseDialogVisible = false; get_queryByPagePre(); loadData(webInfo.id)"
                        @refresh="get_queryByPagePre(); loadData(webInfo.id)"
                    />
               </el-tab-pane>
                <!-- 功能6: 提示 -->
               <!-- <el-tab-pane label="AI融合步骤教程及最近更新内容" name="AI融合步骤教程及最近更新内容">
                    <el-card>
                        <template #header>首先需要将关键字选择为AI视觉融合步骤</template>
                            <img src="https://fp.yangcong345.com/middle/1.0.0/Snipaste_2025-07-17_17-45-32.jpeg" style="width: 50%; height: 5%;"/>
                            <div style="margin-top: 10px;">然后描述你的动作,如：↓</div>
                            <div style="margin-top: 10px;">悬浮在习题管理显示后点击习题查找,查询习题id为：000008d3-af79-4ca7-9099-5ee9192d24bf的习题，在题干处搜索有理数引入，稍作等待后向上滑动一些，再向右滑动一页，将小狗拖拽到dog输入框中</div>
                            <div style="margin-top: 10px;">此时ai会进行分解多个步骤，如：点击，输入，悬浮，拖拽，滑动，等待</div>
                            <div style="margin-top: 10px;">这些都将在一个步骤中完成，所以尽可能优化好你的描述</div>
                    </el-card>
               </el-tab-pane> -->
               <el-tab-pane label="AI视觉融合步骤使用指南" name="AI视觉融合步骤使用指南">
                    <el-card style="border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin-top: 10px;">
                        <!-- 标题区域 -->
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #f0f0f0;">
                            <h3 style="margin: 0; font-size: 18px; color: #333; font-weight: 600;">AI视觉融合步骤使用指南</h3>
                            <div style="font-size: 12px; color: #999;">最近更新：2025-11-27</div>
                        </div>

                        <!-- 步骤1：选择关键字 -->
                        <div style="margin-bottom: 30px; display: flex; align-items: flex-start;">
                            <div style="width: 24px; height: 24px; background-color: #409eff; color: white; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 14px; margin-right: 15px; flex-shrink: 0;">1</div>
                            <div>
                                <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">选择关键字</h4>
                                <p style="margin: 0 0 15px 0; color: #666; font-size: 14px; line-height: 1.6;">首先需要将关键字选择为 <strong>AI视觉融合步骤</strong></p>
                                <div style="margin: 10px 0;">
                                <img src="https://fp.yangcong345.com/middle/1.0.0/Snipaste_2025-07-17_17-45-32.jpeg" alt="选择AI视觉融合步骤关键字" 
                            style="width: 100%; max-width: 600px; border-radius: 4px; border: 1px solid #eee; padding: 5px; box-sizing: border-box;">
                            </div>
                            </div>
                        </div>

                    <!-- 步骤2：描述动作 -->
                    <div style="margin-bottom: 30px; display: flex; align-items: flex-start;">
                        <div style="width: 24px; height: 24px; background-color: #409eff; color: white; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 14px; margin-right: 15px; flex-shrink: 0;">2</div>
                        <div>
                            <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">描述动作</h4>
                            <p style="margin: 0 0 15px 0; color: #666; font-size: 14px; line-height: 1.6;">在输入框中清晰描述需要执行的操作，例如：</p>
                            <div style="background-color: #f5f7fa; border-left: 3px solid #409eff; padding: 12px 15px; border-radius: 0 4px 4px 0; font-size: 13px; color: #555; margin-bottom: 15px; line-height: 1.8; word-break: break-all;">
                            悬浮在习题管理显示后点击习题查找，查询习题id为：000008d3-af79-4ca7-9099-5ee9192d24bf的习题，在题干处搜索有理数引入，稍作等待后向上滑动一些，再向右滑动一页，将小狗拖拽到dog输入框中，如果当前页面有更新弹窗则点击弹窗关闭，等待5s后断言输入框内容是否为加法运算
                            </div>
                        </div>
                    </div>

                    <!-- 步骤3：AI处理结果 -->
                    <div style="margin-bottom: 30px; display: flex; align-items: flex-start;">
                        <div style="width: 24px; height: 24px; background-color: #409eff; color: white; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 14px; margin-right: 15px; flex-shrink: 0;">3</div>
                        <div>
                            <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">AI自动分解步骤</h4>
                            <p style="margin: 0 0 15px 0; color: #666; font-size: 14px; line-height: 1.6;">系统会自动将你的描述分解为多个操作步骤，包括：</p>
                            <div style="margin: 10px 0 15px 0; display: flex; flex-wrap: wrap; gap: 8px;">
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">点击</span>
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">输入</span>
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">悬浮</span>
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">拖拽</span>
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">滑动</span>
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">等待</span>
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">判断</span>
                            <span style="background-color: #ecf5ff; color: #409eff; padding: 4px 10px; border-radius: 12px; font-size: 12px;">断言</span>
                            </div>
                            <p style="color: #f56c6c; font-size: 13px; padding-left: 20px; background: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2214%22 height=%2214%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%23f56c6c%22 stroke-width=%222%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3E%3Ccircle cx=%2212%22 cy=%2212%22 r=%2210%22%3E%3C/circle%3E%3Cline x1=%2212%22 y1=%228%22 x2=%2212%22 y2=%2212%22%3E%3C/line%3E%3Cline x1=%2212%22 y1=%2216%22 x2=%2212.01%22 y2=%2216%22%3E%3C/line%3E%3C/svg%3E') no-repeat left center; margin: 0;">
                            提示：所有操作都基于视觉，也就是步骤执行时显示的页面，所以尽可能用眼睛看到的内容来进行描述操作，有助于提高AI分解的准确性
                            </p>
                            <p style="color: #f56c6c; font-size: 13px; padding-left: 20px; background: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2214%22 height=%2214%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%23f56c6c%22 stroke-width=%222%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3E%3Ccircle cx=%2212%22 cy=%2212%22 r=%2210%22%3E%3C/circle%3E%3Cline x1=%2212%22 y1=%228%22 x2=%2212%22 y2=%2212%22%3E%3C/line%3E%3Cline x1=%2212%22 y1=%2216%22 x2=%2212.01%22 y2=%2216%22%3E%3C/line%3E%3C/svg%3E') no-repeat left center; margin: 0;">
                            提示：（逗号不是步骤分隔，主要看语义）如【稍作等待后向上滑动一些】会执行为：等待3s后向上滑动屏幕一半的距离
                            </p>
                            <p style="color: #f56c6c; font-size: 13px; padding-left: 20px; background: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2214%22 height=%2214%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%23f56c6c%22 stroke-width=%222%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3E%3Ccircle cx=%2212%22 cy=%2212%22 r=%2210%22%3E%3C/circle%3E%3Cline x1=%2212%22 y1=%228%22 x2=%2212%22 y2=%2212%22%3E%3C/line%3E%3Cline x1=%2212%22 y1=%2216%22 x2=%2212.01%22 y2=%2216%22%3E%3C/line%3E%3C/svg%3E') no-repeat left center; margin: 0;">
                            提示：如果你想要执行的步骤类型不存在于AI分解的类型中，那么就不要写入，因为还没有集成进去，可选择其它关键字执行，可填写文档提出需求
                            </p>
                            </div>
                        </div>
                    </el-card>
            </el-tab-pane>
            </el-tabs>
        </el-form-item>
    </el-form>
    <WebInfoFormDialog :visible="dialogVisible"  @close="dialogVisible = false" :project_id="webInfo.project_id" :webinfo_id="webInfo.id"/>
    <!-- 添加前置的弹窗 -->
     <WebInfoFormPreCase></WebInfoFormPreCase>
</template>
<script setup>
import {ref,reactive} from 'vue'
import { queryById, insertData, updateData } from "./WebInfo.js"; // 不同页面不同的接口
// import type { FormInstance, FormRules } from "element-plus";
import { queryByPage as queryAllSetp} from "./WebInfoStep.js"; // 不同页面不同的接口
import { queryAllCreateBy } from "~/views/users/user.js"

import {useRouter,useRoute} from "vue-router"
import { ElMessage } from "element-plus";
// 1. 变量- 添加用例步骤数据 - 临时数据存放
const tmp_webCaseStep = reactive({
  id: 0,
  run_order: 0,
  step_desc: "",
  operation_type: undefined,
  keyword: undefined,
  ref_variable: {}, // 保存关键对应的参数值
});
// 表单实例
const ruleFormRef = ref()
// 要接收的
const route = useRoute()
// 要获取的
const router = useRouter()
// ----------------------功能部分-------------------------------
// 功能：保存的数据
const onSubmit = () => {
    if (ruleFormRef.value){
        ruleFormRef.value.validate((valid)=>{
            if(valid){
             // 提交之前把数组修改为json字符串
            let data = {
                id: webInfo.id,
                project_id: webInfo.project_id,
                case_name: webInfo.case_name,
                case_desc: webInfo.case_desc,
                param_data: JSON.stringify(webInfo.param_data),
                pre_request: webInfo.pre_request, // 执行前事件
                post_request: webInfo.post_request, // 执行后事件
                is_pre: webInfo.is_pre,
                principal:webInfo.principal ?? null 
            };
        if (webInfo.id > 0) {
            updateData(data).then((res) => {
            if (res.data.code == 200) {
                // router.push("/WebInfoList"); // 跳转回列表页面 - 不同的页面，不同的路径
                // 重新加载当前的页面数据
                ElMessage.success("修改成功")
                loadData(data.id);
            }else{
                ElMessage.error(res.data.msg)
            }
            });
        }else {
            insertData(data).then((res) => {
            if (res.data.code == 200) {
                // router.push("/WebInfoList"); // 跳转回列表页面 - 不同的页面，不同的路径
                // 重新加载当前的页面数据
                ElMessage.success("新增成功")
                loadData(res.data.data.id);
            }else{
                ElMessage.error(res.data.msg)
            }
            });
        }
        }else{
            // 表单验证不通过的处理，如提示用户等
            ElMessage.error('表单存在必填项未填写');
        }
        })
    }
}
// 功能：关闭按钮方法
const onCancel = () => {
  router.push("/WebInfoList");
};
// 变量 - 用例的所有数据
const webInfo = reactive({
  id: 0,
  project_id: "",
  case_name: "",
  case_desc: "",
  param_data: [],
  pre_request: "", // 执行前事件
  post_request: "", // 执行后事件
  is_pre: "0", // 默认选择否
  principal: ""
})
// 加载对应的所有项目的数据
import { queryAll as queryAllProject } from "../project/WebProject.js"; // 不同页面不同的接口
const projectList = ref([
//   {
//     id: 0,
//     project_name: "",
//     project_desc: "",
//   },
]);
function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data;
  });
}
getProjectList();
// 变量- 是否下拉列表
const options = [
  {
    value: "1",
    label: "是",
  },
  {
    value: "0",
    label: "否",
  },
]
// 表单验证规则 - 不同的页面，不同的校验规则
const rules = reactive({
  project_id: [{ required: true, message: "必填项", trigger: "blur" }],
  case_name: [{ required: true, message: "必填项", trigger: "blur" }],
  is_pre: [{ required: true, message: "必填项", trigger: "blur" }]
})
// 设置后续的默认的选择的Tab
const tabActiveName = ref("当前用例步骤");
// 功能：加载对应的数据
// 表格数据
const tableDataCaseStep = ref([]);
// 初始化搜索 - 用例搜索
const searchForm = reactive({});
// 功能：加载表格数据-步骤
const loadData = (id) =>{
    queryById(id).then((res)=>{
        // 注意:此处将 后台的json字符串转变为对象
        webInfo.id = res.data.data.id;
        webInfo.project_id = res.data.data.project_id;
        webInfo.case_name = res.data.data.case_name;
        webInfo.case_desc = res.data.data.case_desc;
        webInfo.is_pre = res.data.data.is_pre;
        webInfo.param_data = JSON.parse(res.data.data.param_data);
        webInfo.pre_request = res.data.data.pre_request; // 执行前事件
        webInfo.post_request = res.data.data.post_request; // 执行后事件
        webInfo.principal = res.data.data.principal; // 关键行，将后端返回的principal绑定到webInfo
           // 6.0  加载测试步骤的数据
        let searchData = searchForm;
        searchData["page"] = 1;
        searchData["pageSize"] = 9999;
        searchData["web_info_id"] = webInfo.id;
        const total = ref(0);
        queryAllSetp(searchData).then(
            (res) => {
            tableDataCaseStep.value = res.data.data;
            // console.log("表格显示的数据为",tableDataCaseStep.value )
            // const keywordDesc = JSON.parse(res.data.data.keyword_desc || '[]'); // 处理空值

            // 把 ref_variable 数据由 json字符串转换为 js 对象
            tableDataCaseStep.value.forEach((step, index) => {
                // console.log('转换前 ref_variable:', step.ref_variable); // 输出字符串
                tableDataCaseStep.value[index]["ref_variable"] = JSON.parse(tableDataCaseStep.value[index]["ref_variable"])
                // console.log('转换后 ref_variable:', step.ref_variable); // 输出对象
                tmp_webCaseStep.run_order = getMaxRunOrder() + 5;
            });

            // total.value = res.data.total;
            }
        );
    })
}
// 获取当前路由的id-如果有则加载数据
let query_id = router.currentRoute.value.query.id;
webInfo.id = query_id ? Number(query_id) : 0;
if (webInfo.id > 0) {
  // 当ID大于0的时候，加载当前用例的信息
  loadData(webInfo.id);
  // 获取其它的信息
  getProjectList();
}
// ----------------------关键字 变量定义---------------------------
const vars = reactive({
key: "",
value: "",
});
// 变量定义保存
const onAddVars = () => {
// 保存起来
    webInfo.param_data.push({
        key: vars.key,
        value: vars.value,})
        // 置空
        vars.key = "";
        vars.value = "";
};
// 变量定义删除
const deleteVars = (index) => {
  // splice() 方法可以在任意位置修改数组,并返回被删除的元素 （下标,个数）
    webInfo.param_data.splice(index, 1);
};
// 1. 变量- 添加用例步骤数据 - 临时数据存放
// const tmp_webCaseStep = reactive({
//   id: 0,
//   run_order: 0,
//   step_desc: "",
//   operation_type: undefined,
//   keyword: undefined,
//   ref_variable: {}, // 保存关键对应的参数值
// });
// 级联下拉框的数据
const keyWordAllList = ref([])
import {queryAllKeyWordList as keyWordAllListall} from '../keyword/WebKeyWord.js'
// 查询数据
const getkeyWordAllList = () =>{
    keyWordAllListall().then((res)=>{
        if(res.data.code===200){
            keyWordAllList.value = res.data.data
        }
    })
}
getkeyWordAllList()
// 添加步骤的临时所选select
const cascaderValue = ref([])
// 级联选择后keyword的输入值存储列表
const keydesclist = ref([])
// 级联选择的id
import {queryById as keywordqueryall} from '../keyword/WebKeyWord.js'
const onStepAddKeyHandleChange = (value) =>{
    console.log("级联的leixing-id",value[0])
    console.log("级联的keyword-id",value[1])
    tmp_webCaseStep.keyword = value[1]
    // 需要根据keywordid查询keyword数据，是否有需要填写的值
    keywordqueryall(value[1]).then((res)=>{
        // 重置列表
        keydesclist.value = []
        // 提取keyword_desc，并遍历里面有多少个字典
        console.log(res.data.data.keyword_desc)
        const keywordDesc = JSON.parse(res.data.data.keyword_desc || '[]'); // 处理空值
        if(keywordDesc.length>0){
            console.log(keywordDesc.length)
            console.log("根据关键字的id获取全部数据为",keywordDesc)
            keydesclist.value = keywordDesc
            // 为新参数名 by_type 或旧参数名 定位方式 设置默认值
            keywordDesc.forEach(param=>{
                if(param.name === 'by_type' && !tmp_webCaseStep.ref_variable['by_type']){
                    tmp_webCaseStep.ref_variable['by_type'] = 'xpath';
                }
                if(param.name === '定位方式' && !tmp_webCaseStep.ref_variable['定位方式']){
                    tmp_webCaseStep.ref_variable['定位方式'] = 'xpath';
                }
            })
        }
    })
}
// ✅ 验证函数：检查所有参数是否有值
const validateParameters = (params) => {
    if (!params || typeof params !== 'object') {
        ElMessage.error("参数格式错误");
        return false;
    }
    
    for (const [key, value] of Object.entries(params)) {
        if (value === '' || value === null || value === undefined) {
            ElMessage.error(`"${key}" 不能为空`);
            return false;
        }
    }
    
    return true;
};
// 步骤添加
import {insertData as stepinsertData, updateData as stepupdateData, deleteData as stepdeleteData} from './WebInfoStep.js'
const addWebCaseStep = () =>{
    // 检查是否选择了关键字
    if (!tmp_webCaseStep.keyword) {
    ElMessage.error("请先选择关键字");
        return;
    }
    // 检查动态生成的参数是否填写
    const missingParams = keydesclist.value.filter(variable => {
        return !tmp_webCaseStep.ref_variable[variable.name]; // 空字符串、null、undefined 均视为未填写
    });
    if (missingParams.length > 0) {
        ElMessage.error(`请填写以下参数：${missingParams.map(p => p.name).join(', ')}`);
        return;
    }
    // 构建发送数据，只包含模型需要的字段
    const payload = {
    id: 0,
    run_order: tmp_webCaseStep.run_order,
    step_desc: tmp_webCaseStep.step_desc,
    key_word_id: tmp_webCaseStep.keyword, // 重命名 keyword 为 key_word_id
    ref_variable: JSON.stringify(tmp_webCaseStep.ref_variable), // 转为字符串
    web_info_id: webInfo.id
    }
    if(webInfo.id>0){
        stepinsertData(payload).then((res)=>{
            if(res.data.code===200){
            ElMessage.success("步骤新增成功")
            cascaderValue.value = [] 
            clearvalue()
            loadData(webInfo.id)
            }else{
                ElMessage.error("存在错误")
            }
        })
    }else{
        ElMessage.error("当前用例还未保存，请保存后再添加步骤")
    }

}
// 清空步骤的临时框内容
const clearvalue = () =>{
    tmp_webCaseStep.run_order = 0,
    tmp_webCaseStep.step_desc= "",
    tmp_webCaseStep.operation_type= undefined,
    tmp_webCaseStep.keyword= undefined,
    tmp_webCaseStep.ref_variable= {} // 保存关键对应的参数值
    keydesclist.value = []
}
const expandedRowIds = ref([]); // 初始为空，不展开任何行
// table的关键字修改事件
const onStepKeyModifyChange = (index) =>{
    console.log("需要改的是",tableDataCaseStep.value[index])
    console.log("级联的keyword-id",tableDataCaseStep.value[index].key_word_id[1])
    console.log("转换对象",tableDataCaseStep.value[index].ref_variable)
    // 更改就清空现有的
    tableDataCaseStep.value[index].ref_variable = {}
    console.log("清空后需要改的是",tableDataCaseStep.value[index])
    // 根据已选的key_word_id请求
    keywordqueryall(tableDataCaseStep.value[index].key_word_id[1]).then((res)=>{
        const keywordDesc = JSON.parse(res.data.data.keyword_desc || '[]'); // 处理空值
        if(keywordDesc.length>0){
            // 将参数描述数组转换为键值对对象
            const newRefVariable = {};
            keywordDesc.forEach(param => {
                // 使用参数名称作为键，初始值为空字符串
                newRefVariable[param.name] = '';
            });
            // 更换当前数据的ref_variable
         // 正确赋值键值对对象
            tableDataCaseStep.value[index].ref_variable = newRefVariable;
            console.log("赋值后",tableDataCaseStep.value[index].ref_variable)
              // 获取当前行的唯一标识（通常是 ID）
            const currentRowId = tableDataCaseStep.value[index].id;
            // 更新展开行列表（只展开当前行）
            if(Object.keys(tableDataCaseStep.value[index].ref_variable).length > 0){
                expandedRowIds.value = [currentRowId];
                console.log("执行了展开")
            }else{
                console.log("执行了关闭")

            }
        }else{
            console.log("执行了关闭")
            const currentRowId = tableDataCaseStep.value[index].id; // ✅ 重新定义
            expandedRowIds.value = expandedRowIds.value.filter(id => id !== currentRowId);
        }
    })
}

// 修改table的单条数据
const updateWebCaseStep = (stepData) =>{
    console.log("单条需要改的是",stepData)
  // 处理 key_word_id 为数组的情况
    let keywordId;
    if (Array.isArray(stepData.key_word_id) && stepData.key_word_id.length > 0) {
        keywordId = stepData.key_word_id[1] || stepData.key_word_id[0]; // 优先取第二个元素
    } else {
        keywordId = stepData.key_word_id; // 直接使用数字
    }
    // ✅ 验证所有参数是否有值
    console.log('类型:', typeof stepData.ref_variable);
    const isValid = validateParameters(stepData.ref_variable);
    if (!isValid) return; // 验证失败，终止提交
    let data = {
        id: stepData.id,
        key_word_id: keywordId,
        web_info_id:stepData.web_info_id,
        run_order:stepData.run_order,
        step_desc:stepData.step_desc,
        ref_variable:JSON.stringify(stepData.ref_variable), 
        // ref_variable: JSON.stringify(filteredRefVariable), // 使用过滤后的对象
    }
    console.log("单条需要改的是valueid.value",data)
    console.log("单条需要改的是data",data)
    stepupdateData(data).then((res)=>{
        if(res.data.code===200){
            ElMessage.success("修改成功")
            loadData(webInfo.id)
        }
    })
}
// 删除
const onDelete = (id) =>{
    stepdeleteData(id).then((res)=>{
        if(res.data.code===200){
            ElMessage.success("删除成功")
            loadData(webInfo.id)
        }
    })
}
// 调试执行测试
import WebInfoFormDialog from './WebInfoFormDialog.vue'
// 弹窗的开关控制
const saveinfo = () =>{
    if(webInfo.id===0){
        ElMessage.warning("请先保存当前用例")
    }else{
        dialogVisible.value = true;
    }
}
// 开关控制
const dialogVisible = ref(false);
// 实时计算添加序号值
const getMaxRunOrder = () => {
  if (!tableDataCaseStep.value || tableDataCaseStep.value.length === 0) {
    return 0; // 无步骤时返回0
  }
  return Math.max(...tableDataCaseStep.value.map(step => Number(step.run_order) || 0));
};
// 操作执行修改状态
const handleSwitchChange = (row) =>{
  const updateData = {
    id: row.id,                  // 步骤ID，用于定位修改哪条数据
    is_enabled: row.is_enabled   // 开关的最新状态（true/false）
  };
  stepupdateData(updateData).then((res)=>{
    if(res.data.code==200){
            ElMessage.success(`状态更新成功`);
            loadData(webInfo.id)    //修改成功更新数据
    }else{
        // 接口返回非成功状态时，提示错误并回滚开关状态
        ElMessage.error(`更新失败：${res.data.msg || '服务器异常'}`);
        row.is_enabled = !row.is_enabled; // 回滚，避免前端显示与后端不一致
    }
  }).catch((err)=>{
        // 网络错误或异常时，回滚开关状态
      ElMessage.error('网络错误，状态更新失败');
      row.is_enabled = !row.is_enabled; // 回滚状态
  })
}
// table根据是否执行状态展示颜色
const getRowClassName = ({ row }) => {
  // 仅当开关关闭时，返回深灰色样式类；开启时不返回任何类（即无特殊样式）
  return row.is_enabled ? '' : 'row-disabled';
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

// 前置用例复用部分
// 导包
import WebInfoFormPreCase from './WebInfoFormPreCase.vue'
// 触发前置用例的button-控制弹窗显示状态
const preCaseDialogVisible = ref(false)
// 表单值
const tableDataCaseInfoPre = ref()
import {queryByPagePre as queryByPagePre, updateData as updateDataPre, deleteData as deleteDataPre} from './WebInfoFormPre.js'
// 加载前置用例表单
const get_queryByPagePre = () => {
    let data = {
        webinfo_id:webInfo.id
    }
    queryByPagePre(data).then((res)=>{
        console.log("获取到的前置用例信息为:", res.data.data)
        tableDataCaseInfoPre.value = res.data.data
    })
}
get_queryByPagePre()
// 前置用例-确认修改
const updateWebCaseStepPre = (index) => {
    console.log(index)
    // 构造参数
    let data = {
        web_info_id:webInfo.id,
        pre_info_id:index.pre_info_id,
        pre_id:index.id,
        run_order:index.run_order
    }
    updateDataPre(data).then((res)=>{
        if(res.data.code==200){
            ElMessage.success(`状态更新成功`);
            loadData(webInfo.id)    //修改成功更新数据
            get_queryByPagePre()
        }else{
        // 接口返回非成功状态时
            ElMessage.error(`更新失败：${res.data.msg || '服务器异常'}`);
    }
    })
    // 携带参数请求
}
// 前置用例-删除
const onDeletePre = (row) => {
    let id = row.id
    console.log("删除的ID:", id)
    deleteDataPre(id).then((res)=>{
        if(res.data.code==200){
            ElMessage.success(`删除成功`);
            loadData(webInfo.id)    //修改成功更新数据
            get_queryByPagePre()
        }else{
        // 接口返回非成功状态时
            ElMessage.error(`删除失败：${res.data.msg || '服务器异常'}`);
    }
    })
}
</script>
<style>
/* 开关关闭时的深灰色样式 */
.el-table .row-disabled {
  --el-table-tr-bg-color: #e5e5e5; /* 深灰色背景（可根据需求调整色值） */
  /* 可选：加深文字对比 */
  --el-table-text-color: #333;
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

/* 控制添加的间隙 */
.input-group {
  margin-top: 15px;
  /* 根据需要调整间隔大小 */
}

/* ---------------------调整当前用例步骤的样式--------------------- */
.input-group .el-input {
  width: 180px;
  /* 根据需要调整间隔大小 */
  margin-left: 10px;
}

.input-group .el-button {
  width: 180px;
  /* 根据需要调整间隔大小 */
  margin-left: 10px;
}
/* ---------------------设置当前测试步骤背景颜色--------------------- */
.el-table__expanded-cell {
  background-color: beige;
}
</style>