<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.issuer_id" placeholder="issuer_id" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.private_key_id" placeholder="private_key_id" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.certid" placeholder="证书ID" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.description" placeholder="备注" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.auth_type" placeholder="账户类型" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in auth_type_choices" :key="item.id" :label="item.name" :value="item.id" />
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
      <el-table-column label="issuer_id" width="300">
        <template slot-scope="scope">
          {{ scope.row.issuer_id }}
        </template>
      </el-table-column>
      <el-table-column label="private_key_id" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.private_key_id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="certid" align="center">
        <template slot-scope="scope">
          {{ scope.row.certid }}
        </template>
      </el-table-column>
      <el-table-column label="可用设备数" align="center" width="100">
        <template slot-scope="scope">
          {{ scope.row.usable_number }}
        </template>
      </el-table-column>
      <el-table-column label="消耗设备数" align="center" width="100">
        <template slot-scope="scope">
          <router-link :to="{name: 'devices_info_list',params:{issuer_id:scope.row.issuer_id}}">
            <el-link type="primary"> {{ scope.row.use_number }}</el-link>
          </router-link>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="账户类型" width="130" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.auth_type | certStatusFilter">{{ scope.row| certLableFilter }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="是否激活" width="80" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_actived | statusFilter">{{ scope.row.is_actived }}</el-tag>
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
      <el-table-column align="center" prop="created_time" label="证书过期时间" width="120">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.updated_time">
            <span>{{ scope.row.cert_expire_time|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="160" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="{name: 'developer_user_info_edit',params:{id:scope.row.id}}">
            <el-button type="primary" size="mini">
              查看编辑
            </el-button>
          </router-link>
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
import { getDeveloperInfo } from '@/api/developer'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' },
  { label: '更新时间 Ascending', key: 'updated_time' },
  { label: '更新时间 Descending', key: '-updated_time' },
  { label: '证书过期时间 Ascending', key: 'cert_expire_time' },
  { label: '证书过期时间 Descending', key: '-cert_expire_time' }
]

export default {
  name: 'StorageInfo',
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
        issuer_id: undefined,
        private_key_id: undefined,
        certid: undefined,
        description: undefined,
        user_id: undefined,
        auth_type: undefined
      },
      sortOptions,
      auth_type_choices: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getDeveloperInfo(this.listQuery).then(response => {
        this.list = response.data
        if (this.list && this.list.length > 0) {
          this.auth_type_choices = this.list[0].auth_type_choices
        }
        this.total = response.total
        this.listLoading = false
      })
    }
  }
}
</script>
