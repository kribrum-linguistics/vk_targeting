# !usr/env/bin python3
# -*- coding: utf8 -*-

import vk, datetime, time


def checkOwnerId(owner_id, group=True):
    if owner_id > 0:
        if group:
            return owner_id * -1
        else:
            return owner_id
    else:
        if group:
            return owner_id
        else:
            return owner_id * -1


def endDate():
    today_ = datetime.datetime.today()
    delta_ = datetime.timedelta(days=90)
    d = today_ - delta_
    enddate = datetime.date(d.year, d.month, d.day)
    # print('enddate type', type(enddate))
    return enddate
    

def niceDate(date_unixtime):
    d = datetime.datetime.fromtimestamp(date_unixtime)
    date_normal = datetime.date(d.year, d.month, d.day)
    # print('nicedate type', type(date_normal))
    return date_normal


def getWallPosts(group_domain, api):
    ed = endDate()
    print('collecting posts')
    a = api.wall.get(domain=group_domain, count=100)
    earliest = niceDate(a['items'][-1]['date'])
    offset = 100
    while earliest > ed:
        a += api.wall.get(domain=group_domain, count=100, offset=offset)
        offset += 100
    print('enddate reached')
    while niceDate(a['items'][-1]['date']) < ed:
        a['items'] = a['items'][:-1]
    print('excesses deleted')
    return a['items'][0]['owner_id'], [i['id'] for i in a['items']]


def getPostLikes(owner_id, item_id, api):
    '''owner_id - id группы, post_id - id поста'''
    owner_id = checkOwnerId(owner_id)
    likes = api.likes.getList(type='post', item_id=item_id, owner_id=owner_id)
    return likes['items']


def getPostCommentators(owner_id, item_id, api):
    '''owner_id - id группы, post_id - id поста'''
    owner_id = checkOwnerId(owner_id)
    # print(owner_id)
    comments = api.wall.getComments(post_id=item_id, owner_id=owner_id, count=100)
    if comments['count'] < 100:
        # print('all %s comments collected'%comments['count'])
    else:
        # print('%s comments missed' %(comments['count']-100))
    authors = [i['from_id'] for i in comments['items']]
    authors = list(set(authors))
    return authors


def postActivity(owner_id, item_id, api):
    a = {}
    '''owner_id - id группы, post_id - id поста'''
    a['likes'] = getPostLikes(item_id=item_id, owner_id=owner_id, api=api)
    a['commentators'] = getPostCommentators(item_id=item_id, owner_id=owner_id, api=api)
    return a
    

def main():
    commentators = []
    likes = []
    session = vk.Session(access_token='7d29ae37f7e4c04c2eaa9d1f83b55b4827ac9a72428a89bb3a7e8d06e89845925c78c0ee039919a64281b')
    api = vk.API(session, v='5.62', lang='ru', timeout=10)
    group_domains = ['cremboni']
    for i in group_domains:
        group_id, ids_ = getWallPosts(group_domain=i, api=api)
        counter = 0
        while counter < len(ids_):
            try:
                pa = postActivity(group_id, ids_[counter], api=api)
                likes += pa['likes']
                commentators += pa['commentators']
                counter += 1
                time.sleep(0.3333333)
            except:
                print('sleeping')
                time.sleep(0.3333333)
    likes = list(set(likes))
    commentators = list(set(commentators))
    print('group domain: %s\nlikes: %s\ncommentators: %s'%(group_id, len(likes), len(commentators)))


if __name__ == '__main__':
    main()