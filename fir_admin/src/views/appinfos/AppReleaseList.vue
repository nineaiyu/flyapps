<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.release_id" placeholder="release_id" style="width: 250px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
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
          <el-image :src="scope.row.icon_url" :preview-src-list="[scope.row.icon_url]" fit="contain" style="width: 80px; height: 80px" />
        </template>
      </el-table-column>

      <el-table-column label="Release_Id" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.release_id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="第三方下载URL" align="center">
        <template slot-scope="scope">
          {{ scope.row.binary_url }}
        </template>
      </el-table-column>
      <el-table-column label="更新日志" align="center">
        <template slot-scope="scope">
          {{ scope.row.changelog }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="Master" width="120" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_master | statusFilter">{{ scope.row.is_master }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="版本类型" width="120" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.release_type | appStatusFilter">{{ scope.row |appStatusNameFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="应用大小" align="center" width="80">
        <template slot-scope="scope">
          <span>{{ scope.row.binary_size }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_time" label="上传时间" width="180">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.created_time">
            <span>{{ scope.row.created_time|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="100" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="{name: 'app_release_info_edit',params:{app_id:listQuery.app_id,id:scope.row.id}}">
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
import { getAppReleaseInfos } from '@/api/app'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '上传时间 Ascending', key: 'created_time' },
  { label: '上传时间 Descending', key: '-created_time' }
]

export default {
  name: 'AppInfo',
  components: { Pagination },
  directives: { waves },
  filters: {
    formatTime(time) {
      return time.replace('T', ' ').split('.')[0]
    },
    statusFilter(status) {
      const statusMap = {
        true: 'success',
        false: 'danger'
      }
      return statusMap[status]
    },
    appStatusNameFilter(row) {
      for (const r of row.release_choices) {
        if (r.id === row.release_type) {
          return r.name
        }
      }
    },
    appStatusFilter(status) {
      const statusMap = {
        '0': 'info',
        '1': 'success',
        '2': 'gray',
        '3': 'danger'
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
        release_id: undefined,
        sort: '-created_time'
      },
      sortOptions,
      type_choices: [],
      status_choices: []
    }
  },
  created() {
    this.listQuery.app_id = this.$route.params && this.$route.params.app_id
    this.fetchData()
  },
  methods: {
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getAppReleaseInfos(this.listQuery).then(response => {
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
