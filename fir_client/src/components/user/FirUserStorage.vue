<template>
  <el-main>
    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :title="title"
               :visible.sync="dialogstorageVisible">

      <el-form v-if="editstorageinfo.id !==-1" ref="storageinfoform" :model="editstorageinfo"
               label-width="80px" style="margin:0 auto;">
        <el-form-item label="存储类型" label-width="100px">
          <el-select v-model="editstorageinfo.storage_type" :disabled='disabled' placeholder="存储类型"
                     style="margin-left: -100px">
            <el-option v-for="st in storage_list" :key="st.id" :label="st.name" :value="st.id"/>
          </el-select>
        </el-form-item>

        <div v-if="editstorageinfo.storage_type">
          <el-form-item label="存储名称" label-width="110px">
            <el-input v-model="editstorageinfo.name" :disabled='disabled'/>
          </el-form-item>

          <el-form-item label="key" label-width="110px">
            <el-input v-model="editstorageinfo.access_key" :disabled='disabled'/>
          </el-form-item>
          <el-form-item label="secret" label-width="110px">
            <el-input v-model="editstorageinfo.secret_key" :disabled='disabled' placeholder="为空表示不修改该信息"/>
          </el-form-item>

          <el-form-item label="bucket_name" label-width="110px">
            <el-input v-model="editstorageinfo.bucket_name" :disabled='disabled'/>
          </el-form-item>
          <el-form-item label="下载域名" label-width="110px">
            <el-input v-model="editstorageinfo.domain_name" :disabled='disabled'/>
          </el-form-item>

          <div v-if="editstorageinfo.storage_type === 2">
            <el-form-item label="sts_role_arn" label-width="110px">
              <el-input v-model="editstorageinfo.sts_role_arn"
                        :disabled='disabled'/>
            </el-form-item>

            <el-form-item label="endpoint" label-width="110px">
              <el-select v-model="editstorageinfo.endpoint"
                         :disabled='disabled'
                         placeholder="下载授权方式"
                         style="width: 100%">
                <el-option v-for="st in endpoint_list" :key="st.id"
                           :label="st.name"
                           :value="st.id"/>
              </el-select>
            </el-form-item>

            <el-form-item label="下载授权方式" label-width="110px">
              <el-select v-model="editstorageinfo.download_auth_type"
                         :disabled="disabled"
                         placeholder="下载授权方式" style="width: 80%">
                <el-option v-for="st in editstorageinfo.download_auth_type_choices" :key="st.id"
                           :label="st.name"
                           :value="st.id"/>
              </el-select>

              <el-form-item v-if="editstorageinfo.download_auth_type === 2" label="CDN鉴权主KEY"
                            label-width="120px"
                            style="margin-top: 10px;margin-left: 70px;width: 60%">
                <el-input v-model="editstorageinfo.cnd_auth_key" :disabled='disabled'
                          placeholder="CDN鉴权主KEY"/>
              </el-form-item>

            </el-form-item>

          </div>
          <el-form-item label="存储最大容量" label-width="110px">

            <el-row :gutter="24" style="text-align: left">
              <el-col :span="10">
                <el-input-number v-model="editstorageinfo.max_storage_capacity" :disabled='disabled' :max="999999999"
                                 :min="200"
                                 :step="200">
                </el-input-number>
              </el-col>
              <el-col :span="10">
                <el-tag style="margin-left: 10px">存储空间最大容量
                  {{ diskSize(editstorageinfo.max_storage_capacity * 1024 * 1024) }}
                </el-tag>
              </el-col>
            </el-row>

          </el-form-item>
          <el-form-item label="备注" label-width="110px">
            <el-input v-model="editstorageinfo.description" :disabled='disabled'/>
          </el-form-item>

          <el-button v-if="!disabled" @click="updateorcreate">保存</el-button>
          <el-button v-if="!disabled" @click="dialogstorageVisible=false">取消</el-button>

        </div>
      </el-form>
    </el-dialog>
    <el-dialog
        :visible.sync="showshareSync"
        title="存储详细信息"
        width="600px">

      <el-table
          :data="showshareList"
          border
          stripe
          style="width: 100%">

        <el-table-column
            align="center"
            fixed
            label="存储ID"
            prop="storage_id"
            width="100px">
        </el-table-column>
        <el-table-column
            align="center"
            label="存储名称"
            prop="storage_name">
        </el-table-column>
        <el-table-column
            align="center"
            label="存储大小"
            prop="number"
            width="110px">
          <template slot-scope="scope">
            {{ diskSize(scope.row.number) }}
          </template>
        </el-table-column>
      </el-table>

      <span slot="footer" class="dialog-footer">
            <el-button @click="showshareSync = false">取消</el-button>
        </span>
    </el-dialog>
    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :visible.sync="shareVisible"
               style="text-align:center" title="存储共享" width="700px">
      <el-tag style="margin: 0 auto 20px">存储共享指的是 将您的私有存储共享给目标用户使用</el-tag>
      <el-form label-width="30%">
        <el-form-item label="目标用户UID" style="width: 80%">
          <el-row :gutter="24">
            <el-col :span="19">
              <el-input v-model="target_uid" clearable/>
            </el-col>
            <el-col :span="4">
              <el-button @click="checkuid(target_uid)">查询校验</el-button>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item v-if="shareInfo.uid" label="目标用户信息" style="width: 80%;text-align: left">
          <el-row :gutter="24">
            <el-col :span="22">
              <el-tag> 用户昵称: {{ shareInfo.name }}</el-tag>
              <el-tag style="margin-left: 10px"> 共享存储大小: {{ diskSize(shareInfo.number) }}</el-tag>
            </el-col>
          </el-row>
          <el-col :span="24">
            <el-link :underline="false" @click="showshareSync=true">共
              <el-tag>{{ showshareList.length }}</el-tag>
              个私有存储被共享，点击查看详情
            </el-link>
          </el-col>
        </el-form-item>
        <el-form-item label="共享存储大小" style="width: 80%;text-align: left">
          <el-row :gutter="24">
            <el-col :span="10">
              <el-input-number v-model="target_number" :max="999999999" :min="200" :step="200">
              </el-input-number>
            </el-col>
            <el-col :span="13">
              <el-tag style="margin-left: 30px">共享目标用户存储空间 {{ target_number }}MB</el-tag>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="私有存储节点" style="width: 80%;text-align: left">
          <el-select v-model="use_storage_id" :placeholder="selectlabel" filterable style="width: 400px"
                     @change="select_storage">
            <el-option-group
                v-for="storage_group in fstorage_lists"
                :key="storage_group.group_name"
                :label="storage_group.group_name">
              <el-option
                  v-for="storage in storage_group.storages"
                  :key="storage.id"
                  :label="format_s_name(storage)"
                  :value="storage.id">
              </el-option>
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-button :disabled="canshare" @click="sureShareFun(target_uid,target_number, use_storage_id)">确定共享</el-button>
        <el-button @click="shareVisible=false">取消</el-button>
      </el-form>
    </el-dialog>

    <el-tabs v-model="activeName" tab-position="top" type="border-card" @tab-click="handleClick">
      <el-tab-pane label="存储选择" name="change">'
        <el-row :gutter="24">
          <el-col :span="14">
            存储选择：
            <el-select v-model="use_storage_id" :placeholder="selectlabel" filterable style="width: 400px"
                       @change="select_storage">
              <el-option-group
                  v-for="storage_group in fstorage_lists"
                  :key="storage_group.group_name"
                  :label="storage_group.group_name">
                <el-option
                    v-for="storage in storage_group.storages"
                    :key="storage.id"
                    :label="format_s_name(storage)"
                    :value="storage.id">
                </el-option>
              </el-option-group>
            </el-select>
          </el-col>
          <el-col :span="10">
            <el-popover
                placement="top-start"
                trigger="hover">
              <div>
                <el-link :underline="false">存储最大容量空间： {{ diskSize(storageinfo.max_storage_capacity) }}</el-link>
                <el-link :underline="false">已经使用容量： {{ diskSize(storageinfo.used_number) }}</el-link>
                <el-link :underline="false">当前可用容量：
                  {{ diskSize(storageinfo.max_storage_capacity - storageinfo.used_number) }}
                </el-link>
              </div>
              <el-link slot="reference" :underline="false" style="font-size: small">
                还剩：{{ diskSize(storageinfo.max_storage_capacity - storageinfo.used_number) }} 可用
              </el-link>
            </el-popover>
            <el-progress
                :color="storage_usedColor"
                :percentage="percentage"
                :stroke-width="16"
                :text-inside="true" status="success" style="width: 80%"
                type="line"/>
          </el-col>
        </el-row>


        <div v-if="use_storage_id!==org_storage_id" style="margin-top: 20px">
          <el-button style="margin-left: 10px"
                     type="info"
                     @click="change_storage_info(0)">
            迁移数据并保存
          </el-button>
          <el-button style="margin-left: 10px"
                     type="danger"
                     @click="change_storage_info(1)">
            强制迁移，忽略数据迁移失败错误，可能会导致数据丢失
          </el-button>
        </div>
        <div v-else style="margin-top: 20px">
          <!--          <el-button round style="margin-left: 10px"-->
          <!--                     type="danger"-->
          <!--                     @click="clean_storage_data('all')">-->
          <!--            清理所有app数据-->
          <!--          </el-button>-->
          <!--          <el-button round style="margin-left: 10px"-->
          <!--                     type="danger"-->
          <!--                     @click="clean_storage_data('history')">-->
          <!--            清理app历史版本数据，只保留最新数据-->
          <!--          </el-button>-->
        </div>
        <el-divider/>
        <el-form ref="storageinfoform" :model="storageinfo"
                 label-width="80px" style="width: 50%;margin:0 auto;">

          <el-form-item label="存储最大容量" label-width="110px" style="text-align: left">
            <el-tag>存储最大容量空间 {{ diskSize(storageinfo.max_storage_capacity) }}</el-tag>
          </el-form-item>
          <el-form-item label="已经使用容量" label-width="110px" style="text-align: left">
            <el-tag>存储已经使用容量空间 {{ diskSize(storageinfo.used_number) }}
              可用容量{{ diskSize(storageinfo.max_storage_capacity - storageinfo.used_number) }}
            </el-tag>
          </el-form-item>
          <div v-if="storageinfo.id && storageinfo.id !==-1">
            <el-divider/>
            <el-form-item label="存储类型" label-width="110px">
              <el-select v-model="storageinfo.storage_type" :disabled='Sdisabled' placeholder="存储类型"
                         style="margin-left: -60px">
                <el-option v-for="st in storage_list" :key="st.id" :label="st.name"
                           :value="st.id"/>
              </el-select>
            </el-form-item>

            <div v-if="storageinfo.storage_type">

              <el-form-item label="存储名称" label-width="110px">
                <el-input v-model="storageinfo.name" :disabled='Sdisabled'/>
              </el-form-item>

              <el-form-item label="key" label-width="110px">
                <el-input v-model="storageinfo.access_key" :disabled='Sdisabled'/>
              </el-form-item>
              <el-form-item label="bucket_name" label-width="110px">
                <el-input v-model="storageinfo.bucket_name" :disabled='Sdisabled'/>
              </el-form-item>
              <el-form-item label="下载域名" label-width="110px">
                <el-input v-model="storageinfo.domain_name" :disabled='Sdisabled'/>
              </el-form-item>

              <div v-if="storageinfo.storage_type === 2">
                <el-form-item label="sts_role_arn" label-width="110px">
                  <el-input v-model="storageinfo.sts_role_arn"
                            :disabled='Sdisabled'/>
                </el-form-item>

                <el-form-item label="endpoint" label-width="110px">
                  <el-input v-model="storageinfo.endpoint"
                            :disabled='Sdisabled'/>
                </el-form-item>

                <el-form-item label="下载授权方式" label-width="110px">
                  <el-select v-model="storageinfo.download_auth_type"
                             :disabled="disabled"
                             placeholder="下载授权方式" style="width: 100%">
                    <el-option v-for="st in storageinfo.download_auth_type_choices" :key="st.id"
                               :label="st.name"
                               :value="st.id"/>
                  </el-select>

                  <el-form-item v-if="storageinfo.download_auth_type === 2" label="CDN鉴权主KEY" label-width="120px"
                                style="margin-top: 10px;width: 100%">
                    <el-input v-model="storageinfo.cnd_auth_key" :disabled='disabled'
                              placeholder="CDN鉴权主KEY"/>
                  </el-form-item>

                </el-form-item>

              </div>
              <el-form-item label="备注" label-width="110px">
                <el-input v-model="storageinfo.description" :disabled='Sdisabled'/>
              </el-form-item>

            </div>
          </div>

        </el-form>

      </el-tab-pane>
      <el-tab-pane label="存储管理" name="edit">
        <div style="text-align: left">
          <el-input
              v-model="keysearch"
              clearable
              placeholder="输入存储名称或bucket_name进行搜索"
              style="width: 40%;margin-right: 30px;margin-bottom: 10px"/>

          <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
            搜索
          </el-button>
        </div>
        <el-table
            v-loading="loading"
            :data="storage_info_lists"
            border
            stripe
            style="width: 100%">
          <el-table-column
              align="center"
              fixed
              label="存储名称"
              prop="name"
              width="160">
          </el-table-column>
          <el-table-column
              align="center"
              label="存储类型"
              prop="storage_type_display"
              width="100">
          </el-table-column>
          <el-table-column
              align="center"
              label="共享数量"
              prop="shared"
              width="80">
            <template slot-scope="scope">
              <span v-if="scope.row.shared===0">未共享</span>
              <el-link v-else :underline="false">
                <el-tag @click="showshareinfo(scope.row.name)">{{ scope.row.shared }}</el-tag>
              </el-link>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="使用数量"
              prop="used"
              width="80">
            <template slot-scope="scope">
              <span v-if="scope.row.used===0 && scope.row.shared===0">未使用</span>
              <el-tag v-else>{{ scope.row.used }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column
              align="center"
              label="已用空间"
              prop="used_number"
              width="100">
            <template slot-scope="scope">
              <span>{{ diskSize(scope.row.used_number) }}</span>
            </template>
          </el-table-column>

          <el-table-column
              align="center"
              label="可用空间"
              prop="used_number"
              width="100">
            <template slot-scope="scope">
              <span>{{ diskSize(scope.row.max_storage_capacity - scope.row.used_number) }}</span>
            </template>
          </el-table-column>

          <el-table-column
              align="center"
              label="下载域名"
              prop="domain_name">
          </el-table-column>
          <el-table-column
              align="center"
              label="bucket_name"
              prop="bucket_name"
              width="130">
          </el-table-column>
          <el-table-column
              :formatter="formatter"
              align="center"
              label="修改时间"
              prop="updated_time"
              width="100">
          </el-table-column>
          <el-table-column
              align="center"
              fixed="right"
              label="操作"
              width="150">
            <template slot-scope="scope">
              <div v-if="scope.row.id === org_storage_id">
                <el-button-group>
                  <el-button v-if="scope.row.id === org_storage_id" size="mini"
                             type="success" @click="showstorage(scope.row)">使用中
                  </el-button>
                  <el-button size="mini" type="primary" @click="editstorage(scope.row)">编辑</el-button>
                </el-button-group>
              </div>
              <div v-else>
                <el-button size="small" type="text" @click="showstorage(scope.row)">查看</el-button>
                <el-button size="small" type="text" @click="editstorage(scope.row)">编辑</el-button>
                <el-button size="small" type="text" @click="del_storage_info(scope.row)">删除</el-button>
              </div>

            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="存储新增" name="add">
        <el-form ref="storageinfoform" :model="editstorageinfo"
                 label-width="80px" style="margin:0 auto;">
          <el-form-item label="存储类型" label-width="100px">
            <el-select v-model="editstorageinfo.storage_type" placeholder="存储类型"
                       style="margin-left: -100px">
              <el-option v-for="st in storage_list" :key="st.id" :label="st.name"
                         :value="st.id"/>
            </el-select>
          </el-form-item>

          <div v-if="editstorageinfo.storage_type">
            <el-form-item label="存储名称" label-width="110px">
              <el-input v-model="editstorageinfo.name" clearable/>
            </el-form-item>

            <el-form-item label="key" label-width="110px">
              <el-input v-model="editstorageinfo.access_key" clearable/>
            </el-form-item>
            <el-form-item label="secret" label-width="110px">
              <el-input v-model="editstorageinfo.secret_key" clearable/>
            </el-form-item>

            <el-form-item label="bucket_name" label-width="110px">
              <el-input v-model="editstorageinfo.bucket_name" clearable/>
            </el-form-item>
            <el-form-item label="下载域名" label-width="110px">
              <el-input v-model="editstorageinfo.domain_name" clearable
                        placeholder="若下载授权方式为CDN，则需要填写CDN的域名，否则填写Bucket外网访问域名"/>
            </el-form-item>

            <div v-if="editstorageinfo.storage_type === 2">
              <el-form-item label="sts_role_arn" label-width="110px">
                <el-input
                    v-model="editstorageinfo.sts_role_arn" clearable/>
              </el-form-item>

              <el-form-item label="endpoint" label-width="110px">

                <el-select v-model="editstorageinfo.endpoint"
                           placeholder="下载授权方式"
                           style="width: 100%">
                  <el-option v-for="st in endpoint_list" :key="st.id"
                             :label="st.name"
                             :value="st.id"/>
                </el-select>

              </el-form-item>

              <el-form-item label="下载授权方式" label-width="110px">
                <el-select v-model="editstorageinfo.download_auth_type"
                           placeholder="下载授权方式"
                           style="width: 100%">
                  <el-option v-for="st in editstorageinfo.download_auth_type_choices" :key="st.id"
                             :label="st.name"
                             :value="st.id"/>
                </el-select>

                <el-form-item v-if="editstorageinfo.download_auth_type === 2" label="CDN鉴权主KEY"
                              label-width="120px"
                              style="margin-top: 10px;margin-left: 70px;width: 60%">
                  <el-input v-model="editstorageinfo.cnd_auth_key"
                            clearable placeholder="CDN鉴权主KEY"/>
                </el-form-item>

              </el-form-item>
              <el-form-item label="存储最大容量" label-width="110px">

                <el-row :gutter="24" style="text-align: left">
                  <el-col :span="6">
                    <el-input-number v-model="editstorageinfo.max_storage_capacity" :max="999999999" :min="200"
                                     :step="200">
                    </el-input-number>
                  </el-col>
                  <el-col :span="6">
                    <el-tag style="margin-left: 30px">存储空间最大容量
                      {{ diskSize(editstorageinfo.max_storage_capacity * 1024 * 1024) }}
                    </el-tag>
                  </el-col>
                </el-row>

              </el-form-item>

            </div>

            <el-form-item label="备注" label-width="110px">
              <el-input v-model="editstorageinfo.description" clearable/>
            </el-form-item>

            <el-button @click="updateorcreate">校验并保存</el-button>
          </div>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="存储共享" name="share">
        <div style="text-align: left">
          <el-input
              v-model="uidsearch"
              clearable
              placeholder="输入用户UID或存储名称进行搜索"
              style="width: 40%;margin-right: 30px;margin-bottom: 10px"/>
          <el-select v-model="operatestatus" clearable placeholder="操作状态"
                     style="width: 120px;margin-right: 20px" @change="handleCurrentChange(1)">
            <el-option v-for="item in operate_status_choices" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
            搜索
          </el-button>
          <el-button icon="el-icon-s-unfold" plain @click="shareStorage(undefined)">
            存储共享
          </el-button>
        </div>

        <el-table
            v-loading="loading"
            :data="share_bill_lists"
            border
            stripe
            style="width: 100%">

          <el-table-column
              align="center"
              fixed
              label="目标用户UID">
            <template slot-scope="scope">
              <el-popover placement="top" trigger="hover">
                <el-tooltip content="点击复制到剪贴板">
                  <el-link v-clipboard:copy="scope.row.target_user.uid"
                           v-clipboard:success="copy_success"
                           :underline="false">用户UID: {{ scope.row.target_user.uid }}
                  </el-link>
                </el-tooltip>
                <p>用户昵称: {{ scope.row.target_user.name }}</p>
                <el-tag v-if="scope.row.used">该共享存储已经被使用中</el-tag>
                <div slot="reference" class="name-wrapper">
                  <span v-if="scope.row.used" style="color: #1f4cee">{{ scope.row.target_user.uid }}</span>
                  <span v-else>{{ scope.row.target_user.uid }}</span>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="状态"
              prop="status_display"
              width="100">

          </el-table-column>
          <el-table-column
              align="center"
              label="共享存储大小"
              prop="number"
              width="120">
            <template slot-scope="scope">
              <el-popover content="点击修改共享存储大小" trigger="hover">
                <el-link slot="reference" :underline="false" @click="editShareStorage(scope.row)">
                  <span v-if="scope.row.cancel">-</span> {{ diskSize(scope.row.number) }}
                </el-link>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="共享存储名称"
              prop="storage_name"
              width="120">
            <template slot-scope="scope">
              <el-link :underline="false" @click="showstorageInfo(scope.row)">{{ scope.row.storage_name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="日期"
              prop="created_time"
              width="160">
            <template slot-scope="scope">
              {{ format_time(scope.row.created_time) }}
            </template>
          </el-table-column>

          <el-table-column
              align="center"
              label="备注"
              prop="description">
          </el-table-column>

          <el-table-column
              align="center"
              fixed="right"
              label="操作"
              width="100">
            <template slot-scope="scope">
              <div v-if="scope.row.cancel">
                <el-tooltip v-if="scope.row.status===1" content="点击撤回共享存储，并清理目标用户存储数据" placement="top">
                  <el-tag type="success" @click="cleanshare(scope.row)">成功</el-tag>
                </el-tooltip>
                <el-tag v-else-if="scope.row.status === 2" type="info">已撤回</el-tag>
                <el-tag v-else>状态异常</el-tag>
              </div>

              <div v-else>
                <el-tooltip v-if="scope.row.status !== 2" content="生效中" placement="top">
                  <el-tag>生效中</el-tag>
                </el-tooltip>
                <el-tag v-else type="info">失效</el-tag>
              </div>
            </template>
          </el-table-column>


        </el-table>
      </el-tab-pane>
      <el-tab-pane label="存储设置" name="setting" style="text-align: center">
        <el-tag style="margin: 20px 0"> 应用版本数设置，当应用历史版本超过该限制，将会自动清理较老的版本</el-tag>
        <div style="margin: auto;width: 700px;height: 100%">
          <el-form ref="form" :model="storage_config" label-width="180px">
            <el-form-item label="应用历史版本数" style="text-align: left">
              <el-input-number v-model="storage_config.user_history_limit" :min="1"
                               style="width: 300px;margin: 0 10px"></el-input-number>
              <el-button @click="updateConfig('update')">保存修改</el-button>
            </el-form-item>
            <el-form-item label="当前存储空间大小" style="text-align: left">
              <el-tag>{{ diskSize(storage_config.user_max_storage_capacity) }}</el-tag>
              已经使用
              <el-tag>{{ diskSize(storage_config.user_used_storage_capacity) }}</el-tag>
              还剩
              <el-tag>
                {{ diskSize(storage_config.user_max_storage_capacity - storage_config.user_used_storage_capacity) }}
              </el-tag>
            </el-form-item>


            <el-form-item label="存储迁移状态" style="text-align: left">
              <el-tag v-if="!storage_config.storage_status">未迁移，状态正常</el-tag>
              <div v-else>
                <el-tag>迁移中，迁移时间 {{ getFormatDate(storage_config.storage_status) }}</el-tag>
                <el-tag type="warning">若存储状态长时间处于迁移中，可能是迁移卡死了，可以尝试
                  <el-button plain size="mini" type="text" @click="cancelStorage">解除迁移锁</el-button>
                  进行解除
                </el-tag>
              </div>
            </el-form-item>
            <el-form-item label="清理所有应用数据" style="text-align: left">
              <el-button style="margin-left: 10px"
                         type="danger"
                         @click="clean_storage_data('all')">
                清理所有应用数据
              </el-button>
            </el-form-item>
            <el-form-item label="清理应用历史数据" style="text-align: left">
              <el-button style="margin-left: 10px"
                         type="danger"
                         @click="clean_storage_data('history')">
                清理应用历史版本数据，只保留最新版本数据
              </el-button>
            </el-form-item>
          </el-form>
        </div>

      </el-tab-pane>

      <div v-if="activeName!== 'change' && activeName!== 'add'&& activeName!== 'setting'" style="margin-top: 20px">
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
import {cleanStorageData, configStorageData, getStorageinfo, shareStorageData} from "@/restful";
import {deepCopy, diskSize, getFormatDate, getUserInfoFun} from "@/utils";
import {format_time} from "@/utils/base/utils";

export default {
  name: "FirUserStorage",
  data() {
    return {
      pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
      target_uid: '',
      shareInfo: '',
      storage_config: {
        'user_history_limit': 0,
        'user_max_storage_capacity': 0,
        'user_used_storage_capacity': 0,
        'storage_status': 0
      },
      target_number: '',
      fstorage_lists: [],
      share_bill_lists: [],
      Sdisabled: true,
      canshare: true,
      use_storage_id: 0,
      org_storage_id: 0,
      title: '',
      uidsearch: '',
      keysearch: '',
      operatestatus: '',
      dialogstorageVisible: false,
      editstorageinfo: {},
      selectlabel: "",
      storageinfo: {'used_number': 0, 'max_storage_capacity': 1},
      storage_list: [],
      endpoint_list: [],
      disabled: true,
      isaddflag: false,
      shareVisible: false,
      showshareSync: false,
      activeName: 'change',
      storage_info_lists: [],
      showshareList: [],
      operate_status_choices: [],
      loading: false,
    }
  }, methods: {
    format_time,
    diskSize,
    getFormatDate,
    cancelStorage() {

      this.$confirm("确定要解除迁移锁么，在未完成迁移状态下解除迁移锁之后，可能会导致数据异常?", '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        configStorageData(res => {
          if (res.code === 1000) {
            this.$message.success("操作成功")
            this.refreshactiveFun()
          } else {
            this.$message.error("操作失败了，" + res.msg)
          }
        }, {"methods": "POST", "data": this.storage_config})
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消撤回操作'
        });
      });
    },
    storage_usedColor(percentage) {
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
    updateConfig() {
      const loading = this.$loading({
        lock: true,
        text: '执行中,请耐心等待...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      configStorageData(res => {
        loading.close()
        if (res.code === 1000) {
          this.$message.success("操作成功")
          this.refreshactiveFun()
        } else {
          this.$message.error("操作失败了，" + res.msg)
        }
      }, {"methods": "PUT", "data": this.storage_config})
    },
    formatStorageId() {
      if (this.activeName === 'share') {
        for (let i = 0; i < this.fstorage_lists.length; i++) {
          for (let j = 0; j < this.fstorage_lists[i]['storages'].length; j++) {
            let storage = this.fstorage_lists[i]['storages'][j]
            if (storage.id !== -1) {
              this.use_storage_id = storage.id
              return
            }
          }
        }
      }
      this.use_storage_id = ""
    },
    shareStorage(row) {
      getStorageinfo(data => {
        if (data.code === 1000) {
          this.fstorage_lists = data.storage_group_list;
          this.storage_list = data.storage_list;
          if (row) {
            this.use_storage_id = row.storage_id;
          } else {
            this.use_storage_id = data.storage;
            this.formatStorageId()
          }
          if (row && row.target_user) {
            this.target_uid = row.target_user.uid
            this.checkuid(this.target_uid)
            this.target_number = parseInt(row.number / 1024 / 1024)
          }
          this.shareVisible = true;
        } else {
          this.$message.error('存储类别获取失败,' + data.msg);
        }
      }, {"methods": 'GET', "data": {'act': 'storage_group', 'is_default': false}});
    },
    editShareStorage(row) {
      // if (row.status !== 1) return
      if (!row.cancel) return
      this.shareStorage(row)
    },
    showshareinfo(name) {
      this.uidsearch = name
      this.activeName = 'share'
      this.refreshactiveFun()
    },
    format_s_name(storage) {
      if (storage.ext && storage.ext.username) {
        return '共享存储-' + storage.name + '-' + storage.ext.username
      }
      if (storage.ext && storage.ext.share_count) {
        return `${storage.name}-已共享给${storage.ext.share_count}个用户，有效用户${storage.ext.share_used}个`
      } else {
        return storage.name
      }
    },
    showstorageInfo(row) {
      getStorageinfo(data => {
        if (data.code === 1000) {
          if (data.data.length === 1) {
            this.showstorage(data.data[0])
            this.storage_list = data.storage_list
          }
        } else {
          this.$message.error('存储信息获取失败,' + data.msg);
        }
        this.loading = false;
      }, {"methods": 'GET', 'data': {'pk': row.storage_id}});
    },
    cleanshare(rowinfo) {
      this.$confirm("确定要撤回么，撤回之后，会清理对方账户已经分配的储存，并删除对方账号所有应用数据?", '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loadingobj = this.$loading({
          lock: true,
          text: '操作中，请耐心等待',
          spinner: 'el-icon-loading',
          // background: 'rgba(0, 0, 0, 0.7)'
        });
        shareStorageData(data => {
          loadingobj.close()
          if (data.code === 1000) {
            this.$message.success("操作成功")
            this.refreshactiveFun()
          } else {
            this.$message.error("操作失败 " + data.msg)
          }
        }, {
          'methods': 'DELETE',
          data: {uid: rowinfo.target_user.uid, status: rowinfo.status, number: rowinfo.number, sid: rowinfo.storage_id}
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消撤回操作'
        });
      });
    },
    sureShareFun(target_uid, target_number, target_sid) {
      shareStorageData(data => {
        if (data.code === 1000) {
          this.$message.success("操作成功")
          this.shareVisible = false;
          this.refreshactiveFun()
        } else {
          this.$message.error('操作失败了,' + data.msg)
        }
      }, {
        'methods': 'POST', data: {target_uid, target_number, target_sid}
      })
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
      this.refreshactiveFun()
    },
    refreshactiveFun() {
      this.get_data_from_tabname(this.activeName, {
        "size": this.pagination.pagesize,
        "page": this.pagination.currentPage
      })
    },
    getSizeFromId() {
      for (let i = 0; i < this.showshareList.length; i++) {
        if (this.use_storage_id === this.showshareList[i].storage_id) return this.showshareList[i].number
      }
      return 200 * 1024 * 1024
    },
    checkuid(uid) {
      shareStorageData(data => {
        if (data.code === 1000) {
          this.shareInfo = data.data
          this.showshareList = this.shareInfo.info_list
          this.target_number = parseInt(this.getSizeFromId() / 1024 / 1024)
          this.canshare = false
        } else {
          this.shareInfo = {}
          this.canshare = true
          this.$message.error("查询失败 " + data.msg)
        }
      }, {'methods': 'PUT', data: {uid: uid}})
    },
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    getStorageGroup() {
      getStorageinfo(data => {
        if (data.code === 1000) {
          this.fstorage_lists = data.storage_group_list;
          this.org_storage_id = this.use_storage_id = data.storage;
          this.storage_list = data.storage_list;
          this.getstorageinfobyid(this.use_storage_id)
        } else {
          this.$message.error('存储类别获取失败,' + data.msg);
        }
      }, {"methods": 'GET', "data": {'act': 'storage_group'}});
    },
    showstorage(editstorageinfo) {
      this.title = '查看存储信息';
      this.disabled = true;
      this.dialogstorageVisible = true;
      this.editstorageinfo = deepCopy(editstorageinfo);
      this.editstorageinfo.max_storage_capacity = parseInt(this.editstorageinfo.max_storage_capacity / 1024 / 1024)
    },
    editstorage(editstorageinfo) {
      this.title = '存储编辑';
      this.disabled = false;
      this.dialogstorageVisible = true;
      this.editstorageinfo = deepCopy(editstorageinfo);
      this.editstorageinfo.max_storage_capacity = parseInt(this.editstorageinfo.max_storage_capacity / 1024 / 1024)
      this.isaddflag = false;
    },
    // eslint-disable-next-line no-unused-vars
    handleClick(tab, event) {
      this.get_data_from_tabname(tab.name);
    },
    updateorcreate() {
      let methods = "PUT";
      if (this.isaddflag) {
        if (this.editstorageinfo.access_key && this.editstorageinfo.secret_key && this.editstorageinfo.bucket_name) {
          methods = "POST";
        } else {
          this.$message.error("参数不正确");
          return
        }
      }
      this.editstorageinfo.storage_capacity = this.editstorageinfo.max_storage_capacity
      getStorageinfo(data => {
        if (data.code === 1000) {
          this.$message.success('操作成功');
          this.dialogstorageVisible = false;
          if (this.isaddflag) {
            this.activeName = 'edit';
          }
          this.get_data_from_tabname(this.activeName);

        } else {
          this.$message.error('操作失败，' + data.msg);
        }
      }, {"methods": methods, 'data': this.editstorageinfo});
    }, del_storage_info(sinfo) {

      this.$confirm('此操作可能会导致程序异常, 是否继续?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        getStorageinfo(data => {
          if (data.code === 1000) {
            this.$message.success('删除成功');
            this.refreshactiveFun();
          }
        }, {"methods": 'DELETE', 'data': {'id': sinfo.id, 'tid': sinfo.storage_type}})
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });

    },
    validFun(val) {
      return val && val.length > 6;
    },
    clean_storage_data(act) {

      this.$prompt('此操作属于危险操作，请悉知你操作将导致的影响，输入登录密码进行确认该操作', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '该用户的登录密码',
        inputValidator: this.validFun
      }).then(({value}) => {
        const loading = this.$loading({
          lock: true,
          text: '执行中,请耐心等待...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
        cleanStorageData(data => {
          loading.close();
          if (data.code === 1000) {
            this.$message.success('清理成功');
            this.refreshactiveFun();
          } else {
            this.$message.error(data.msg)
          }
        }, {"methods": 'POST', 'data': {'act': act, 'confirm_pwd': value}});

      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        });
      });
    },
    change_storage_info(force) {
      this.$confirm('此操作将导致应用，图片，显示下载异常, 是否继续?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({
          lock: true,
          text: '执行中,请耐心等待...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
        getStorageinfo(data => {
          loading.close();
          if (data.code === 1000) {
            this.$message.success('修改成功');
            this.getStorageGroup();
          } else {
            this.$message.error(data.msg)
          }
        }, {"methods": 'PUT', 'data': {'use_storage_id': this.use_storage_id, 'force': force}});
        this.getStorageGroup();
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        });
      });
    },
    select_storage(a) {
      this.disabled = true;
      this.getstorageinfobyid(a);
    },
    getstorageinfobyid(id) {
      // if (id === -1) {
      //   this.storageinfo = {}
      //   return
      // }
      this.target_number = parseInt(this.getSizeFromId() / 1024 / 1024)
      getStorageinfo(data => {
        if (data.code === 1000) {
          if (data.data.length === 1) {
            this.storageinfo = data.data[0];
          }
        } else {
          this.$message.error('存储信息获取失败,' + data.msg);
        }
        this.loading = false;
      }, {"methods": 'GET', 'data': {'pk': id}});
    },
    formatter(row) {
      return format_time(row.updated_time)
    },
    // eslint-disable-next-line no-unused-vars
    get_data_from_tabname(tabname, data = {}) {
      data.uidsearch = this.uidsearch.replace(/^\s+|\s+$/g, "");
      data.keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");

      this.$router.push({"name": 'FirUserStorage', params: {act: tabname}});
      if (tabname === "change") {
        this.getStorageGroup()
      } else if (tabname === "edit") {
        this.loading = true;
        getStorageinfo(data => {
          if (data.code === 1000) {
            this.org_storage_id = this.use_storage_id = data.storage;
            this.storage_list = data.storage_list;
            this.endpoint_list = data.endpoint_list;
            this.storage_info_lists = data.data;
            this.disabled = true;
            this.isaddflag = false;
            this.pagination.total = data.count
          } else {
            this.$message.error('存储获取失败,' + data.msg);
          }
          this.loading = false;
        }, {"methods": 'GET', 'data': data});
      } else if (tabname === "add") {
        getStorageinfo(data => {
          if (data.code === 1000) {
            this.storage_list = data.storage_list;
            this.endpoint_list = data.endpoint_list;
            this.editstorageinfo = {
              download_auth_type: 1,
              storage_type: this.storage_list[0].id,
              endpoint: this.endpoint_list[0].id,
              download_auth_type_choices: data.download_auth_type_choices,
              domain_name: '',
              max_storage_capacity: parseInt(data.default_max_storage_capacity / 1024 / 1024)
            };
            this.isaddflag = true;
          } else {
            this.$message.error('存储列表获取失败,' + data.msg);
          }
        }, {"methods": 'GET', "data": {'act': 'storage_type'}});
      } else if (tabname === "share") {
        data.operatestatus = this.operatestatus
        shareStorageData(res => {
          if (res.code === 1000) {
            this.share_bill_lists = res.data
            this.pagination.total = res.count
            this.operate_status_choices = res.status_choices
          } else {
            this.$message.error("数据获取失败，" + data.msg)
          }
        }, {"methods": 'GET', "data": data})
      } else if (tabname === 'setting') {
        configStorageData(res => {
          if (res.code === 1000) {
            this.storage_config = res.data
          } else {
            this.$message.error("获取数据失败了，" + res.msg)
          }
        }, {"methods": 'GET', "data": data})

      }
    },
  }, mounted() {
    getUserInfoFun(this);
    if (this.$route.params.act) {
      let activeName = this.$route.params.act;
      let activeName_list = ["change", "edit", "add", "share", "setting"];
      for (let index in activeName_list) {
        if (activeName_list[index] === activeName) {
          this.activeName = activeName;
          this.get_data_from_tabname(activeName);
          return
        }
      }
    }
    this.get_data_from_tabname(this.activeName);
  }, filters: {},
  watch: {
    watchObj: function () {
      if (this.editstorageinfo.bucket_name && this.editstorageinfo.download_auth_type === 1 && this.isaddflag) {
        this.editstorageinfo.domain_name = this.editstorageinfo.bucket_name + '.' + this.editstorageinfo.endpoint.replace("-internal", "")
      }
    }
  },
  computed: {
    watchObj() {
      return [this.editstorageinfo.endpoint, this.editstorageinfo.bucket_name, this.editstorageinfo.download_auth_type]
    },
    percentage() {
      let p = parseInt(this.storageinfo.used_number * 100 / this.storageinfo.max_storage_capacity);
      if (p < 0 || p >= 100) {
        p = 100
      }
      return p
    }
  }
}
</script>

<style scoped>
.el-main {
  text-align: center;
  margin: 20px auto 100px;
  width: 1166px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}
</style>
