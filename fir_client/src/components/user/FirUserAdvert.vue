<template>
  <el-main>

    <!-- vueCropper 剪裁图片实现-->
    <el-dialog :visible.sync="dialogVisible" append-to-body title="图片剪裁">
      <div style="height: 500px">
        <vueCropper
            ref="cropper"
            :autoCrop="option.autoCrop"
            :autoCropHeight="option.autoCropHeight"
            :autoCropWidth="option.autoCropWidth"
            :canMove="option.canMove"
            :canMoveBox="option.canMoveBox"
            :canScale="option.canScale"
            :centerBox="option.centerBox"
            :fixed="option.fixed"
            :fixedBox="option.fixedBox"
            :fixedNumber="option.fixedNumber"
            :full="option.full"
            :img="option.img"
            :info="true"
            :infoTrue="option.infoTrue"
            :original="option.original"
            :outputSize="option.size"
            :outputType="option.outputType"
        />
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="finish">确认</el-button>
      </div>
    </el-dialog>

    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :title="advert_title"
        :visible.sync="bind_advert_sure"
        center
        width="666px">

      <el-form :model="editadvertinfo"
               label-width="180px" style="margin:0 auto;">

        <el-form-item label="广告名称">
          <el-input v-model="editadvertinfo.ad_name" clearable/>
        </el-form-item>
        <el-form-item label="展示图片【高80像素】">
          <el-upload
              :auto-upload="false"
              :on-change="onUploadChange"
              :show-file-list="false"
              accept=".png , .jpg , .jpeg"
              action="#"
              drag
              style="max-height: 200px">
            <img v-if="upload_pic_b" :src="upload_pic_b" class="avatar" alt="">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>
        <el-form-item label="点击跳转连接">
          <el-input v-model="editadvertinfo.ad_uri" clearable/>
        </el-form-item>
        <el-form-item label="展示权重">
          <el-input-number v-model="editadvertinfo.weight" :max="100" :min="0"
                           label="展示权重"/>
          <el-tag style="margin-left: 10px">权重越大，广告展示频率越高</el-tag>
        </el-form-item>
        <el-form-item label="是否发布">
          <el-switch
              v-model="editadvertinfo.is_enable"
              active-color="#13ce66"
              active-text="发布"
              inactive-color="#ff4949"
              inactive-text="未发布">
          </el-switch>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editadvertinfo.description" :autosize="{ minRows: 3, maxRows: 6}"
                    type="textarea"/>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button v-if="!disabled" @click="saveadvert">保存</el-button>
        <el-button v-if="!disabled" @click="bind_advert_sure=false,init_advertinfo()">取消</el-button>
      </div>

    </el-dialog>
    <div>
      <el-input
          v-model="search_key"
          clearable
          placeholder="输入名称搜索"
          style="width: 30%;margin-right: 30px;margin-bottom: 5px"/>
      <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
        搜索
      </el-button>
      <div style="float: right">
        <el-button plain type="primary" @click="bind_advert_sure=true,init_advertinfo()">
          添加
        </el-button>
      </div>


      <el-table
          v-loading="loading"
          :data="advert_info_list"
          border
          stripe
          style="width: 100%">

        <el-table-column
            align="center"
            fixed
            label="名称"
            prop="ad_name">
        </el-table-column>
        <el-table-column
            align="center"
            fixed
            label="展示图片"
            prop="ad_pic">
          <template slot-scope="scope">
            <img :src="scope.row.ad_pic" style="max-height: 80px;width: 100%;object-fit: cover"/>
          </template>
        </el-table-column>
        <el-table-column
            align="center"
            fixed
            label="点击跳转连接"
            prop="ad_uri">
        </el-table-column>


        <el-table-column
            align="center"
            label="是否发布"
            prop="is_enable"
            width="110">

          <template slot-scope="scope">
            <el-button v-if="scope.row.is_enable === true" size="small" type="success">已发布
            </el-button>
            <el-button v-else size="small" type="warning">未发布
            </el-button>

          </template>

        </el-table-column>
        <el-table-column
            align="center"
            label="展示权重"
            prop="weight"
            width="110">
        </el-table-column>
        <el-table-column
            :formatter="format_create_time"
            align="center"
            label="添加时间"
            prop="created_time"
            width="170"
        >
        </el-table-column>
        <el-table-column
            align="center"
            fixed="right"
            label="操作"
            width="150">
          <template slot-scope="scope">

            <el-button
                size="mini"
                @click="handleEditAdvert(scope.row)">编辑
            </el-button>
            <el-button
                size="mini"
                type="danger"
                @click="handleDeleteAdvert(scope.row)">删除
            </el-button>

          </template>
        </el-table-column>
      </el-table>


    </div>
    <div style="margin-top: 20px;margin-bottom: 20px">
      <el-pagination
          :current-page.sync="pagination.currentPage"
          :page-size="pagination.pagesize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total,sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange">
      </el-pagination>
    </div>
  </el-main>
</template>

<script>

import {advertinfo} from "@/restful";
import {VueCropper} from 'vue-cropper'
import {AvatarUploadUtils, dataURLtoFile, getUserInfoFun} from '@/utils'

