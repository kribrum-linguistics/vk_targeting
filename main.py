# !usr/env/bin python3
# -*- coding: utf8 -*-

import vk, time, sys, datetime
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


def collectFromList(list_of_lists, exclude=[[]]):
    result = []
    for i in list_of_lists:
        if i not in exclude:
            result += i
    return result


def getAllUsersFromOneGroup(groupid, api):
    members_gl = []
    offset = 0 
    g = api.groups.getMembers(group_id=int(groupid), offset=offset)['count']
    strt = datetime.datetime.now()
    est = datetime.timedelta(seconds = 0.3333333) * g/25000 * 11/5
    print(g)
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


# даём на вход список id групп, на выходе - словарь вида {группа:[юзер1, ..., юзерN]}
def getUsersFromGroups(groups_list, api):
    people = {}
    for i in groups_list:
        print(i)
        try:
            people[i] = getAllUsersFromOneGroup(i, api)
            print('\nsuccessfully collected %s members from %s'%(len(people[i]), i))
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
    if top != 0:
        return n[:top]
    else:
        return n


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


def getGroupsWithBackup(api, backup_file = 'groups.txt'):
    user_id_list = getIdList()
    user_id_set = set(user_id_list)

    g = getGroups(user_id_list, api)
    allgroups = []

    for l in g.values():
        allgroups += l
    allgroups_set = list(set(allgroups))

    with open(backup_file, 'w', encoding='utf8') as f:
        for i in allgroups_set:
            print(i, file=f)


def getAllGroupsUsers(api, top = 10, groups_file = 'groups.txt', users_file = 'allusers.txt'):
    allgroups = open('groups.txt', 'r', encoding='utf8').read().split('\n')        

    top = popularityTop(allgroups, top=top)
    print('top:')
    for i in top:
        print('\t%s'%i)
    try:
        aufile = open(users_file, 'a', encoding='utf8')
        print('allusers.txt found, adding info')
    except:
        aufile = open(users_file, 'w', encoding='utf8')
        print('allusers.txt created, adding info')

    allusers = getUsersFromGroups([i[0] for i in top], api)

    for i in allusers:
        print('%s\t%s'%(i, allusers[i]), file=aufile)

    aufile.close()


def getAllIntersections(api, au_file = 'allusers.txt'):
    allusers = {}
    aufile = open(au_file, 'r', encoding='utf8')
    for line in aufile:
        line = line.strip('\n')
        line = line.split('\t')
        allusers[line[0]] = eval(line[1])
    aufile.close()

    print('usersFromFile collected')

    group_pairs = pairs(allusers.keys())
    print('pairs made')
    resulttable = open('groups_distribution.csv', 'w', encoding='utf8')
    for i in group_pairs:
        print('working with pair %s * %s'%(i[0], i[1]))
        try:
            fst = i[0]
            snd = i[1]

            f_usrs = set(allusers[fst])
            s_usrs = set(allusers[snd])

            inters = f_usrs & s_usrs
            # print(inters)
            # print(len(list(inters)))
            inters_with_aud = inters & user_id_set
            in_aud = len(list(inters_with_aud))
            # print(in_aud)
            # print(len(user_id_list))
            # print('%s * %s - %s percent (%s) from given audience'%(fst, snd, float(in_aud/len(user_id_list)), in_aud))
            resulttable.write('%s*%s\t%s\t%s\n'%(fst, snd, float(in_aud/len(user_id_list)), in_aud))
        except Exception as e:
            pass
    resulttable.close()


if __name__ == '__main__':
    session = vk.Session(access_token='090f759f96a5275d93064832baa22e672f271ec603ee3b0177d9c113caa58100fd2ed5a8981c60c564554')
    api = vk.API(session, v='5.62', lang='ru', timeout=10)

    getGroupsWithBackup(api)
    getAllGroupsUsers(api, top = 3)
    getAllIntersections(api)

    


        