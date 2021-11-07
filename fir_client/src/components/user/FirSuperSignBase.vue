<template>
  <el-main>

    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :visible.sync="importcertDeveloperVisible"
               style="text-align:center" title="发布证书导入" width="700px">
      <el-form label-width="30%">
        <el-form-item label="发布证书p12文件" style="width: 80%">
          <el-upload
              ref="upload"
              :auto-upload="false"
              :before-upload="beforeAvatarUpload"
              :file-list="fileList"
              :limit="1"
              accept=".p12"
              action="#"
              drag
          >
            <i class="el-icon-upload"/>
            <div class="el-upload__text">将p12证书文件拖到此处，或<em>点击上传</em></div>
          </el-upload>
        </el-form-item>
        <el-form-item label="发布证书p12密码" style="width: 80%">
          <el-input v-model="cert_pwd" label="证书密码"/>
        </el-form-item>
        <el-button @click="$refs.upload.submit()">确定导入</el-button>
        <el-button @click="importcertDeveloperVisible=false">取消</el-button>
      </el-form>
    </el-dialog>
    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :title="title"
               :visible.sync="dialogaddDeveloperVisible" style="text-align:center" width="750px">

      <el-form ref="storageinfoform" :model="editdeveloperinfo"
               label-width="80px" style="margin:0 auto;">

        <div v-if="editdeveloperinfo.auth_type===0">
          <el-form-item label="issuer_id" label-width="110px">
            <el-input v-model="editdeveloperinfo.issuer_id" :disabled='isedit'/>
          </el-form-item>

          <el-form-item label="private_key_id" label-width="110px">
            <el-input v-model="editdeveloperinfo.private_key_id"/>
          </el-form-item>

          <el-form-item label="p8key" label-width="110px">
            <el-input v-model="editdeveloperinfo.p8key"
                      :placeholder="placeholder" :rows="6" type="textarea"/>
          </el-form-item>
        </div>

        <el-form-item label="设备数量" label-width="110px" style="text-align: left">
          <el-input-number v-model="editdeveloperinfo.usable_number" :max="100" :min="0" label="设备数量"/>
        </el-form-item>
        <el-form-item label="证书id" label-width="110px">
          <el-input v-model="editdeveloperinfo.certid" :disabled='isedit'/>
        </el-form-item>
        <el-form-item label="备注" label-width="110px">
          <el-input v-model="editdeveloperinfo.description"/>
        </el-form-item>
        <div style="">
          <el-button v-if="isedit && editdeveloperinfo.is_actived && editdeveloperinfo.certid" size="small"
                     @click="exportcert">导出证书
          </el-button>
          <el-button v-if="isedit && editdeveloperinfo.is_actived && !editdeveloperinfo.certid" size="small"
                     @click="importcertDeveloperVisible=true">导入p12证书
          </el-button>
          <el-button v-if="isedit && editdeveloperinfo.is_actived && editdeveloperinfo.certid" size="small"
                     type="danger"
                     @click="cleandevices">清理签名数据
          </el-button>
          <el-button v-if="isedit && editdeveloperinfo.is_actived" size="small" @click="syncdevices">同步设备信息
          </el-button>
          <el-tooltip content="发布证书只能创建两个，请谨慎操作">
            <el-button v-if="isedit && editdeveloperinfo.is_actived && !editdeveloperinfo.certid"
                       size="small"
                       @click="isocertcert">手动创建发布证书
            </el-button>
          </el-tooltip>
          <el-tooltip content="清理发布证书，如果发布证书过期时间大于3天，将不会删除开发者发布证书，发布证书只能同时创建两个，请谨慎操作">
            <el-button v-if="isedit && editdeveloperinfo.is_actived && editdeveloperinfo.certid"
                       size="small"
                       type="danger"
                       @click="isorenewcert">删除发布证书
            </el-button>
          </el-tooltip>
          <el-button v-if="isedit && editdeveloperinfo.is_actived" size="small" type="success"
                     @click="activedeveloperFun(editdeveloperinfo,'checkauth')">账户激活检测
          </el-button>

          <el-button @click="updateorcreate">保存</el-button>
          <el-button @click="canceledit">取消</el-button>
        </div>


      </el-form>
    </el-dialog>

    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :visible.sync="dialogShowDeviceBillInfo"
               center title="设备消耗详细信息" width="750px">

      <el-table
          v-loading="loading"
          :data="app_bill_info_lists"
          border
          stripe
          style="width: 100%">
        <el-table-column
            align="center"
            label="应用名称"
            prop="app_name"
        >
        </el-table-column>

        <el-table-column
            align="center"
            label="客户端IP"
            prop="remote_addr">
        </el-table-column>
        <el-table-column
            align="center"
            label="账单类型"
            prop="action"
            width="100">
        </el-table-column>

        <el-table-column
            :formatter="deviceformatter"
            align="center"
            label="日期"
            prop="created_time"
            width="160">
        </el-table-column>
        <el-table-column
            align="center"
            label="应用状态"
            width="110">
          <template slot-scope="scope">
            <el-tag v-if="scope.row.app_status===false" type="info">应用删除</el-tag>
            <el-tag v-else>
              应用存在
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
            align="center"
            label="设备状态"
            width="110">
          <template slot-scope="scope">
            <el-tag v-if="scope.row.is_used===false" type="info">已经释放</el-tag>
            <el-tag v-else>
              使用中
            </el-tag>
          </template>
        </el-table-column>

      </el-table>
      <div style="margin-top: 20px">
        <el-pagination
            :current-page.sync="billpagination.currentPage"
            :page-size="billpagination.pagesize"
            :page-sizes="[10, 20, 50, 100]"
            :total="billpagination.total"
            layout="total,sizes, prev, pager, next"
            @size-change="billhandleSizeChange"
            @current-change="billhandleCurrentChange">
        </el-pagination>
      </div>
      <span slot="footer">
            <el-button @click="closeDeviceBillInfo">关闭</el-button>
            </span>
    </el-dialog>

    <el-tabs v-model="activeName" tab-position="top" type="border-card" @tab-click="handleClick">
      <el-tab-pane label="开发者账户" name="iosdeveloper">
        <el-input
            v-model="appidseach"
            clearable
            placeholder="输入用户ID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(pagination.currentPage)">
          搜索
        </el-button>
        <div style="width: 40%;margin-right: 30px;float:right">
          <el-link :underline="false">总设备量：{{ developer_used_info.all_usable_number }} 已经使用：【平台：{{
              developer_used_info.all_use_number
            }} 】【其他：{{ developer_used_info.other_used_sum }} 】
            还剩：{{ developer_used_info.all_usable_number - developer_used_info.flyapp_used_sum }} 可用
          </el-link>
          <el-progress
              :color="developer_usedColor"
              :percentage="percentage"
              :stroke-width="18" :text-inside="true" status="success"
              type="line"/>
        </div>

        <el-table
            v-loading="loading"
            :data="app_developer_lists"
            border
            stripe
            style="width: 100%">

          <el-table-column
              align="center"
              fixed
              label="用户 issuer_id"
              prop="issuer_id"
              width="300">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>开发者账户已使用设备数: {{ scope.row.developer_used_number }}</p>
                <p>开发者账户可用设备数: {{ 100 - scope.row.developer_used_number }}</p>
                <p>由于您设置可用设备数: {{ scope.row.usable_number }} ,所以现在可用设备数: {{
                    scope.row.usable_number - scope.row.developer_used_number > 0
                        ? scope.row.usable_number - scope.row.developer_used_number : 0
                  }}</p>

                <div slot="reference" class="name-wrapper">
                  <el-tag v-if="scope.row.issuer_id" size="medium"><i class="el-icon-key"/> {{
                      scope.row.issuer_id
                    }}
                  </el-tag>
                </div>
              </el-popover>
            </template>

          </el-table-column>
          <el-table-column
              align="center"
              label="是否激活"
              prop="is_actived"
              width="110">
            <template slot-scope="scope">
              <el-button v-if="scope.row.is_actived === true" size="small" type="success">已激活</el-button>
              <el-button v-else size="small" type="danger"
                         @click="activedeveloperFun(scope.row,'checkauth')">点击激活
              </el-button>

            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="账户状态"
              prop="certid"
              width="100">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p v-if="!scope.row.certid && scope.row.is_actived === true">
                  开发证书不可用，请在编辑中导入或手动创建发布证书</p>
                <p v-if="!scope.row.certid && scope.row.is_actived !== true">请先激活开发者账户</p>
                <p v-if="scope.row.certid && scope.row.is_actived === true">账户已经启用</p>
                <div slot="reference" class="name-wrapper">
                  <el-button v-if="scope.row.certid " size="small" type="success">可用</el-button>
                  <el-button v-else size="small" type="danger">不可用</el-button>
                </div>
              </el-popover>

            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="可用设备"
              prop="usable_number"
              width="60">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>可用设备数: {{
                    scope.row.usable_number - scope.row.developer_used_number > 0
                        ? scope.row.usable_number - scope.row.developer_used_number : 0
                  }}</p>
                <div slot="reference" class="name-wrapper">
                  <el-tag size="medium"> {{
                      scope.row.usable_number - scope.row.developer_used_number >
                      0 ? scope.row.usable_number - scope.row.developer_used_number : 0
                    }}
                  </el-tag>
                </div>
              </el-popover>
            </template>
          </el-table-column>

          <el-table-column
              align="center"
              label="设备消耗"
              prop="use_number"
              width="60">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>开发者账户已使用设备数【本平台】: {{ scope.row.use_number }}</p>
                <p>开发者账户已使用设备数【其他】: {{ scope.row.developer_used_other_number }}</p>
                <div slot="reference" class="name-wrapper">
                  <el-tag size="medium">{{ scope.row.use_number }}</el-tag>
                </div>
              </el-popover>
            </template>
          </el-table-column>

          <el-table-column
              :formatter="formatter"
              align="center"
              label="证书到期时间"
              prop="cert_expire_time"
              width="160">
          </el-table-column>
          <el-table-column
              align="center"
              label="备注"
              prop="description"
          >
          </el-table-column>
          <el-table-column
              align="center"
              fixed="right"
              label="操作"
              width="150">
            <template slot-scope="scope">

              <el-button
                  size="mini"
                  @click="handleEditDeveloper(scope.row)">编辑
              </el-button>
              <el-button
                  size="mini"
                  type="danger"
                  @click="handleDeleteDeveloper(scope.row)">删除
              </el-button>

            </template>
          </el-table-column>
        </el-table>


      </el-tab-pane>
      <el-tab-pane label="添加开发者" name="adddeveloper" style="text-align:center">
        <el-form ref="storageinfoform" :model="editdeveloperinfo"
                 label-width="80px" style="margin:0 auto;">

          <el-form-item label="认证类型" label-width="100px">
            <el-select v-model="editdeveloperinfo.auth_type" placeholder="认证类型"
                       style="margin-left: -100px">
              <el-option v-for="st in apple_auth_list" :key="st.id" :label="st.name"
                         :value="st.id"/>
            </el-select>
          </el-form-item>
          <div v-if="editdeveloperinfo.auth_type===0">
            <el-form-item label="issuer_id" label-width="110px">
              <el-input v-model="editdeveloperinfo.issuer_id" :disabled='isedit'/>
            </el-form-item>

            <el-form-item label="private_key_id" label-width="110px">
              <el-input v-model="editdeveloperinfo.private_key_id" :placeholder="placeholder"/>
            </el-form-item>

            <el-form-item label="p8key" label-width="110px">
              <el-input v-model="editdeveloperinfo.p8key"
                        :placeholder="placeholder" :rows="6" type="textarea"/>
            </el-form-item>
          </div>

          <el-form-item label="设备数量" label-width="110px" style="text-align: left">
            <el-input-number v-model="editdeveloperinfo.usable_number" :max="100" :min="0" label="设备数量"/>
          </el-form-item>

          <el-form-item label="备注" label-width="110px">
            <el-input v-model="editdeveloperinfo.description"/>
          </el-form-item>
          <div style="">
            <el-button plain type="primary" @click="updateorcreate">保存信息并添加</el-button>
          </div>

        </el-form>
        <el-card header="获取密钥帮助" style="margin-top: 20px;text-align: left">
          <h1>获取密钥：</h1>
          <p>前往 AppStore Connect 。按照
            <el-button plain size="small" type="primary" @click="$router.push({name:'FirSuperSignHelp'})">
              此步骤
            </el-button>
            获取 API 密钥，将获取到的密钥添加到这里。
          </p>

          <h1>注意事项：</h1>
          <p>1.添加后，请勿撤销 API 密钥，否则会导致用户安装的软件闪退或无法安装！</p>
          <p>2.每个开发者账号最多可创建两本证书，请确保至少还可以创建一本证书！</p>
          <p>3.添加后，激活开发者账户，然后您就可以上传p12证书或者通过系统自动创建证书、设备和描述文件，请勿删除这些文件，否则会导致用户安装的软件闪退或无法安装！</p>

        </el-card>
      </el-tab-pane>
      <el-tab-pane label="设备消耗" name="useddevices">
        <el-input
            v-model="udidsearch"
            clearable
            placeholder="输入UDID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-input
            v-model="Bundleidsearch"
            clearable
            placeholder="输入BundleID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-input
            v-model="appidseach"
            clearable
            placeholder="输入用户ID"
            style="width: 23%;margin-right: 30px;margin-bottom: 10px"/>
        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(pagination.currentPage)">
          搜索
        </el-button>

        <el-table
            v-loading="loading"
            :data="app_devices_lists"
            border
            stripe
            style="width: 100%">
          <el-table-column
              align="center"
              fixed
              label="设备ID"
              prop="device_udid"
          >
          </el-table-column>
          <el-table-column
              align="center"
              label="设备名称"
              prop="device_name"
              width="120">
          </el-table-column>
          <el-table-column
              align="center"
              label="应用ID"
              prop="bundle_id"
              width="180">
          </el-table-column>
          <el-table-column
              align="center"
              label="应用名称"
              prop="bundle_name"
              width="160">
          </el-table-column>
          <el-table-column
              align="center"
              label="开发者ID"
              prop="developer_id"
              width="200">
          </el-table-column>
          <el-table-column
              v-if="$store.state.userinfo&&$store.state.userinfo.role == 3"
              align="center"
              label="被使用户uid"
              prop="other_uid">
          </el-table-column>
          <el-table-column
              :formatter="deviceformatter"
              align="center"
              label="授权时间"
              prop="created_time"
              width="160">
          </el-table-column>
        </el-table>


      </el-tab-pane>
      <el-tab-pane label="设备管理" name="devicesudid">
        <el-input
            v-model="udidsearch"
            clearable
            placeholder="输入UDID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-input
            v-model="Bundleidsearch"
            clearable
            placeholder="输入BundleID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(pagination.currentPage)">
          搜索
        </el-button>


        <el-table
            v-loading="loading"
            :data="app_udid_lists"
            border
            stripe
            style="width: 100%">

          <el-table-column
              align="center"
              fixed
              label="设备ID"
              prop="udid"
          >
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>Bundle_ID: {{ scope.row.bundle_id }}</p>
                <p>应用名称: {{ scope.row.bundle_name }}</p>
                <p>UDID: {{ scope.row.udid }}</p>
                <div slot="reference" class="name-wrapper">
                  <el-tag size="medium">{{ scope.row.udid }}</el-tag>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="imei"
              prop="imei"
              width="160">

          </el-table-column>
          <el-table-column
              align="center"
              label="设备名称"
              prop="product"
              width="100">
          </el-table-column>
          <el-table-column
              align="center"
              label="设备型号"
              prop="version"
              width="100">
          </el-table-column>
          <el-table-column
              align="center"
              label="设备序列号"
              prop="serial"
              width="140">
          </el-table-column>
          <el-table-column
              v-if="$store.state.userinfo&&$store.state.userinfo.role == 3"
              align="center"
              label="被使用户uid"
              prop="other_uid">
          </el-table-column>
          <el-table-column
              :formatter="deviceformatter"
              align="center"
              label="添加时间"
              prop="created_time"
              width="160">
          </el-table-column>
          <el-table-column
              align="center"
              fixed="right"
              label="操作"
              width="110">
            <template slot-scope="scope">
              <el-button
                  v-if="scope.row.is_mine"
                  size="mini"
                  type="danger"
                  @click="udidDeleteFun(scope)">删除
              </el-button>
              <el-tag v-else>
                ...
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

      </el-tab-pane>
      <el-tab-pane label="设备消耗账单" name="devicesbill">
        <el-input
            v-model="udidsearch"
            clearable
            placeholder="输入UDID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>

        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(pagination.currentPage)">
          搜索
        </el-button>


        <el-table
            v-loading="loading"
            :data="app_bill_lists"
            border
            stripe
            style="width: 100%">

          <el-table-column
              align="center"
              fixed
              label="设备ID"
              prop="udid"
          >
            <template slot-scope="scope">
              <el-tooltip content="点击查看设备安装详细信息" effect="dark" placement="top">
                <el-link :underline="false" @click="showDeviceBill(scope.row.udid)">
                  {{ scope.row.udid }}
                </el-link>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="设备名称"
              prop="product"
              width="200">

          </el-table-column>
          <el-table-column
              align="center"
              label="设备版本"
              prop="version"
          >
          </el-table-column>

          <el-table-column
              align="center"
              label="设备安装次数"
              prop="counts"
              width="110">

          </el-table-column>

          <el-table-column
              align="center"
              label="设备状态"
              width="110">
            <template slot-scope="scope">
              <el-tag v-if="!scope.row.udid_sync_info_id" type="info">已经释放</el-tag>
              <el-tag v-else>
                使用中
              </el-tag>
            </template>
          </el-table-column>

        </el-table>

      </el-tab-pane>
      <div v-if="activeName!== 'adddeveloper'" style="margin-top: 20px">
        <el-pagination
            :current-page.sync="pagination.currentPage"
            :page-size="pagination.pagesize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total,sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-tabs>

  </el-main>
