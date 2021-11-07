<template>
  <el-main>
    <h2 v-if="is_admin_storage">管理员存储，您配置的存储将决定其他用户配置的默认存储，请谨慎修改</h2>
    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :title="title"
               :visible.sync="dialogstorageVisible">

      <el-form v-if="editstorageinfo.id !==-1" ref="storageinfoform" :model="editstorageinfo"
               label-width="80px" style="margin:0 auto;">
        <el-form-item label="存储类型" label-width="100px">
          <el-select v-model="editstorageinfo.storage_type" :disabled='disabled' placeholder="存储类型"
                     style="margin-left: -100px">
            <el-option v-for="st in storage_list" :key="st.id" :label="st.name" :value="st.id"/>
          </el-select>
        </el-form-item>

        <div v-if="editstorageinfo.storage_type">
          <el-form-item label="存储名称" label-width="110px">
            <el-input v-model="editstorageinfo.name" :disabled='disabled'/>
          </el-form-item>

          <el-form-item label="key" label-width="110px">
            <el-input v-model="editstorageinfo.access_key" :disabled='disabled'/>
          </el-form-item>
          <el-form-item label="secret" label-width="110px">
            <el-input v-model="editstorageinfo.secret_key" :disabled='disabled' placeholder="为空表示不修改该信息"/>
          </el-form-item>

          <el-form-item label="bucket_name" label-width="110px">
            <el-input v-model="editstorageinfo.bucket_name" :disabled='disabled'/>
          </el-form-item>
          <el-form-item label="下载域名" label-width="110px">
            <el-input v-model="editstorageinfo.domain_name" :disabled='disabled'/>
          </el-form-item>

          <div v-if="editstorageinfo.storage_type === 2">
            <el-form-item label="sts_role_arn" label-width="110px">
              <el-input v-model="editstorageinfo.sts_role_arn"
                        :disabled='disabled'/>
            </el-form-item>

            <el-form-item label="endpoint" label-width="110px">
              <el-input v-model="editstorageinfo.endpoint"
                        :disabled='disabled'/>
            </el-form-item>

            <el-form-item label="下载授权方式" label-width="110px">
              <el-select v-model="editstorageinfo.download_auth_type"
                         :disabled="disabled"
                         placeholder="下载授权方式" style="width: 80%">
                <el-option v-for="st in editstorageinfo.download_auth_type_choices" :key="st.id"
                           :label="st.name"
                           :value="st.id"/>
              </el-select>

              <el-form-item v-if="editstorageinfo.download_auth_type === 2" label="CDN鉴权主KEY"
                            label-width="120px"
                            style="margin-top: 10px;margin-left: 70px;width: 60%">
                <el-input v-model="editstorageinfo.cnd_auth_key" :disabled='disabled'
                          placeholder="CDN鉴权主KEY"/>
              </el-form-item>

            </el-form-item>

          </div>

          <el-form-item label="备注" label-width="110px">
            <el-input v-model="editstorageinfo.description" :disabled='disabled'/>
          </el-form-item>

          <el-button v-if="!disabled" @click="updateorcreate">保存</el-button>
          <el-button v-if="!disabled" @click="dialogstorageVisible=false">取消</el-button>

        </div>
      </el-form>
    </el-dialog>

    <el-tabs v-model="activeName" tab-position="top" type="border-card" @tab-click="handleClick">
      <el-tab-pane label="存储选择" name="change">
        <el-select v-model="use_storage_id" :placeholder="selectlabel" filterable @change="select_storage">
          <el-option-group
              v-for="storage_group in fstorage_lists"
              :key="storage_group.group_name"
              :label="storage_group.group_name">
            <el-option
                v-for="storage in storage_group.storages"
                :key="storage.id"
                :label="storage.name"
                :value="storage.id">
            </el-option>
          </el-option-group>
        </el-select>
        <div v-if="use_storage_id!==org_storage_id" style="margin-top: 20px">
          <el-button icon="el-icon-thumb" round style="margin-left: 10px"
                     type="info"
                     @click="change_storage_info(0)">
            迁移数据并保存
          </el-button>
          <el-button icon="el-icon-thumb" round style="margin-left: 10px"
                     type="danger"
                     @click="change_storage_info(1)">
            强制迁移，忽略数据迁移失败错误，可能会导致数据丢失
          </el-button>
        </div>
        <el-divider/>
        <el-form v-if="storageinfo.id && storageinfo.id !==-1" ref="storageinfoform" :model="storageinfo"
                 label-width="80px" style="width: 39%;margin:0 auto;">
          <el-form-item label="存储类型" label-width="110px">
            <el-select v-model="storageinfo.storage_type" :disabled='Sdisabled' placeholder="存储类型"
                       style="margin-left: -60px">
              <el-option v-for="st in storage_list" :key="st.id" :label="st.name"
                         :value="st.id"/>
            </el-select>
          </el-form-item>

          <div v-if="storageinfo.storage_type">

            <el-form-item label="存储名称" label-width="110px">
              <el-input v-model="storageinfo.name" :disabled='Sdisabled'/>
            </el-form-item>

            <el-form-item label="key" label-width="110px">
              <el-input v-model="storageinfo.access_key" :disabled='Sdisabled'/>
            </el-form-item>
            <el-form-item label="bucket_name" label-width="110px">
              <el-input v-model="storageinfo.bucket_name" :disabled='Sdisabled'/>
            </el-form-item>
            <el-form-item label="下载域名" label-width="110px">
              <el-input v-model="storageinfo.domain_name" :disabled='Sdisabled'/>
            </el-form-item>

            <div v-if="storageinfo.storage_type === 2">
              <el-form-item label="sts_role_arn" label-width="110px">
                <el-input v-model="storageinfo.sts_role_arn"
                          :disabled='Sdisabled'/>
              </el-form-item>

              <el-form-item label="endpoint" label-width="110px">
                <el-input v-model="storageinfo.endpoint"
                          :disabled='Sdisabled'/>
              </el-form-item>

              <el-form-item label="下载授权方式" label-width="110px">
                <el-select v-model="storageinfo.download_auth_type"
                           :disabled="disabled"
                           placeholder="下载授权方式" style="width: 100%">
                  <el-option v-for="st in storageinfo.download_auth_type_choices" :key="st.id"
                             :label="st.name"
                             :value="st.id"/>
                </el-select>

                <el-form-item v-if="storageinfo.download_auth_type === 2" label="CDN鉴权主KEY" label-width="120px"
                              style="margin-top: 10px;width: 100%">
                  <el-input v-model="storageinfo.cnd_auth_key" :disabled='disabled'
                            placeholder="CDN鉴权主KEY"/>
                </el-form-item>

              </el-form-item>

            </div>
            <el-form-item label="备注" label-width="110px">
              <el-input v-model="storageinfo.description" :disabled='Sdisabled'/>
            </el-form-item>

          </div>

        </el-form>

      </el-tab-pane>
      <el-tab-pane label="存储管理" name="edit">
        <el-table
            v-loading="loading"
            :data="storage_info_lists"
            border
            stripe
            style="width: 100%">

          <el-table-column
              fixed
              label="存储名称"
              prop="name"
              width="180">
          </el-table-column>
          <el-table-column
              label="存储类型"
              prop="storage_type_display"
              width="100">
          </el-table-column>
          <el-table-column
              label="下载域名"
              prop="domain_name">
          </el-table-column>
          <el-table-column
              label="bucket_name"
              prop="bucket_name"
              width="130">
          </el-table-column>

          <el-table-column
              :formatter="formatter"
              label="修改时间"
              prop="updated_time"
              width="170">
          </el-table-column>
          <el-table-column
              label="备注"
              prop="description">
          </el-table-column>
          <el-table-column
              fixed="right"
              label="操作"
              width="120">
            <template slot-scope="scope">
              <div v-if="scope.row.id === org_storage_id">
                <el-button v-if="scope.row.id === org_storage_id" size="small"
                           type="success" @click="showstorage(scope.row)">使用中
                </el-button>
              </div>
              <div v-else>
                <el-button size="small" type="text" @click="showstorage(scope.row)">查看</el-button>
                <el-button size="small" type="text" @click="editstorage(scope.row)">编辑</el-button>
                <el-button size="small" type="text" @click="del_storage_info(scope.row)">删除</el-button>
              </div>

            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="存储新增" name="add">
        <el-form ref="storageinfoform" :model="editstorageinfo"
                 label-width="80px" style="margin:0 auto;">
          <el-form-item label="存储类型" label-width="100px">
            <el-select v-model="editstorageinfo.storage_type" placeholder="存储类型"
                       style="margin-left: -100px">
              <el-option v-for="st in storage_list" :key="st.id" :label="st.name"
                         :value="st.id"/>
            </el-select>
          </el-form-item>

          <div v-if="editstorageinfo.storage_type">
            <el-form-item label="存储名称" label-width="110px">
              <el-input v-model="editstorageinfo.name"/>
            </el-form-item>

            <el-form-item label="key" label-width="110px">
              <el-input v-model="editstorageinfo.access_key"/>
            </el-form-item>
            <el-form-item label="secret" label-width="110px">
              <el-input v-model="editstorageinfo.secret_key"/>
            </el-form-item>

            <el-form-item label="bucket_name" label-width="110px">
              <el-input v-model="editstorageinfo.bucket_name"/>
            </el-form-item>
            <el-form-item label="下载域名" label-width="110px">
              <el-input v-model="editstorageinfo.domain_name"/>
            </el-form-item>

            <div v-if="editstorageinfo.storage_type === 2">
              <el-form-item label="sts_role_arn" label-width="110px">
                <el-input
                    v-model="editstorageinfo.sts_role_arn"/>
              </el-form-item>

              <el-form-item label="endpoint" label-width="110px">
                <el-input
                    v-model="editstorageinfo.endpoint"/>
              </el-form-item>

              <el-form-item label="下载授权方式" label-width="110px">
                <el-select v-model="editstorageinfo.download_auth_type"
                           placeholder="下载授权方式"
                           style="width: 80%">
                  <el-option v-for="st in editstorageinfo.download_auth_type_choices" :key="st.id"
                             :label="st.name"
                             :value="st.id"/>
                </el-select>

                <el-form-item v-if="editstorageinfo.download_auth_type === 2" label="CDN鉴权主KEY"
                              label-width="120px"
                              style="margin-top: 10px;margin-left: 70px;width: 60%">
                  <el-input v-model="editstorageinfo.cnd_auth_key"
                            placeholder="CDN鉴权主KEY"/>
                </el-form-item>

              </el-form-item>

            </div>

            <el-form-item label="备注" label-width="110px">
              <el-input v-model="editstorageinfo.description"/>
            </el-form-item>

            <el-button @click="updateorcreate">校验并保存</el-button>
          </div>
        </el-form>
      </el-tab-pane>

    </el-tabs>

  </el-main>
