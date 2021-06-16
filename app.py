'''
from flask import Flask, request, make_response, json
'''

from flask import Flask,request,jsonify, json
app = Flask(__name__)

@app.route("/")
def hello2():
    return "Hello2 again, Universal!"

@app.route('/testme')
def home():
    return 'success'

companies = [{"id":11,"name":"Jack"},{"id":22,"name":"Jill"}]
@app.route('/companies', methods=['GET'])
def getcos():
    return json.dumps(companies)

@app.route('/simulate',methods=['POST'])
def recommend():
    df_result=get_recommendation(request)
    return(jsonify(df_result.to_json(orient='records')))
#     return recommendation(request)
if __name__=='__main__':
    app.run(debug=True)


