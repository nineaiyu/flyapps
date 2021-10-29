<template>


    <div style="margin-top: 20px;width: 66%;margin-left: 8%">
        <el-form label-width="80px" v-if="currentapp.type === 1 && $store.state.userinfo.supersign_active">


            <el-form-item label-width="200px"
                          label="超级签名">

                <el-tooltip :content="supersign.msg" placement="top">
                    <el-switch
                            @change="supersignevent"
                            v-model="supersign.val"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>
                </el-tooltip>
                <el-button @click="clean_app" v-if="!currentapp.issupersign && currentapp.count !== 0"
                           style="margin-left: 20px" size="small" type="info" plain>清理该应用脏数据
                </el-button>
                <el-link v-else :underline="false" style="margin-left: 20px">超级签名，iOS专用，需要配置好苹果开发者账户，方可开启</el-link>

            </el-form-item>

            <el-form-item label-width="200px" label="签名限额">


                <el-tooltip content="本应用签名使用额度，超过该额度，新设备将无法安装本应用。0代表不限额" placement="top">
                    <el-input-number v-model="currentapp.supersign_limit_number" :disabled="supersign_disable" :min="0"
                                     style="width: 40%;margin-right: 10px" label="签名限额"/>
                </el-tooltip>

                <el-button @click="saveappinfo({supersign_limit_number:currentapp.supersign_limit_number})"
                           :disabled="supersign_disable"
                >保存
                </el-button>
                <el-tooltip content="点击查看使用详情" placement="top">
                    <el-link :underline="false" type="primary" style="margin-left: 20px"
                             @click="$router.push({name:'FirSuperSignBase',params:{act:'useddevices'},query:{bundleid: currentapp.bundle_id}})">
                        已经使用 <a style="color: #dd6161;font-size: larger">{{ currentapp.supersign_used_number }}</a>
                        个设备额度
                    </el-link>
                </el-tooltip>
            </el-form-item>


            <el-form-item label-width="200px" label="签名类型">
                <el-select v-model="currentapp.supersign_type" placeholder="特殊签名权限"
                           style="width: 60%;margin-right: 10px" :disabled="supersign_disable">
                    <el-option v-for="st in sign_type_list" :key="st.id" :label="st.name"
                               :value="st.id"/>
                </el-select>
                <el-button @click="saveappinfo({supersign_type:currentapp.supersign_type})"
                           :disabled="supersign_disable"
                >保存
                </el-button>
            </el-form-item>


            <el-form-item label-width="200px" label="自定义BundleID">
                <el-tooltip content="新的BundleID可能会导致推送等服务失效，请了解之后进行修改" placement="top">
                    <el-input v-model="currentapp.new_bundle_id" clearable :disabled="supersign_disable"
                              style="width: 60%;margin-right: 10px" prefix-icon="el-icon-s-data"
                              :placeholder="defualt_dtitle"/>
                </el-tooltip>
                <el-button @click="saveappinfo({new_bundle_id:currentapp.new_bundle_id})" :disabled="supersign_disable"
                >保存
                </el-button>
            </el-form-item>

            <el-form-item label-width="200px" label="自定义应用名称">
                <el-input v-model="currentapp.new_bundle_name" clearable :disabled="supersign_disable"
                          style="width: 60%;margin-right: 10px" prefix-icon="el-icon-s-data"
                          :placeholder="defualt_dtitle_name"/>
                <el-button @click="saveappinfo({new_bundle_name:currentapp.new_bundle_name})"
                           :disabled="supersign_disable"
                >保存
                </el-button>
            </el-form-item>

        </el-form>
        <el-link v-else :underline="false" type="warning"> 该用户暂未开通超级签权限,请联系管理员申请开通</el-link>
    </div>


</template>

<script>
    import {apputils,} from "@/restful"
    import {deepCopy} from "@/utils";

    export default {
        name: "FirAppInfossupersign",
        data() {
            return {
                currentapp: {},
                orgcurrentapp: {},
                supersign: {'msg': ''},
                showsupersignflag: false,
                supersign_disable: true,
                sign_type_list: [],
                sign_type: 0,
                defualt_dtitle: '',
                defualt_dtitle_name: ''
            }
        },
        methods: {

            set_default_flag() {
                this.showsupersignflag = false;
            },
            clean_app() {
                this.saveappinfo({"clean": true});
                this.currentapp.count = 0;
            },
            saveappinfo(data) {
                const loading = this.$loading({
                    lock: true,
                    text: '执行中,请耐心等待...',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });
                apputils(data => {
                    if (data.code === 1000) {
                        this.$message.success('数据更新成功');
                    } else {
                        this.$message.error('操作失败,' + data.msg);
                        this.$store.dispatch('doucurrentapp', this.orgcurrentapp);
                    }
                    loading.close();
                }, {
                    "methods": "PUT",
                    "app_id": this.currentapp.app_id,
                    "data": data
                });
            },
            setbuttonsignshow(currentapp) {
                if (currentapp.issupersign === true) {
                    this.supersignevent("on");
                    this.supersign.val = 'on';
                } else {
                    this.supersignevent("off");
                    this.supersign.val = 'off';
                }
                this.showsupersignflag = true;
            },

            setbuttondefault(currentapp) {
                this.setbuttonsignshow(currentapp);
            },

            supersignevent(newval) {
                if (newval === "on") {
                    if (this.showsupersignflag) {
                        this.saveappinfo({
                            "issupersign": 1,
                        });
                        this.currentapp.issupersign = 1;
                    }
                    this.supersign.msg = '已经开启超级签名';
                    this.supersign_disable = false
                } else {
                    if (this.showsupersignflag) {
                        this.saveappinfo({
                            "issupersign": 0,
                        });
                        this.currentapp.issupersign = 0;
                    }
                    this.supersign.msg = '关闭';
                    this.supersign_disable = true
                }
            },
            set_default_ms(currentapp) {
                this.sign_type_list = currentapp.sign_type_choice;
                if (this.currentapp.new_bundle_id && currentapp.new_bundle_id.length > 5) {
                    this.defualt_dtitle = currentapp.new_bundle_id
                } else {
                    this.defualt_dtitle = currentapp.bundle_id
                }
                if (this.currentapp.new_bundle_name && currentapp.new_bundle_name.length > 0) {
                    this.defualt_dtitle_name = currentapp.new_bundle_name
                } else {
                    this.defualt_dtitle_name = currentapp.name
                }
            },
            appinit() {
                this.currentapp = this.$store.state.currentapp;
                this.set_default_flag();
                this.orgcurrentapp = deepCopy(this.currentapp);
                this.set_default_ms(this.currentapp);
                this.setbuttondefault(this.currentapp);
            }
        },
        mounted() {
            this.$store.dispatch('doappInfoIndex', [[57, 57], [57, 57]]);
            if (!this.currentapp.app_id) {
                this.appinit();
            }
        },
        watch: {
            '$store.state.currentapp': function () {
                this.appinit();
            },
            'currentapp.new_bundle_id': function () {
                if (!this.currentapp.new_bundle_id || this.currentapp.new_bundle_id.length === 0) {
                    this.defualt_dtitle = this.currentapp.bundle_id
                }
            },
            'currentapp.new_bundle_name': function () {
                if (!this.currentapp.new_bundle_name || this.currentapp.new_bundle_name.length === 0) {
                    this.defualt_dtitle_name = this.currentapp.name
                }
            }
        }, computed: {}
    }
</script>

<style scoped>

</style>
