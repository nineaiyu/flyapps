<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" label-width="100px">
      <el-row>
        <el-col :span="12">
          <el-form-item label="用户ID">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.user_id" placeholder="邮箱，手机号，或者uid" />
              </el-col>
              <el-col :span="4">
                <el-button @click="check_balance('user_id')">查询校验</el-button>
              </el-col>
            </el-row>
            <el-row v-if="user_info.private_balance_info.all_balance+user_info.public_balance_info.all_balance">
              <el-col>
                <el-link :underline="false"> 公有池数量 {{ user_info.public_balance_info.all_balance }}   已经使用数量 {{ user_info.public_balance_info.used_balance }}</el-link>
              </el-col>
              <el-col>
                <el-link :underline="false"> 私有池数量 {{ user_info.private_balance_info.all_balance }}   已经使用数量 {{ user_info.private_balance_info.used_balance }}</el-link>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="目标用户">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.to_user_id" placeholder="邮箱，手机号，或者uid" />
              </el-col>
              <el-col :span="4">
                <el-button @click="check_balance('to_user_id')">查询校验</el-button>
              </el-col>
            </el-row>
            <el-row v-if="to_user_info.private_balance_info.all_balance+to_user_info.public_balance_info.all_balance">
              <el-col>
                <el-link :underline="false"> 公有池数量 {{ to_user_info.public_balance_info.all_balance }}   已经使用数量 {{ to_user_info.public_balance_info.used_balance }}</el-link>
              </el-col>
              <el-col>
                <el-link :underline="false"> 私有池数量 {{ to_user_info.private_balance_info.all_balance }}   已经使用数量 {{ to_user_info.private_balance_info.used_balance }}</el-link>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="转移数量">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input-number v-model="postForm.number" :min="0" :max="10000" label="可使用设备数" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <el-col :span="9" style="float: right">
      <el-button type="primary" @click="addbill">确定</el-button>
    </el-col>
  </div>
</template>

<script>
import waves from '@/directive/waves'
import { addBillInfo, getUserBillInfo } from '@/api/developer'

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' }
]


export default {
  name: 'BillAddInfo',
  directives: { waves },
  filters: {
    formatTime(time) {
      return time.split('T')[0]
    }
  },
  data() {
    return {
      list: null,
      listLoading: true,
      total: 0,
      postForm: {
        to_user_id: undefined,
        user_id: undefined,
        number: undefined
      },
      user_info: { public_balance_info: { all_balance: undefined }, private_balance_info: { used_balance: undefined }},
      to_user_info: { public_balance_info: { all_balance: undefined }, private_balance_info: { used_balance: undefined }},
      action_choices: undefined,
      sortOptions
    }
  },
  created() {

  },
  methods: {
    check_balance(act) {
      let user_id = this.postForm.user_id
      if (act === 'to_user_id') {
        user_id = this.postForm.to_user_id
      }
      getUserBillInfo({ user_id: user_id }).then(response => {
        if (act === 'user_id') {
          this.user_info = response
        } else if (act === 'to_user_id') {
          this.to_user_info = response
        }
        console.log(this.user_info)
      })
    },
    addbill() {
      addBillInfo(this.postForm).then(response => {
        this.$message.success('充值成功')
      })
    }
  }
}
</script>
