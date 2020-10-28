<template>
    <div ref="appbase">
        <el-container>
            <el-header>
                <FirHeader></FirHeader>

            </el-header>
            <div class="pbody">
                <router-view></router-view>
            </div>
            <el-footer>
                <el-divider/>
                <FirFooter></FirFooter>
            </el-footer>
        </el-container>
    </div>

</template>

<script>
    import FirHeader from "@/components/FirHeader";
    import FirFooter from "@/components/FirFooter";

    export default {
        name: "FirAppBase",
        components: {FirFooter, FirHeader},
        mounted() {
        }, watch: {}
    }
</script>

<style scoped>
    .pbody {
        padding-top: 20px;
    }
</style>
