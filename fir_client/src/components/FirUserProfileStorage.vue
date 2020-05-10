<template>
    <div style="text-align:center">
        <h2 v-if="is_admin_storage">管理员存储，您配置的存储将决定其他用户配置的默认存储，请谨慎修改</h2>
        <el-dialog :title="title" :visible.sync="dialogstorageVisible" :destroy-on-close="true"
                   :close-on-click-modal="false">

            <el-form v-if="editstorageinfo.id !==-1" ref="storageinfoform" :model="editstorageinfo"
                     label-width="80px" style="margin:0 auto;">
                <el-form-item label-width="100px" label="存储类型">
                    <el-select :disabled='disabled' v-model="editstorageinfo.storage_type" placeholder="存储类型"
                               style="margin-left: -100px">
                        <el-option v-for="st in storage_list" :key="st.id" :label="st.name" :value="st.id"></el-option>
                    </el-select>
                </el-form-item>

                <div v-if="editstorageinfo.storage_type">
                    <el-form-item label-width="110px" label="存储名称">
                        <el-input :disabled='disabled' v-model="editstorageinfo.name"></el-input>
                    </el-form-item>

                    <el-form-item label-width="110px" label="key">
                        <el-input :disabled='disabled' v-model="editstorageinfo.access_key"></el-input>
                    </el-form-item>
                    <el-form-item label-width="110px" label="secret">
                        <el-input :disabled='disabled' v-model="editstorageinfo.secret_key"></el-input>
                    </el-form-item>

                    <el-form-item label-width="110px" label="bucket_name">
                        <el-input :disabled='disabled' v-model="editstorageinfo.bucket_name"></el-input>
                    </el-form-item>
                    <el-form-item label-width="110px" label="下载域名">
                        <el-input :disabled='disabled' v-model="editstorageinfo.domain_name"></el-input>
                    </el-form-item>

                    <div v-if="editstorageinfo.storage_type === 2">
                        <el-form-item label-width="110px" label="sts_role_arn">
                            <el-input :disabled='disabled'
                                      v-model="editstorageinfo.additionalparameter.sts_role_arn"></el-input>
                        </el-form-item>

                        <el-form-item label-width="110px" label="endpoint">
                            <el-input :disabled='disabled'
                                      v-model="editstorageinfo.additionalparameter.endpoint"></el-input>
                        </el-form-item>

                    </div>

                    <el-form-item label-width="110px" label="备注">
                        <el-input :disabled='disabled' v-model="editstorageinfo.description"></el-input>
                    </el-form-item>

                    <el-button v-if="!disabled" @click="updateorcreate">保存</el-button>
                    <el-button v-if="!disabled" @click="dialogstorageVisible=false">取消</el-button>

                </div>
            </el-form>
        </el-dialog>

        <el-tabs v-model="activeName" @tab-click="handleClick" tab-position="right">
            <el-tab-pane label="存储选择" name="chostorage">


                <el-select v-model="use_storage_id" filterable :placeholder="selectlabel" @change="select_storage">
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
                <el-button style="margin-left: 10px" round type="info" icon="el-icon-thumb"
                           @click="change_storage_info">保存
                </el-button>

                <!--                <el-button-group style="margin-left: 10px">-->
                <!--                    <el-button round type="info" icon="el-icon-edit" @click="change_storage_info"></el-button>-->
                <!--                    <el-button round type="info" icon="el-icon-plus" @click="add_storage_info"></el-button>-->
                <!--                    <el-button round type="info" icon="el-icon-delete" @click="del_storage_info"></el-button>-->
                <!--                </el-button-group>-->
                <el-divider></el-divider>
                <el-form v-if="storageinfo.id && storageinfo.id !==-1" ref="storageinfoform" :model="storageinfo"
                         label-width="80px" style="width: 39%;margin:0 auto;">
                    <el-form-item label-width="110px" label="存储类型">
                        <el-select :disabled='Sdisabled' v-model="storageinfo.storage_type" placeholder="存储类型"
                                   style="margin-left: -60px">
                            <el-option v-for="st in storage_list" :key="st.id" :label="st.name"
                                       :value="st.id"></el-option>
                        </el-select>
                    </el-form-item>

                    <div v-if="storageinfo.storage_type">

                        <el-form-item label-width="110px" label="存储名称">
                            <el-input :disabled='Sdisabled' v-model="storageinfo.name"></el-input>
                        </el-form-item>

                        <el-form-item label-width="110px" label="key">
                            <el-input :disabled='Sdisabled' v-model="storageinfo.access_key"></el-input>
                        </el-form-item>
                        <el-form-item label-width="110px" label="secret">
                            <el-input :disabled='Sdisabled' v-model="storageinfo.secret_key"></el-input>
                        </el-form-item>

                        <el-form-item label-width="110px" label="bucket_name">
                            <el-input :disabled='Sdisabled' v-model="storageinfo.bucket_name"></el-input>
                        </el-form-item>
                        <el-form-item label-width="110px" label="下载域名">
                            <el-input :disabled='Sdisabled' v-model="storageinfo.domain_name"></el-input>
                        </el-form-item>

                        <div v-if="storageinfo.storage_type === 2">
                            <el-form-item label-width="110px" label="sts_role_arn">
                                <el-input :disabled='Sdisabled'
                                          v-model="storageinfo.additionalparameter.sts_role_arn"></el-input>
                            </el-form-item>

                            <el-form-item label-width="110px" label="endpoint">
                                <el-input :disabled='Sdisabled'
                                          v-model="storageinfo.additionalparameter.endpoint"></el-input>
                            </el-form-item>

                            <el-form-item label-width="110px" label="备注">
                                <el-input :disabled='Sdisabled' v-model="storageinfo.description"></el-input>
                            </el-form-item>

                        </div>

                    </div>

                </el-form>

            </el-tab-pane>
            <el-tab-pane label="存储管理" name="setstorage">
                <el-table
                        :data="storage_info_lists"
                        border
                        stripe
                        style="width: 100%">

                    <el-table-column
                            fixed
                            prop="name"
                            label="存储名称"
                            width="180">
                    </el-table-column>
                    <el-table-column
                            prop="storage_type_display"
                            label="存储类型"
                            width="100">
                    </el-table-column>
                    <el-table-column
                            prop="domain_name"
                            label="下载域名"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            prop="bucket_name"
                            label="bucket_name"
                            width="120">
                    </el-table-column>

                    <el-table-column
                            :formatter="formatter"
                            prop="updated_time"
                            label="修改时间"
                            width="170">
                    </el-table-column>
                    <el-table-column
                            prop="description"
                            label="备注"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            fixed="right"
                            label="操作"
                            width="120">
                        <template slot-scope="scope">
                            <div v-if="scope.row.id === org_storage_id">
                                <el-button v-if="scope.row.id === org_storage_id" @click="showstorage(scope.row)"
                                           type="success" size="small">使用中
                                </el-button>
                            </div>
                            <div v-else>
                                <el-button @click="showstorage(scope.row)" type="text" size="small">查看</el-button>
                                <el-button @click="editstorage(scope.row)" type="text" size="small">编辑</el-button>
                                <el-button @click="del_storage_info(scope.row)" type="text" size="small">删除</el-button>
                            </div>

                        </template>
                    </el-table-column>
                </el-table>
            </el-tab-pane>
            <el-tab-pane label="新增存储" name="addstorage">
            </el-tab-pane>

        </el-tabs>

    </div>
