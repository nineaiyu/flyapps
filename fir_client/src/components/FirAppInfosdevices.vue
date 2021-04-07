<template>


    <div style="margin-top: 20px;width: 90%;margin-left: 8%">
        <el-link type="primary" v-if="this.currentapp.issupersign" style="margin-bottom: 30px;font-size: x-large"
                 @click="$router.push({name:'FirSuperSignBase',params:{act:'useddevices'},query:{bundleid: currentapp.bundle_id}})">
            该应用已经开启超级签，请点击查看最新设备列表
        </el-link>
        <h2>UDID列表及用户信息 - {{ udidlists.length }}个设备</h2>
        <el-table
                :data="udidlists"
                stripe
                style="width: 100%">
            <el-table-column width="180"
                             prop="model"
                             label="设备型号">
            </el-table-column>
            <el-table-column width="180"
                             prop="version"
                             label="系统版本">
            </el-table-column>
            <el-table-column width="380"
                             prop="udid"
                             label="UDID">
            </el-table-column>
        </el-table>

    </div>


</template>

<script>
    export default {
        name: "FirAppInfosdevices",
        data() {
            return {
                currentapp: {},
                udidlists: []
            }
        },
        methods: {},
        mounted() {
            this.$store.dispatch('doappInfoIndex', [[70, 70], [70, 70]]);
            if (!this.currentapp.app_id) {
                this.currentapp = this.$store.state.currentapp;
                if (this.currentapp.master_release) {
                    this.udidlists = this.currentapp.master_release.udid;
                }
            }
        },
        watch: {
            '$store.state.currentapp': function () {
                this.currentapp = this.$store.state.currentapp;
                this.udidlists = this.currentapp.master_release.udid;
            }
        }, computed: {}
    }
</script>

<style scoped>


    .avatar-uploader .el-upload {
        border: 1px dashed #d9d9d9;
        border-radius: 6px;
        cursor: pointer;
        position: relative;
        overflow: hidden;

    }

    .avatar-uploader .el-upload:hover {
        border-color: #409EFF;
    }

    .avatar-uploader-icon {
        font-size: 28px;
        color: #8c939d;
        width: 178px;
        height: 178px;
        line-height: 178px;
        text-align: center;
    }

    .avatar {
        height: 100px;
        width: 100px;
        border-radius: 10px;
        display: block;
    }
</style>
