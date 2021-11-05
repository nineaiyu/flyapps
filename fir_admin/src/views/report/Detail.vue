<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" label-width="100px" :disabled="!is_edit">
      <el-row>
        <el-col :span="12">
          <el-form-item label="应用ID">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input :value="postForm.app_id" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="应用名称">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.app_name" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="举报类型">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.report_type" class="filter-item" disabled>
                  <el-option v-for="item in postForm.report_type_choices" :key="item.id" :label="item.name" :value="item.id" />
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

          <el-form-item label="举报原因">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.report_reason" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" disabled />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">

          <el-form-item label="举报者姓名" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.username" disabled />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="举报联系方式" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.email" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="举报者IP地址" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.remote_addr" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="处理状态" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.status" class="filter-item">
                  <el-option v-for="item in postForm.status_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="处理备注" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.description" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" />
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
import { getAppReportIfo, updateAppReportIfo } from '@/api/report'

const defaultForm = {
  app_id: undefined,
  app_name: undefined,
  bundle_id: undefined,
  created_time: undefined,
  description: undefined,
  email: undefined,
  remote_addr: undefined,
  report_reason: undefined,
  status: undefined,
  report_type: undefined,
  username: undefined
}

export default {
  name: 'ReportDetail',
  components: { }, filters: {},
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
      getAppReportIfo({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateAppReportIfo(this.postForm).then(response => {
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
