#
# File: user.py
# Copyright: Grimm Project, Ren Pin NGO, all rights reserved.
# License: MIT
# -------------------------------------------------------------------------
# Authors:  Ming Li(adagio.ming@gmail.com)
#
# Description: user related view functions for wxapp,
#
# To-Dos:
#   1. make other supplements if needed.
#
# Issues:
#   No issue so far.
#
# Revision History (Date, Editor, Description):
#   1. 2019/09/19, Ming, create first revision.
#

from datetime import datetime
from flask import request, url_for, jsonify

import server.core.db as db
import server.utils.sms_verify as sms_verify
from server.core import grimm as app
from server.core import socketio
from server import user_logger
from server.utils.misc import json_load_request, request_success, request_fail

from server.core.globals import SMS_VRF_EXPIRY


SMS_VERIFIED_OPENID = {}

@app.route('/register', methods=['POST'])
def register():
    '''view function for registering new user to database'''
    if request.method == 'POST':
        global SMS_VERIFIED_OPENID
        userinfo = {}
        info = json_load_request(request)  # get http POST data bytes format
        # fetch data from front end
        userinfo['openid'] = request.headers.get('Authorization')
        openid = userinfo['openid']
        if not db.exist_row('user', openid=openid):
            # confirm sms-code
            if not ('verification_code' in info or openid in SMS_VERIFIED_OPENID):
                user_logger.warning('%s: user registers before sms verification', openid)
                return request_fail('未认证注册用户')
            if 'verification_code' in info:
                vrfcode = info['verification_code']
                phone_number = info['tel']
                sms_token = sms_verify.fetch_token(phone_number)
                if sms_token is None:
                    user_logger.warning('%s: no such a sms token for number', phone_number)
                    return request_fail('未向该用户发送验证短信')
                if sms_token.expired:
                    user_logger.warning('%s, %s: try to validate user with expired token', phone_number, sms_token.vrfcode)
                    sms_verify.drop_token(phone_number)
                    return request_fail('过期验证码')
                if not sms_token.valid:
                    user_logger.warning('%s: try to validate user with invalid token', phone_number)
                    sms_verify.drop_token(phone_number)
                    return request_fail('无效验证码')

                result = sms_token.validate(phone_number=phone_number, vrfcode=vrfcode)
                if result is not True:
                    user_logger.warning('%s, %s: sms code validation failed, %s', phone_number, vrfcode, result)
                    return request_fail(result)
                user_logger.info('%s, %s: sms code validates successfully', phone_number, vrfcode)
                sms_verify.drop_token(phone_number)  # drop token from pool after validation
            else:
                del SMS_VERIFIED_OPENID[openid]
            # mock user info and do inserting
            userinfo['role'] = 0 if info['role'] == "志愿者" else 1
            if userinfo['role'] == 1:
                userinfo['disabled_id'] = info['disabledID']
                userinfo['emergent_contact'] = info['emergencyPerson']
                userinfo['emergent_contact_phone'] = info['emergencyTel']
            userinfo['birth'] = info['birthdate']
            userinfo['remark'] = info['comment']
            userinfo['gender'] = info['gender']
            userinfo['idcard'] = info['idcard']
            userinfo['address'] = info['linkaddress']
            userinfo['contact'] = info['linktel']
            userinfo['name'] = info['name']
            userinfo['audit_status'] = 0
            userinfo['registration_date'] = datetime.now().strftime('%Y-%m-%d')
            userinfo['phone'] = info['tel']
            userinfo['phone_verified'] = 1
            try:
                if db.expr_insert('user', userinfo) != 1:
                    user_logger.error('%s: user registration failed', openid)
                    return request_fail('录入用户失败，请重新注册')
            except:
                user_logger.error('%s: user registration failed', openid)
                return request_fail('未知错误，请重新注册')

            socketio.emit('new-users', [userinfo])
            try:
                rc = db.expr_update(tbl = 'user', vals = {'push_status':1}, openid = userinfo['openid'])
            except Exception as e:
                user_logger.error('update push_status fail, %s', e)
            user_logger.info('%s: complete user registration success', openid)
            return request_success()

        user_logger.error('%s: user is registered already', openid)
        return request_fail('用户已注册，请登录')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    '''view function for displaying or updating user profile'''
    feedback = {'status': 'success'}
    if request.method == 'GET':
        openid = request.headers.get('Authorization')
        if db.exist_row('user', openid=openid):
            try:
                userinfo = db.expr_query('user', openid=openid)[0]
            except:
                return request_fail('未知错误')
            feedback['openid'] = userinfo['openid']
            feedback['birthDate'] = userinfo['birth']
            feedback['usercomment'] = userinfo['remark']
            feedback['disabledID'] = userinfo['disabled_id']
            feedback['emergencyPerson'] = userinfo['emergent_contact']
            feedback['emergencyTel'] = userinfo['emergent_contact_phone']
            feedback['gender'] = userinfo['gender']
            feedback['idcard'] = userinfo['idcard']
            feedback['linkaddress'] = userinfo['address']
            feedback['linktel'] = userinfo['contact']
            feedback['name'] = userinfo['name']
            feedback['role'] = "志愿者" if userinfo['role'] == 0 else "视障人士"
            feedback['tel'] = userinfo['phone']
            feedback['registrationDate'] = userinfo['registration_date']
            user_logger.info('%s: user login successfully', userinfo['openid'])
            return jsonify(feedback)

        user_logger.warning('%s: user not registered', openid)
        return request_fail('用户未注册')

    if request.method == 'POST':
        newinfo = json_load_request(request)  # get request POST user data
        userinfo = {}
        openid = request.headers.get('Authorization')
        if newinfo['role'] == '视障人士':
            userinfo['disabled_id'] = newinfo['disabledID']
            userinfo['emergent_contact'] = newinfo['emergencyPerson']
            userinfo['emergent_contact_phone'] = newinfo['emergencyTel']
        userinfo['phone'] = newinfo['tel']
        userinfo['gender'] = newinfo['gender']
        userinfo['birth'] = newinfo['birthDate']
        userinfo['contact'] = newinfo['linktel']
        userinfo['address'] = newinfo['linkaddress']
        userinfo['remark'] = newinfo['usercomment']
        userinfo['idcard'] = newinfo['idcard']
        userinfo['name'] = newinfo['name']
        try:
            status = db.expr_query('user', 'audit_status', openid=openid)[0]
            if status['audit_status'] == -1:
                userinfo['audit_status'] = 0
            if db.expr_update('user', userinfo, openid=openid) != 1:
                user_logger.error('%s: user update info failed', openid)
                return request_fail('更新失败，请重新输入')
        except:
            return request_fail('未知错误')

        user_logger.info('%s: complete user profile updating successfully', openid)
        return request_success()


