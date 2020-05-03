<template>
    <el-main>

        <el-dialog :title="title" :visible.sync="dialogaddDeveloperVisible" :destroy-on-close="true" :close-on-click-modal="false" style="text-align:center">

            <el-form  ref="storageinfoform" :model="editdeveloperinfo"
                     label-width="80px" style="margin:0 auto;">

                    <el-form-item label-width="110px" label="APP_ID">
                        <el-input :disabled='isedit' v-model="editdeveloperinfo.email" ></el-input>
                    </el-form-item>

                    <el-form-item label-width="110px" label="password">
                        <el-input  v-model="editdeveloperinfo.password" :placeholder="placeholder"></el-input>
                    </el-form-item>
                    <el-form-item label-width="110px" label="设备数量">
                        <el-input  v-model="editdeveloperinfo.usable_number"></el-input>
                    </el-form-item>

                    <el-form-item label-width="110px" label="备注">
                        <el-input  v-model="editdeveloperinfo.description"></el-input>
                    </el-form-item>
                    <div style="" >
                        <el-button  @click="updateorcreate">保存</el-button>
                        <el-button  @click="canceledit">取消</el-button>
                    </div>


            </el-form>
        </el-dialog>


        <el-dialog
                title="请输入验证码"
                :visible.sync="codeactiveVisible"
                width="30%"
                center>
            <span slot="footer" class="dialog-footer">
                <el-button @click="codeactiveVisible = false">取 消</el-button>
                <el-button type="primary" @click="codeactiveVisible = false">确 定</el-button>
          </span>
        </el-dialog>



        <el-tabs v-model="activeName" type="border-card" @tab-click="handleClick" tab-position="top">
            <el-tab-pane label="开发者账户" name="iosdeveloper">
                <el-table
                        :data="app_developer_lists"
                        border
                        stripe
                        style="width: 100%">

                    <el-table-column
                            fixed
                            prop="email"
                            label="用户"
                            width="220">
                    </el-table-column>
                    <el-table-column
                            prop="is_actived"
                            label="是否激活"
                            width="110">
                        <template slot-scope="scope" >
                            <el-button v-if="scope.row.is_actived === true"  type="success" size="small">已激活</el-button>
                            <el-button v-else  type="danger" size="small" @click="activedeveloperFun(scope.row)">点击激活</el-button>

                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="usable_number"
                            label="可用设备数"
                            width="100">
                    </el-table-column>

                    <el-table-column
                            prop="use_number"
                            label="已消耗设备数"
                            width="120">
                    </el-table-column>

                    <el-table-column
                            :formatter="formatter"
                            prop="updated_time"
                            label="更新时间"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            prop="description"
                            label="备注"
                            >
                    </el-table-column>
                    <el-table-column
                            fixed="right"
                            label="操作"
                            width="150">
                        <template slot-scope="scope" >

                            <el-button
                                    size="mini"
                                    @click="handleEditDeveloper(scope.row)">编辑</el-button>
                            <el-button
                                    size="mini"
                                    type="danger"
                                    @click="handleDelete(scope.$index, scope.row)">删除</el-button>

                        </template>
                    </el-table-column>
                </el-table>


            </el-tab-pane>
            <el-tab-pane label="添加开发者" name="adddeveloper">添加开发者</el-tab-pane>
            <el-tab-pane label="设备消耗" name="useddevices">
                <el-table
                        :data="app_devices_lists"
                        border
                        stripe
                        style="width: 100%">
                    <el-table-column
                            fixed
                            prop="device_udid"
                            label="设备ID"
                            >
                    </el-table-column>
                    <el-table-column
                            prop="device_name"
                            label="设备名称"
                            width="120">
                    </el-table-column>
                    <el-table-column
                            prop="bundle_id"
                            label="应用ID"
                            width="180">
                    </el-table-column>
                    <el-table-column
                            prop="bundle_name"
                            label="应用名称"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            prop="developer_id"
                            label="开发者ID"
                            width="200">
                    </el-table-column>
                    <el-table-column
                            :formatter="deviceformatter"
                            prop="created_time"
                            label="授权时间"
                            width="160">
                    </el-table-column>
                </el-table>


            </el-tab-pane>
            <el-tab-pane label="设备管理" name="devicesudid">
                <el-input
                        style="width: 30%;margin-right: 30px;margin-bottom: 10px"
                        v-model="udidsearch"
                        clearable
                        placeholder="输入UDID" />
                <el-input
                        style="width: 20%;margin-right: 30px;margin-bottom: 10px"
                        v-model="Bundleidsearch"
                        clearable
                        placeholder="输入BundleID" />
                <el-button type="primary" icon="el-icon-search" @click="iosdevicesudidFun('GET',{udid:udidsearch,bundleid:Bundleidsearch})">搜索</el-button>
                <el-table
                        :data="app_udid_lists"
                        border
                        stripe
                        style="width: 100%">

                    <el-table-column
                            fixed
                            prop="udid"
                            label="设备ID"
                            >
                        <template slot-scope="scope">
                            <el-popover trigger="hover" placement="top">
                                <p>Bundle_ID: {{ scope.row.bundle_id }}</p>
                                <p>应用名称: {{ scope.row.bundle_name }}</p>
                                <p>UDID: {{ scope.row.udid }}</p>
                                <div slot="reference" class="name-wrapper">
                                    <el-tag size="medium">{{ scope.row.udid }}</el-tag>
                                </div>
                            </el-popover>
                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="imei"
                            label="imei"
                            width="180">

                    </el-table-column>
                    <el-table-column
                            prop="product"
                            label="设备名称"
                            width="100">
                    </el-table-column>
                    <el-table-column
                            prop="version"
                            label="设备型号"
                            width="100">
                    </el-table-column>
                    <el-table-column
                            prop="serial"
                            label="设备序列号"
                            width="150">
                    </el-table-column>
                    <el-table-column
                            :formatter="deviceformatter"
                            prop="created_time"
                            label="添加时间"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            fixed="right"
                            label="操作"
                            width="80">
                        <template slot-scope="scope" >
                            <el-button
                                    size="mini"
                                    type="danger"
                                    @click="iosdevicesudidFun('DELETE',{id:scope.row.id,aid:scope.row.app_id})">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>

            </el-tab-pane>
        </el-tabs>

    </el-main>
