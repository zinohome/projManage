#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import traceback

from fastapi_user_auth.auth.models import User, Role, CasbinRule
from sqlalchemy import select, text
from sqlmodel import Session

# @Time    : 2025/04/11 15:45
# @Author  : ZhangJun
# @FileName: batchuserreg.py

from core.globals import auth, site
from utils.log import log as log
from utils.userselect import UserSelect


class BatchUserReg(object):
    def _create_role_user_sync(self, session: Session, username: str="root", nickname: str="root", email: str="root", role_key: str = "root") -> User:
        try:
            # create admin role
            role = session.scalar(select(Role).where(Role.key == role_key))
            if not role:
                role = Role(key=role_key, name=f"{role_key}")
                session.add(role)
                session.flush()

            # create user
            user = session.scalar(select(auth.user_model).where(auth.user_model.username == username))
            if not user:
                user = auth.user_model(
                    username=username,
                    password=auth.pwd_context.hash(username),
                    nickname=nickname,
                    email=email,
                )
                session.add(user)
                session.flush()
            # create casbin rule
            rule = session.scalar(
                select(CasbinRule).where(
                    CasbinRule.ptype == "g",
                    CasbinRule.v0 == "u:" + username,
                    CasbinRule.v1 == "r:" + role_key,
                )
            )
            if not rule:
                rule = CasbinRule(ptype="g", v0="u:" + username, v1="r:" + role_key)
                session.add(rule)
                session.flush()
            return user
        except Exception as exp:
            print('Exception at BatchUserReg._create_role_user_sync() %s ' % exp)
            traceback.print_exc()

    async def reguser(self):
        userselect = UserSelect()
        log.debug(userselect.TLS)
        log.debug(userselect.Mission)
        log.debug(userselect.Sales)

        try:
            for tls in userselect.TLS:
                user = await auth.db.async_run_sync(self._create_role_user_sync, tls['id'], tls['nickname'], tls['email'], 'TLS')
                log.debug(f'TLS： {user.username} registered !')
            await auth.db.async_commit()
            for mission in userselect.Mission:
                user = await auth.db.async_run_sync(self._create_role_user_sync, mission['id'], mission['nickname'], mission['email'], 'TLSMission')
                log.debug(f'Mission： {user.username} registered !')
            await auth.db.async_commit()
            for sales in userselect.Sales:
                user = await auth.db.async_run_sync(self._create_role_user_sync, sales['id'], sales['nickname'], sales['email'], 'GlobalSales')
                log.debug(f'Sales： {user.username} registered !')
            await auth.db.async_commit()
            #user = await auth.db.async_run_sync(self._create_role_user_sync, 'liuyuly@cn.ibm.com','LIU YU','liuyuly@cn.ibm.com','SSR')
            #await auth.db.async_commit()
        except Exception as exp:
            print('Exception at BatchUserReg.reguser() %s ' % exp)
            traceback.print_exc()


if __name__ == '__main__':
    bur = BatchUserReg()
    import asyncio
    asyncio.run(bur.reguser())

