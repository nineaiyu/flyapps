<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" label-width="100px" :disabled="!is_edit">
      <el-row>
        <el-col :span="12">
          <el-form-item label="Release_ID">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input :value="postForm.release_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="build版本">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.build_version" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="app版本">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.app_version" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用大小">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.binary_size" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="版本类型">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.release_type" class="filter-item" placeholder="Please select" disabled>
                  <el-option v-for="item in postForm.release_choices" :key="item.id" :label="item.name" :value="item.id" />
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
          <el-form-item label="更新日志">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.changelog" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" placeholder="Please input" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="应用图标" label-width="200px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-image :src="postForm.icon_url" :preview-src-list="[postForm.icon_url]" fit="contain" style="width: 100px; height: 100px" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="是否master版本" label-width="200px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-tooltip :content="postForm.is_master|statusFilter" placement="top">
                  <el-switch
                    v-model="postForm.is_master"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="企业签名名称" label-width="200px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.distribution_name" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="第三方下载URL" label-width="200px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input :value="postForm.binary_url" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用可安装的最低系统版本" label-width="200px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.minimum_os_version" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="ios内测版 udid" label-width="200px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-if="postForm.udid" :value="JSON.stringify(postForm.udid)" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" disabled />
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
import { getAppReleaseInfos, updateReleaseAppInfo } from '@/api/app'

const defaultForm = {
  is_master: undefined,
  udid: undefined,
  distribution_name: undefined,
  release_id: undefined,
  build_version: undefined,
  app_version: undefined,
  release_type: undefined,
  binary_size: undefined,
  icon_url: undefined,
  binary_url: undefined,
  changelog: undefined,
  created_time: undefined,
  release_choices: undefined,
  minimum_os_version: undefined
}

export default {
  name: 'AppReleaseDetail',
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
  data() {
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      is_edit: false,
      id: ''
    }
  },
  computed: {
  },
  created() {
    this.id = this.$route.params && this.$route.params.id
    this.fetchData(this.id)
  },
  methods: {
    fetchData(id) {
      getAppReleaseInfos(id).then(response => {
        if (response.data) {
          this.postForm = response.data
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateReleaseAppInfo(this.id, this.postForm).then(response => {
        this.$message.success('更新成功')
        this.postForm = response.data
      }).catch(err => {
        console.log(err)
      })
    }
  }
}
</script>