</template>

<script>

    import {iosdeveloper, iosdevices,iosdevicesudid } from "../restful";

    export default {
        name: "FirSuperSignBase",
        data() {
            return {
                app_developer_lists:[],
                app_devices_lists:[],
                app_udid_lists:[],
                activeName:"iosdeveloper",
                udidsearch:"",
                Bundleidsearch:"",
                dialogaddDeveloperVisible:false,
                title:"",
                editdeveloperinfo:{},
                isedit:false,
                placeholder:"",
                codeactiveVisible:false,

            }
        },
        methods: {
            IsNum(s){
                if(s!=null){
                    var r,re;
                    re = /\d*/i; //\d表示数字,*表示匹配多个数字
                    r = s.match(re);
                    return (r==s)?true:false;
                }
                return false;
            },
    inputcode(developer){
                this.$prompt('请输入验证码', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    closeOnClickModal:false,
                }).then(({ value }) => {
                    if(value.toString().length>5 && this.IsNum(value)){
                        this.iosdeveloperFun({"methods":"PUT","data":{"email":developer.email,"act":"nowactive","code":value}});
                    }
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '取消激活'
                    });
                });
            },
            activedeveloperFun(developer){
                this.iosdeveloperFun({"methods":"PUT","data":{"email":developer.email,"act":"preactive"}});
                this.inputcode(developer)
            },
            canceledit(){
                this.dialogaddDeveloperVisible=false;
                this.editdeveloperinfo={};
                this.isedit=false;
                this.placeholder=""
            },
            handleEditDeveloper(developer_info){
                this.editdeveloperinfo=developer_info;
                this.title='编辑开发者账户';
                this.dialogaddDeveloperVisible=true;
                this.isedit=true;
                this.placeholder="为空表示不修改密码"
            },
            updateorcreate(){
                if(this.isedit){
                    this.iosdeveloperFun({"methods":"PUT","data":this.editdeveloperinfo})
                }else {
                    if(this.editdeveloperinfo.email && this.editdeveloperinfo.password  && this.editdeveloperinfo.usable_number ){
                        this.iosdeveloperFun({"methods":"POST","data":this.editdeveloperinfo});
                    }else {
                        this.$message.warning("输入格式有误")
                    }
                }
            },
            handleDelete(b){
                // eslint-disable-next-line no-console
                console.log(b)
            },
            handleClick(tab, event) {
                // eslint-disable-next-line no-console
                console.log(tab, event);
                if(tab.name === "useddevices"){
                    this.iosdevicesFun()
                }else if(tab.name === "devicesudid"){
                    this.iosdevicesudidFun('GET')
                }else if(tab.name === "adddeveloper"){
                    this.title='新增私有开发者账户';
                    this.dialogaddDeveloperVisible=true;
                }

            },
            // eslint-disable-next-line no-unused-vars
            deviceformatter(row, column){
                let stime = row.created_time;
                if (stime) {
                    stime = stime.split(".")[0].split("T");
                    return stime[0] + " " + stime[1]
                } else
                    return '';
            },
            // eslint-disable-next-line no-unused-vars
            formatter(row, column){
                let stime = row.updated_time;
                if (stime) {
                    stime = stime.split(".")[0].split("T");
                    return stime[0] + " " + stime[1]
                } else
                    return '';
            },
            iosdevicesFun(){
                iosdevices(data=>{
                    if(data.code === 1000){
                        this.app_devices_lists = data.data;
                        // eslint-disable-next-line no-console
                        console.log(data)
                    }
                },{
                    "methods":"GET"
                })
            },
            iosdeveloperFun(params){
                iosdeveloper(data=>{
                    if(data.code === 1000){
                        this.app_developer_lists = data.data;
                        this.$store.dispatch("getUser",data.userinfo);
                        this.$store.dispatch('doucurrentapp', {});
                        if(this.dialogaddDeveloperVisible){
                            this.canceledit();
                            this.$message.success("操作成功");
                            this.activeName="iosdeveloper";
                            this.editdeveloperinfo={};

                        }
                    }
                    else if(data.code === 1008){
                        this.$message.error(data.msg);
                    }
                    else {
                        this.$message.error("操作失败")
                    }
                },params)
            },
            iosdevicesudidFun(action,data){
                iosdevicesudid(data=>{
                    if(data.code === 1000){
                        this.app_udid_lists = data.data;
                    }
                },{
                    "methods":action,"data":data
                })
            }

        }, mounted() {
                this.iosdeveloperFun({"methods":"GET"})
        }, watch: {
            // eslint-disable-next-line no-unused-vars
            udidsearch: function (val, oldVal) {
                // this.searchapps()
            },
        },filters:{

        },computed:{

        }
    }
</script>

<style scoped>
    .el-main {
        margin: 10px auto 100px;
        width: 1166px;
        position: relative;
        padding-bottom: 1px;
        background-color: #bfe7f9;
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }

</style>