</template>

<script>
    import {getStorageinfo} from "../restful";
    import {deepCopy} from "../utils";

    export default {
        name: "FirUserProfileStorage",
        data() {
            return {
                fstorage_lists: [],
                Sdisabled: true,
                use_storage_id: 0,
                org_storage_id: 0,
                title: '',
                dialogstorageVisible: false,
                editstorageinfo: {'additionalparameter': {}},
                selectlabel: "",
                storageinfo: {'additionalparameter': {}},
                storage_list: [],
                disabled: true,
                isaddflag: false,
                activeName: 'chostorage',
                storage_info_lists: [],
                is_admin_storage: false,
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
            }, add_storage_click() {
                this.title = '新增存储';
                this.disabled = false;
                this.dialogstorageVisible = true;
                this.editstorageinfo = {'additionalparameter': {}};
                this.isaddflag = true;
            },
            // eslint-disable-next-line no-unused-vars
            handleClick(tab, event) {
                if (tab.name === 'addstorage') {
                    this.add_storage_click()
                }
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
                            this.activeName = 'setstorage';
                        }
                        this.getstorageinfoFun();

                    }
                }, {"methods": methods, 'data': this.editstorageinfo});
                this.getstorageinfoFun();
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
            change_storage_info() {
                this.$confirm('此操作将导致应用，图片，显示下载异常, 是否继续?', '警告', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    getStorageinfo(data => {
                        if (data.code === 1000) {
                            this.$message.success('修改成功');
                            this.getstorageinfoFun();
                        }
                    }, {"methods": 'PUT', 'data': {'use_storage_id': this.use_storage_id}});
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
        }, mounted() {
            this.$store.dispatch('douserInfoIndex', 2);
            this.getstorageinfoFun();
        }, filters: {}
    }
</script>

<style scoped>

</style>
