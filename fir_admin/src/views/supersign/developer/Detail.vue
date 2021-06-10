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
          <el-form-item label="issuer_id">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.issuer_id" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="可使用设备数">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input-number v-model="postForm.usable_number" :min="0" :max="100" label="可使用设备数" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="已消耗设备数">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input-number v-model="postForm.use_number" :min="0" :max="100" label="已消耗设备数" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="账户类型">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.auth_type" class="filter-item" disabled>
                  <el-option v-for="item in postForm.auth_type_choices" :key="item.id" :label="item.name" :value="item.id" />
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
          <el-form-item label="描述信息">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.description" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="账户状态" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-tooltip :content="postForm.is_actived|userStatusFilter" placement="top">
                  <el-switch
                    v-model="postForm.is_actived"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    :active-value="true"
                    :inactive-value="false"
                  />
                </el-tooltip>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="证书过期时间" prop="timestamp" label-width="160px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.cert_expire_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="private_key_id" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.private_key_id" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="p8key" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.p8key" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="certid" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.certid" />
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
import { getDeveloperInfo, updatedeveloperInfo } from '@/api/developer'

const defaultForm = {
  user_id: undefined,
  is_actived: undefined,
  issuer_id: undefined,
  private_key_id: undefined,
  p8key: undefined,
  certid: undefined,
  created_time: undefined,
  description: undefined,
  usable_number: undefined,
  use_number: undefined,
  auth_type: undefined,
  cert_expire_time: undefined,
  updated_time: undefined,
  auth_type_choices: []
}

export default {
  name: 'DeveloperDetail',
  components: { }, filters: {
    userStatusFilter(status) {
      const statusMap = {
        true: '激活，允许使用',
        false: '禁用，禁止使用'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      is_edit: false
    }
  },
  computed: {},
  created() {
    const id = this.$route.params && this.$route.params.id
    this.fetchData(id)
  },
  methods: {
    fetchData(id) {
      getDeveloperInfo({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updatedeveloperInfo(this.postForm).then(response => {
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
