<template>
    <div ref="appbase">
        <canvas ref="canvas" class="canvas" @mousemove="canvas_move" @mouseleave="canvas_leave"/>
        <el-container>
            <el-header>
                <FirHeader/>
            </el-header>
            <div class="pbody">
                <router-view/>
            </div>
            <el-footer>
                <el-divider/>
                <FirFooter/>
            </el-footer>
        </el-container>
    </div>

</template>

<script>
    import FirHeader from "@/components/FirHeader";
    import FirFooter from "@/components/FirFooter";
    import {show_beautpic,} from "@/utils";

    export default {
        name: "FirBase",
        components: {FirFooter, FirHeader},
        data() {
            return {
                'mousePosition': {},
            }
        },
        mounted() {
            let canvas = this.$refs.canvas;
            show_beautpic(this, canvas, 200);
        }, watch: {}
        , methods: {
            canvas_move(e) {
                this.mousePosition.x = e.pageX;
                this.mousePosition.y = e.pageY;
            },
            // eslint-disable-next-line no-unused-vars
            canvas_leave(e) {
                let canvas = this.$refs.canvas;
                this.mousePosition.x = canvas.width / 2;
                this.mousePosition.y = canvas.height / 2;
            },
        }
    }
</script>

<style scoped>
    .pbody {
        padding-top: 30px;
    }

</style>
