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
          <el-form-item label="微信openid">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.openid" disabled />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="微信昵称">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.nickname" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="地址">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.address" />
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
          <el-form-item label="用户头像" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-image :src="postForm.head_img_url" :preview-src-list="[postForm.head_img_url]" fit="contain" style="width: 100px; height: 100px" />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="订阅状态" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.subscribe" class="filter-item">
                  <el-option v-for="item in wxbind_state_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="性别" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.sex" class="filter-item">
                  <el-option v-for="item in wxbind_sex_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
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
import { getWxBindInfos, updateWxBindInfo } from '@/api/wxbind'
const wxbind_state_choices = [
  { id: false, name: '未订阅' },
  { id: true, name: '已订阅' }
]

const wxbind_sex_choices = [
  { id: 0, name: '未知' },
  { id: 1, name: '男' },
  { id: 2, name: '女' }
]

const defaultForm = {
  user_id: undefined,
  address: undefined,
  created_time: undefined,
  head_img_url: undefined,
  id: undefined,
  nickname: undefined,
  openid: undefined,
  sex: undefined,
  subscribe: undefined,
  subscribe_time: undefined
}

export default {
  name: 'OrderDetail',
  components: { }, filters: {},
  data() {
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      is_edit: false,
      wxbind_state_choices,
      wxbind_sex_choices,
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
      getWxBindInfos(id).then(response => {
        if (response.data) {
          this.postForm = response.data
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateWxBindInfo(this.id, this.postForm).then(response => {
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

</style>
