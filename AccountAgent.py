from time import sleep
from selenium.common.exceptions import NoSuchElementException
import datetime
import DBUsers, Constants
import traceback
import random
import sys


followed = 0
countLikes = 0
limitFollowed = 50
limitLikes = 50

def login(webdriver):
    #Open the instagram login page
    webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
    #sleep for 3 seconds to prevent issues with the server
    sleep(3)
    #Find username and password fields and set their input using our constants
    username = webdriver.find_element_by_name('username')
    username.send_keys(Constants.INST_USER)
    password = webdriver.find_element_by_name('password')
    password.send_keys(Constants.INST_PASS)
    #Get the login button
    try:
        button_login = webdriver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button')
    except:
        button_login = webdriver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[6]/button/div')
    #sleep again
    sleep(2)
    #click login
    button_login.click()
    sleep(3)
    #In case you get a popup after logging in, press not now.
    #If not, then just return
    try:
        notnow = webdriver.find_element_by_css_selector(
            'body > div.RnEpo.Yx5HN > div > div > div.mt3GC > button.aOOlW.HoLwm')
        notnow.click()
    except:
        return
    

def follow_people(webdriver):
    #all the followed user
    prev_user_list = DBUsers.get_followed_users()
    #a list to store newly followed users
    new_followed = []
    #counters    
    global followed 
    likes = 0
    global countLikes

    #Iterate through all the hashtags from the constants
    for hashtag in Constants.HASHTAGS:
        #Visit the hashtag
        webdriver.get('https://www.instagram.com/explore/tags/' + hashtag+ '/')
        sleep(5)

        #Get the first post thumbnail and click on it
        first_thumbnail = webdriver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div/div[2]')

        first_thumbnail.click()
        sleep(random.randint(1,3))

        try:
            #iterate over the first 240 posts in the hashtag
            for x in range(1,240):
                t_start = datetime.datetime.now()
                #Get the poster's username                  
                username = webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/span/a').text
                likes_over_limit = False
                try:
                    #get number of likes and compare it to the maximum number of likes to ignore post
                    likes = webdriver.find_element_by_xpath(
                        '/html/body/div[4]/div[2]/div/article/div[3]/section[2]/div/div/button/span').text
                    likes = likes.replace(',', '')
                    likes = int(likes)
                        
                    if likes > Constants.LIKES_LIMIT:
                        print("likes over {0}".format(Constants.LIKES_LIMIT))
                        likes_over_limit = True

                    print("Detected: {0}".format(username))
                    #If username isn't stored in the database and the likes are in the acceptable range
                    #if username not in prev_user_list and not likes_over_limit:
                    if not likes_over_limit:
                        #Don't press the button if the text doesn't say follow 
                        if webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button').text == 'Follow' and followed < limitFollowed:
                            #Use DBUsers to add the new user to the database
                            DBUsers.add_user(username)
                            #Click follow                    
                            #thi is the old line code
                            webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button').click()
                           # buttoon = webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button')
                            #webdriver.execute_script("arguments[0].click();", buttoon)
                            
                            followed += 1
                            print("Followed: {0}, #{1}".format(username, followed))
                            new_followed.append(username)


                        if countLikes < limitLikes:
                           # button_like = webdriver.find_element_by_xpath("/html/body/div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button")
                            button_like = webdriver.find_element_by_css_selector("span.fr66n > button  > div > svg")
                            valueButton = button_like.get_attribute('aria-label')
                            if valueButton == 'Like':
                                button_like.click()
                                likes += 1
                                countLikes += 1
                            #webdriver.execute_script("arguments[0].click();", button_like)
                           
                            
                            print("Liked {0}'s post, #{1}, Total likes from me: {2}".format(username, likes, countLikes))
                            sleep(random.randint(80, 118))
                            

                    # Next picture
                    #webdriver.find_element_by_link_text('Next').click()
                    #sleep(random.randint(20, 30))
                    
                except NoSuchElementException:
                    #traceback.print_exc()
                    #webdriver.find_element_by_link_text('Next').click()
                    #sleep(random.randint(20, 30))
                    continue
                
                finally:
                    # Next picture
                    webdriver.find_element_by_link_text('Next').click()
                    sleep(random.randint(80, 99))
                    
                    t_end = datetime.datetime.now()
                    #calculate elapsed time
                    t_elapsed = t_end - t_start
                    print("This post took {0} seconds".format(t_elapsed.total_seconds()))
                    if followed == limitFollowed and countLikes == limitLikes:
                        print(datetime.datetime.now())
                        webdriver.quit()
                        sys.exit()


        except NoSuchElementException:
            #traceback.print_exc()
            continue

        #add new list to old list
        for n in range(0, len(new_followed)):
            prev_user_list.append(new_followed[n])
        print('Liked {} photos.'.format(likes))
        print('Followed {} new people.'.format(followed))
        

def unfollow_people(webdriver, people):
    #if only one user, append in a list
    global followed

    if not isinstance(people, (list,)):
        p = people
        people = []
        people.append(p)

    for user in people:
        try:
            webdriver.get('https://www.instagram.com/' + user + '/')
            sleep(5) 
            unfollow_xpath = '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button'
            unfollow_confirm_xpath = '/html/body/div[5]/div/div/div[3]/button[1]'
            
            

            if webdriver.find_element_by_xpath(unfollow_xpath).text == "Following" and followed < limitFollowed:
                sleep(random.randint(4, 15))
                webdriver.find_element_by_xpath(unfollow_xpath).click()
                sleep(2)
                webdriver.find_element_by_xpath(unfollow_confirm_xpath).click()
                sleep(4)
                followed += 1
            DBUsers.delete_user(user)

        except Exception:
            traceback.print_exc()
            continue
    print("people unfollowed ",followed)
