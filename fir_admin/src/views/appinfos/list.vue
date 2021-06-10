<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.bundle_id" placeholder="Bundle_Id" style="width: 250px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.name" placeholder="应用名称" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.short" placeholder="短连接" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.domain_name" placeholder="应用专属访问域名" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-if="type_choices" v-model="listQuery.type" placeholder="应用类型" clearable class="filter-item" style="width: 120px" @change="handleFilter">
        <el-option v-for="item in type_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-if="status_choices" v-model="listQuery.status" placeholder="应用状态" clearable class="filter-item" style="width: 120px" @change="handleFilter">
        <el-option v-for="item in status_choices" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
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
      <el-table-column label="应用图标" align="center" width="130">
        <template slot-scope="scope">
          <el-image :src="scope.row.master_release.icon_url" :preview-src-list="[scope.row.master_release.icon_url]" fit="contain" style="width: 80px; height: 80px" />
        </template>
      </el-table-column>
      <el-table-column label="应用名称">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="Bundle_Id" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.bundle_id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="关联应用" align="center" width="130">
        <template slot-scope="scope">
          <el-image v-if="scope.row.has_combo" :src="scope.row.has_combo.master_release.icon_url" :preview-src-list="[scope.row.has_combo.master_release.icon_url]" fit="contain" style="width: 80px; height: 80px" />
          <el-link v-else>无关联应用</el-link>
        </template>
      </el-table-column>
      <el-table-column label="应用专属访问域名" align="center">
        <template slot-scope="scope">
          {{ scope.row.domain_name }}
        </template>
      </el-table-column>
      <el-table-column label="用户ID" width="100" align="center">
        <template slot-scope="scope">
          <router-link :to="{name: 'user_info_edit',params:{id:scope.row.user_id}}">
            <el-link type="primary"> {{ scope.row.user_id }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="短连接" width="80" align="center">
        <template slot-scope="scope">
          {{ scope.row.short }}
        </template>
      </el-table-column>
      <el-table-column label="下载次数" width="100" align="center">
        <template slot-scope="scope">
          {{ scope.row.count_hits }}
        </template>
      </el-table-column>
      <el-table-column label="应用大小" width="80" align="center">
        <template slot-scope="scope">
          {{ scope.row.master_release.binary_size }}
        </template>
      </el-table-column>
      <el-table-column label="历史版本数" width="100" align="center">
        <template slot-scope="scope">
          <router-link :to="{name: 'app_release_info_list',params:{app_id:scope.row.id}}">
            <el-link type="primary"> {{ scope.row.release_count }}</el-link>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="应用状态" width="80" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | appStatusFilter">{{ scope.row |appStatusNameFilter }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="下载页显示" width="100" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.isshow | statusFilter">{{ scope.row.isshow }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" prop="created_at" label="更新时间" width="120">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.updated_time">
            <span>{{ scope.row.updated_time|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="160" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="{name: 'app_info_edit',params:{id:scope.row.id}}">
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
import { getAppInfos, deleteApp } from '@/api/app'
import { baseFilter } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '更新时间 Ascending', key: 'updated_time' },
  { label: '更新时间 Descending', key: '-updated_time' },
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' },
  { label: '下载次数 Ascending', key: 'count_hits' },
  { label: '下载次数 Descending', key: '-count_hits' }
]

export default {
  name: 'AppInfo',
  components: { Pagination },
  directives: { waves },
  filters: {
    formatTime(time) {
      return time.split('T')[0]
    },
    statusFilter(status) {
      const statusMap = {
        true: 'success',
        false: 'danger'
      }
      return statusMap[status]
    },
    appStatusNameFilter(row) {
      return baseFilter(row.status,row.status_choices)
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
        bundle_id: undefined,
        sort: '-count_hits',
        type: undefined,
        domain_name: undefined,
        user_id: undefined
      },
      sortOptions,
      type_choices: [],
      status_choices: []
    }
  },
  created() {
    this.listQuery.user_id = this.$route.params && this.$route.params.user_id
    this.fetchData()
  },
  methods: {
    deleteApp(app_id) {
      this.$confirm('此操作将永久删除该应用, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.listLoading = true
        deleteApp({ id: app_id }).then(response => {
          this.$message.success('删除成功')
          this.fetchData()
          this.listLoading = false
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getAppInfos(this.listQuery).then(response => {
        this.list = response.data
        if (this.list && this.list.length > 0) {
          this.type_choices = this.list[0].type_choices
          this.status_choices = this.list[0].status_choices
        }
        this.total = response.total
        this.listLoading = false
      })
    }
  }
}
</script>
