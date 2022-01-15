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
          <el-form-item  v-if="postForm.app_info&& postForm.app_info.app_id" label="应用ID">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.app_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item v-if="postForm.app_info&& postForm.app_info.app_id" label="应用名称">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.app_info.name" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="域名类型">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.domain_type" class="filter-item" disabled>
                  <el-option v-for="item in postForm.domain_type_choices" :key="item.id" :label="item.name" :value="item.id" />
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

        </el-col>
        <el-col :span="12">

          <el-form-item label="绑定的域名" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.domain_name" />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="绑定状态" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.is_enable" class="filter-item">
                  <el-option v-for="item in domain_state_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="CnameID"  label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.cname_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
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
import { getDomainInfos, updateDomainInfo } from '@/api/domain'
const domain_state_choices = [
  { id: false, name: '继续绑定' },
  { id: true, name: '绑定成功' }
]
const defaultForm = {
  user_id: undefined,
  app_info: undefined,
  domain_type: undefined,
  domain_name: undefined,
  cname_id: undefined,
  is_enable: undefined,
  domain_type_choices: undefined,
  created_time: undefined
}

export default {
  name: 'OrderDetail',
  components: { }, filters: {},
  data() {
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      is_edit: false,
      domain_state_choices,
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
      getDomainInfos(id).then(response => {
        if (response.data) {
          this.postForm = response.data
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateDomainInfo(this.id, this.postForm).then(response => {
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