</template>

<script>
import {getStorageinfo} from "@/restful";
import {deepCopy, getUserInfoFun} from "@/utils";

export default {
  name: "FirUserStorage",
  data() {
    return {
      fstorage_lists: [],
      Sdisabled: true,
      use_storage_id: 0,
      org_storage_id: 0,
      title: '',
      dialogstorageVisible: false,
      editstorageinfo: {},
      selectlabel: "",
      storageinfo: {},
      storage_list: [],
      disabled: true,
      isaddflag: false,
      activeName: 'change',
      storage_info_lists: [],
      is_admin_storage: false,
      loading: false,
    }
  }, methods: {
    showstorage(editstorageinfo) {
      this.title = '查看存储信息';
      this.disabled = true;
      this.dialogstorageVisible = true;
      this.editstorageinfo = deepCopy(editstorageinfo);
    },
    editstorage(editstorageinfo) {
      this.title = '存储编辑';
      this.disabled = false;
      this.dialogstorageVisible = true;
      this.editstorageinfo = deepCopy(editstorageinfo);
      this.isaddflag = false;
    },
    // eslint-disable-next-line no-unused-vars
    handleClick(tab, event) {
      this.get_data_from_tabname(tab.name);
    },
    updateorcreate() {
      let methods = "PUT";
      if (this.isaddflag) {
        if (this.editstorageinfo.access_key && this.editstorageinfo.secret_key && this.editstorageinfo.bucket_name) {
          methods = "POST";
        } else {
          this.$message.error("参数不正确");
          return
        }
      }
      getStorageinfo(data => {
        if (data.code === 1000) {
          this.$message.success('操作成功');
          this.dialogstorageVisible = false;
          if (this.isaddflag) {
            this.activeName = 'edit';
          }
          this.get_data_from_tabname(this.activeName);

        } else {
          this.$message.error('操作失败，' + data.msg);
        }
      }, {"methods": methods, 'data': this.editstorageinfo});
    }, del_storage_info(sinfo) {

      this.$confirm('此操作可能会导致程序异常, 是否继续?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        getStorageinfo(data => {
          if (data.code === 1000) {
            this.$message.success('删除成功');
            this.getstorageinfoFun();
          }
        }, {"methods": 'DELETE', 'data': {'id': sinfo.id, 'tid': sinfo.storage_type}})
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });

    },
    change_storage_info(force) {
      this.$confirm('此操作将导致应用，图片，显示下载异常, 是否继续?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({
          lock: true,
          text: '执行中,请耐心等待...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
        getStorageinfo(data => {
          loading.close();
          if (data.code === 1000) {
            this.$message.success('修改成功');
            this.getstorageinfoFun();
          } else {
            this.$message.error(data.msg)
          }
        }, {"methods": 'PUT', 'data': {'use_storage_id': this.use_storage_id, 'force': force}});
        this.getstorageinfoFun();
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        });
      });
    },
    select_storage(a) {
      this.disabled = true;
      this.getstorageinfobyid(a);
    },
    getstorageinfobyid(id) {
      for (let i = 0; i < this.fstorage_lists.length; i++) {
        let storages = this.fstorage_lists[i].storages;
        for (let j = 0; j < storages.length; j++) {
          if (id === storages[j].id) {
            this.storageinfo = storages[j];
            break
          }
        }
      }

    },
    format_storage(storage_data_lists) {
      let storage_f = [];
      let storage_lists = {};
      for (let key in storage_data_lists) {
        let storage = storage_data_lists[key];
        let storage_type = storage.storage_type;
        if (!storage_lists[storage_type]) {
          storage_lists[storage_type] = [];
        }
        storage_lists[storage_type].unshift(storage);
      }
      for (let key in storage_lists) {
        let storage = storage_lists[key];
        if (storage[0].storage_type_display) {
          storage_f.unshift({'group_name': storage[0].storage_type_display, 'storages': storage})
        }
        if (!this.selectlabel) {
          for (let i = 0; i < storage.length; i++) {
            if (this.use_storage_id === storage[i].id) {
              this.selectlabel = storage[i].name;
              break
            }
          }
        }
      }

      storage_f.unshift({'group_name': '默认存储', 'storages': [{'id': -1, 'name': '默认存储'}]});
      if (!this.selectlabel) {
        this.selectlabel = "默认存储"
      }
      this.fstorage_lists = storage_f.slice();
      this.getstorageinfobyid(this.use_storage_id)

    },
    getstorageinfoFun() {
      this.loading = true;
      getStorageinfo(data => {
        if (data.code === 1000) {
          this.org_storage_id = this.use_storage_id = data.storage;
          this.storage_list = data.storage_list;
          this.storage_info_lists = data.data;
          this.is_admin_storage = data.is_admin_storage;
          this.format_storage(data.data);
          this.disabled = true;
          this.isaddflag = false;
        } else {
          this.$message.error('存储获取失败,' + data);
        }
        this.loading = false;
      }, {"methods": 'GET'});
    },
    // eslint-disable-next-line no-unused-vars
    formatter(row, column) {
      let stime = row.updated_time;
      if (stime) {
        stime = stime.split(".")[0].split("T");
        return stime[0] + " " + stime[1]
      } else
        return '';
    },
    // eslint-disable-next-line no-unused-vars
    get_data_from_tabname(tabname, data = {}) {
      this.$router.push({"name": 'FirUserStorage', params: {act: tabname}});
      if (tabname === "change") {
        this.getstorageinfoFun();
      } else if (tabname === "edit") {
        this.getstorageinfoFun();
      } else if (tabname === "add") {
        getStorageinfo(data => {
          if (data.code === 1000) {
            this.storage_list = data.storage_list;
            this.editstorageinfo = {
              download_auth_type: 1,
              storage_type: this.storage_list[0].id,
              download_auth_type_choices: data.download_auth_type_choices
            };
            this.isaddflag = true;
          } else {
            this.$message.error('存储列表获取失败,' + data);
          }
        }, {"methods": 'GET', "data": {'act': 'storage_type'}});
      }
    },
  }, mounted() {
    getUserInfoFun(this);
    if (this.$route.params.act) {
      let activeName = this.$route.params.act;
      let activeName_list = ["change", "edit", "add"];
      for (let index in activeName_list) {
        if (activeName_list[index] === activeName) {
          this.activeName = activeName;
          this.get_data_from_tabname(activeName);
          return
        }
      }
    }
    this.get_data_from_tabname(this.activeName);
  }, filters: {}
}
</script>

<style scoped>
.el-main {
  text-align: center;
  margin: 20px auto 100px;
  width: 1166px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}
</style>
