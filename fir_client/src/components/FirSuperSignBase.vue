<template>
    <el-main>
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
                            width="100">
                        <template slot-scope="scope" >
                            <el-button v-if="scope.row.is_actived === true"  type="success" size="small">已激活</el-button>
                            <el-button v-else  type="danger" size="small">未激活</el-button>

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
                                    @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
                            <el-button
                                    size="mini"
                                    type="danger"
                                    @click="handleDelete(scope.$index, scope.row)">删除</el-button>

                        </template>
                    </el-table-column>
                </el-table>


            </el-tab-pane>
            <el-tab-pane label="添加开发者">添加开发者</el-tab-pane>
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
                Bundleidsearch:""
            }
        },
        methods: {
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
            iosdeveloperFun(){
                iosdeveloper(data=>{
                    if(data.code === 1000){
                        this.app_developer_lists = data.data;
                        this.$store.dispatch("getUser",data.userinfo);
                        this.$store.dispatch('doucurrentapp', {});
                        // eslint-disable-next-line no-console
                        console.log(data)
                    }
                },{
                    "methods":"GET"
                })
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
                this.iosdeveloperFun()
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
