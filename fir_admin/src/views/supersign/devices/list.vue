<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.issuer_id" placeholder="开发者issuer_id" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.udid" placeholder="设备UDID" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.name" placeholder="应用名称" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.bundle_id" placeholder="BundleID" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.short" placeholder="短连接" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />

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
      <el-table-column label="应用ID" width="100" align="center">
        <template slot-scope="scope">
          <router-link :to="{name: 'app_info_edit',params:{id:scope.row.app_id}}">
            <el-link type="primary"> {{ scope.row.app_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="开发者issuer_id" align="center">
        <template slot-scope="scope">
          <router-link :to="{name: 'developer_user_info_edit',params:{id:scope.row.developer_pk}}">
            <el-link type="primary"> {{ scope.row.developer_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="应用名称" align="center" >
        <template slot-scope="scope">
          {{ scope.row.bundle_name }}
        </template>
      </el-table-column>
      <el-table-column label="短连接" align="center" width="100">
        <template slot-scope="scope">
          {{ scope.row.short }}
        </template>
      </el-table-column>
      <el-table-column label="BundleID" align="center">
        <template slot-scope="scope">
          {{ scope.row.bundle_id }}
        </template>
      </el-table-column>
      <el-table-column label="设备UDID" align="center" width="350">
        <template slot-scope="scope">
          {{ scope.row.device_udid }}
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
          <el-button type="danger" size="mini" @click="deleteApp(scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { getDevicesList } from '@/api/devices'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' }
]

export default {
  name: 'DevicesInfo',
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
        ordering: '-created_time',
        issuer_id: undefined,
        short: undefined,
        bundle_id: undefined,
        name: undefined,
        user_id: undefined,
        udid: undefined
      },
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
    fetchData() {
      this.listLoading = true
      getDevicesList(this.listQuery).then(response => {
        this.list = response.data.results
        if (this.list && this.list.length > 0) {
          this.auth_type_choices = this.list[0].auth_type_choices
        }
        this.total = response.data.count
        this.listLoading = false
      })
    }
  }
}
</script>
