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
        #log.debug(userselect.SSR)
        #log.debug(userselect.SDM)
        #log.debug(userselect.TSG)
        #log.debug(userselect.TSGLeader)
        try:
            for ssr in userselect.SSR:
                user = await auth.db.async_run_sync(self._create_role_user_sync, ssr['id'], ssr['nickname'], ssr['email'], 'SSR')
                log.debug(f'SSR： {user.username} registered !')
            await auth.db.async_commit()
            for tsg in userselect.TSG:
                user = await auth.db.async_run_sync(self._create_role_user_sync, tsg['id'], tsg['nickname'], tsg['email'], 'TSG')
                log.debug(f'TSG： {user.username} registered !')
            await auth.db.async_commit()
            for sdm in userselect.SDM:
                user = await auth.db.async_run_sync(self._create_role_user_sync, sdm['id'], sdm['nickname'], sdm['email'], 'SDM')
                log.debug(f'SDM： {user.username} registered !')
            await auth.db.async_commit()
            for leader in userselect.TSGLeader:
                user = await auth.db.async_run_sync(self._create_role_user_sync, leader['id'], leader['nickname'], leader['email'], 'TSGLeader')
                log.debug(f'TSGLeader： {user.username} registered !')
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

