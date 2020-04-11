<template>
    <div>

        <el-select v-model="use_storage_id"  clearable filterable  placeholder="请选择" @change="select_storage">
            <el-option-group
                    v-for="storage_group in fstorage_lists"
                    :key="storage_group.group_name"
                    :label="storage_group.group_name">
                <el-option
                        v-for="storage in storage_group.storage"
                        :key="storage.id"
                        :label="storage.name"
                        :value="storage.id">
                </el-option>
            </el-option-group>
        </el-select>

    </div>
</template>

<script>
    import {getStorageinfo} from "../restful";

    export default {
        name: "FirUserProfileStorage",
        data() {
            return {
                fstorage_lists:[[]],
                use_storage_id:null
            }
        }, methods: {
            select_storage(a){
                // eslint-disable-next-line no-console
                console.log(a)
            },
            format_storage(storage_lists){


                for(let key in  storage_lists){
                    let storage = storage_lists[key];
                    if(storage[0].storage_type_display){
                        this.fstorage_lists.unshift({'group_name':storage[0].storage_type_display,'storage':storage})
                    }
                }
            },
            getstorageinfoFun() {
                // eslint-disable-next-line no-console
                    getStorageinfo(data=>{
                        if(data.code === 1000){
                            this.format_storage(data.data);
                            this.use_storage_id = data.data.storage;
                        }else {
                            this.$message.error('存储获取失败,'+data);
                        }
                    },{"methods":false});
            }
        }, mounted() {
            this.$store.dispatch('douserInfoIndex', 2);
            this.getstorageinfoFun();
        }
    }
</script>

<style scoped>

</style>
