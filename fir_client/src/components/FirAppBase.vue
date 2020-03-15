<template>
    <div ref="appbase">
        <el-container>
            <el-header>
                <FirHeader></FirHeader>

            </el-header>
            <div class="pbody">
                <router-view></router-view>
            </div>
        </el-container>
    </div>

</template>

<script>
    import FirHeader from "@/components/FirHeader";

    export default {
        name: "FirAppBase",
        components: {FirHeader},
        mounted() {
        }, watch: {}
    }
</script>

<style scoped>
    .pbody {
        padding-top: 20px;
    }
</style>
