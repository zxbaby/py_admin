#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""URL处理器

[description]
"""

import json
import tornado

from applications.core.settings_manager import settings
from applications.core.logger.client import SysLogger
from applications.core.cache import sys_config
from applications.core.decorators import required_permissions
from applications.core.utils import utc_to_timezone
from applications.core.utils.encrypter import RSAEncrypter
from applications.core.utils.hasher import make_password

from applications.core.handler import BaseHandler

from applications.admin.models.system import User
from applications.admin.models.system import Role
from applications.admin.models.system import AdminMenu


class UserHandler(BaseHandler):
    """docstring for Passport"""
    @tornado.web.authenticated
    @required_permissions('admin:user:index')
    def get(self, *args, **kwargs):
        """后台首页
        """
        # return self.show('<script type="text/javascript">alert(1)</script>')
        params = {
        }
        self.render('user/index.html', **params)

    @tornado.web.authenticated
    @required_permissions('admin:user:delete')
    def delete(self, *args, **kwargs):
        """删除用户
        """
        # return self.show('<script type="text/javascript">alert(1)</script>')
        uuid = self.get_argument('uuid', None)

        User.Q.filter(User.uuid==uuid).delete()
        User.session.commit()
        return self.success()

class UserUnlockedHandler(BaseHandler):
    @tornado.web.authenticated
    @required_permissions('admin:user:unlocked')
    def post(self, *args, **kwargs):
        password = self.get_argument('password', None)
        if not password:
            return self.error('请输入密码')

        return self.success()

class UserListHandler(BaseHandler):
    """docstring for Passport"""
    @tornado.web.authenticated
    @required_permissions('admin:user:index')
    def get(self, *args, **kwargs):
        limit = self.get_argument('limit', 10)
        page = self.get_argument('page', 1)
        pagelist_obj = User.Q.filter().paginate(page=page, per_page=limit)
        if pagelist_obj is None:
            return self.error('暂无数据')

        total = pagelist_obj.total
        page = pagelist_obj.page
        items = pagelist_obj.items

        params = {
            'count': total,
            'uri': self.request.uri,
            'path': self.request.path,
            'data': [user.as_dict() for user in items],
        }
        return self.success(**params)

class UserAddHandler(BaseHandler):
    """docstring for Passport"""
    @tornado.web.authenticated
    @required_permissions('admin:user:add')
    def get(self, *args, **kwargs):
        role_id = '6b0642103a1749949a07f4139574ead9'
        menu_list = AdminMenu.children(status=1)
        user = User(status=1, role_id=role_id)

        data_info = user.as_dict()
        try:
            data_info['permission'] = json.loads(user.permission)
        except Exception as e:
            data_info['permission'] = []

        params = {
            'user': user,
            'role_option': Role.option_html(role_id),
            'menu_list': menu_list,
            'data_info': data_info,
            'public_key': sys_config('sys_login_rsa_pub_key'),
            'rsa_encrypt': sys_config('login_pwd_rsa_encrypt'),
            'xsrf_token': self.xsrf_token,
        }
        self.render('user/add.html', **params)

    @tornado.web.authenticated
    @required_permissions('admin:user:add')
    def post(self, *args, **kwargs):
        role_id = self.get_argument('role_id', None)
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        rsa_encrypt = self.get_argument('rsa_encrypt', None)
        email = self.get_argument('email', None)
        mobile = self.get_argument('mobile', None)
        status = self.get_argument('status', 1)
        permission = self.get_body_arguments('permission')

        if not username:
            return self.error('用户名不能为空')
        if not password:
            return self.error('密码不能为空')

        if username:
            res = User.Q.filter(User.username==username).count()
            if res>0:
                return self.error('用户名已被占用')

        if settings.login_pwd_rsa_encrypt and int(rsa_encrypt)==1 and len(password)>10:
            private_key = sys_config('sys_login_rsa_priv_key')
            password = RSAEncrypter.decrypt(password, private_key)

        params = {
            'username': username,
            'password': make_password(password),
            'status': status,
        }
        if role_id:
            params['role_id'] = role_id
        if mobile:
            params['mobile'] = mobile
            res = User.Q.filter(User.mobile==mobile).count()
            if res>0:
                return self.error('电话号码已被占用')
        if email:
            params['email'] = email
            res = User.Q.filter(User.email==email).count()
            if res>0:
                return self.error('Email已被占用')

        user = User(**params)
        User.session.add(user)
        # 为了输出
        user = user.as_dict()
        User.session.commit()

        return self.success(data=user)

class UserEditHandler(BaseHandler):
    """docstring for Passport"""
    @tornado.web.authenticated
    @required_permissions('admin:user:edit')
    def get(self, *args, **kwargs):
        uuid = self.get_argument('uuid', None)

        menu_list = AdminMenu.children(status=1)
        user = User.Q.filter(User.uuid==uuid).first()

        role_id = user.role_id

        data_info = user.as_dict()
        try:
            data_info['permission'] = json.loads(user.permission)
        except Exception as e:
            data_info['permission'] = []

        params = {
            'user': user,
            'role_option': Role.option_html(role_id),
            'menu_list': menu_list,
            'data_info': data_info,
            'public_key': sys_config('sys_login_rsa_pub_key'),
            'rsa_encrypt': sys_config('login_pwd_rsa_encrypt'),
            'xsrf_token': self.xsrf_token,
        }
        self.render('user/edit.html', **params)

    @tornado.web.authenticated
    @required_permissions('admin:user:edit')
    def post(self, *args, **kwargs):
        role_id = self.get_argument('role_id', None, strip=True)
        uuid = self.get_argument('uuid', None, strip=True)
        username = self.get_argument('username', None, strip=True)
        password = self.get_argument('password', None, strip=True)
        rsa_encrypt = self.get_argument('rsa_encrypt', 0)
        email = self.get_argument('email', None, strip=True)
        mobile = self.get_argument('mobile', None, strip=True)
        status = self.get_argument('status', 0)
        permission = self.get_body_arguments('permission[]', strip=True)

        email = None if email=='None' else email
        mobile = None if mobile=='None' else mobile

        if not uuid:
            return self.error('用户ID不能为空')

        user = {
            'status': status,
        }

        if username:
            user['username'] = username
            res = User.Q.filter(User.uuid!=uuid).filter(User.username==username).count()
            if res>0:
                return self.error('用户名已被占用')
        if password:
            if settings.login_pwd_rsa_encrypt and int(rsa_encrypt)==1 and len(password)>10:
                private_key = sys_config('sys_login_rsa_priv_key')
                password = RSAEncrypter.decrypt(password, private_key)
            user['password'] = make_password(password)

        if mobile:
            user['mobile'] = mobile
            res = User.Q.filter(User.uuid!=uuid).filter(User.mobile==mobile).count()
            if res>0:
                return self.error('电话号码已被占用')
        if email:
            user['email'] = email
            res = User.Q.filter(User.uuid!=uuid).filter(User.email==email).count()
            if res>0:
                return self.error('Email已被占用')

        if permission:
            user['permission'] = json.dumps(permission)

        if role_id:
            user['role_id'] = role_id

        User.Q.filter(User.uuid==uuid).update(user)
        User.session.commit()

        return self.success(data=user)