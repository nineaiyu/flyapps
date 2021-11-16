<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.to_user_id" placeholder="目标用户" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.udid" placeholder="设备UDID" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.app_id" placeholder="应用id" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.action" placeholder="充值类型" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in action_choices" :key="item.id" :label="item.name" :value="item.id" />
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
      <el-table-column label="用户ID" width="100" align="center">
        <template slot-scope="scope">
          <router-link :to="{name: 'user_info_edit',params:{id:scope.row.user_id}}">
            <el-link type="primary"> {{ scope.row.user_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="目标用户ID" width="100" align="center">
        <template slot-scope="scope">
          <router-link v-if="scope.row.to_user_id" :to="{name: 'user_info_edit',params:{id:scope.row.to_user_id}}">
            <el-link type="primary"> {{ scope.row.to_user_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="应用ID" width="100" align="center">
        <template slot-scope="scope">
          <router-link v-if="scope.row.app_id" :to="{name: 'app_info_edit',params:{id:scope.row.app_id}}">
            <el-link type="primary"> {{ scope.row.app_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="UDID" align="center">
        <template slot-scope="scope">
          {{ scope.row.udid }}
        </template>
      </el-table-column>
      <el-table-column label="客户端IP" align="center" >
        <template slot-scope="scope">
          {{ scope.row.remote_addr }}
        </template>
      </el-table-column>
      <el-table-column label="账单类型" align="center" width="100">
        <template slot-scope="scope">
          {{ scope.row.action }}
        </template>
      </el-table-column>
      <el-table-column label="备注" align="center">
        <template slot-scope="scope">
          {{ scope.row.description }}
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

      <el-table-column label="操作" align="center" width="160" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="danger" size="mini" @click="delbill(scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves'
import { getBillInfo, delBillInfo } from '@/api/developer'

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' }
]

export default {
  name: 'BillInfo',
  components: { Pagination },
  directives: { waves },
  filters: {
    formatTime(time) {
      return time.split('T')[0]
    },
    certStatusFilter(status) {
      const statusMap = {
        '0': 'danger',
        '1': 'success',
        '2': 'gray',
        '3': 'info'
      }
      return statusMap[status]
    },
    certLableFilter(row) {
      for (const v of row.auth_type_choices) {
        if (v.id === row.auth_type) {
          return v.name
        }
      }
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
        sort: '-created_time',
        action: undefined,
        app_id: undefined,
        to_user_id: undefined,
        user_id: undefined,
        udid: undefined
      },
      action_choices: undefined,
      sortOptions
    }
  },
  created() {
    this.listQuery.issuer_id = this.$route.params && this.$route.params.issuer_id
    this.listQuery.user_id = this.$route.params && this.$route.params.user_id
    this.fetchData()
  },
  methods: {
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    delbill(app_id) {
      delBillInfo({ id: app_id }).then(response => {
        this.$message.success('删除成功')
        this.fetchData()
        this.listLoading = false
      })
    },
    fetchData() {
      console.log(this.listQuery)
      this.listLoading = true
      getBillInfo(this.listQuery).then(response => {
        this.list = response.data
        if (this.list && this.list.length > 0) {
          this.action_choices = this.list[0].action_choices
        }
        this.total = response.total
        this.listLoading = false
      })
    }
  }
}
</script>
