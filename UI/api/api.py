import os
import time
import random
from urllib import response

from flask import Flask, jsonify, json, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    task = db.Column(db.Integer, nullable=False)

    def __init__(self, task):
        self.task = task


class Responses(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    q_id = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    ans = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Float, nullable=False)

    def __init__(self, q_id, user_id, ans, time):
        self.q_id = q_id
        self.user_id = user_id
        self.ans = ans
        self.time = time


class Survey(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    q1 = db.Column(db.Integer, nullable=False)
    q2 = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, q1, q2):
      self.user_id = user_id
      self.q1 = q1
      self.q2 = q2


# define image names. You can load this information from a local file or a database
images = [
        {'name': 'health_posts/uti.png', 'label': 'False', 
        'outputA': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: /n ❌FALSE!❌  'Baking soda has been proven to cure UTIs.' /n ❌FALSE!❌  'Take 2 teaspoons of baking soda every hour to treat a UTI.' /n ❌FALSE!❌   'If you take baking soda, your UTI will be gone within 4 hours!!'",
        'outputB': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Based on our database of misinformation, we are 85% sure that the above comment is ❌FALSE!❌",
        'outputC': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! DO NOT DO THIS ADVICE!"},
        {'name': 'health_posts/cold.png', 'label': 'False', 
        'outputA': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: /n ❌FALSE!❌  'Debrox has been proven to cure ear infections.' /n ❌FALSE!❌  'Flushing or irrigating an infected ear will make swelling go down.' /n ❌FALSE!❌   'False statement 3'",
        'outputB': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Based on our database of misinformation, we are 97% sure that the above comment is ❌FALSE!❌",
        'outputC': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! DO NOT DO THIS ADVICE!"}, 
        {'name': 'health_posts/sinusinfection.png', 'label': 'False', 
        'outputA': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: /n ❌FALSE!❌  'False statement 1.' /n ❌FALSE!❌  'False statement 2' /n ❌FALSE!❌   'False statement 3'",
        'outputB': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Based on our database of misinformation, we are 68% sure that the above comment is ❌FALSE!❌",
        'outputC': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! DO NOT DO THIS ADVICE!"},
        {'name': 'health_posts/painmed.png', 'label': 'True', 
        'outputA': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: /n ❌FALSE!❌  'False statement 1.' /n ❌FALSE!❌  'False statement 2' /n ❌FALSE!❌   'False statement 3'",
        'outputB': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Based on our database of misinformation, we are 71% sure that the above comment is ❌FALSE!❌",
        'outputC': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! DO NOT DO THIS ADVICE!"},
        {'name': 'health_posts/anxiety.png', 'label': 'True', 
        'outputA': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: /n ❌FALSE!❌  'False statement 1.' /n ❌FALSE!❌  'False statement 2' /n ❌FALSE!❌   'False statement 3'",
        'outputB': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Based on our database of misinformation, we are 82% sure that the above comment is ❌FALSE!❌",
        'outputC': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! DO NOT DO THIS ADVICE!"},
        {'name': 'health_posts/earinfection.png', 'label': 'True', 
        'outputA': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: /n ❌FALSE!❌  'False statement 1.' /n ❌FALSE!❌  'False statement 2' /n ❌FALSE!❌   'False statement 3'",
        'outputB': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! Based on our database of misinformation, we are 94% sure that the above comment is ❌FALSE!❌",
        'outputC': "🚨 ALERT! 🚨 /n HealthAdviceCheckBot here! DO NOT DO THIS ADVICE!"}]


# check that the backend is connected
@app.route('/time')
def get_current_time():
    return jsonify({'time': time.strftime("%I:%M:%S %p", time.localtime())})


@app.route('/setup', methods=['GET'])
def setup():
    # assign a random task to the current user
    task_num = random.randint(1,2)
    new_user = User(task=task_num)
    db.session.add(new_user)
    db.session.commit()
    user_id = new_user.user_id
    response = {'user_id': user_id, 'task_number': task_num}
    return jsonify(response)


@app.route('/imageInfo', methods=['GET'])
def getImageInfo():
    # define the order of the images to be loaded
    random.shuffle(images)
    response_body = {'imgs': images}
    return jsonify(response_body)


# send data from frontend to backend
@app.route('/responsesData', methods=['POST'])
def responsesData():
    request_data = json.loads(request.data)
    q_id = request_data['q_id']
    user_id = request_data['user_id']
    ans = request_data['ans']
    time = request_data['time']
    print('saving data')
    new_entry = Responses(q_id, user_id, ans, time)
    db.session.add(new_entry)
    db.session.commit()
    msg = "Record successfully added"
    print(msg)
    response_body = {'user_id': user_id}
    return jsonify(response_body)


@app.route('/surveyData', methods=['POST'])
def surveyData():
    request_data = json.loads(request.data)
    user_id = request_data['user_id']
    q1 = request_data['q1']
    q2 = request_data['q2']
    new_entry = Survey(user_id=user_id, q1=q1, q2=q2)
    db.session.add(new_entry)
    db.session.commit()
    msg = "Record successfully added"
    print(msg)
    response_body = {'user_id': user_id}
    return jsonify(response_body) 


# auxiliary functions to visualize data
def responses_serializer(obj):
    return {
      'id': obj.id,
      'q_id': obj.q_id,
      'user_id': obj.user_id,
      'ans': obj.ans,
      'time': obj.time
    }


def user_serializer(obj):
  return {
    'user_id': obj.user_id,
    'task': obj.task
  }


# visualize the current entries in the tables
@app.route('/api', methods=['GET'])
def api():
    return jsonify([*map(responses_serializer, Responses.query.all())])
    # return jsonify([*map(user_serializer, User.query.all())])


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

