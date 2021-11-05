<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.app_id" placeholder="应用ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.app_name" placeholder="应用名称" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.bundle_id" placeholder="Bundle_Id" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.remote_addr" placeholder="远端地址" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.email" placeholder="联系信息" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.report_type" placeholder="举报类型" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in report_type_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.status" placeholder="处理状态" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in status_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>

      <el-select v-model="listQuery.sort" style="width: 140px" class="filter-item" @change="handleFilter">
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
      <el-table-column label="应用ID" width="100" align="center">
        <template slot-scope="scope">
          <router-link :to="{name: 'app_info_edit',params:{id:scope.row.app_id}}">
            <el-link type="primary"> {{ scope.row.app_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="应用名称" width="80px">
        <template slot-scope="scope">
          {{ scope.row.app_name }}
        </template>
      </el-table-column>
      <el-table-column label="Bundle_Id" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.bundle_id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="联系信息" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.email }}</span>
        </template>
      </el-table-column>
      <el-table-column label="联系姓名" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.username }}</span>
        </template>
      </el-table-column>
      <el-table-column label="举报者IP" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.remote_addr }}</span>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="举报类型" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.report_type | payStatusFilter">{{ scope.row| payLableFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="处理状态" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | certStatusFilter">{{ scope.row| statusLableFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_time" label="提交时间" width="120">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.created_time">
            <span>{{ scope.row.created_time|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="160" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="{name: 'report_info_edit',params:{id:scope.row.id}}">
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
import { getAppReportIfo, deleteAppReportIfo } from '@/api/report'
import { baseFilter } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' }
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
      return baseFilter(row.report_type, row.report_type_choices)
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
        app_id: undefined,
        sort: '-created_time',
        report_type: undefined,
        app_name: undefined,
        bundle_id: undefined,
        email: undefined,
        status: undefined,
        remote_addr: undefined,
        username: undefined
      },
      sortOptions,
      report_type_choices: [],
      status_choices: []
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
      deleteAppReportIfo({ id: order_info.id }).then(response => {
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
      getAppReportIfo(this.listQuery).then(response => {
        this.list = response.data
        if (this.list && this.list.length > 0) {
          this.report_type_choices = this.list[0].report_type_choices
          this.status_choices = this.list[0].status_choices
        }
        this.total = response.total
        this.listLoading = false
      })
    }
  }
}
</script>
