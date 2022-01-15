<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.bucket_name" placeholder="bucket_name" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.access_key" placeholder="access_key" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.name" placeholder="存储名称" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.domain_name" placeholder="下载域名" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.storage_type" placeholder="存储类型" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in storage_choices" :key="item.id" :label="item.name" :value="item.id" />
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
      <el-table-column label="存储名称">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="存储访问access_key" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.access_key }}</span>
        </template>
      </el-table-column>
      <el-table-column label="存储空间bucket_name" align="center">
        <template slot-scope="scope">
          {{ scope.row.bucket_name }}
        </template>
      </el-table-column>
      <el-table-column label="下载域名" align="center">
        <template slot-scope="scope">
          {{ scope.row.domain_name }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="存储类型" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.storage_type | certStatusFilter">{{ scope.row| certLableFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="存储状态" width="95" align="center">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.id === scope.row.used_id" type="success">已启用</el-tag>
          <el-tag v-else type="info">未启用</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_time" label="更新时间" width="120">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.updated_time">
            <span>{{ scope.row.updated_time|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="160" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="{name: 'storage_info_edit',params:{id:scope.row.id}}">
            <el-button type="primary" size="mini">
              查看编辑
            </el-button>
          </router-link>

        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { getStorageList } from '@/api/storage'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' },
  { label: '更新时间 Ascending', key: 'updated_time' },
  { label: '更新时间 Descending', key: '-updated_time' }
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
      for (const v of row.storage_choices) {
        if (v.id === row.storage_type) {
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
        name: undefined,
        bucket_name: undefined,
        access_key: undefined,
        storage_type: undefined,
        domain_name: undefined,
        user_id: undefined,
        ordering: '-created_time'
      },
      sortOptions,
      storage_choices: []
    }
  },
  created() {
    this.listQuery.user_id = this.$route.params && this.$route.params.user_id
    this.fetchData()
  }, mounted() {
    if (this.$route.query.user_id) {
      this.listQuery.user_id = this.$route.query.user_id
    }
  },
  methods: {
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getStorageList(this.listQuery).then(response => {
        this.list = response.data.results
        console.log(this.list)
        if (this.list && this.list.length > 0) {
          this.storage_choices = this.list[0].storage_choices
        }
        this.total = response.data.count
        this.listLoading = false
      })
    }
  }
}
</script>