</template>

<script>

import {developercert, DeviceBillInfo, iosdeveloper, iosdevices, iosdevicesudid} from "@/restful";
import {getUserInfoFun, removeAaary} from "@/utils";

export default {
  name: "FirSuperSignBase",
  data() {
    return {
      dialogShowDeviceBillInfo: false,
      currentudid: '',
      fileList: [],
      app_developer_lists: [],
      app_devices_lists: [],
      app_bill_lists: [],
      app_bill_info_lists: [],
      app_udid_lists: [],
      activeName: "iosdeveloper",
      udidsearch: "",
      Bundleidsearch: "",
      appidseach: "",
      dialogaddDeveloperVisible: false,
      importcertDeveloperVisible: false,
      title: "",
      editdeveloperinfo: {auth_type: 0, usable_number: 100},
      isedit: false,
      placeholder: "",
      pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
      billpagination: {"currentPage": 1, "total": 0, "pagesize": 10},
      developer_used_info: {"all_usable_number": 0, "other_used_sum": 0, "all_use_number": 0},
      percentage: 0,
      apple_auth_list: [],
      apple_auth_type: 0,
      loadingfun: {},
      loading: false,
      cert_pwd: '',
    }
  }, watch: {
    'dialogaddDeveloperVisible': function () {
      if (this.dialogaddDeveloperVisible === false) {
        this.canceledit();
      }
    }
  },
  methods: {
    closeDeviceBillInfo() {
      this.dialogShowDeviceBillInfo = false;
      this.currentudid = '';
      this.app_bill_info_lists = [];
    },
    showDeviceBill(udid) {
      this.currentudid = udid;
      this.iosdevicebillFun({"methods": "GET", "data": {'udid': udid, 'act': 'info'}});
      this.dialogShowDeviceBillInfo = true;
    },
    billhandleSizeChange(val) {
      this.billpagination.pagesize = val;
      this.iosdevicebillFun({
        "methods": "GET", "data": {
          "size": this.billpagination.pagesize,
          "page": 1,
          "act": "info",
          'udid': this.currentudid
        }
      })
    },
    billhandleCurrentChange(val) {
      this.billpagination.currentPage = val;
      this.iosdevicebillFun({
        "methods": "GET", "data": {
          "size": this.billpagination.pagesize,
          "page": this.billpagination.currentPage,
          "act": "info",
          'udid': this.currentudid
        }
      })
    },
    beforeAvatarUpload(file) {
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (file.type === 'application/x-pkcs12') {
        if (isLt2M) {
          if (this.cert_pwd && this.cert_pwd.toString().trim().length > 0) {
            let reader = new FileReader();
            reader.onload = evt => {
              developercert(data => {
                if (data.code === 1000) {
                  this.$message.success("证书导入成功");
                  this.importcertDeveloperVisible = false;
                  this.dialogaddDeveloperVisible = false;
                  this.handleCurrentChange(this.pagination.currentPage)
                } else {
                  this.$message.error("证书导入失败 " + data.msg)
                }
              }, {
                methods: 'POST',
                data: {
                  issuer_id: this.editdeveloperinfo.issuer_id,
                  cert_pwd: this.cert_pwd,
                  cert_content: evt.target.result
                }
              })
            };
            reader.readAsDataURL(file);
            return false;
          } else {
            this.$message.warning('密码不能为空');
          }
        } else {
          this.$message.warning('上传大小有误');
        }
      } else {
        this.$message.warning('上传文件格式不正确!');
      }
      return false;
    },
    developer_usedColor(percentage) {
      if (percentage < 20) {
        return '#6f7ad3';
      } else if (percentage < 40) {
        return '#1989fa';
      } else if (percentage < 60) {
        return '#5cb87a';

      } else if (percentage < 80) {
        return '#e6a23c';
      } else if (percentage < 90) {
        return '#E63918';
      } else {
        return '#F50346';
      }
    },
    udidDeleteFun(scope) {
      this.iosdevicesudidFun('DELETE', {id: scope.row.id, aid: scope.row.app_id}, scope);
    },
    handleSizeChange(val) {
      this.pagination.pagesize = val;
      this.get_data_from_tabname(this.activeName, {
        "size": this.pagination.pagesize,
        "page": 1
      })
    },
    handleCurrentChange(val) {
      this.pagination.currentPage = val;
      this.get_data_from_tabname(this.activeName, {
        "size": this.pagination.pagesize,
        "page": this.pagination.currentPage
      })
    },
    syncdevices() {
      this.iosdeveloperFun({
        "methods": "PUT",
        "data": {"issuer_id": this.editdeveloperinfo.issuer_id, "act": "syncdevice"}
      });
    },
    cleandevices() {
      this.iosdeveloperFun({
        "methods": "PUT",
        "data": {"issuer_id": this.editdeveloperinfo.issuer_id, "act": "cleandevice"}
      });
    },
    isocertcert() {

      this.$confirm('此操作将要创建新的发布证书, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.iosdeveloperFun({
          "methods": "PUT",
          "data": {"issuer_id": this.editdeveloperinfo.issuer_id, "act": "ioscert"}
        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消'
        });
      });
    },
    exportcert() {
      // eslint-disable-next-line no-unused-vars
      developercert(data => {
      }, {methods: 'FILE', data: {issuer_id: this.editdeveloperinfo.issuer_id}})
    },
    isorenewcert() {
      this.$confirm('此操作将永久删除该发布证书, 建议先导出证书。是否继续删除?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.iosdeveloperFun({
          "methods": "PUT",
          "data": {"issuer_id": this.editdeveloperinfo.issuer_id, "act": "renewcert"}
        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消'
        });
      });

    },
    activedeveloperFun(developer, act) {
      this.iosdeveloperFun({"methods": "PUT", "data": {"issuer_id": developer.issuer_id, "act": act}});
    },
    canceledit() {
      this.dialogaddDeveloperVisible = false;
      this.editdeveloperinfo = {auth_type: 0, usable_number: 100};
      this.isedit = false;
      this.placeholder = ""
    },
    handleEditDeveloper(developer_info) {
      this.editdeveloperinfo = developer_info;
      this.title = '编辑开发者账户';
      this.dialogaddDeveloperVisible = true;
      this.isedit = true;
      this.placeholder = "为空表示不修改该信息"
    },
    updateorcreate() {
      if (this.isedit) {
        this.iosdeveloperFun({"methods": "PUT", "data": this.editdeveloperinfo})
      } else {
        if (this.editdeveloperinfo.auth_type === 0) {
          if (this.editdeveloperinfo.issuer_id && this.editdeveloperinfo.private_key_id && this.editdeveloperinfo.usable_number && this.editdeveloperinfo.p8key) {
            this.iosdeveloperFun({"methods": "POST", "data": this.editdeveloperinfo});
          } else {
            this.$message.warning("输入格式有误")
          }
        } else {
          this.$message.error("输入格式有误")
        }

      }
    },
    handleDeleteDeveloper(developer_info) {
      this.$confirm('此操作会删除该苹果开发者账户下面的生成的证书等数据,可能会导致超级签包的闪退, 是否继续?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.iosdeveloperFun({"methods": "DELETE", "data": {"issuer_id": developer_info.issuer_id}});
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    get_data_from_tabname(tabname, data = {}) {
      data.udid = this.udidsearch.replace(/^\s+|\s+$/g, "");
      data.bundleid = this.Bundleidsearch.replace(/^\s+|\s+$/g, "");
      data.appid = this.appidseach.replace(/^\s+|\s+$/g, "");
      this.$router.push({"name": 'FirSuperSignBase', params: {act: tabname}});
      if (tabname === "useddevices") {
        this.iosdevicesFun('GET', data)
      } else if (tabname === "devicesudid") {
        this.iosdevicesudidFun('GET', data, null)
      } else if (tabname === "adddeveloper") {
        this.iosdeveloperFun({"methods": "GET", "data": data})
        // this.title='新增私有开发者账户';
        // this.dialogaddDeveloperVisible=true;
      } else if (tabname === "iosdeveloper") {
        this.iosdeveloperFun({"methods": "GET", "data": data})
      } else if (tabname === "devicesbill") {
        this.iosdevicebillFun({"methods": "GET", "data": data})
      }

    },
    // eslint-disable-next-line no-unused-vars
    handleClick(tab, event) {
      this.pagination = {"currentPage": 1, "total": 0, "pagesize": 10};
      this.get_data_from_tabname(tab.name);
    },
    // eslint-disable-next-line no-unused-vars
    deviceformatter(row, column) {
      let stime = row.created_time;
      if (stime) {
        stime = stime.split(".")[0].split("T");
        return stime[0] + " " + stime[1]
      } else
        return '';
    },
    // eslint-disable-next-line no-unused-vars
    formatter(row, column) {
      let stime = row.cert_expire_time;
      if (stime) {
        stime = stime.split(".")[0].split("T");
        return stime[0] + " " + stime[1]
      } else
        return '';
    },
    iosdevicesFun(methods, data) {
      this.loading = true;
      iosdevices(data => {
        if (data.code === 1000) {
          this.app_devices_lists = data.data;
          this.pagination.total = data.count;
        }
        this.loading = false;
      }, {
        "methods": methods, "data": data
      })
    },
    iosdeveloperFun(params) {
      if (params.methods !== 'GET') {
        this.loadingfun = this.$loading({
          lock: true,
          text: '执行中,请耐心等待...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
      } else {
        this.loading = true
      }
      iosdeveloper(data => {
        if (data.code === 1000) {
          this.app_developer_lists = data.data;
          this.pagination.total = data.count;
          this.apple_auth_list = data.apple_auth_list;
          if (data.use_num) {
            this.developer_used_info = data.use_num;
            if (this.developer_used_info.all_usable_number !== 0) {
              let p = parseInt(this.developer_used_info.flyapp_used_sum * 100 / this.developer_used_info.all_usable_number);
              if (p < 0 || p >= 100) {
                p = 100
              }
              this.percentage = p;
            }
          }

          if (this.dialogaddDeveloperVisible) {
            this.canceledit();
            this.$message.success("操作成功");
            this.activeName = "iosdeveloper";
            this.editdeveloperinfo = {auth_type: 0, usable_number: 100};
          }
          if (!this.edit && this.editdeveloperinfo.issuer_id) {
            this.$message.success("添加成功");
            this.activeName = "iosdeveloper";
            this.editdeveloperinfo = {auth_type: 0, usable_number: 100};
          }
        } else if (data.code === 1008) {
          this.$message.error(data.msg);
        } else {
          this.$message.error("操作失败")
        }
        if (params.methods !== 'GET') {
          this.loadingfun.close();
        } else {
          this.loading = false
        }
      }, params)
    },
    iosdevicebillFun(params) {
      this.loading = true;
      DeviceBillInfo(data => {
        if (data.code === 1000) {
          if (params.data.act && params.data.act === 'info') {
            this.app_bill_info_lists = data.data;
            this.billpagination.total = data.count;
          } else {
            this.app_bill_lists = data.data;
            this.pagination.total = data.count;
          }
        } else {
          this.$message.error("操作失败了 " + data.msg);
        }
        this.loading = false
      }, params)
    },
    iosdevicesudidFun(action, data, scope) {
      if (action !== 'GET') {
        this.loadingfun = this.$loading({
          lock: true,
          text: '执行中,请耐心等待...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
      } else {
        this.loading = true
      }
      iosdevicesudid(data => {
        if (data.code === 1000) {
          if (action !== "DELETE") {
            this.app_udid_lists = data.data;
            this.pagination.total = data.count;
          } else {
            if (scope) {
              this.app_udid_lists = removeAaary(this.app_udid_lists, scope.row)
            }
          }
        } else {
          this.$message.error("操作失败了 " + data.msg);
        }
        if (action !== 'GET') {
          this.loadingfun.close()
        } else {
          this.loading = false
        }
      }, {
        "methods": action, "data": data
      })
    },
  }, mounted() {
    getUserInfoFun(this);
    if (this.$route.params.act) {
      let activeName = this.$route.params.act;
      let activeName_list = ["useddevices", "devicesudid", "adddeveloper", "iosdeveloper"];
      for (let index in activeName_list) {
        if (activeName_list[index] === activeName) {
          this.activeName = activeName;
          let bundleid = this.$route.query.bundleid;
          if (bundleid) {
            this.Bundleidsearch = bundleid;
          }
          this.get_data_from_tabname(activeName);
          return
        }
      }
    }
    this.get_data_from_tabname(this.activeName);
  }
}
</script>

<style scoped>
.el-main {
  margin: 20px auto 100px;
  width: 1166px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}

</style>
