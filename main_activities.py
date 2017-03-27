# !usr/env/bin python3
# -*- coding: utf8 -*-

print('main_activities imported')
import vk


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


def getPostLikes(owner_id, item_id, api):
    '''owner_id - id группы, post_id - id поста'''
    owner_id = checkOwnerId(owner_id)
    likes = api.likes.getList(type='post', item_id=item_id, owner_id=owner_id)
    return likes['items']


def getPostCommentators(owner_id, item_id, api):
    '''owner_id - id группы, post_id - id поста'''
    owner_id = checkOwnerId(owner_id)
    print(owner_id)
    comments = api.wall.getComments(post_id=item_id, owner_id=owner_id, count=100)
    if comments['count'] < 100:
        print('all %s comments collected'%comments['count'])
    else:
        print('%s comments missed' %(comments['count']-100))
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
    session = vk.Session(access_token='7d29ae37f7e4c04c2eaa9d1f83b55b4827ac9a72428a89bb3a7e8d06e89845925c78c0ee039919a64281b')
    api = vk.API(session, v='5.62', lang='ru', timeout=10)
    print(postActivity(owner_id = 11843074, item_id = 3502, api=api))


if __name__ == '__main__':
    main()