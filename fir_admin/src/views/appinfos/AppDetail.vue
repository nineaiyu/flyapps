<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" label-width="100px" :disabled="!is_edit">
      <el-row>
        <el-col :span="12">
          <el-form-item label="APP_ID">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input :value="postForm.app_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="Bundle_Id">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.bundle_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用名称">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.name" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="短连接" label-width="100px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.short" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用状态" label-width="100px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.status" class="filter-item" placeholder="Please select">
                  <el-option v-for="item in postForm.status_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用类型">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.type" class="filter-item" placeholder="Please select" disabled>
                  <el-option v-for="item in postForm.type_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="创建时间" prop="timestamp">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.created_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="更新时间" prop="timestamp">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.updated_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="下载次数" prop="download_times">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-input :value="postForm.count_hits" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用描述">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.description" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" placeholder="Please input" />
              </el-col>
            </el-row>
          </el-form-item>

        </el-col>
        <el-col :span="12">
          <el-form-item label="应用图标" label-width="200px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-image v-if="postForm.master_release" :src="postForm.master_release.icon_url" :preview-src-list="[postForm.master_release.icon_url]" fit="contain" style="width: 100px; height: 100px" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="访问密码" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.password" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用所属用户ID" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.user_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>

          <div v-if="postForm.type===1">
            <el-form-item label="是否开启超级签" label-width="160px">
              <el-row :gutter="12">
                <el-col :span="16">
                  <el-tooltip :content="postForm.issupersign|statusFilter" placement="top">
                    <el-switch
                      v-model="postForm.issupersign"
                      active-color="#13ce66"
                      inactive-color="#ff4949"
                      :active-value="true"
                      :inactive-value="false"
                    />
                  </el-tooltip>
                </el-col>
              </el-row>
            </el-form-item>
            <div v-if="postForm.issupersign===true">
              <el-form-item label="超级签名签名类型" label-width="160px">
                <el-row :gutter="12">
                  <el-col :span="16">
                    <el-select v-model="postForm.supersign_type" class="filter-item" placeholder="Please select">
                      <el-option v-for="item in postForm.supersign_type_choices" :key="item.id" :label="item.name" :value="item.id" />
                    </el-select>
                  </el-col>
                </el-row>
              </el-form-item>
              <el-form-item label="超级签名使用限额" label-width="160px">
                <el-row :gutter="12">
                  <el-col :span="16">
                    <el-input v-model="postForm.supersign_limit_number" />
                  </el-col>
                </el-row>
              </el-form-item>
              <el-form-item label="超级签名新Bundle_Id" label-width="160px">
                <el-row :gutter="12">
                  <el-col :span="16">
                    <el-input v-model="postForm.new_bundle_id" />
                  </el-col>
                </el-row>
              </el-form-item>
            </div>
          </div>
          <el-form-item label="应用专属访问域名" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.domain_name" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="下载页对所有人可见" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-tooltip :content="postForm.isshow|statusFilter" placement="top">
                  <el-switch
                    v-model="postForm.isshow"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="微信内简易访问模式" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-tooltip :content="postForm.wxeasytype|statusFilter" placement="top">
                  <el-switch
                    v-model="postForm.wxeasytype"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="微信内第三方自动跳转" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-tooltip :content="postForm.wxredirect|userStatusFilter" placement="top">
                  <el-switch
                    v-model="postForm.wxredirect"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
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
import { getAppInfos, updateAppInfo } from '@/api/app'

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
  head_img: '',
  memo: undefined,
  date_joined: undefined,
  storage_active: undefined,
  supersign_active: undefined,
  role_choices: [],
  gender_choices: [],
  storage_choices: []
}

export default {
  name: 'AppDetail',
  components: { }, filters: {
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
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      is_edit: false
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
    fetchData(id) {
      getAppInfos({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateAppInfo(this.postForm).then(response => {
        this.$message.success('更新成功')
        this.postForm = response.data
      }).catch(err => {
        console.log(err)
      })
    }
  }
}
</script>

