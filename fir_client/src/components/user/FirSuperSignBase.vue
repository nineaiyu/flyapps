<template>
  <el-main>
    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :title="appletoapp_title"
        :visible.sync="bind_appletoapp_sure"
        width="1166px">
      <apple-developer-bind-app v-if="bind_appletoapp_sure" :issuer_id="editdeveloperinfo.issuer_id"
                                transitionName="bind_appletoapp"/>
    </el-dialog>
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
          <el-input-number v-model="editdeveloperinfo.usable_number" :max="100" :min="0" label="设备数量" size="small"/>
          <el-tag style="margin-left: 10px" type="warning">可消耗设备数量，超过该数量，将无法进行新设备签名。已经消耗
            {{ editdeveloperinfo.developer_used_number }} 个设备
          </el-tag>
        </el-form-item>
        <el-form-item label="应用数量" label-width="110px" style="text-align: left">
          <el-input-number v-model="editdeveloperinfo.app_limit_number" :max="160" :min="0" label="应用数量" size="small"/>
          <el-tag style="margin-left: 10px" type="warning">可签名应用数量，超过该数量，将无法进行新应用签名。已经分配
            {{ editdeveloperinfo.app_used_count }} 个应用
          </el-tag>
        </el-form-item>
        <el-form-item label="维护模式" label-width="110px" style="text-align: left">
          <el-switch
              v-model="read_only_mode"
              :disabled="read_only_mode==='on'"
              active-color="#13ce66"
              active-value="on"
              inactive-color="#ff4949"
              inactive-value="off">
          </el-switch>
          <el-tag style="margin-left: 10px" type="warning"> 该模式下，新设备，新应用无法进行注册安装，但是已经安装的不影响</el-tag>
          <el-tag v-if="read_only_mode==='on'" style="margin-left: 50px" type="warning"> 通过账户激活进行关闭维护模式</el-tag>
        </el-form-item>
        <el-form-item label="清理禁用设备" label-width="110px" style="text-align: left">
          <el-switch
              v-model="editdeveloperinfo.clean_status"
              :active-value="true"
              :inactive-value="false"
              active-color="#13ce66"
              inactive-color="#ff4949">
          </el-switch>
          <el-tag style="margin-left: 10px" type="warning"> 清理数据的时候，是否同时将开发者设备禁用，默认不禁用</el-tag>
        </el-form-item>
        <el-form-item label="证书id" label-width="110px">
          <el-input v-model="editdeveloperinfo.certid" :disabled='isedit'/>
        </el-form-item>
        <el-form-item label="备注" label-width="110px">
          <el-input v-model="editdeveloperinfo.description"/>
        </el-form-item>
        <div style="">
          <el-button v-if="isedit && editdeveloperinfo.certid" size="small"
                     @click="exportcert">导出证书
          </el-button>
          <el-button v-if="isedit && !editdeveloperinfo.certid" size="small"
                     @click="importcertDeveloperVisible=true">导入p12证书
          </el-button>
          <el-button v-if="isedit && editdeveloperinfo.certid" size="small"
                     type="danger"
                     @click="cleandevices">清理签名数据
          </el-button>
          <el-button v-if="isedit && editdeveloperinfo.status!==0 || editdeveloperinfo.certid" size="small"
                     @click="syncdevices">同步设备信息
          </el-button>
          <el-tooltip content="发布证书只能创建两个，请谨慎操作">
            <el-button v-if="isedit &&  !editdeveloperinfo.certid"
                       size="small"
                       @click="isocertcert">手动创建发布证书
            </el-button>
          </el-tooltip>
          <el-tooltip content="清理发布证书，如果发布证书过期时间大于3天，将不会删除开发者发布证书，发布证书只能同时创建两个，请谨慎操作">
            <el-button v-if="isedit &&  editdeveloperinfo.certid"
                       size="small"
                       type="danger"
                       @click="isorenewcert">删除发布证书
            </el-button>
          </el-tooltip>
          <el-button v-if="isedit && editdeveloperinfo.status!==0" size="small" type="success"
                     @click="activedeveloperFun(editdeveloperinfo,'checkauth')">账户激活检测
          </el-button>
          <!--          <el-button v-if="isedit && editdeveloperinfo.is_actived" size="small" @click="bindAppletoapp(editdeveloperinfo)">专属应用</el-button>-->
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
        >
          <template slot-scope="scope">
            <div v-if="scope.row.action==='消费'">
              <el-tag v-if="scope.row.app_status===false" type="info">应用删除</el-tag>
              <el-tag v-else>
                应用存在
              </el-tag>
            </div>
            <span v-else>{{ scope.row.description }}</span>
          </template>
        </el-table-column>
        <el-table-column
            align="center"
            label="设备状态">
          <template slot-scope="scope">
            <div v-if="scope.row.action==='消费'">
              <el-tag v-if="scope.row.is_used===false" type="info">已经释放</el-tag>
              <el-tag v-else>
                使用中
              </el-tag>
            </div>
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
    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :visible.sync="udeviceappinfoVisible"
               center title="设备消耗应用详细信息" width="750px">

      <el-table
          v-loading="loading"
          :data="app_used_info_list"
          border
          stripe
          style="width: 100%">
        <el-table-column
            align="center"
            label="应用名称"
            prop="bundle_name"
        >
        </el-table-column>


        <el-table-column
            align="center"
            label="应用ID"
            prop="bundle_id"
        >
        </el-table-column>


        <el-table-column
            :formatter="deviceformatter"
            align="center"
            label="日期"
            prop="created_time"
            width="160">
        </el-table-column>

      </el-table>
      <span slot="footer">
            <el-button @click="udeviceappinfoVisible=false">关闭</el-button>
            </span>
    </el-dialog>

    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :visible.sync="setdeveloperstatusVisible"
               style="text-align:center" title="批量修改账户状态" width="700px">
      <el-select v-model="change_developer_status" clearable
                 placeholder="账户状态" style="width: 49%;margin-right: 45px;margin-bottom: 10px">
        <el-option
            v-for="item in status_choices"
            :key="item.id"
            :disabled="item.disabled"
            :label="item.name"
            :value="item.id">
        </el-option>
      </el-select>

      <el-button @click="setdeveloperstatus">确定</el-button>
      <el-button @click="setdeveloperstatusVisible=false">取消</el-button>
      <div style="text-align: left">
        <p>受影响的开发者ID</p>
        <el-row v-for="isid in multipleSelection" :key="isid.issuer_id">
          <el-col :span="16">账户ID：{{ isid.issuer_id }}</el-col>
          <el-col :span="8">当前状态：{{ format_status(isid.status) }}</el-col>
        </el-row>
      </div>
    </el-dialog>


    <el-tabs v-model="activeName" tab-position="top" type="border-card" @tab-click="handleClick">
      <el-tab-pane label="开发者账户" name="iosdeveloper">
        <el-input
            v-model="appidseach"
            clearable
            placeholder="输入开发者ID或者备注或应用BundleID"
            style="width: 30%;margin-right: 10px;margin-bottom: 10px"/>

        <el-select v-model="developer_choice" clearable placeholder="账户类型"
                   style="width: 18%;margin-right: 10px;margin-bottom: 10px">
          <el-option
              v-for="item in developer_options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
          </el-option>
        </el-select>

        <div style="width: 45%;margin-right: 20px;float:right;margin-bottom: 10px">
          <el-link :underline="false">总设备量：{{ developer_used_info.all_usable_number }} 已使用：【平台：{{
              developer_used_info.all_use_number
            }} 】【其他：{{ developer_used_info.other_used_sum }}】
            还剩：{{
              developer_used_info.all_usable_number - developer_used_info.flyapp_used_sum - developer_used_info.other_used_sum
            }} 可用
          </el-link>
          <el-progress
              :color="developer_usedColor"
              :percentage="percentage"
              :stroke-width="18" :text-inside="true" status="success"
              type="line"/>
        </div>

        <el-row>
          <el-col :span="24">
            <div>
              <el-select v-model="developer_status_choice" clearable multiple
                         placeholder="账户状态" style="width: 49%;margin-right: 45px;margin-bottom: 10px">
                <el-option
                    v-for="item in status_choices"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id">
                </el-option>
              </el-select>
              <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
                搜索
              </el-button>
              <el-button type="plain" @click="activemanydeveloperFun">
                账户状态检测
              </el-button>
              <el-button type="plain" @click="setdeveloperstatusFun">
                批量设置账户状态
              </el-button>
            </div>
          </el-col>
        </el-row>

        <el-table
            v-loading="loading"
            :data="app_developer_lists"
            border
            stripe
            style="width: 100%"
            @selection-change="handleSelectionChange">
          <el-table-column
              type="selection"
              width="39">
          </el-table-column>
          <el-table-column
              align="center"
              fixed
              label="开发者ID issuer_id"
              prop="issuer_id"
              width="200">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <el-tooltip content="点击复制到剪贴板">

                  <el-link v-clipboard:copy="scope.row.issuer_id"
                           v-clipboard:success="copy_success"
                           :underline="false">开发者账户ID: {{ scope.row.issuer_id }}
                  </el-link>
                </el-tooltip>
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
              prop="status"
              width="110">
            <template slot-scope="scope">
              <el-tooltip v-if="scope.row.status!==0" content="点击禁用">
                <el-button size="small" type="success" @click="disabledeveloperFun(scope.row,'disable')">已激活</el-button>
              </el-tooltip>
              <el-button v-else size="small" type="danger"
                         @click="activedeveloperFun(scope.row,'checkauth')">点击激活
              </el-button>

            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="账户状态"
              prop="certid"
              sortable
              width="110">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p v-if="!scope.row.certid && scope.row.status!==0">
                  开发证书不可用，请在编辑中导入或手动创建发布证书</p>
                <p v-if="!scope.row.certid && scope.row.status=== 0">请先激活开发者账户</p>
                <p v-if="scope.row.certid && scope.row.status!==0">{{ format_status(scope.row.status) }}</p>
                <div slot="reference" class="name-wrapper">
                  <div v-if="scope.row.certid">
                    <el-button v-if="scope.row.status === 1" size="small" type="success">
                      {{ format_status(scope.row.status) }}
                    </el-button>
                    <el-button v-else size="small" type="warning" @click="activedeveloperFun(scope.row,'checkauth')">
                      {{ format_status(scope.row.status) }}
                    </el-button>
                  </div>

                  <el-button v-else size="small" type="danger">不可用</el-button>
                </div>
              </el-popover>

            </template>
          </el-table-column>
          <el-table-column
              :formatter="formatter_usable_number"
              :sort-method="sort_method_usable_number"
              align="center"
              label="可用设备"
              prop="usable_number"
              sortable
              width="70">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>可用设备数: {{ formatter_usable_number(scope.row) }}</p>
                <div slot="reference" class="name-wrapper">
                  <el-tag size="medium"> {{ formatter_usable_number(scope.row) }}</el-tag>
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
              align="center"
              label="应用签名"
              prop="app_used_count"
              width="60">
            <template slot-scope="scope">

              <el-popover placement="top" trigger="hover">
                <p>签名了 {{ scope.row.app_used_count }} 个应用</p>
                <p>应用限额 {{ scope.row.app_limit_number }} 个应用</p>
                <p>还可以签名 {{ scope.row.app_limit_number - scope.row.app_used_count }} 个新应用</p>
                <div slot="reference" class="name-wrapper">
                  <el-link v-if="scope.row.app_used_count > 0" :underline="false"
                           @click="show_device_ubill(scope.row.issuer_id)">
                    <el-tag size="medium">{{ scope.row.app_used_count }}</el-tag>
                  </el-link>
                  <el-tag v-else size="medium">{{ scope.row.app_used_count }}</el-tag>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="专属账户"
              prop="is_private"
              width="60">
            <template slot-scope="scope">
              <el-popover placement="top"
                          trigger="hover">
                <p>专属开发者被分配给了 {{ scope.row.app_private_number }} 个应用</p>
                <p>专属开发者一共分配了 {{ scope.row.private_usable_number }} 个设备名额</p>
                <p>专属开发者已经被专属应用使用了 {{ scope.row.app_private_used_number }} 个设备名额</p>
                <div slot="reference" class="name-wrapper">
                  <el-link v-if="scope.row.app_private_number > 0" :underline="false"
                           @click="bindAppletoapp(scope.row)">
                    <el-tag size="medium">是</el-tag>
                  </el-link>
                  <el-link v-else :underline="false" @click="bindAppletoapp(scope.row)">
                    <el-tag size="medium" type="info">否</el-tag>
                  </el-link>
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
              <el-row>
                <el-col :span="18">
                  <el-input v-model="editdeveloperinfo.p8key"
                            placeholder="请填写或者上传p8key" :rows="6" type="textarea"/>
                </el-col>
                <el-col :span="6">
                  <el-upload
                      style="margin-top: 50px"
                      :before-upload="beforep8keyUpload"
                      :limit="1"
                      accept=".p8"
                      action="#"
                  >
                    <el-button size="small" type="primary">点击上传p8证书文件</el-button>
                  </el-upload>
                </el-col>
              </el-row>
            </el-form-item>
          </div>

          <el-form-item label="设备数量" label-width="110px" style="text-align: left">
            <el-input-number v-model="editdeveloperinfo.usable_number" :max="100" :min="0" label="设备数量"/>
            <el-tag style="margin-left: 10px" type="warning">该开发者可以可消耗设备数量，超过该数量，将无法进行新设备签名</el-tag>
          </el-form-item>
          <el-form-item label="应用数量" label-width="110px" style="text-align: left">
            <el-input-number v-model="editdeveloperinfo.app_limit_number" :max="160" :min="0" label="应用数量"/>
            <el-tag style="margin-left: 10px" type="warning">该开发者可以签名应用数量，超过该数量，将无法进行新应用签名</el-tag>
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
          <p>2.每个开发者账号最多可创建两本证书，请确保至少还可以创建一本证书！若您有可用的开发者证书，可将可用的p12开发证书导入使用。</p>
          <p>3.添加完成后，您可以上传p12证书或者通过系统自动创建证书、设备和描述文件，请勿删除这些文件，否则会导致用户安装的软件闪退或无法安装！</p>

        </el-card>
      </el-tab-pane>
      <el-tab-pane label="UDID管理" name="iosudevices">
        <el-input
            v-model="udidsearch"
            clearable
            placeholder="输入UDID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-input
            v-model="appidseach"
            clearable
            placeholder="输入开发者用户ID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
          搜索
        </el-button>
        <el-button @click="syncalldevices">
          同步设备信息
        </el-button>
        <el-table
            v-loading="loading"
            :data="developer_udevices_lists"
            border
            stripe
            style="width: 100%">
          <el-table-column
              align="center"
              fixed
              label="设备序列号"
              prop="serial"
              width="120"
          >
          </el-table-column>
          <el-table-column
              align="center"
              label="设备名称"
              prop="product"
              width="120">
          </el-table-column>
          <el-table-column
              align="center"
              label="设备UDID"
              prop="udid">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>该设备UDID 被分配到了 {{ scope.row.app_used_count }} 个应用</p>
                <el-button v-if="scope.row.app_used_count > 0" size="mini" @click="show_app_used_info(scope.row)">
                  点击查看分配信息
                </el-button>
                <div slot="reference" class="name-wrapper">
                  <span>{{ scope.row.udid }}</span>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="设备产品"
              prop="product"
              width="160">
          </el-table-column>
          <el-table-column
              align="center"
              label="设备版本"
              prop="version"
              width="200">
          </el-table-column>
          <el-table-column
              align="center"
              label="设备状态"
              width="110">
            <template slot-scope="scope">
              <el-tooltip v-if="!scope.row.status" content="点击启用">
                <el-link :underline="false" type="info" @click="changeDevice(scope.row,1)">
                  <el-tag type="info">禁用</el-tag>
                </el-link>
              </el-tooltip>
              <el-tooltip v-else content="点击禁用，禁用会自动清理已经安装的数据">
                <el-link :underline="false" @click="changeDevice(scope.row,0)">
                  <el-tag>启用</el-tag>
                </el-link>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="开发者ID"
              prop="developer_id"
              width="200">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>开发者ID: {{ scope.row.developer_id }}</p>
                <p>开发者备注: {{ scope.row.developer_description }}</p>
                <p>开发者状态: {{ scope.row.developer_status }}</p>
                <div slot="reference" class="name-wrapper">
                  <span>{{ scope.row.developer_id }}</span>
                </div>
              </el-popover>
            </template>
          </el-table-column>

        </el-table>


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
        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
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
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>点击下载签名后的应用包</p>
                <div slot="reference" class="name-wrapper">
                  <el-link :underline="false" @click="downloadipa(scope.row)">{{ scope.row.bundle_name }}</el-link>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="开发者ID"
              prop="developer_id"
              width="200">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>开发者ID: {{ scope.row.developer_id }}</p>
                <p>开发者备注: {{ scope.row.developer_description }}</p>
                <p>开发者状态: {{ scope.row.developer_status }}</p>
                <div slot="reference" class="name-wrapper">
                  <span>{{ scope.row.developer_id }}</span>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <!--          <el-table-column-->
          <!--              v-if="$store.state.userinfo&&$store.state.userinfo.role === 3"-->
          <!--              align="center"-->
          <!--              label="被使用户uid"-->
          <!--              prop="other_uid">-->
          <!--          </el-table-column>-->
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
            style="width: 27%;margin-right: 10px;margin-bottom: 10px"/>
        <el-input
            v-model="Bundleidsearch"
            clearable
            placeholder="输入BundleID"
            style="width: 27%;margin-right: 10px;margin-bottom: 10px"/>
        <el-input
            v-model="appidseach"
            clearable
            placeholder="输入开发者ID"
            style="width: 27%;margin-right: 10px;margin-bottom: 10px"/>
        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
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
                <p>开发者ID: {{ scope.row.issuer_id }}</p>
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
              width="100">

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

            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>设备型号: {{ scope.row.version }}</p>
                <p>设备序列号: {{ scope.row.serial }}</p>
                <div slot="reference" class="name-wrapper">
                  <span>{{ scope.row.version }}</span>
                </div>
              </el-popover>
            </template>

          </el-table-column>
          <el-table-column
              align="center"
              label="开发者ID"
              prop="issuer_id">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <p>开发者ID: {{ scope.row.issuer_id }}</p>
                <p>开发者备注: {{ scope.row.developer_description }}</p>
                <p>开发者状态: {{ scope.row.developer_status }}</p>
                <div slot="reference" class="name-wrapper">
                  <span>{{ scope.row.issuer_id }}</span>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <!--          <el-table-column-->
          <!--              v-if="$store.state.userinfo&&$store.state.userinfo.role === 3"-->
          <!--              align="center"-->
          <!--              label="被使用户uid"-->
          <!--              prop="other_uid">-->
          <!--          </el-table-column>-->
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
              width="150">
            <template slot-scope="scope">
              <div>
                <el-tooltip content="仅仅删除数据库数据，不操作苹果开发者设备" placement="top">
                  <el-button
                      size="mini"
                      type="danger"
                      @click="udidDeleteFun(scope,0)">仅删除
                  </el-button>
                </el-tooltip>
              </div>
              <div style="margin-top: 5px">
                <el-tooltip content="删除的同时，会检测并同时禁用苹果开发者设备" placement="bottom">
                  <el-button
                      size="mini"
                      type="danger"
                      @click="udidDeleteFun(scope,1)">删除并禁用设备
                  </el-button>
                </el-tooltip>
              </div>
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

        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
          搜索
        </el-button>
        <div style="width: 40%;margin-right: 30px;float:right">
          <el-link :underline="false">公共签名池设备数量：{{ balance_info.all_balance }} 已经使用：【 {{
              balance_info.used_balance
            }} 】
            还剩：【 {{ balance_info.all_balance - balance_info.used_balance }} 】 可用
          </el-link>
          <el-progress
              :color="developer_usedColor"
              :percentage="bill_percent"
              :stroke-width="18" :text-inside="true" status="success"
              type="line"/>
        </div>

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
              width="160">

          </el-table-column>
          <el-table-column
              align="center"
              label="设备版本"
              prop="version"
          >
          </el-table-column>

          <el-table-column
              align="center"
              label="次数"
              prop="counts"
              width="100">

          </el-table-column>

          <el-table-column
              align="center"
              label="设备状态"
              width="110">
            <template slot-scope="scope">
              <div v-if="scope.row.udid_sync_info_id!==null">
                <el-tag v-if="!scope.row.udid_sync_info_id" type="info">已经释放</el-tag>
                <el-tag v-else>
                  使用中
                </el-tag>
              </div>
            </template>
          </el-table-column>

        </el-table>

      </el-tab-pane>
      <el-tab-pane label="设备消耗统计" name="devicesrank">
        <el-input
            v-model="appnamesearch"
            clearable
            placeholder="输入应用名称或应用BundleID或开发者ID"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>
        <el-date-picker
            v-model="timerangesearch"
            :picker-options="pickerOptions"
            align="right"
            end-placeholder="结束日期"
            range-separator="至"
            start-placeholder="开始日期"
            style="width: 30%;margin-right: 30px;margin-bottom: 10px"
            type="daterange"
            unlink-panels
            value-format="timestamp">
        </el-date-picker>
        <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
          搜索
        </el-button>
        <el-link :underline="false" style="margin-top:10px;text-align: center;float: right"> 当前总消耗设备数 【
          {{ app_rank_number }} 】
        </el-link>
        <el-table
            v-loading="loading"
            :data="app_rank_lists"
            border
            stripe
            style="width: 100%">

          <el-table-column
              align="center"
              fixed
              label="应用名称"
              prop="name"
          >
            <template slot-scope="scope">
              <el-tooltip content="点击查看设备安装详细信息" effect="dark" placement="top">
                <el-link :underline="false" @click="show_device_uinfo(scope.row.bundle_id)">
                  {{ scope.row.name }}
                </el-link>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="应用ID"
              prop="bundle_id">

          </el-table-column>
          <el-table-column
              align="center"
              label="消耗设备数"
              prop="count"
              width="100"
          >
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

