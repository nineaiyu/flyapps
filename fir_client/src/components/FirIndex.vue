<template>
    <div>
        <div style="margin: 10px 0 10px 0 ;position:absolute;right:20px;top:auto;">
            <!--            <el-button round icon="el-icon-star-off" @click="$router.push({name:'FirLogin'})"></el-button>-->
            <el-button round icon="el-icon-apple" @click="$router.push({name:'FirApps'})"></el-button>

        </div>

        <div class="firplane">
            <img src="../assets/plane.svg">
            <div style="margin-top: -195px;margin-left: 107px">
                <img src="../assets/propeller.svg">
            </div>
        </div>
    </div>

</template>

<script>
    export default {
        name: "FirIndex",
        data() {
            return {}
        },
        created() {
        }
    }
</script>

<style scoped>

    .firplane {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
    }

</style>
