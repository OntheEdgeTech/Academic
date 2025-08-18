from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Static Files</title>
        <link rel="stylesheet" href="/static/docs.css">
    </head>
    <body>
        <h1>Test Static Files</h1>
        <p>If you can see this text in the styled format, static files are working.</p>
        <script src="/static/docs.js"></script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)