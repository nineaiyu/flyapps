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
          <el-form-item label="真实姓名">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.name" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="身份证号码">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.card" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="居住地址">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.addr" />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="实名认证">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.status" class="filter-item" placeholder="Please select">
                  <el-option v-for="item in postForm.certification_status_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="提交时间" prop="timestamp">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.created_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="审核时间" prop="timestamp">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.reviewed_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="审核备注">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.msg" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" placeholder="Please input" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="实名认证照片">
            <div v-for="info in postForm.certification_infos" :key="info.name" style="width: 320px; height: 340px;float: left;border: #409EFF 1px solid;text-align: center;margin-left: 20px;margin-bottom: 20px">
              <el-image :src="info.certification_url" :preview-src-list="[info.certification_url]" fit="contain" style="width: 260px; height: 260px" />
              <el-link :underline="false"> {{ info.name }}</el-link>
            </div>
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
import { getCertificationInfo, updateCertificationInfo } from '@/api/user'

const defaultForm = {
  user_id: undefined,
  name: undefined,
  card: undefined,
  addr: undefined,
  mobile: undefined,
  status: undefined,
  msg: undefined,
  created_time: undefined,
  reviewed_time: undefined
}

export default {
  name: 'CertificationDetail',
  components: { }, filters: {
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
    const id = this.$route.params && this.$route.params.id
    this.fetchData(id)
  },
  methods: {
    fetchData(id) {
      getCertificationInfo({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateCertificationInfo(this.postForm).then(response => {
        this.$message.success('更新成功')
        this.postForm = response.data
      }).catch(err => {
        console.log(err)
      })
    }
  }
}
</script>

