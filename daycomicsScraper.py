import undetected_chromedriver as uc
import requests
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import os
import pandas as pd
from random import randint
from time import sleep
from csvManager import CsvManager
from shutil import rmtree, make_archive

EMAIL:str = "emailName"   #INSERT THE EMAIL NOT INCLUDING THE SERVICE PROVIDER
EMAIL_DOMAIN:str = "gmail.com"  #INSERT EMAIL SERVICE (gmail.com), do NOT insert the @
PASSWORD:str = "password"
PROGRESS_FILE_PATH:str = ".\\progress.csv"
PROGRESS_COLUMNS = ["url", "status", "chapter"]
DOWNLOAD_PATH:str = ".\\downloads"
REPLACE_CHAR = "_"

#DO NOT CHANGE THIS
BAD_CHARS = ['"', "<", ">", ":", "/", "\\", "|", "?", "*", "."]
TUTORIAL_DONE = False

cm = CsvManager(csvFilePath=PROGRESS_FILE_PATH, columns=PROGRESS_COLUMNS)

#create empty csv file and download path if not found
def createPaths():
    if not os.path.exists(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)
        print(f"Download directory created: {DOWNLOAD_PATH}")
    if not os.path.exists(PROGRESS_FILE_PATH):
        df = pd.DataFrame(columns=PROGRESS_COLUMNS)
        df.to_csv(PROGRESS_FILE_PATH, index=False)
        print(f"Progress file created: {PROGRESS_FILE_PATH}")
    print("\n")

#setting up driver with options
def setup():
    options = ChromeOptions() 
    options.add_argument("--auto-open-devtools-for-tabs")
    options.add_argument("--headless")
    driver = uc.Chrome(options=options)
    print("Driver setted")
    return driver

#logging in daycomics account
def login(driver):
    print("\nLogging in")
    driver.get("https://daycomics.com/")
    sleep(randint(2, 4))
    loginButton = driver.find_element(By.XPATH, '//*[@id="sideMenuRight"]/ul/li[1]')
    loginButton.click()
    sleep(1)
    showButton = driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[2]/form/div[5]/button')
    showButton.click()
    sleep(1.5)
    emailField = driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[2]/form/div[3]/input')
    emailField.send_keys(EMAIL)
    print("email inserted")
    sleep(randint(1,2))
    emailMenu = driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[2]/form/div[3]/button')
    emailMenu.click()
    sleep(0.5)
    otherEmailDomainButton = driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[2]/form/div[3]/button/div[2]/div[6]')
    otherEmailDomainButton.click()
    sleep(0.7)
    emailDomainField = driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[2]/form/div[3]/input[2]')
    emailDomainField.send_keys(EMAIL_DOMAIN)
    print("email domain inserted")
    sleep(randint(1,2))
    passwordField = driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[2]/form/div[4]/input')
    passwordField.send_keys(PASSWORD)
    print("password inserted")
    sleep(randint(1,2))
    signInButton = driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[2]/form/div[5]')
    signInButton.click()
    sleep(randint(1,2))
    print("Log in successful\n")
    sleep(10)

#getting all the manwhas in the genres page
def getManwha(driver):
    urls = []
    print("\nNow searching for manwhas in the page")
    driver.get("https://daycomics.com/genres")
    sleep(7)
    for manwha in driver.find_elements(By.CSS_SELECTOR, ".snap-start"):
        url = manwha.find_element(By.TAG_NAME, "a").get_attribute("href")
        urls.append(url)
    print(f"Found a total of {len(urls)} manwhas")
    return urls

#from the manwha page, it returns the title, it's status (publishing or completed) and the chapter urls list
def getInfo(driver, url):
    driver.get(url)
    sleep(2)
    print(f"\nNow scanning info for the following url: {url}")
    title = driver.find_element(By.XPATH, '//*[@id="titleSubWrapper"]/span').text
    print(f"Found the following title: {title}")
    status = driver.find_element(By.XPATH, '//*[@id="episodeItemCon"]/div[2]/div[1]/div/p').text.lower()
    if "end" in status:
        status = "completed"
    else:
        status = "publishing"
    print(f"Found the following status: {status}")
    chapterUrls = []
    for chapterUrl in driver.find_elements(By.ID, "episodeItemCon"):
        chapterUrl = chapterUrl.get_attribute("href")
        chapterUrls.append(chapterUrl)
    print(f"Found a total of {len(chapterUrls)} chapters")
    return (title, status, chapterUrls)  

