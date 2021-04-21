<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" :rules="rules" label-width="80px" :disabled="!is_edit">
      <el-row>
        <el-col :span="12">
          <el-form-item label="UID">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input :value="postForm.uid" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="账号" prop="username">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.username" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="昵称">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.first_name" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="性别">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.gender" class="filter-item" placeholder="Please select">
                  <el-option v-for="item in postForm.gender_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="角色">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.role" class="filter-item" placeholder="Please select">
                  <el-option v-for="item in postForm.role_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.email" />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="手机" prop="mobile">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.mobile" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="Q Q" prop="number">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.qq" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="职位">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.job" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="公司">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.company" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="备注">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.memo" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" placeholder="Please input" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="用户头像">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-image :src="postForm.head_img" :preview-src-list="[postForm.head_img]" fit="contain" style="width: 100px; height: 100px" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="账户状态">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-tooltip :content="postForm.is_active|userStatusFilter" placement="top">
                  <el-switch
                    v-model="postForm.is_active"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="超级签名">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-tooltip :content="postForm.supersign_active|statusFilter" placement="top">
                  <el-switch
                    v-model="postForm.supersign_active"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="存储权限">
            <el-row :gutter="12">
              <el-col :span="3">
                <el-tooltip :content="postForm.storage_active|statusFilter" placement="top">
                  <el-switch
                    v-model="postForm.storage_active"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
              </el-col>
              <el-col :span="5">
                <el-select v-model="postForm.storage" filterable>
                  <el-option-group
                    v-for="storage_group in storage_selection"
                    :key="storage_group.id"
                    :label="storage_group.name"
                  >
                    <el-option
                      v-for="storage in storage_group.storage_info"
                      :key="storage.id"
                      :label="storage.name"
                      :value="storage.id"
                    />
                  </el-option-group>
                </el-select>
              </el-col>
              <el-col :span="4">
                <el-button type="primary" style="margin-left: 20px" @click="changeStorageData(null)">
                  迁移数据
                </el-button>
              </el-col>
              <el-col :span="4">
                <el-button type="primary" style="margin-left: 20px" @click="changeStorageData(force)">
                  强制切换
                </el-button>
              </el-col>
              <el-col :span="5">
                <router-link :to="{name: 'storage_info_list',query:{user_id:postForm.id}}">
                  <el-button type="primary" style="margin-left: 20px">
                    查看存储信息
                  </el-button>
                </router-link>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="实名认证">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.certification" class="filter-item" placeholder="Please select" :disabled="postForm.certification === -1">
                  <el-option v-for="item in postForm.certification_status_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
                <router-link v-if="postForm.certification_id" :to="{name: 'user_authentication_info_edit',params:{id:postForm.certification_id.id}}">
                  <el-button type="primary">
                    审核认证信息
                  </el-button>
                </router-link>
              </el-col>
              <el-col v-if="postForm.certification === -1" :span="16">
                <el-link :underline="false" type="danger"> 用户需要先提交认证信息，才可以进行认证修改</el-link>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="下载域名" prop="domain_name">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.domain_name" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="下载次数" prop="download_times">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-input :value="postForm.download_times" disabled />
              </el-col>
              <el-col :span="8">
                <el-button>后台充值</el-button>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="注册时间" prop="timestamp">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.date_joined" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用版本历史记录">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-input v-model="postForm.history_release_limit" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <el-col :span="9" style="float: right">
      <el-button v-if="!is_edit" type="primary" @click="is_edit=true">修改</el-button>
      <div v-else>
        <el-button type="primary" @click="is_edit=false">取消</el-button>
        <el-button type="primary" @click="updateData">保存修改</el-button>
      </div>
    </el-col>
  </div>
</template>

<script>
import { validURL } from '@/utils/validate'
import { getUserInfos, updateUserInfo } from '@/api/user'
import { getStorageInfo,changeStorageInfo } from '@/api/storage'
import { CommentDropdown, PlatformDropdown, SourceUrlDropdown } from './Dropdown'

const defaultForm = {
  email: undefined,
  job: undefined,
  qq: undefined,
  id: undefined,
  company: undefined,
  gender: undefined,
  username: undefined,
  first_name: undefined,
  role: undefined,
  history_release_limit: undefined,
  domain_name: undefined,
  download_times: undefined,
  is_active: undefined,
  head_img: undefined,
  memo: undefined,
  date_joined: undefined,
  storage_active: undefined,
  storage: undefined,
  supersign_active: undefined,
  role_choices: [],
  gender_choices: [],
  storage_choices: []
}

export default {
  name: 'UserDetail',
  components: { CommentDropdown, PlatformDropdown, SourceUrlDropdown }, filters: {
    userStatusFilter(status) {
      const statusMap = {
        true: '激活，允许登录',
        false: '禁用，禁止登录'
      }
      return statusMap[status]
    },
    statusFilter(status) {
      const statusMap = {
        true: '启用，允许配置',
        false: '禁用，禁止配置'
      }
      return statusMap[status]
    }
  },
  props: {
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    const validateRequire = (rule, value, callback) => {
      if (value === '') {
        this.$message({
          message: rule.field + '为必传项',
          type: 'error'
        })
        callback(new Error(rule.field + '为必传项'))
      } else {
        callback()
      }
    }
    const validateSourceUri = (rule, value, callback) => {
      if (value) {
        if (validURL(value)) {
          callback()
        } else {
          this.$message({
            message: '外链url填写不正确',
            type: 'error'
          })
          callback(new Error('外链url填写不正确'))
        }
      } else {
        callback()
      }
    }
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      userListOptions: [],
      rules: {
        image_uri: [{ validator: validateRequire }],
        title: [{ validator: validateRequire }],
        content: [{ validator: validateRequire }],
        source_uri: [{ validator: validateSourceUri, trigger: 'blur' }]
      },
      is_edit: false,
      certification_status_choices: [],
      storage_selection: []
    }
  },
  computed: {
  },
  created() {
    if (this.isEdit) {
      const id = this.$route.params && this.$route.params.id
      this.fetchData(id)
    }
  },
  methods: {
    changeStorageData(force) {
      changeStorageInfo({id: this.postForm.id, use_storage_id: this.postForm.storage,force: force}).then(response => {
        this.$message.success('存储数据迁移并设置刷新成功')
      }).catch(err => {
        console.log(err)
      })
    },
    fetchStorageData(user_id) {
      getStorageInfo({ user_id: user_id }).then(response => {
        if (response.storage_selection) {
          this.storage_selection = response.storage_selection
        }
      }).catch(err => {
        console.log(err)
      })
    },
    setStorageInfo() {
      if (!this.postForm.storage) {
        this.postForm.storage = -1
      }
      this.fetchStorageData(this.postForm.id)
    },
    fetchData(id) {
      getUserInfos({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
          this.certification_status_choices = this.postForm.certification_status_choices
          this.setStorageInfo()
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateUserInfo(this.postForm).then(response => {
        this.$message.success('更新成功')
        this.postForm = response.data
        this.setStorageInfo()
      }).catch(err => {
        console.log(err)
      })
    }
  }
}
</script>

