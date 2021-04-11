<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" :rules="rules">

      <el-row>
        <el-form-item label="UID">
          <el-row :gutter="20">
            <el-col :span="9">
              <el-input :value="postForm.uid" disabled />
            </el-col>
            <el-col :span="9">
              <el-button type="primary">保存本次修改</el-button>
            </el-col>
          </el-row>
        </el-form-item>
        <el-col :span="12">
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
                  <el-option v-for="item in gender_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="角色">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.role" class="filter-item" placeholder="Please select">
                  <el-option v-for="item in role_choices" :key="item.id" :label="item.name" :value="item.id" />
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

        </el-col>

        <el-col :span="12">
          <el-form-item label="头像">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-image :src="postForm.head_img" :preview-src-list="[postForm.head_img]" fit="contain" style="width: 100px; height: 100px" />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="用户名称" prop="username">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.username" />
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

      <!--        <el-form-item label="Status">-->
      <!--          <el-select v-model="postForm.status" class="filter-item" placeholder="Please select">-->
      <!--            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />-->
      <!--          </el-select>-->
      <!--        </el-form-item>-->

      <el-form-item label="备注">
        <el-input v-model="postForm.memo" :autosize="{ minRows: 2, maxRows: 6}" type="textarea" placeholder="Please input" />
      </el-form-item>
    </el-form>
    <!--      <div slot="footer" class="dialog-footer">-->
    <!--        <el-button @click="dialogFormVisible = false">-->
    <!--          Cancel-->
    <!--        </el-button>-->
    <!--        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">-->
    <!--          Confirm-->
    <!--        </el-button>-->
    <!--      </div>-->
    <!--    </el-form>-->
  </div>
</template>

<script>
import { validURL } from '@/utils/validate'
import { getUserInfos } from '@/api/user'
import { CommentDropdown, PlatformDropdown, SourceUrlDropdown } from './Dropdown'

const defaultForm = {
  id: undefined,
  role_choices: [],
  gender_choices: []

}

export default {
  name: 'UserDetail',
  components: { CommentDropdown, PlatformDropdown, SourceUrlDropdown },
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
      postFormRoute: {}
    }
  },
  computed: {

    displayTime: {
      // set and get is useful when the data
      // returned by the back end api is different from the front end
      // back end return => "2013-06-25 06:59:25"
      // front end need timestamp => 1372114765000
      get() {
        return (+new Date(this.postForm.display_time))
      },
      set(val) {
        this.postForm.display_time = new Date(val)
      }
    }
  },
  created() {
    if (this.isEdit) {
      const id = this.$route.params && this.$route.params.id
      this.fetchData(id)
    }

    // Why need to make a copy of this.$route here?
    // Because if you enter this page and quickly switch tag, may be in the execution of the setTagsViewTitle function, this.$route is no longer pointing to the current page
    // https://github.com/PanJiaChen/vue-element-admin/issues/1221
    this.postFormRoute = Object.assign({}, this.$route)
  },
  methods: {
    fetchData(id) {
      getUserInfos({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
          this.gender_choices = response.gender_choices
          this.role_choices = response.role_choices
        }

        // just for test
        this.postForm.title += `   Article Id:${this.postForm.id}`
        this.postForm.content_short += `   Article Id:${this.postForm.id}`

        // set tagsview title
        // this.setTagsViewTitle()

        // set page title
        // this.setPageTitle()
      }).catch(err => {
        console.log(err)
      })
    },
    setTagsViewTitle() {
      const title = 'Edit Article'
      const route = Object.assign({}, this.postFormRoute, { title: `${title}-${this.postForm.id}` })
      this.$store.dispatch('tagsView/updateVisitedView', route)
    },
    setPageTitle() {
      const title = 'Edit Article'
      document.title = `${title} - ${this.postForm.id}`
    },
    submitForm() {
      console.log(this.postForm)
      this.$refs.postForm.validate(valid => {
        if (valid) {
          this.loading = true
          this.$notify({
            title: '成功',
            message: '发布文章成功',
            type: 'success',
            duration: 2000
          })
          this.postForm.status = 'published'
          this.loading = false
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    draftForm() {
      if (this.postForm.content.length === 0 || this.postForm.title.length === 0) {
        this.$message({
          message: '请填写必要的标题和内容',
          type: 'warning'
        })
        return
      }
      this.$message({
        message: '保存成功',
        type: 'success',
        showClose: true,
        duration: 1000
      })
      this.postForm.status = 'draft'
    },
    getRemoteUserList(query) {
      searchUser(query).then(response => {
        if (!response.data.items) return
        this.userListOptions = response.data.items.map(v => v.name)
      })
    }
  }
}
</script>

