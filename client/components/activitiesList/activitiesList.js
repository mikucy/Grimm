// components/activitiesList/activitiesList.js
const { getActivityList, getFilteredActivities} = require('../../utils/requestUtil.js');

Component({
  /**
   * 组件的属性列表
   */
  properties: {
    activitiesProp: {
      type: Array,
      value:[],
    }
  },

  /**
   * 组件的初始数据
   */
  data: {
  },

  pageLifetimes: {
    show: function() {
      getActivityList((res) => {
        this._setActivities(res);
      })
    }
  },

  /**
   * 组件的方法列表
   */
  methods: {
    _setActivities: function (activities) {
        let formattedActivities = [];
        for (let index = 0; index < activities.length; index++) {
          let activity = activities[0];
          let startTime = activity.start_time.replace('T', ' ');
          let endTime = activity.end_time.replace('T', ' ');
          activity.schedule = startTime + " - " + endTime;
          formattedActivities.push(activity);
        }
        this.setData({activitiesProp: formattedActivities});
    },

    _getFilteredCategoryParams(category) {
      return category != -1 ? "tags=" + category : "";
    },

    _getFilteredTimeParams(time) {
      let timeParams = "";
      if (time == "-1") {
        timeParams = "latest";
      } else if (time == "2") {
        timeParams = "weekends";
      } else if (time == "3") {
        let date = new Date();
        let nextWeek = date.setDate(date.getDate() + 7);
        timeParams = date.toISOString.substr(0, 10) + " - " + nextWeek.toISOString.substr(0, 10);
      }
      
      if (timeParams != "") {
        timeParams = "time=" + timeParams;
      }
      return timeParams;
    },

    onTapActivity: function (event) {
      wx.navigateTo({
        url: '/pages/activityDetail/activityDetail?id=1',
      })
    },

    onFilterParamChange: function(event) {
      console.log(event);
      let categoryParam = this._getFilteredCategoryParams(event.detail.category);
      let timeParam = this._getFilteredTimeParams(event.detail.time);

      if (categoryParam == "" && timeParam == "") {
        getActivityList((res) => {
          this._setActivities(res);
        });
      } else {
        var params = "";
        if (timeParam == "") {
          params = categoryParam;
        } else if (categoryParam == "") {
          params = filteredTime;
        } else {
          params = timeParam + "&" + categoryParam;
        }
        getFilteredActivities(params, (res) => {
          this._setActivities(res);
        });
      }
    },
    
    onPulling: function() {
      
    }
  }
})
