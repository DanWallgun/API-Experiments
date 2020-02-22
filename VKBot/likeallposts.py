import random
import time

import vk_api

import captcha

PHONE = "80000000000"
PASSWORD = "()(()())"

TARGET_SCREEN_NAME = "tArGeT"

def teenageMutantNinjaTurtles(captchaException):
    print(captchaException.get_url())
    # print(type(captchaUrl))
    # print(captchaUrl["captcha_img"])
    resp = captcha.textFromCaptchaImage(captchaException.get_image())
    return captchaException.try_again(key=resp)

vk_session = vk_api.VkApi(PHONE, PASSWORD, captcha_handler=teenageMutantNinjaTurtles, api_version="5.95", scope=6274527)
vk_session.auth()
vk = vk_session.get_api()

MY_ID = vk.users.get()[0]["id"]
TARGET_ID = vk.users.get(user_ids=TARGET_SCREEN_NAME)[0]["id"]

def getAllPosts(vkApi, ownerId):
    firstPack = vkApi.wall.get(owner_id=ownerId, offset=0, count=100)
    count = firstPack["count"]
    res = firstPack["items"]
    while len(res) < count:
        res += vkApi.wall.get(owner_id=ownerId, offset=len(res), count=100)["items"]
    return res

def likePosts(vkApi, target):
    posts = getAllPosts(vkApi, target)
    posts = posts[:50]
    for post in posts:
        while True:
            try:
                if post["from_id"] == target:
                    vkApi.likes.add(type='post', owner_id=post['owner_id'], item_id=post['id'])
                break;
            except Exception as e:
                print('Failed:', type(e))
                if type(e) == vkApi.exceptions.ApiError:
                    print(e.error)
                # time.sleep(5)

def deleteFavePosts(vkApi):
    deleted = 0
    while True:
        posts = vkApi.fave.getPosts(count=100)
        count = posts["count"]
        posts = posts["items"]
        print(count, "posts left")
        if count == 0:
            break;
        elif len(posts) == 0:
            continue;
        post = posts[0]
        vkApi.likes.delete(type='post', owner_id=post["owner_id"], item_id=post["id"])
        deleted += 1
        if deleted == 10:
            deleted = 0
            # print("Waiting")
            # time.sleep(30)

def dislikePosts(vkApi, target):
    posts = getAllPosts(vkApi, target)
    for post in posts:
        while True:
            try:
                vkApi.likes.delete(type='post', owner_id=post['owner_id'], item_id=post['id'])
                break;
            except Exception as e:
                print('Failed:', type(e))
                if type(e) == vkApi.exceptions.ApiError:
                    print(e.error)
                # time.sleep(5)

def strangeComment(vkApi, target, msgs):
    posts = getAllPosts(vkApi, target)
    for post in posts:
        while True:
            try:
                if post["from_id"] == target:
                    vkApi.wall.createComment(type='post', owner_id=post['owner_id'], post_id=post['id'], message=random.choice(msgs))
                break;
            except Exception as e:
                print('Failed:', type(e))
                if type(e) == vkApi.exceptions.ApiError:
                    print(e.error)
                # time.sleep(5)

def deleteStrangeComment(vkApi, target, msgs, fromId):
    posts = getAllPosts(vkApi, target)
    for post in posts:
        while True:
            try:
                if post["from_id"] == target:
                    comments = vkApi.wall.getComments(owner_id=post["owner_id"], post_id=post["id"])["items"]
                    for comment in comments:
                        if comment["from_id"] == fromId and comment["text"] in msgs:
                            vkApi.wall.deleteComment(owner_id=post["owner_id"], comment_id=comment["id"])
                break;
            except Exception as e:
                print('Failed:', type(e))
                if type(e) == vkApi.exceptions.ApiError:
                    print(e.error)
                # time.sleep(5)

strange = [
    "НЛО прилетело и опубликовало эту надпись здесь",
]

likePosts(vk, TARGET_ID)
# deleteFavePosts(vk
# dislikePosts(vk, TARGET_ID)
# strangeComment(vk, TARGET_ID, strange)
# deleteStrangeComment(vk, TARGET_ID, strange, MY_ID)