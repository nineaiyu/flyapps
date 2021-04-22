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
          <el-form-item label="商家名称">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.payment_name" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="支付类型">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.payment_type" class="filter-item" disabled>
                  <el-option v-for="item in postForm.payment_type_choices" :key="item.id" :label="item.name" :value="item.id" />
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
          <el-form-item label="支付时间" prop="timestamp">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-date-picker :value="postForm.pay_time" type="datetime" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="订单备注">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.description" :autosize="{ minRows: 4, maxRows: 6}" type="textarea" />
              </el-col>
            </el-row>
          </el-form-item>
        </el-col>
        <el-col :span="12">

          <el-form-item label="服务器订单号" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.order_number" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="第3方订单号" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.payment_number" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="支付金额" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.actual_amount" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="购买数量" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.actual_download_times" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="赠送数量" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-input v-model="postForm.actual_download_gift_times" disabled />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="订单类型" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.order_type" class="filter-item" disabled>
                  <el-option v-for="item in postForm.order_type_choices" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="支付状态" label-width="160px">
            <el-row :gutter="12">
              <el-col :span="16">
                <el-select v-model="postForm.status" class="filter-item">
                  <el-option v-for="item in postForm.status_choices" :key="item.id" :label="item.name" :value="item.id" />
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
import { getOrderInfo, updateOrderInfo } from '@/api/order'

const defaultForm = {
  user_id: undefined,
  payment_type: undefined,
  payment_number: undefined,
  payment_name: undefined,
  order_number: undefined,
  actual_amount: undefined,
  actual_download_times: undefined,
  actual_download_gift_times: undefined,
  description: undefined,
  status: undefined,
  order_type: undefined,
  pay_time: undefined,
  created_time: undefined
}

export default {
  name: 'OrderDetail',
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
      getOrderInfo({ id: id }).then(response => {
        if (response.data.length === 1) {
          this.postForm = response.data[0]
        }
      }).catch(err => {
        console.log(err)
      })
    },
    updateData() {
      updateOrderInfo(this.postForm).then(response => {
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
