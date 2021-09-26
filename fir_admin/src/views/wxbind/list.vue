<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.user_id" placeholder="用户ID" style="width: 140px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.openid" placeholder="微信openid" style="width: 300px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.nickname" placeholder="微信昵称" style="width: 200px;" class="filter-item" clearable @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.subscribe" placeholder="玩家是否订阅" clearable class="filter-item" style="width: 140px" @change="handleFilter">
        <el-option v-for="item in wxbind_state_choices" :key="item.id" :label="item.name" :value="item.id" />
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
      <el-table-column label="头像" align="center">
        <template slot-scope="scope">
          <el-image :src="scope.row.head_img_url" :preview-src-list="[scope.row.head_img_url]" fit="contain" style="width: 80px; height: 80px" />
        </template>
      </el-table-column>
      <el-table-column label="微信昵称" min-width="180px" align="center">
        <template slot-scope="scope">
          {{ scope.row.nickname }}
        </template>
      </el-table-column>
      <el-table-column label="微信openid" min-width="280px" align="center">
        <template slot-scope="scope">
          {{ scope.row.openid }}
        </template>
      </el-table-column>
      <el-table-column label="地址" min-width="200px" align="center">
        <template slot-scope="scope">
          {{ scope.row.address }}
        </template>
      </el-table-column>
      <el-table-column label="性别" min-width="60px" align="center">
        <template slot-scope="scope">
          {{ scope.row |sexLableFilter }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="订阅状态" width="95" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.subscribe | statusFilter">{{ scope.row| statusLableFilter }}</el-tag>
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
          <router-link :to="{name: 'wxbind_info_edit',params:{id:scope.row.id}}">
            <el-button type="primary" size="mini">
              查看编辑
            </el-button>
          </router-link>
          <el-button type="danger" size="mini" @click="remove_wxbind(scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />

  </div>
</template>

<script>
import { getWxBindInfos, deleteWxBind } from '@/api/wxbind'
import { baseFilter } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import waves from '@/directive/waves' // waves directive

const sortOptions = [
  { label: '创建时间 Ascending', key: 'created_time' },
  { label: '创建时间 Descending', key: '-created_time' }
]

const wxbind_state_choices = [
  { id: false, name: '未订阅' },
  { id: true, name: '已订阅' }
]

const wxbind_sex_choices = [
  { id: 0, name: '未知' },
  { id: 1, name: '男' },
  { id: 2, name: '女' }
]

export default {
  name: 'WxBindInfo',
  components: { Pagination },
  directives: { waves },
  filters: {
    formatTime(time) {
      if (time) {
        return time.split('T')[0]
      }
    },
    wxbindStatusFilter(status) {
      const statusMap = {
        '1': 'success',
        '0': 'gray',
        '2': 'info' }
      return statusMap[status]
    },
    wxbindLableFilter(row) {
      if (row.wxbind_type === 2) {
        return '应用' + row.app_info.name + '域名'
      }
      return baseFilter(row.wxbind_type, row.wxbind_type_choices)
    },
    statusLableFilter(row) {
      return baseFilter(row.subscribe, wxbind_state_choices)
    },
    sexLableFilter(row) {
      return baseFilter(row.sex, wxbind_sex_choices)
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
        sort: '-created_time',
        openid: undefined,
        nickname: undefined,
        subscribe: undefined
      },
      sortOptions,
      wxbind_state_choices
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
    remove_wxbind(wxbind_id) {
      deleteWxBind({ id: wxbind_id }).then(response => {
        this.list = response.data
        this.total = response.total
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },
    fetchData() {
      this.listLoading = true
      getWxBindInfos(this.listQuery).then(response => {
        this.list = response.data
        this.total = response.total
        this.listLoading = false
      })
    }
  }
}
</script>
