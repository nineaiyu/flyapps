<template>


    <div style="margin-top: 20px;width: 56%;margin-left: 8%">
        <el-form label-width="80px">

            <el-form-item label-width="160px" label="是否下载页显示">

                <el-tooltip :content="downtip.msg" placement="top">
                    <el-switch
                            @change="showdownloadevent"
                            v-model="downtip.val"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>
                </el-tooltip>

            </el-form-item>


            <el-form-item label-width="160px" label="是否开启访问密码" >

                <el-tooltip  placement="top">
                    <div slot="content">
                        {{passwordtip.msg}}<br>
                        <div v-if="passwordtip.val === 'on'">
                            <el-link  icon="el-icon-edit" :underline="false" @click="setaccesspassword">修改</el-link>
                        </div>
                    </div>
                    <el-switch
                            v-model="passwordtip.val"
                            @change="showpasswordevent"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>

                </el-tooltip>

            </el-form-item>

        </el-form>

    </div>


</template>

<script>
    import { updateapp, } from "../restful"

    export default {
        name: "FirAppInfossecurity",
        data() {
            return {
                currentapp: {},
                downtip:{},
                passwordtip:{'msg':''},
                passwordflag:false,
                showdownloadflag:false,
            }
        },
        methods: {
            saveappinfo(data) {
                updateapp(data => {
                    if (data.code === 1000) {
                        this.$message.success('数据更新成功');
                    }else {
                        this.$message.error('操作失败,'+data.msg);
                    }
                }, {
                    "app_id": this.currentapp.app_id,
                    "data": data
                });
            },
            setbuttondefaltpass(currentapp){
                if(currentapp.password === ''){
                    this.passwordtip.val='off';
                    this.showpasswordevent("off");
                }else {
                    this.passwordtip.val='on';
                    this.showpasswordevent("on");
                }
                this.passwordflag=true;
            },
            setbuttondefaltshow(currentapp){
                if(currentapp.isshow === 1){
                    this.showdownloadevent("on");
                    this.downtip.val='on';
                }else {
                    this.showdownloadevent("off");
                    this.downtip.val='off';
                }
                this.showdownloadflag=true;
            },
            setbuttondefault(currentapp){
                this.setbuttondefaltpass(currentapp);
                this.setbuttondefaltshow(currentapp);
            },
            passwordswitch(state){
                this.passwordflag=false;
                this.showpasswordevent(state);
                this.passwordtip.val=state;
                this.passwordflag=true;
            },
            setaccesspassword(){
                this.$prompt('', '请设置访问密码', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    closeOnClickModal:false,
                    inputValue:`${this.currentapp.password}`,
                }).then(({ value }) => {
                    value = value.replace(/\s+/g,"");
                    if(this.currentapp.password === value ) {
                        if(value === ''){
                            this.$message({
                                type: 'success',
                                message: '访问密码未变'
                            });
                            this.passwordflag = false;
                            this.setbuttondefaltpass(this.currentapp);
                            return
                        }else {
                            return
                        }
                    }
                        this.saveappinfo({
                            "password": value,
                        });
                        if(value === ''){
                            this.passwordswitch("off");
                            this.$message({
                                type: 'success',
                                message: '设置成功，取消密码访问'
                            });
                        }else {
                            this.passwordtip.msg='访问密码:' + value;
                            this.$message({
                                type: 'success',
                                message: '设置成功，访问密码是: ' + value
                            });
                        }
                        this.currentapp.password=value;
                        this.$store.dispatch('doucurrentapp', this.currentapp)
                }).catch(() => {
                    if(this.currentapp.password === ''){
                        this.passwordswitch("off")
                    }
                });
            },
            showdownloadevent(newval){
                if(newval === "on"){
                    if(this.showdownloadflag){
                        this.saveappinfo({
                            "isshow": 1,
                        });
                        this.currentapp.isshow=1;
                    }else {
                        this.downtip.msg='下载页对所有人可见';
                    }
                }else {
                    if(this.showdownloadflag){
                        this.saveappinfo({
                            "isshow": 0,
                        });
                        this.currentapp.isshow=0;
                    }else {
                        this.downtip.msg = '下载页不可见'
                    }
                }
            },
            showpasswordevent(newval){
                if(newval === "on"){
                    if(this.passwordflag){
                        this.setaccesspassword()
                    }else {
                        this.passwordtip.msg='访问密码:' + this.currentapp.password ;
                    }
                }else {
                    if(this.passwordflag){
                        this.saveappinfo({
                            "password": '',
                        });
                    }
                    this.currentapp.password='';
                    this.$store.dispatch('doucurrentapp', this.currentapp);
                    this.passwordtip.msg='无访问密码'
                }
            },
            appinit(){
                this.currentapp = this.$store.state.currentapp;
                this.passwordflag=false;
                this.showdownloadflag=false;
                this.setbuttondefault(this.currentapp);
            }
        },
        mounted() {
            this.$store.dispatch('doappInfoIndex', [[31, 31], [31, 31]]);
            if(!this.currentapp.app_id){
                this.appinit();
            }
        },
        watch: {
            '$store.state.currentapp': function () {
                this.appinit();
            },
        },computed:{
    }
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
