# !usr/env/bin python3
# -*- coding: utf8 -*-

import vk, time, sys, datetime


def backupDict(dict_, fname):
    with open(fname, 'w', encoding='utf8') as f:
        for k in dict_.keys():
            if dict_[k] != []:
                for i in dict_[k]:
                    f.write('%s\t%s\n'%(k, i))

def restoreDict(fname):
    fin = {}
    with open(fname, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip('\n')
            line = line.split('\t')
            try:
                fin[line[0]].append(line[1])
            except:
                fin[line[0]] = [line[1]]
    return fin


def getUserIdFromFile(fname='positions_slice.txt', set_=False):
    # открывает файл fname
    # возвращает список id пользователей вк из файла
    f = open(fname, 'r', encoding='utf8')
    ids = [line[3:][:-1] for line in f]
    ids_set = set(ids)
    if set_:
        print('returning SET of user ids')
        return ids_set
    else:
        print('returning LIST of user ids')
        return list(ids_set)


def getGroups(user_id_list, api, bfile=''):
    # возвращает словарь:
    # ключи - id пользователя
    # значения - список id групп, где состоит пользователь
    print('collecting groups from %s users'%len(user_id_list))
    groups = {}
    for user_id in user_id_list:
        print(user_id)
        try:
            g = api.groups.get(user_id=user_id)
            groups[user_id] = g['items']
            print('successfully collected %s groups'%len(g['items']))
        except Exception as e:
            print(e)
            groups[user_id] = []
        time.sleep(0.3333333333)
        print('')
    print('groups collected')
    backupDict(groups, 'groups.txt')
    return groups


def collectFromList(list_of_lists):
    ## берет на вход список списков
    ## возвращает сумму этих списков
    result = []
    for i in list_of_lists:
        if type(i) == list:
            result += collectFromList(i)
        else:
            result.append(i)
    return result


def getGroupUsers(groupid, api):
    ## берет на вход id группы вк
    ## возвращает список id пользователей этой группы
    members_gl = []
    offset = 0 
    g = api.groups.getMembers(group_id=int(groupid), offset=offset)['count']
    strt = datetime.datetime.now()
    est = datetime.timedelta(seconds = 0.3333333) * g/25000 * 11/5
    print(g)
    if g == 0:
        print('api method returned no users. perhaps group is blocked')
        return []
    else:
        print('estimated time: %s'%est)
        if offset > g:
            print('1 iteration')
            code = open('getAllUsersFromOneGroup.vkcode', 'r', encoding='utf8').read()
            code = code%(offset, groupid)
            members = api.execute(code=code)
            print(len(members))
        else:
            print('several iterations')
            while offset < g + 25000:
                code = open('getAllUsersFromOneGroup.vkcode', 'r', encoding='utf8').read()
                code = code%(offset, groupid)
                returned = api.execute(code=code)
                offset_ = returned[0]
                members = returned[1]
                members_gl += members
                offset = offset_
                time.sleep(0.3333333)
                sys.stdout.write('\rcollected %s users out of %s'%(len(collectFromList(members_gl)), g))
                sys.stdout.flush()
        fnsh = datetime.datetime.now()
        print('\nspent time: %s'%(fnsh-strt))
        return collectFromList(members_gl)


def getUsersFromGroups(groups_list, api):
    groups_list = restoreDict('groups.txt')
    # берет на вход список id групп вк
    # возвращает словарь вида {id_группы:[id_юзера_1, ..., id_юзера_n]}
    people = {}
    for i in groups_list:
        print(i)
        try:
            people[i] = getGroupUsers(i, api)
            print('\nsuccessfully collected %s members from %s'%(len(people[i]), i))
        except Exception as e:
            print(e)
            people[i] = []
        time.sleep(0.3333333333)
        print('')
    print('users from groups collected')
    for i in people:
        print(i, len(people[i]))
    backupDict(people, 'people.txt')
    return people


def pairs(list_, exclude_doubles=True):
    fin = []
    for i in list_:
        for j in list_:
            if exclude_doubles:
                if i != j and [j,i] not in fin:
                    fin.append([i,j])
            else:
                fin.append([i,j])
    return fin


def intersections(people):

    pairs_ = pairs(people.keys())
    user_id_set = getUserIdFromFile(set_=True)

    for p in pairs_:
        f_g, s_g = p[0], p[1]
        # print(f_g, s_g)
        f_usrs, s_usrs = set(people[f_g]), set(people[s_g])
        # print(f_usrs, s_usrs)
        pair_intersection = f_usrs & s_usrs
        print('%s * %s: %s people'%(f_g, s_g, len(list(pair_intersection))))
        main_intersection = pair_intersection & user_id_set
        print('%s * %s * main: %s people'%(f_g, s_g, len(list(main_intersection))))
        


if __name__ == '__main__':

    session = vk.Session(access_token='090f759f96a5275d93064832baa22e672f271ec603ee3b0177d9c113caa58100fd2ed5a8981c60c564554')
    api = vk.API(session, v='5.62', lang='ru', timeout=10)

    # user_id_list = getUserIdFromFile()
    groups = getGroups(user_id_list, api)
    # groups = restoreDict('groups.txt')
    people = getUsersFromGroups(groups, api)
    # people = restoreDict('people.txt')
    intersections(people)
    

