<template>
  <el-timeline>
    <el-timeline-item v-for="(app) in release_apps" :key="app.release_id"
                      :color="app.master_color"
                      :timestamp="app.created_time|formatdatatimeline"
                      placement="top">
      <el-card :body-style="{border: app.is_master ? '#2abb9d 1px solid' : ''}">
        <div class="directive-view-release">

          <i v-if="! app.is_master" class="el-icon-cloudy"/>
          <i v-else class="el-icon-cloudy" style="background-color: rgb(139,195,248)"/>

          <b class="ng-binding">{{ app.app_version }} (Build {{ app.build_version }})</b>
          <div v-if="app.release_type === 0"
               class="release-metainfo ng-hide">
            <small>
              <i class="icon-calendar"/>
              <span class="el-icon-date">&nbsp;{{ app.created_time|formattimeline }}</span>
            </small>
          </div>

          <div v-else class="release-metainfo">
            <small>
              <i class="icon-calendar"/>
              <span class="el-icon-date">&nbsp;{{ app.created_time|formattimeline }}</span>
            </small> &nbsp;&nbsp;·&nbsp;&nbsp;

            <small>{{ app.release_type|getiOStype }}</small>
            <small v-if="app.distribution_name"
                   style="margin-left: 5px">&nbsp;&nbsp;·&nbsp;{{ app.distribution_name }}</small>
          </div>

          <p>{{ app.changelog }}</p>
          <label>
                        <textarea v-if="app.editing.changelog"
                                  v-model="app.changelog"
                                  placeholder="更新日志">
                        </textarea>
          </label>
          <div v-if="app.editing.changelog" class="release-actions editing ">
            <button class="btn-cancel" @click="endEdit(app,'changelog')"><span
            >取消</span></button>
            <button class="btn-save" @click="updateChangelog(app,'changelog')"><span
            >保存</span></button>
          </div>
          <el-input v-if="app.editing.binary_url"
                    v-model="app.binary_url"
                    clearable placeholder="下载地址,默认本服务器，填写第三方可以 自动跳转到第三方平台">
          </el-input>
          <div v-if="app.editing.binary_url" class="release-actions editing " style="margin-top: 10px">

            <button class="btn-cancel" @click="endEdit(app,'binary_url')"><span
            >取消</span></button>
            <button class="btn-save" @click="updateChangelog(app,'binary_url')"><span
            >保存</span></button>
          </div>
          <div v-show="!app.editing.changelog && !app.editing.binary_url " class="release-actions">
            <el-tooltip class="tooltip-top" content="编辑更新日志" placement="top">
              <el-button class="tooltip-top "
                         tooltip="编辑更新日志"
                         @click="startEdit(app,'changelog')">
                <i class="el-icon-edit"/>
              </el-button>
            </el-tooltip>
            <el-tooltip class="tooltip-top" content="下载原文件" placement="top">
              <el-button class="tooltip-top" tooltip="下载原文件"
                         @click="downloadPackage(app)">
                <i class="el-icon-download"/>
                <span>{{ app.binary_size }}</span>
              </el-button>
            </el-tooltip>

            <el-tooltip :content="app.binary_url|downcontent" class="tooltip-top" placement="top">

              <el-button class="tooltip-top" tooltip="修改下载地址"
                         @click="startEdit(app,'binary_url')"><i class="el-icon-link"/> <span>下载地址</span>
              </el-button>

            </el-tooltip>

            <el-button v-if="!currentapp.issupersign" class="tooltip-top" @click="previewRelease(app)"><i
                class="el-icon-view"/> <span
                class="ng-binding">预览该版本</span>
            </el-button>

            <el-button v-if="! app.is_master" class="tooltip-top" @click="make_master_release(app)">
              <i class="el-icon-view"/>
              <span class="ng-binding ng-scope">标记上线</span>
            </el-button>

            <el-button v-if="(! app.is_master )|| (app.is_master && release_apps.length === 1)"
                       class="tooltip-top" @click="del_release_app(app)">
              <i class="el-icon-delete"/>
              <span class="ng-binding ng-scope">删除</span>
            </el-button>

          </div>
        </div>
      </el-card>
    </el-timeline-item>
    <el-button v-if="has_next" class="time-line-more" @click="getAppTimelineFun('more')">显示更多版本</el-button>
  </el-timeline>
