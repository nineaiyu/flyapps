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
                <el-select v-model="postForm.storage_type" class="filter-item" placeholder="Please select">
                  <el-option v-for="item in postForm.storage_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="存储额外参数">
            <el-row :gutter="12">
              <el-col :span="21">

                <div class="editor-container">
                  <json-editor ref="jsonEditor" v-model="postForm.additionalparameters" />
                </div>
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="创建时间" prop="timestamp" label-width="160px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.created_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="更新时间" prop="timestamp" label-width="160px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.updated_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
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
          <el-form-item label="存储描述信息" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.description" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" placeholder="Please input" />
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
import { getStorageInfo, updateStorageInfo } from '@/api/storage'
import JsonEditor from '@/components/JsonEditor'

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
  updated_time: undefined
}

export default {
  name: 'StorageDetail',
  components: { JsonEditor }, filters: {
  },
  data() {
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      is_edit: false,
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
      getStorageInfo({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
          this.postForm.additionalparameters = this.postForm.additionalparameter
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateStorageInfo(this.postForm).then(response => {
        this.$message.success('更新成功')
        this.postForm = response.data
        this.postForm.additionalparameters = this.postForm.additionalparameter
      }).catch(err => {
        console.log(err)
      })
    }
  }
}
</script>

<style scoped>
  .editor-container{
    position: relative;
    height: 100%;
  }
</style>
