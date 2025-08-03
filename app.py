from flask import Flask, render_template, request

app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return render_template("index.html", title="Hello")


@app.route("/", methods = ['GET','POST'])
def devPage() :
    return render_template("calculator.html", title = "Calculator Page")

@app.route("/calc", methods = ['GET','POST'])
def calculate() :
    if(request.method == 'POST') :
        ops = request.form['operation']
        num1 = request.form['num1']
        num2 = request.form['num2']

        num1 = float(num1)
        num2 = float(num2)

        if(ops == 'add') :
            result = num1 + num2
        elif(ops == 'sub') :
            result = num1 - num2
        elif(ops == 'mul') :
            result = num1 * num2
        else :
            result = num1 / num2    

    return render_template("result.html", value=result)