export default {
  name: "FirUserAdvert",
  components: {
    VueCropper,
  },
  data() {
    return {
      dialogVisible: false,
      option: {
        img: '', // 裁剪图片的地址
        info: true, // 裁剪框的大小信息
        outputSize: 1, // 裁剪生成图片的质量
        outputType: 'jpeg', // 裁剪生成图片的格式
        canScale: true, // 图片是否允许滚轮缩放
        autoCrop: true, // 是否默认生成截图框
        autoCropWidth: 200, // 默认生成截图框宽度
        autoCropHeight: 80, // 默认生成截图框高度
        fixedBox: false, // 固定截图框大小 不允许改变
        fixed: false, // 是否开启截图框宽高固定比例
        fixedNumber: [7, 2], // 截图框的宽高比例
        full: true, // 是否输出原图比例的截图
        canMoveBox: true, // 截图框能否拖动
        original: false, // 上传图片按照原始比例渲染
        centerBox: true, // 截图框是否被限制在图片里面
        infoTrue: true // true 为展示真实输出图片宽高 false 展示看到的截图框宽高
      },
      advert_title: '添加新宣传广告',
      bind_advert_sure: false,
      advert_info_list: [],
      search_key: "",
      pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
      loading: false,
      editadvertinfo: {},
      upload_file: undefined,
      disabled: false,
      upload_pic_b: ''
    }
  },
  methods: {
    finish() {
      this.$refs.cropper.getCropData((data) => {
        this.upload_pic_b = data;
        this.upload_file = dataURLtoFile(data, this.upload_file.name);
        this.dialogVisible = false;
      })
    },
    init_advertinfo() {
      this.editadvertinfo = {
        'ad_name': '',
        'ad_pic': '',
        'ad_uri': '',
        'is_enable': true,
        'weight': 10
      };
      this.upload_file = undefined;
      this.upload_pic_b = '';
    },
    saveadvert() {
      if (this.editadvertinfo.ad_pic && this.editadvertinfo.ad_pic.indexOf("http") > -1) {
        advertinfo(data => {
          if (data.code === 1000) {
            if (data.data && data.data.id) {
              if (this.upload_file) {
                this.beforeAvatarUpload(this.upload_file, data.data.id, 'update')
              } else {
                this.$message.success("更新成功")
              }
            } else {
              this.$message.error("操作失败 " + data.msg)
            }

          } else {
            this.$message.error("更新失败 " + data.msg)
          }
          this.loading = false;
        }, {methods: 'PUT', data: this.editadvertinfo})
      } else {
        advertinfo(data => {
          if (data.code === 1000) {
            if (data.data && data.data.id) {
              this.beforeAvatarUpload(this.upload_file, data.data.id, 'create')
            } else {
              this.$message.error("操作失败 " + data.msg)
            }

          } else {
            this.$message.error("添加失败 " + data.msg)
          }
          this.loading = false;
        }, {methods: 'POST', data: this.editadvertinfo})
      }
    },
    beforeAvatarUpload(file, id, act) {
      return AvatarUploadUtils(this, file, {
        'app_id': this.$store.state.userinfo.uid,
        'upload_key': file.name,
        'ftype': 'advert',
        'ext': {'id': id}
        // eslint-disable-next-line no-unused-vars
      }, res => {
        this.get_data_from_tabname();
        this.upload_file = undefined;
        let msg = '添加成功';
        if (act === 'update') {
          msg = '更新成功'
        } else {
          this.bind_advert_sure = false;
          this.upload_pic_b = '';
        }
        this.$message.success(msg);

      });

    },
    // eslint-disable-next-line no-unused-vars
    onUploadChange(file, fileList) {
      this.upload_file = file.raw;
      const reader = new FileReader();
      reader.readAsDataURL(file.raw);
      // eslint-disable-next-line no-unused-vars
      reader.onload = res => {
        this.upload_pic_b = reader.result;
        this.option.img = reader.result;
        this.dialogVisible = true
      };
    },
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    handleSizeChange(val) {
      this.pagination.pagesize = val;
      this.get_data_from_tabname({
        "size": this.pagination.pagesize,
        "page": 1
      })
    },
    handleCurrentChange(val) {
      this.pagination.currentPage = val;
      this.get_data_from_tabname({
        "size": this.pagination.pagesize,
        "page": this.pagination.currentPage
      })
    },
    handleEditAdvert(ad_info) {
      this.editadvertinfo = ad_info;
      this.upload_pic_b = ad_info.ad_pic;
      this.advert_title = "编辑广告信息";
      this.bind_advert_sure = true;
    },
    handleDeleteAdvert(ad_info) {
      this.loading = true;
      advertinfo(data => {
        if (data.code === 1000) {
          this.advert_info_list = data.data;
          this.pagination.total = data.count;
          this.$message.success("操作成功")
        } else {
          this.$message.error("信息获取失败")
        }
        this.loading = false;
      }, {methods: 'DELETE', data: {'pk': ad_info.id}})
    },
    get_data_from_tabname(data = {}) {
      data.search_key = this.search_key.replace(/^\s+|\s+$/g, "");
      this.UseradvertFun(data)
    },
    UseradvertFun(params) {
      this.loading = true;
      advertinfo(data => {
        if (data.code === 1000) {
          this.advert_info_list = data.data;
          this.pagination.total = data.count;
        } else {
          this.$message.error("信息获取失败")
        }
        this.loading = false;
      }, {methods: 'GET', data: params})
    },

    format_create_time(row) {
      return this.format_time(row.created_time)
    },

    format_time(stime) {
      if (stime) {
        stime = stime.split(".")[0].split("T");
        return stime[0] + " " + stime[1]
      } else
        return '';
    },
  }, mounted() {
    getUserInfoFun(this);
    this.get_data_from_tabname();
  },
}
</script>

<style scoped>
.el-main {
  margin: 20px auto 100px;
  width: 1166px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
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
  max-height: 80px;
  margin-top: 50px;
  object-fit: cover;
}

</style>