import {
  developercert,
  DeviceBillInfo,
  DeviceRankInfo,
  iosdeveloper,
  iosdevices,
  iosdevicesudid,
  iosudevices
} from "@/restful";
import {format_choices, getUserInfoFun, removeAaary} from "@/utils";
import AppleDeveloperBindApp from "@/components/base/AppleDeveloperBindApp";

export default {
  name: "FirSuperSignBase",
  components: {AppleDeveloperBindApp},
  data() {
    return {
      dialogShowDeviceBillInfo: false,
      currentudid: '',
      balance_info: {all_balance: 0, used_balance: 0},
      bill_percent: 0,
      fileList: [],
      developer_udevices_lists: [],
      app_developer_lists: [],
      app_devices_lists: [],
      app_bill_lists: [],
      app_rank_lists: [],
      app_rank_number: 0,
      app_bill_info_lists: [],
      app_udid_lists: [],
      activeName: "iosdeveloper",
      udidsearch: "",
      Bundleidsearch: "",
      appidseach: "",
      appnamesearch: "",
      timerangesearch: [],
      dialogaddDeveloperVisible: false,
      importcertDeveloperVisible: false,
      title: "",
      editdeveloperinfo: {auth_type: 0, usable_number: 100, app_limit_number: 100,p8key: ''},
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
      pickerOptions: {
        shortcuts: [{
          text: '今天',
          onClick(picker) {
            const end = new Date();
            const start = new Date();
            picker.$emit('pick', [start, end]);
          }
        }, {
          text: '最近一周',
          onClick(picker) {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
            picker.$emit('pick', [start, end]);
          }
        }, {
          text: '最近一个月',
          onClick(picker) {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
            picker.$emit('pick', [start, end]);
          }
        }, {
          text: '最近三个月',
          onClick(picker) {
            const end = new Date();
            const start = new Date();
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
            picker.$emit('pick', [start, end]);
          }
        }]
      },
      developer_options: [
        {
          value: 'private',
          label: '专属应用账户'
        }, {
          value: 'public',
          label: '公共应用账户'
        }
      ],
      developer_choice: '',
      bind_appletoapp_sure: false,
      appletoapp_title: '',
      status_choices: [],
      read_only_mode: 'off',
      developer_status_choice: [],
      multipleSelection: [],
      setdeveloperstatusVisible: false,
      change_developer_status: '',
      udeviceappinfoVisible: false,
      app_used_info_list: []
    }
  }, watch: {
    'dialogaddDeveloperVisible': function () {
      if (this.dialogaddDeveloperVisible === false) {
        this.canceledit();
      }
    }
  },
  methods: {
    changeDevice(info, disabled) {
      this.iosudevicesFun("PUT", {developer_id: info.developer_id, udid: info.udid, disabled: disabled})
    },
    show_app_used_info(info) {
      this.loading = true;
      iosdevices(data => {
        if (data.code === 1000) {
          this.app_used_info_list = data.data;
          this.udeviceappinfoVisible = true
        } else {
          this.$message.error("数据获取失败" + data.msg)
          this.app_used_info_list = [];
        }
        this.loading = false;
      }, {
        "methods": 'GET', "data": {udid: info.udid, issuer_id: info.developer_id, page: 1, size: 200}
      })
    },
    setdeveloperstatusFun() {
      if (this.multipleSelection && this.multipleSelection.length > 0) {
        this.setdeveloperstatusVisible = true
      } else {
        this.$message.warning("开发者账户未选择")
      }
    },
    setdeveloperstatus() {
      if (this.change_developer_status === '') {
        this.$message.warning("账户状态未选择")
      } else {
        this.iosdeveloperFun({
          "methods": "PUT",
          "data": {"issuer_ids": this.getIssuerIds(), "act": 'setstatus', "status": this.change_developer_status}
        });
      }
    },
    handleSelectionChange(val) {
      this.multipleSelection = val;
    },
    sort_method_usable_number(a, b) {
      return this.formatter_usable_number(a) - this.formatter_usable_number(b)
    },
    formatter_usable_number(row) {
      return row.usable_number - row.developer_used_number > 0 ? row.usable_number - row.developer_used_number : 0
    },
    format_status(status) {
      return format_choices(status, this.status_choices)
    },
    downloadipa(info) {
      this.loading = true;
      iosdevices(data => {
        if (data.code === 1000 && data.data && data.data.download_url) {
          window.location.href = data.data.download_url;
        } else {
          this.$message.error(data.msg);
        }
        this.loading = false;
      }, {
        "methods": "POST", "data": info
      })
    },
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    bindAppletoapp(developinfo) {
      if (developinfo) {
        this.editdeveloperinfo = developinfo
      }
      this.appletoapp_title = "开发者ID " + this.editdeveloperinfo.issuer_id + " 【专属账户分配之后，其他应用将无法使用该专属开发者的设备余额】";
      this.bind_appletoapp_sure = true;
    },
    disabledeveloperFun(developer, act) {
      this.$confirm('如您不再使用该开发账户进行签名，可以点击进行禁用，是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.iosdeveloperFun({"methods": "PUT", "data": {"issuer_id": developer.issuer_id, "act": act}});
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消禁用操作'
        });
      });
    },
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
    beforep8keyUpload(file){
      let reader = new FileReader(); //这是核心,读取操作就是由它完成.
      reader.readAsText(file); //读取文件的内容,也可以读取文件的URL
      // eslint-disable-next-line no-unused-vars
      reader.onload = res => {
        //当读取完成后回调这个函数,然后此时文件的内容存储到了result中,直接操作即可
        let text = reader.result;
        if(text.startsWith('-----BEGIN PRIVATE KEY')){
          this.editdeveloperinfo.p8key = reader.result.toString()
        }else {
          this.$message.warning("p8key文件不正确")
        }
      }
      return false
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
    udidDeleteFun(scope, disabled) {
      this.$confirm('此操作会禁用该苹果开发者账户下面的该设备,可能会导致超级签包的闪退, 是否继续?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.iosdevicesudidFun('DELETE', {id: scope.row.id, aid: scope.row.app_id, disabled: disabled}, scope);
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
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
    syncalldevices() {
      this.iosdeveloperFun({
        "methods": "PUT",
        "data": {"issuer_id": this.appidseach, "act": "syncalldevice"}
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
    activemanydeveloperFun() {
      let issuer_ids = this.getIssuerIds()
      if (issuer_ids.length === 0) {
        this.$message.warning("开发者账户未选择")
      } else {
        this.iosdeveloperFun({"methods": "PUT", "data": {"issuer_ids": issuer_ids, "act": 'checkauth'}});
      }
    },
    getIssuerIds() {
      let issuer_ids = []
      for (let i = 0; i < this.multipleSelection.length; i++) {
        issuer_ids.push(this.multipleSelection[i]['issuer_id'])
      }
      return issuer_ids
    },
    canceledit() {
      this.dialogaddDeveloperVisible = false;
      this.editdeveloperinfo = {auth_type: 0, usable_number: 100, app_limit_number: 100};
      this.isedit = false;
      this.placeholder = ""
    },
    handleEditDeveloper(developer_info) {
      this.editdeveloperinfo = developer_info;
      this.title = '编辑开发者账户';
      this.dialogaddDeveloperVisible = true;
      this.isedit = true;
      this.placeholder = "为空表示不修改该信息"
      if (this.editdeveloperinfo.status === 3) {
        this.read_only_mode = 'on'
      } else {
        this.read_only_mode = 'off'
      }
    },
    updateorcreate() {
      if (this.isedit) {
        this.editdeveloperinfo.read_only_mode = this.read_only_mode
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
    show_device_uinfo(bundle_id) {
      this.Bundleidsearch = bundle_id;
      this.activeName = 'useddevices'
      this.get_data_from_tabname(this.activeName);
    },
    show_device_ubill(issuer_id) {
      this.appnamesearch = issuer_id;
      this.activeName = 'devicesrank'
      this.get_data_from_tabname(this.activeName);
    },
    get_data_from_tabname(tabname, data = {}) {
      data.udid = this.udidsearch.replace(/^\s+|\s+$/g, "");
      data.bundleid = this.Bundleidsearch.replace(/^\s+|\s+$/g, "");
      data.issuer_id = this.appidseach.replace(/^\s+|\s+$/g, "");
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
        data.developer_choice = this.developer_choice;
        data.developer_status_choice = JSON.stringify(this.developer_status_choice);
        this.iosdeveloperFun({"methods": "GET", "data": data})
      } else if (tabname === "devicesbill") {
        this.iosdevicebillFun({"methods": "GET", "data": data})
      } else if (tabname === "devicesrank") {
        if (this.timerangesearch && this.timerangesearch.length === 2) {
          data.start_time = this.timerangesearch[0];
          data.end_time = this.timerangesearch[1];
        }
        data.appnamesearch = this.appnamesearch.replace(/^\s+|\s+$/g, "");
        this.iosdevicerankFun({"methods": "GET", "data": data})
      } else if (tabname === "iosudevices") {
        this.iosudevicesFun("GET", data)
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
      if (params.methods === 'PUT') {
        params.data.size = this.pagination.pagesize
        params.data.page = this.pagination.currentPage
      }
      iosdeveloper(data => {
        if (data.code === 1000) {
          if (params.methods !== 'PUT') {
            this.app_developer_lists = data.data;
            this.pagination.total = data.count;
            this.apple_auth_list = data.apple_auth_list;
            this.status_choices = data.status_choices;
            if (data.use_num) {
              this.developer_used_info = data.use_num;
              if (this.developer_used_info.all_usable_number !== 0) {
                let p = parseInt((this.developer_used_info.flyapp_used_sum + this.developer_used_info.other_used_sum) * 100 / this.developer_used_info.all_usable_number);
                if (p < 0 || p >= 100) {
                  p = 100
                }
                this.percentage = p;
              }
            }
          }
          if (params.methods === 'PUT') {
            this.$message.success("操作成功");
          }
          if (params.data.act === 'setstatus') {
            this.setdeveloperstatusVisible = false
            this.change_developer_status = ''
          }
          if (this.dialogaddDeveloperVisible) {
            this.canceledit();
            this.$message.success("操作成功");
            this.activeName = "iosdeveloper";
            this.editdeveloperinfo = {auth_type: 0, usable_number: 100, app_limit_number: 100};
          }
          if (params.methods === 'POST') {
            this.$message.success("添加成功");
            this.activeName = "iosdeveloper";
            this.editdeveloperinfo = {auth_type: 0, usable_number: 100, app_limit_number: 100};
          }
        } else if (data.code === 1008) {
          this.$message.error(data.msg);
        } else {
          this.$message.error("操作失败")
        }
        if (params.methods === 'PUT' || params.methods === 'DELETE') {
          this.get_data_from_tabname(this.activeName, {
            "size": this.pagination.pagesize,
            "page": this.pagination.currentPage
          })
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
            if (data.balance_info) {
              this.balance_info = data.balance_info;
              if (this.balance_info.all_balance - this.balance_info.used_balance === 0) {
                if (this.balance_info.all_balance === 0) {
                  this.bill_percent = 0;
                } else {
                  this.bill_percent = 100;
                }
              } else {
                if (this.balance_info.all_balance - this.balance_info.used_balance < 0) {
                  this.bill_percent = 100;
                } else {
                  this.bill_percent = parseInt(this.balance_info.used_balance * 100 / this.balance_info.all_balance);
                }
              }
            }
          }
        } else {
          this.$message.error("操作失败了 " + data.msg);
        }
        this.loading = false
      }, params)
    },
    iosdevicerankFun(params) {
      this.loading = true;
      DeviceRankInfo(data => {
        if (data.code === 1000) {
          this.app_rank_lists = data.data;
          this.pagination.total = data.count;
          this.app_rank_number = data.number
        } else {
          this.$message.error("信息获取失败了 " + data.msg);
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
    iosudevicesFun(action, data) {
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
      iosudevices(data => {
        if (data.code === 1000) {
          if (action !== "PUT") {
            this.developer_udevices_lists = data.data;
            this.pagination.total = data.count;
          } else {
            this.get_data_from_tabname(this.activeName, {
              "size": this.pagination.pagesize,
              "page": this.pagination.currentPage
            })
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
          let appidseach = this.$route.query.appidseach;
          if (bundleid) {
            this.Bundleidsearch = bundleid;
          }
          if (appidseach) {
            this.appidseach = appidseach;
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
  width: 1188px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}

</style>
