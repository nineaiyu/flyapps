<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.payment_number" placeholder="payment_number" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.order_number" placeholder="order_number" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.payment_name" placeholder="支付商家" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.payment_type" placeholder="支付类型" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in payment_type_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.status" placeholder="订单状态" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in status_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.order_type" placeholder="订单类型" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in order_type_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.ordering" style="width: 140px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        Search
      </el-button>
    </div>
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      fit
      highlight-current-row
      stripe
    >
      <el-table-column align="center" label="ID" width="90">
        <template slot-scope="scope">
          {{ scope.row.id }}
        </template>
      </el-table-column>
      <el-table-column label="用户ID" width="100" align="center">
        <template slot-scope="scope">
          <router-link :to="{name: 'user_info_edit',params:{id:scope.row.user_id}}">
            <el-link type="primary"> {{ scope.row.user_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="支付商家" width="80px">
        <template slot-scope="scope">
          {{ scope.row.payment_name }}
        </template>
      </el-table-column>
      <el-table-column label="订单号" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.order_number }}</span>
        </template>
      </el-table-column>
      <el-table-column label="第三方订单号" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.payment_number }}</span>
        </template>
      </el-table-column>
      <el-table-column label="实付金额" align="center" width="80px">
        <template slot-scope="scope">
          ￥ {{ scope.row.actual_amount/100 }}
        </template>
      </el-table-column>
      <el-table-column label="购买数量" align="center" width="90px">
        <template slot-scope="scope">
          {{ scope.row.actual_download_times }}
        </template>
      </el-table-column>
      <el-table-column label="赠送数量" align="center" width="90px">
        <template slot-scope="scope">
          {{ scope.row.actual_download_gift_times }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="支付类型" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.payment_type | payStatusFilter">{{ scope.row| payLableFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="订单状态" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | certStatusFilter">{{ scope.row| statusLableFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_time" label="创建时间" width="120">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.created_time">
            <span>{{ scope.row.created_time|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_time" label="支付时间" width="120">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.pay_time">
            <span>{{ scope.row.pay_time|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="160" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="{name: 'order_info_edit',params:{id:scope.row.id}}">
            <el-button type="primary" size="mini">
              查看编辑
            </el-button>
          </router-link>
          <el-button type="danger" size="mini" @click="remove_order_info(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { deleteOrderInfo, getOrderList } from '@/api/order'
import { baseFilter } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' },
  { label: '付款时间 Ascending', key: 'pay_time' },
  { label: '付款时间 Descending', key: '-pay_time' },
  { label: '付款金额 Ascending', key: 'actual_amount' },
  { label: '付款金额 Descending', key: '-actual_amount' }
]

export default {
  name: 'OrderInfo',
  components: { Pagination },
  directives: { waves },
  filters: {
    formatTime(time) {
      if (time) {
        return time.split('T')[0]
      }
    },
    payStatusFilter(status) {
      const statusMap = {
        '0': 'gray',
        '1': 'success' }
      return statusMap[status]
    },
    certStatusFilter(status) {
      const statusMap = {
        '0': 'success',
        '1': 'info',
        '2': 'gray' }
      return statusMap[status]
    },
    payLableFilter(row) {
      return baseFilter(row.payment_type, row.payment_type_choices)
    },
    statusLableFilter(row) {
      return baseFilter(row.status, row.status_choices)
    },
    statusFilter(status) {
      const statusMap = {
        true: 'success',
        false: 'danger'
      }
      return statusMap[status]
    },
    appStatusNameFilter(row) {
      for (const r of row.status_choices) {
        if (r.id === row.status) {
          return r.name
        }
      }
    },
    appStatusFilter(status) {
      const statusMap = {
        '0': 'danger',
        '1': 'success',
        '2': 'gray'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      list: null,
      listLoading: true,
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        user_id: undefined,
        ordering: '-created_time',
        payment_type: undefined,
        payment_name: undefined,
        payment_number: undefined,
        order_number: undefined,
        status: undefined,
        order_type: undefined
      },
      sortOptions,
      payment_type_choices: [],
      status_choices: [],
      order_type_choices: []
    }
  },
  created() {
    this.fetchData()
  }, mounted() {
    if (this.$route.params.user_id) {
      this.listQuery.user_id = this.$route.params.user_id
    }
  },
  methods: {
    remove_order_info(order_info) {
      deleteOrderInfo(order_info.id).then(response => {
        this.list = response.data
        if (response.code === 1000) {
          this.fetchData()
        } else {
          this.$message.error('操作失败了 ' + response.msg)
        }
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getOrderList(this.listQuery).then(response => {
        this.list = response.data.results
        if (this.list && this.list.length > 0) {
          this.payment_type_choices = this.list[0].payment_type_choices
          this.status_choices = this.list[0].status_choices
          this.order_type_choices = this.list[0].order_type_choices
        }
        this.total = response.data.count
        this.listLoading = false
      })
    }
  }
}
</script>
