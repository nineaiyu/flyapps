<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.domain_name" placeholder="下载域名" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.app_name" placeholder="应用名称" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.domain_type" placeholder="下载域名类型" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in domain_type_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.is_enable" placeholder="域名绑定状态" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in domain_state_choices" :key="item.id" :label="item.name" :value="item.id" />
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
      <el-table-column label="下载域名" min-width="280px" align="center">
        <template slot-scope="scope">
          {{ scope.row.domain_name }}
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="下载域名类型" width="160" align="center">
        <template slot-scope="scope">
          <router-link v-if="scope.row.domain_type===2" :to="{name: 'app_info_list',params:{user_id:scope.row.user_id,app_id:scope.row.app_id}}">
            <el-tag :type="scope.row.domain_type | domainStatusFilter">{{ scope.row| domainLableFilter }}</el-tag>
          </router-link>
          <el-tag v-else :type="scope.row.domain_type | domainStatusFilter">{{ scope.row| domainLableFilter }}</el-tag>

        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="绑定状态" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_enable | statusFilter">{{ scope.row| statusLableFilter }}</el-tag>
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
          <router-link :to="{name: 'domain_info_edit',params:{id:scope.row.id}}">
            <el-button type="primary" size="mini">
              查看编辑
            </el-button>
          </router-link>
          <el-button type="danger" size="mini" @click="remove_domain(scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { deleteDomain, getDomainList } from '@/api/domain'
import { baseFilter } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' }
]

const domain_state_choices = [
  { id: false, name: '继续绑定' },
  { id: true, name: '绑定成功' }
]

export default {
  name: 'DomainInfo',
  components: { Pagination },
  directives: { waves },
  filters: {
    formatTime(time) {
      if (time) {
        return time.split('T')[0]
      }
    },
    domainStatusFilter(status) {
      const statusMap = {
        '1': 'success',
        '0': 'gray',
        '2': 'info' }
      return statusMap[status]
    },
    domainLableFilter(row) {
      if (row.domain_type === 2) {
        return '应用' + row.app_info.name + '域名'
      }
      return baseFilter(row.domain_type, row.domain_type_choices)
    },
    statusLableFilter(row) {
      return baseFilter(row.is_enable, domain_state_choices)
    },
    statusFilter(status) {
      const statusMap = {
        true: 'success',
        false: 'danger'
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
        domain_name: undefined,
        app_name: undefined,
        domain_type: undefined,
        is_enable: undefined
      },
      sortOptions,
      domain_type_choices: [],
      domain_state_choices
    }
  },
  created() {
    this.fetchData()
  }, mounted() {
    if (this.$route.params.user_id) {
      this.listQuery.user_id = this.$route.params.user_id
    }
    console.log(this.$router)
  },
  methods: {
    remove_domain(domain_id) {
      deleteDomain(domain_id).then(response => {
        this.fetchData()
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getDomainList(this.listQuery).then(response => {
        this.list = response.data.results
        if (this.list && this.list.length > 0) {
          this.domain_type_choices = this.list[0].domain_type_choices
        }
        this.total = response.data.count
        this.listLoading = false
      })
    }
  }
}
</script>
