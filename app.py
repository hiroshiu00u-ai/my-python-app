from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hello, Render!</h1><p>これはPythonで作った動的Webアプリです。</p>"

if __name__ == '__main__':
    app.run(debug=True)