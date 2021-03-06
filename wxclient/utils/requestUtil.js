const {request} = require('interceptor.js');

const getProfile = (successCallback, failCallback) => {
    return request({
        url: "profile", 
        success: successCallback,
        fail: failCallback
    });
}

const updateProfile = (userInfo, successCallback, failCallback) => {
    return request({
        url: "profile", 
        method: "POST",
        data: userInfo,
        success: successCallback,
        fail: failCallback
    });
}

const getVerifyCode = (tel) => {
    //get
}

const verifyCode = (obj, successCallback, failCallback) =>{
    //send
    let {tel, code} = obj;
    successCallback();
}

const register =  (obj, successCallback, failCallback) => {
    return request({
        url: "register", 
        data: obj,
        success: successCallback,
        fail: failCallback,
        method: "POST"
    });
}

module.exports = {
    getProfile,
    updateProfile,
    getVerifyCode,
    verifyCode,
    register
}
  