@app.route('/smscode', methods=['GET', 'POST'])
def smscode():
    '''view function to send and verify sms verification code'''
    # send smscode
    if request.method == 'GET':
        phone_number = request.args.get('tel')
        if phone_number is None:
            user_logger.warning('invalid url parameter phone_number')
            return request_fail('无效url参数')
        try:
            sms_verify.drop_token(phone_number)  # drop old token if it exists
            sms_token = sms_verify.SMSVerifyToken(phone_number=phone_number,
                                                  expiry=SMS_VRF_EXPIRY,
                                                  template='REGISTER_USER')
            if not sms_token.send_sms():
                user_logger.warning('%s, unable to send sms to number', phone_number)
                return request_fail('发送失败')
        except Exception as err:
            return request_fail(f"{err.args}")
        # append new token to pool
        sms_verify.append_token(sms_token)

        user_logger.info('%s, %s: send sms to number successfully', phone_number, sms_token.vrfcode)
        return request_success()

    # verify smscode
    if request.method == 'POST':
        global SMS_VERIFIED_OPENID
        data = json_load_request(request)
        phone_number = data['tel']
        vrfcode = data['verification_code']
        openid = request.headers.get('Authorization')
        sms_token = sms_verify.fetch_token(phone_number)
        if sms_token is None:
            user_logger.warning('%s: no such a sms token for number', phone_number)
            return request_fail('未向该用户发送验证短信')
        result = sms_token.validate(phone_number=phone_number, vrfcode=vrfcode)
        if result is not True:
            user_logger.warning('%s, %s: sms code validation failed, %s', phone_number, vrfcode, result)
            return request_fail(result)
        sms_verify.drop_token(phone_number)  # drop token from pool if validated
        # try update database first, if no successful, append this openid.
        try:
            if db.expr_update('user', {'phone_verified': 1}, openid=openid) is False:
                SMS_VERIFIED_OPENID[openid] = phone_number
        except:
            user_logger.warning('%s: update user phone valid status failed', openid)
            return request_fail('未知错误，请重新短信验证')

        user_logger.info('%s, %s: sms code validates successfully', phone_number, vrfcode)
        return request_success()