</template>

<script>
import {releaseapputils} from "@/restful"

export default {
  name: "FirAppInfostimeline",
  data() {
    return {
      release_apps: [],
      currentapp: {},
      activity: {
        editing: {'changelog': false, 'binary_url': false}
      },
      updatas: {},
      query: {'page': 1, size: 10},
      has_next: false,
    }
  },
  methods: {
    set_query_page() {
      if (this.has_next) {
        this.query.page += 1;
      }
    },
    downloadPackage(app) {

      releaseapputils(res => {
            if (res.code === 1000) {
              window.location.href = res.data.download_url;
            } else {
              this.$message.error(res.msg);
            }
          }, {
            methods: 'POST',
            app_id: this.currentapp.app_id,
            release_id: app.release_id,
            data: {'token': app.download_token, 'short': this.currentapp.short}
          }
      );
    },
    previewRelease(app) {
      window.open(this.currentapp.preview_url + '?release_id=' + app.release_id, '_blank', '');
    },
    getAppTimelineFun(act = '') {
      const loading = this.$loading({
        lock: true,
        text: '加载中',
        spinner: 'el-icon-loading',
        // background: 'rgba(0, 0, 0, 0.7)'
      });
      if (act === 'more') {
        this.set_query_page();
      } else {
        this.release_apps = [];
        this.query = {'page': 1, size: 10};
      }
      releaseapputils(data => {
        if (data.code === 1000) {
          this.currentapp = data.data.currentapp;
          this.has_next = data.data.has_next;
          this.release_apps = this.release_apps.concat(data.data.release_apps);
        } else if (data.code === 1003) {
          loading.close();
          this.$router.push({name: 'FirApps'});
        }
        loading.close();
      }, {
        "methods": "GET",
        "app_id": this.$route.params.id,
        "release_id": "timeline",
        "data": {
          "page": this.query.page,
          "size": this.query.size
        }
      })
    },
    del_release_app(app) {
      //发送删除APP的操作
      this.$confirm('确认删除 ' + this.currentapp.name + '下 当前 release 版本吗?')
          // eslint-disable-next-line no-unused-vars
          .then(res => {
            let loadingobj = this.$loading({
              lock: true,
              text: '操作中，请耐心等待',
              spinner: 'el-icon-loading',
              // background: 'rgba(0, 0, 0, 0.7)'
            });
            releaseapputils(data => {
              loadingobj.close();
              if (data.code === 1000) {
                this.$message({
                  message: '删除成功',
                  type: 'success'
                });
                this.getAppTimelineFun();

              } else {
                this.$message({
                  message: '删除失败，请联系管理员',
                  type: 'error'
                });
              }
            }, {
              "methods": "DELETE",
              "app_id": this.currentapp.app_id,
              "release_id": app.release_id,
            });
          });

    },
    updatereleaseappFun(params) {
      releaseapputils(data => {
            if (data.code === 1000) {
              this.$message({
                message: '更新成功',
                type: 'success'
              });
              this.release_apps = data.data.release_apps;
              this.currentapp = data.data.currentapp;
            } else {
              this.$message({
                message: '更新失败，请联系管理员',
                type: 'error'
              });
            }
          }, params
      );
    },
    make_master_release(app) {
      this.updatereleaseappFun({
        "methods": "PUT",
        "app_id": this.currentapp.app_id,
        "release_id": app.release_id,
        "data": {
          "make_master": app.release_id
        }
      });

    },
    endEdit(app, type) {
      if (type === 'changelog') {
        app.editing.changelog = false;

      } else if (type === 'binary_url') {
        app.editing.binary_url = false;
      }
    },
    updateChangelog(app, type) {
      if (type === 'changelog') {
        this.activity.editing.changelog = false;
        this.updatas = {"changelog": app.changelog}
      } else if (type === 'binary_url') {
        this.activity.editing.binary_url = false;
        this.updatas = {"binary_url": app.binary_url}
      }
      this.updatereleaseappFun({
        "methods": "PUT",
        "app_id": this.currentapp.app_id,
        "release_id": app.release_id,
        "data": this.updatas
      });
      this.updatas = {}
    },
    startEdit(app, type) {
      if (type === 'changelog') {

        app.editing.changelog = true;
      } else if (type === 'binary_url') {
        app.editing.binary_url = true;
      }
    }

  }, created() {

  }, watch: {},
  computed: {}, mounted() {
    this.$store.dispatch('doappInfoIndex', [[5, 5], [5, 5]]);
    this.getAppTimelineFun();
  }, filters: {
    downcontent(content) {
      if (content) {
        return content
      } else {
        return "修改下载地址"
      }
    },
    formatdatatimeline: function (timestr) {
      return timestr.split("T")[0];
    },
    formattimeline: function (timestr) {
      return timestr.split(".")[0].split("T")[1];
    },
    getiOStype: function (type) {
      let ftype = '';
      if (type === 1) {
        ftype = '内测版'
      } else if (type === 2) {
        ftype = '企业版'
      }
      return ftype
    },
  }
}
</script>

