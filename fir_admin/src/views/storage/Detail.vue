<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" label-width="100px" :disabled="!is_edit">
      <el-row>
        <el-col :span="12">
          <el-form-item label="用户ID">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input :value="postForm.user_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="存储名称">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.name" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="存储类型">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.storage_type" class="filter-item" disabled>
                  <el-option v-for="item in postForm.storage_choices" :key="item.id" :label="item.name" :value="item.id" />
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
          <el-form-item label="存储描述信息">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.description" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">

          <el-form-item label="存储访问access_key" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.access_key" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="存储访问secret_key" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.secret_key" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="存储空间bucket_name" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.bucket_name" />
              </el-col>
            </el-row>
          </el-form-item>
          <div v-if="postForm.storage_type===2">
            <el-form-item label="阿里云sts_role_arn" label-width="160px">
              <el-row :gutter="12">
                <el-col :span="16">
                  <el-input v-model="postForm.sts_role_arn" />
                </el-col>
              </el-row>
            </el-form-item>

            <el-form-item label="阿里云endpoint" label-width="160px">
              <el-row :gutter="12">
                <el-col :span="16">
                  <el-input v-model="postForm.endpoint" />
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item label="阿里云下载授权方式" label-width="160px">
              <el-row :gutter="12">
                <el-col :span="16">
                  <el-select v-model="postForm.download_auth_type" class="filter-item" style="width: 100%">
                    <el-option v-for="item in postForm.download_auth_type_choices" :key="item.id" :label="item.name" :value="item.id" />
                  </el-select>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item v-if="postForm.download_auth_type===2" label="阿里云cnd_auth_key" label-width="160px">
              <el-row :gutter="12">
                <el-col :span="16">
                  <el-input v-model="postForm.cnd_auth_key" />
                </el-col>
              </el-row>
            </el-form-item>
          </div>
        </el-col>
      </el-row>
    </el-form>
    <el-link v-if="postForm.id === postForm.used_id" type="danger" :underline="false">存储使用中，无法修改存储相关配置，请悉知</el-link>
    <el-col :span="9" style="float: right">
      <el-button v-if="!is_edit" type="primary" :disabled="postForm.id === postForm.used_id" @click="is_edit=true">修改</el-button>
      <div v-else>
        <el-button type="primary" @click="is_edit=false">取消</el-button>
        <el-button type="primary" @click="updateData">保存修改</el-button>
      </div>
    </el-col>
  </div>
</template>

<script>
import { getStorageInfo, updateStorageInfo } from '@/api/storage'

const defaultForm = {
  user_id: undefined,
  name: undefined,
  storage_type: undefined,
  access_key: undefined,
  secret_key: undefined,
  bucket_name: undefined,
  domain_name: undefined,
  created_time: undefined,
  description: undefined,
  sts_role_arn: undefined,
  endpoint: undefined,
  download_auth_type: undefined,
  cnd_auth_key: undefined,
  updated_time: undefined,
  used_id: undefined,
  download_auth_type_choices: []
}

export default {
  name: 'StorageDetail',
  components: { }, filters: {},
  data() {
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      is_edit: false,
      id: ''
    }
  },
  computed: {},
  created() {
    this.id = this.$route.params && this.$route.params.id
    this.fetchData(this.id)
  },
  methods: {
    fetchData(id) {
      getStorageInfo(id).then(response => {
        if (response.data) {
          this.postForm = response.data
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateStorageInfo(this.id, this.postForm).then(response => {
        this.$message.success('更新成功')
        this.postForm = response.data
      }).catch(err => {
        console.log(err)
      })
    }
  }
}
</script>

<style scoped>
  .editor-container {
    position: relative;
    height: 100%;
  }
</style>
