import asyncio
from tokenize import String
from pyppeteer import launch, errors
import base64
from bs4 import BeautifulSoup
import time
import re

class AIMS_AUTOMATION:
    async def createBrowserInstance(self):
        self.browser = await launch(headless=False, executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
    
    async def getLoginCaptcha(self):
        try:
            pages = await self.browser.pages()
            if len(pages) >1:
                await self.page.close()

            self.page = await self.browser.newPage()
            await self.page.goto('https://aims.iiitr.ac.in/iiitraichur/')

            page_source = await self.page.content()
            page_source_length = len(page_source)
            if(page_source_length < 10000):
                await self.page.reload()

            await self.page.waitForSelector('#appCaptchaLoginImg')
            captchaElement = await self.page.querySelector('#appCaptchaLoginImg')

            captchaData = await captchaElement.screenshot()

            captchaImageBase64 = base64.b64encode(captchaData).decode('utf-8')

            response = {
                "status": "Success",
                "message": "Captcha Recieved Successfuly",
                "captchaImageBase64": captchaImageBase64
            }
            
            return response
        
        except Exception as e:
            print(e)
            response = {
                "status": "Error",
                "message": "Error Occured in fetching captcha",
                "captchaImageBase64": "None"
            }
            return response
        

    async def requestLogin(self, loginId, password, captchaText):
        await self.page.evaluate("() => {document.getElementById('uid').value = ''; }")
        await self.page.evaluate("() => {document.getElementById('pswrd').value = ''; }")
        await self.page.evaluate("() => {document.getElementById('captcha').value = ''; }")
        await self.page.type('#uid', loginId)
        await self.page.type('#pswrd', password)
        await self.page.type('#captcha', captchaText)
        await self.page.click('#login')

        try:
            try:
                await self.page.waitForNavigation(timeout=10000) 

            except errors.TimeoutError:
                response = {
                    "status": "error",
                    "message": "Invalid Captcha",
                    "captchaImageBase64": "None"
                }
                return response

            errorText = await self.page.evaluate("() => {return document.getElementById('errTxt').innerText;}")

            if errorText.strip() != '':
                response = {
                    "status": "Error",
                    "message": errorText,
                    "captchaImageBase64": "None"
                }
                return response

        except Exception as e:
            print(e)

        try:
            page_source = await self.page.content()
            page_source_length = len(page_source)
            if(page_source_length < 10000):
                await self.page.reload()
            
            await self.page.waitForSelector('#appCaptchaLoginImg')
            captchaElement = await self.page.querySelector('#appCaptchaLoginImg')

            captchaData = await captchaElement.screenshot()
            captchaImageBase64 = base64.b64encode(captchaData).decode('utf-8')

            response = {
                "status": "Success",
                "message": "Login Requested",
                "captchaImageBase64": captchaImageBase64
            }

            return response
        except Exception as e:
            print(e)
            response  = {
                "status": "Error",
                "message": "Captcha Invalid or Timeout Ocuurs. Please Try Again",
                "captchaImageBase64": "None"
            }
            return response
            
    
    async def login(self, captchaText):
        await self.page.evaluate("() => {document.getElementById('captcha').value = ''; }")
        await self.page.type('#captcha', captchaText)
        await self.page.click('#submit')

        try:
            time.sleep(1.5)
            errorText = await self.page.evaluate("() => {return document.getElementById('errTxt').innerText;}")

            if errorText.strip() != '':
                response = {
                    "status": "error",
                    "name": "None",
                    "message": errorText
                }
                return response
        except Exception as e:
            print(e)
        
        try:
            page_source = await self.page.content()
            page_source_length = len(page_source)
            if(page_source_length < 10000):
                await self.page.reload()

            userName = await self.page.evaluate("() => {return document.getElementById('appUsername').innerText;}")

            response  = {
                "status": "Success",
                "name": userName,
                "message": f"Login Successful as {userName}"
            }

            return response
        
        except Exception as e:
            print(e)
            response  = {
                "status": "Error",
                "name": "None",
                "message": "Captcha Invalid or Timeout Ocuurs. Please Try Again"
            }
            return response
        

    async def viewMyCourses(self):
        try:
            url = self.page.url
            print(url)
            # if( url != "https://aims.iiitr.ac.in/iiitraichur/"):
            #     await self.page.goto('https://aims.iiitr.ac.in/iiitraichur/')

            # await self.page.evaluate("onTreemenuItemClick(7, '/courseReg/myCrsHistoryPage', this);")
            # await self.page.waitForNavigation()
            # pageSource = await self.page.content()

            # pattern = re.compile(r'studentId = "(.*?)";')
            # studentId = pattern.findall(pageSource)[0]

            courseData = await self.page.evaluate("() => {return fetch('https://aims.iiitr.ac.in/iiitraichur/courseReg/loadMyCoursesHistroy?studentId=&courseCd=&courseName=&orderBy=1&degreeIds=&acadPeriodIds=&regTypeIds=&gradeIds=&resultIds=&isGradeIds=').then(response => response.json()).then(data => data);}")

            # gradeData = await self.page.evaluate("() => {return fetch('https://aims.iiitr.ac.in/iiitraichur/courseReg/loadStdCrsHistSrchFlds/').then(response => response.json()).then(data => data);}")

            jsonResponse = {
                "status": "Success",
                "message": "Courses and Grades Successfully Retrieved",
                "gradeSource": {"data": "nothing"},
                "coursePageSource": courseData,
            }

            return jsonResponse
        
        except Exception as e:
            print(e)
            response  = {
                "status": "Error",
                "message": "Courses and Grades Data Retrieval Failed !",
                "gradeSource": {},
                "coursePageSource": [],
            }
            return response
        
    async def dispose(self):
        await self.browser.close()
    
    async def __del__(self):
        await self.dispose()
        print("Object destroyed")