<style scoped>


.directive-view-release {
  position: relative;
  padding-left: 80px;
  color: #9b9b9b;
}

.directive-view-release > i {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  height: 50px;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  position: absolute;
  left: 0;
  z-index: 2;
  width: 50px;
  border: 1px solid rgba(151, 151, 151, .2);
  border-radius: 50%;
  background-color: #f6f6f6;
  text-align: center;
  font-size: 22px
}

.directive-view-release > i:before {
  display: inline-block;
  margin-top: 2px;
  margin-left: 2px
}

.directive-view-release .release-metainfo {
  margin-top: 2px
}

.directive-view-release .release-metainfo small {
  display: inline-block;
  vertical-align: middle;
  margin: 8px 0;
  line-height: 14px
}

.directive-view-release .release-metainfo small i, .directive-view-release .release-metainfo small span {
  display: inline-block;
  vertical-align: middle
}

.directive-view-release .release-metainfo small i {
  margin-right: 2px;
  line-height: 14px
}

.directive-view-release > b {
  display: inline-block;
  vertical-align: middle;
  margin-right: 30px;
  color: #4a4a4a;
  font-weight: 400;
  font-size: 20px
}

.directive-view-release pre, .directive-view-release textarea {
  margin: 14px 0;
  padding: 0;
  border: 0;
  background-color: transparent;
  color: #4a4a4a;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif
}

.directive-view-release textarea {
  padding: 12px 16px;
  width: 500px;
  height: 120px;
  border-radius: 5px;
  resize: none;
  border: 1px solid #bdc6c7;
  color: #555;
  font-size: 16px
}

.directive-view-release .tooltip-top {
  position: relative;
  overflow: visible;
  color: #9b9b9b;
}


.directive-view-release .release-actions {
  margin-top: 10px;
  position: relative
}

.directive-view-release .release-actions a, .directive-view-release .release-actions button {
  display: inline-block;
  vertical-align: middle;
  margin-right: 8px;
  background-color: transparent;
  border: 1px solid;
  overflow: hidden;
  border-radius: 17px;
  padding: 4px 10px
}

.directive-view-release .release-actions .tooltip-top {
  overflow: visible;
  position: relative
}

.directive-view-release .release-actions a i, .directive-view-release .release-actions button i {
  display: inline-block;
  vertical-align: middle
}

.directive-view-release .release-actions a.btn-save, .directive-view-release .release-actions button.btn-save {
  border-color: #3d6df8;
  background-color: #92c1f8;
  color: #fff
}

.directive-view-release .release-actions a.btn-cancel, .directive-view-release .release-actions button.btn-cancel {
  border: 0;
}

.directive-view-release .release-actions a.btn-cancel:hover, .directive-view-release .release-actions button.btn-cancel:hover {
  color: #686868
}

.directive-view-release .release-actions a {
  color: #9b9b9b
}

.directive-view-release .release-actions a:focus, .directive-view-release .release-actions a:hover {
  text-decoration: none
}


.directive-view-release .release-actions .has-text i {
  border-right: 1px solid
}

.directive-view-release .release-actions.editing {
  margin-top: 0;
  text-align: right;
  width: 500px
}

.time-line-more {
  background: #F6F6F6;
  border: 1px solid;
  position: relative;
  z-index: 99;
  width: 160px;
  padding: 10px 0;
  border-radius: 40px;
  margin-top: 10px;
}
</style>
