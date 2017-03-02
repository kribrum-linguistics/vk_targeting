# !usr/env/bin python3
# -*- coding: utf8 -*-

import vk, time

def getIdList(fname='positions_slice.txt'):
    f = open(fname, 'r', encoding='utf8')
    ids = [line[3:][:-1] for line in f]
    return list(set(ids))


def getGroups(user_id_list, api):
    groups = {}
    for i in user_id_list:
        print(i)
        try:
            g = api.groups.get(user_id=i)
            groups[i] = g['items']
            print('successfully collected %s groups'%len(g['items']))
        except Exception as e:
            print(e)
            groups[i] = [e]
        time.sleep(0.3333333333)
        print('\n')
    return groups


def popularityTop(allgroups, top=10):
    d = {}
    for i in allgroups:
        try:
            d[i] += 1
        except:
            d[i] = 1
    n = [[i,d[i]] for i in d]
    n = sorted(n, key=lambda x: x[1], reverse=True)
    return n[:top]



if __name__ == '__main__':

    session = vk.Session(access_token='090f759f96a5275d93064832baa22e672f271ec603ee3b0177d9c113caa58100fd2ed5a8981c60c564554')
    api = vk.API(session, v='5.62', lang='ru', timeout=10)
    user_id_list = getIdList()
    g = getGroups(user_id_list, api)
    # for i in g:
    #     print(i, g[i])
    allgroups = []
    for l in g.values():
        allgroups += l
    for i in popularityTop(allgroups):
        print(i)
