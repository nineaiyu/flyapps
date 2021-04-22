<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.username" placeholder="登录名" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.first_name" placeholder="昵称" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.mobile" placeholder="手机" style="width: 150px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.email" placeholder="邮箱" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.certification" placeholder="实名认证状态" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in certification_status_choices" :key="item.id" :label="item.name" :value="item.id" />
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
      <el-table-column label="头像" align="center">
        <template slot-scope="scope">
          <el-image :src="scope.row.head_img" :preview-src-list="[scope.row.head_img]" fit="contain" style="width: 80px; height: 80px" />
        </template>
      </el-table-column>
      <el-table-column label="登录名">
        <template slot-scope="scope">
          {{ scope.row.username }}
        </template>
      </el-table-column>
      <el-table-column label="昵称">
        <template slot-scope="scope">
          {{ scope.row.first_name }}
        </template>
      </el-table-column>
      <el-table-column label="手机" width="110" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.mobile }}</span>
        </template>
      </el-table-column>
      <el-table-column label="邮箱" width="210" align="center">
        <template slot-scope="scope">
          {{ scope.row.email }}
        </template>
      </el-table-column>

      <el-table-column label="下载次数" width="100" align="center">
        <template slot-scope="scope">
          {{ scope.row.download_times }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="是否激活" width="80" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_active | statusFilter">{{ scope.row.is_active }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="私有存储" width="80" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.storage_active | statusFilter">{{ scope.row.storage_active }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="超级签" width="80" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.supersign_active | statusFilter">{{ scope.row.supersign_active }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="实名认证" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.certification | certStatusFilter">{{ scope.row| certLableFilter }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" prop="created_at" label="注册时间" width="120">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <el-tooltip :content="scope.row.date_joined">
            <span>{{ scope.row.date_joined|formatTime }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="100" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="{name: 'user_info_edit',params:{id:scope.row.id}}">
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
import { getUserInfos } from '@/api/user'
import { baseFilter } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '注册时间 Ascending', key: 'date_joined' },
  { label: '注册时间 Descending', key: '-date_joined' },
  { label: '下载次数 Ascending', key: 'download_times' },
  { label: '下载次数 Descending', key: '-download_times' }
]

export default {
  name: 'UserInfo',
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
    certStatusFilter(status) {
      const statusMap = {
        '-1': 'info',
        '1': 'success',
        '0': 'gray',
        '2': 'danger'
      }
      return statusMap[status]
    },
    certLableFilter(row) {
      return baseFilter(row.certification,row.certification_status_choices)
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
        first_name: undefined,
        certification: undefined,
        sort: '-date_joined',
        email: undefined,
        mobile: undefined
      },
      sortOptions,
      certification_status_choices: []
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
      getUserInfos(this.listQuery).then(response => {
        this.list = response.data
        this.total = response.total
        if (this.list && this.list.length > 0) {
          this.certification_status_choices = this.list[0].certification_status_choices
        }
        this.listLoading = false
      })
    }
  }
}
</script>
