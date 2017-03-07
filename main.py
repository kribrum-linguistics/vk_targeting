# !usr/env/bin python3
# -*- coding: utf8 -*-

import vk, time
import _pickle as pickle


def getIdList(fname='positions_slice.txt'):
    f = open(fname, 'r', encoding='utf8')
    ids = [line[3:][:-1] for line in f]
    return list(set(ids))


def getGroups(user_id_list, api):
    print('collecting groups...')
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
        print('')
    print('groups collected')
    return groups


 # даём на вход список id групп, на выходе - словарь вида {группа:[юзер1, ..., юзерN]}
def getUsersFromGroups(groups_list, api):
    people = {}
    for i in groups_list:
        print(i)
        try:
            g = api.groups.getMembers(group_id=int(i))
            people[i] = g['items'] 
            print('successfully collected %s members from %s'%(g['count'], i))
        except Exception as e:
            print(e)
            people[i] = []
        time.sleep(0.3333333333)
        print('')
    print('users from groups collected')
    return people


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


def pairs(list_, exclude_doubles=True):
    fin = []
    for i in list_:
        for j in list_:
            if exclude_doubles:
                if i != j:
                    fin.append([i,j])
            else:
                fin.append([i,j])
    return fin



if __name__ == '__main__':
    session = vk.Session(access_token='090f759f96a5275d93064832baa22e672f271ec603ee3b0177d9c113caa58100fd2ed5a8981c60c564554')
    api = vk.API(session, v='5.62', lang='ru', timeout=10)
    user_id_list = getIdList()
    g = getGroups(user_id_list, api)
    allgroups = []

    for l in g.values():
        allgroups += l
    allgroups_set = set(allgroups)

    with open('groups.txt', 'w', encoding='utf8') as f:
        for i in allgroups:
            print(i, file=f)

    allgroups = open('groups.txt', 'r', encoding='utf8').read().split('\n')        

    top = popularityTop(allgroups)
    allusers = getUsersFromGroups([i[0] for i in top], api)
    # print(allusers)

    group_pairs = pairs(allgroups)
    for i in group_pairs:
        try:
            fst = i[0]
            snd = i[1]
            f_usrs = set(allusers[fst])
            s_usrs = set(allusers[snd])
            inters = f_usrs & s_usrs
            inters_with_aud = inters & allgroups_set
            in_aud = len(list(inters_with_aud))
            print('%s * %s - %s percent from given audience'%(fst, snd, float(in_aud/len(user_id_list))))
        except Exception as e:
            pass