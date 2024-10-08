from flask import Flask, jsonify, Response, make_response, request
import uuid
import base64
from automation import AIMS_AUTOMATION
from asgiref.wsgi import WsgiToAsgi
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
asgi_app = WsgiToAsgi(app)

sessions = {}

@app.route("/api/v1/getCaptcha", methods=["POST"])
async def getCaptcha():
    try:
        sessionId = request.json.get("sessionId")
        try:
            session = sessions[sessionId]['session']

            response = await session.getLoginCaptcha()

            # # For Testing Purpose only

            imageString = f'<img src="data:image/png;base64,{response['captchaImageBase64']}" alt="captcha">'
            with open('captcha.html','w') as f:
                f.write(imageString)   
                f.close()

            # # 

            jsonResponse = {
                "sessionId": sessionId,
                "status": response['status'],
                "message": response['message'],
                "captchaBase64": response['captchaImageBase64']
            }

            return jsonify(jsonResponse)

        except Exception as e:
            None

        # id = str(uuid.uuid4())
        id = "CS23B1066"
        session = AIMS_AUTOMATION()
        await session.createBrowserInstance()
        response = await session.getLoginCaptcha()

        sessions[id]= {
            "session": session
        }

        # # For Testing Purpose only

        imageString = f'<img src="data:image/png;base64,{response['captchaImageBase64']}" alt="captcha">'
        with open('captcha.html','w') as f:
            f.write(imageString)   
            f.close()

        # # 

        jsonResponse = {
            "sessionId": id,
            "status": response['status'],
            "message": response['message'],
            "captchaBase64": response['captchaImageBase64']
        }

        return jsonify(jsonResponse)
    
    except Exception as e:
        print(e)
        jsonResponse = {
            "sessionId": "None",
            "status": "Error",
            "message": "Internal Server Error",
            "captchaBase64": "None"
        }
        return jsonify(jsonResponse)
    
@app.route("/api/v1/requestLogin", methods=["POST"])
async def requestLogin():
    try:
        id = request.json.get("sessionId")
        loginId = request.json.get("loginId")
        password = request.json.get("password")
        captcha = request.json.get("captcha")

        try:
            session = sessions[id]['session']
        except Exception as e:
            jsonResponse = {
                "sessionId": "None",
                "status": "Error",
                "message": "Invalid Session Id !",
                "captchaBase64": "None"
            }
            return jsonify(jsonResponse)
        
        response = await session.requestLogin(loginId, password, captcha)
        
        # # For Testing Purpose only

        imageString = f'<img src="data:image/png;base64,{response['captchaImageBase64']}" alt="captcha">'
        with open('captcha.html','w') as f:
            f.write(imageString)   
            f.close()

        # # 

        jsonResponse = {
            "sessionId": id,
            "captchaBase64": response['captchaImageBase64'],
            "status": response['status'],
            "message": response['message']
        }

        return jsonify(jsonResponse)
    
    except Exception as e:
        print(e)
        jsonResponse = {
            "sessionId": "None",
            "status": "Error",
            "message": "Internal Server Error in requesting login",
            "captchaBase64": "None"
        }
        return jsonify(jsonResponse)

@app.route("/api/v1/login", methods=["POST"])
async def login():
    try:
        id = request.json.get("sessionId")
        captcha = request.json.get("captcha")

        try:
            session = sessions[id]['session']
        except Exception as e:
            jsonResponse = {
                "sessionId": "None",
                "status": "Error",
                "name": "None",
                "message": "Invalid Session Id !"
            }
            return jsonify(jsonResponse)

        response = await session.login(captcha)
        jsonResponse = {
            "sessionId": id,
            "status": response['status'],
            "name": response['name'],
            "message": response['message']
        }

        return jsonify(jsonResponse)
    
    except Exception as e:
        print(e)
        jsonResponse = {
            "sessionId": "None",
            "status": "Error",
            "name": "None",
            "message": "Internal Server Error in login"
        }
        return jsonify(jsonResponse)
    
@app.route("/api/v1/getCourseHistory", methods=["POST"])
async def getCourseHistory():
    try:
        id = request.json.get("sessionId")

        try:
            session = sessions[id]['session']
        except Exception as e:
            jsonResponse = {
                "sessionId": "None",
                "status": "Error",
                "message": "Invalid Session Id !",
                "gradeSource": {},
                "courses": []
            }
            return jsonify(jsonResponse)
        
        response = await session.viewMyCourses()
        jsonResponse = {
            "id": id,
            "status": response['status'],
            "message": response['message'],
            "gradeSource": response['gradeSource'],
            "courses": response['coursePageSource']
        }

        return jsonify(jsonResponse)
    
    except Exception as e:
        # print(e)
        jsonResponse = {
            "id": id,
            "status": "Error",
            "message": "Internal Serval Error in fetching grades and courses",
            "gradeSource": {},
            "courses": []
        }
        return jsonify(jsonResponse)
    
@app.route("/api/v1/disposeUser", methods=["POST"])
async def disposeUser():
    try:
        id = request.json.get("sessionId")
        print('dispose user called: '+ id)

        try:
            session = sessions[id]['session']
        except Exception as e:
            jsonResponse = {
                "sessionId": "None",
                "status": "Error",
                "message": "Invalid Session Id to dispose or Session already disposed"
            }
            return jsonify(jsonResponse)
        
        await session.dispose()
        del sessions[id]

        jsonResponse = {
            "status": "Success",
            "message": f"User Disposed with session id : {id}",
        }

        return jsonify(jsonResponse)
    
    except Exception as e:
        print(e)
        jsonResponse = {
            "status": "Error",
            "message": f"User Disposed Failed ! with session id : {id}",
        }
        return jsonify(jsonResponse)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=5001)