#given a manwha title it creates a folder for it
def createManwhaFolder(titile):
    dir = os.path.join(DOWNLOAD_PATH, titile)
    if not os.path.exists(dir):
        os.mkdir(dir)
        print(f"Created the following directory: {dir}")
    else:
        print(f"Found the following directory: {dir}")
    return dir            

#given the manwha folder path and chapter number it creates a folder for the chapter
def createChapterFolder(manwhaDir, chapterNum):
    dir = os.path.join(manwhaDir, str(chapterNum))
    if os.path.exists(dir):
        print(f"The following dir for the chapter already exists when it shouldn't: {dir}\nProbably an error occured while downloading it, it will be re-downloaded")
        rmtree(dir)
    os.mkdir(dir)
    return dir

#download images from a chapter saves them in it's chapter dir
def downloadChapter(driver, url, downloadDir):
    global TUTORIAL_DONE
    driver.get(url)
    sleep(3)
    if not TUTORIAL_DONE:
        try:
            driver.find_element(By.XPATH, '//*[@id="ModalContainer"]/div[2]/div/div[4]/button').click()
        except:
            TUTORIAL_DONE = True
    imgCount = 1
    for image in driver.find_elements(By.CSS_SELECTOR, '.rendering-auto'):
        imageSrc = image.get_attribute("data-src")
        r = requests.get(imageSrc)
        imgName = str(imgCount).zfill(3) + ".webp"
        imgPath = os.path.join(downloadDir, imgName)
        with open(imgPath, "wb") as f:
            f.write(r.content)
        sleep(randint(10, 20)/10)
        imgCount += 1

def main():
    createPaths()
    driver = setup()
    login(driver=driver)
    manwhaUrlList = getManwha(driver=driver)
    alreadyInProgress = cm.getColumn(columnName="url")
    for url in manwhaUrlList:
        if url not in alreadyInProgress:
            cm.appendRow(values=[url, "publishing", "0"])
            print(f"New manwha added to the csv file: {url}")
    for url in cm.getColumn(columnName="url"):
        if cm.getValue(columnName="url", key=url, valueColumn="status") != "completed":
            manwhaTitle, status, chapters = getInfo(driver=driver, url=url)
            for char in BAD_CHARS:
                if char in manwhaTitle:
                    manwhaTitle = manwhaTitle.replace(char, REPLACE_CHAR)
            DownloadedChapters = int(cm.getValue(columnName="url", key=url, valueColumn="chapter"))
            print(f"Chapters already downloaded: {DownloadedChapters}")
            chapters.reverse()
            totalChapters = len(chapters)
            chapters = chapters[DownloadedChapters:]
            print(f"A total of {len(chapters)} new chapters to download had been found")
            manwhaFolder = createManwhaFolder(titile=manwhaTitle)
            for chapter in chapters:
                currentChapter = DownloadedChapters + 1
                chapterDir = createChapterFolder(manwhaDir=manwhaFolder, chapterNum=currentChapter)
                print(f"Now downloading chapter number: {currentChapter}/{totalChapters}")
                downloadChapter(driver=driver, url=chapter, downloadDir=chapterDir)
                make_archive(chapterDir, 'zip', chapterDir)
                rmtree(chapterDir)
                print(f"Download completed for chapter number: {currentChapter}")
                cm.modifyValue(columnName="url", key=url, newValueColumn="chapter", newValue=str(currentChapter))
                DownloadedChapters += 1
            if status == "completed":
                cm.modifyValue(columnName="url", key=url, newValueColumn="status", newValue=status)
                print(f"Status updated to: {status}")
    

if __name__ == "__main__":
    main()