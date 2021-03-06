#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .handlers import index
from .handlers import passport
from .handlers import member

# 其他 URL 通过 acl 获取
urls = [
    # index
    (r"/?(.html)?", index.IndexHandler),

    # passport
    (r"/passport/login/?(.html)?", passport.LoginHandler),
    (r"/passport/logout/?(.html)?", passport.LogoutHandler),
    (r"/passport/reg/?(.html)?", passport.RegisterHandler),
    (r"/passport/forget/?(.html)?", passport.ForgetHandler),
    (r"/passport/captcha/?(.png)?", passport.CaptchaHandler),

    # memeber
    (r"/member/?(.html)?", member.IndexHandler),
    (r"/member/index/?(.html)?", member.IndexHandler),
    (r"/member/set/?(.html)?", member.SetHandler),
    (r"/member/sendmail/?(.html)?", member.SendmailHandler),
    (r"/member/activate/?(.html)?", member.ActivateHandler),
    (r"/member/repass/?(.html)?", member.ResetPasswordHandler),
    (r"/member/upload/avator/?(.html)?", member.UploadAvatorHandler),
    (r"/member/message/?(.html)?", member.MessageHandler),
    (r"/member/invite/?(.html)?", member.InviteHandler),
    (r"/member/home/?(.html)?", member.HomeHandler),
    (r"/member/unlocked/?(.html)?", member.MemberUnlockedHandler),

]