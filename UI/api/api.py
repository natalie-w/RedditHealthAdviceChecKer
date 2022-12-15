import os
import time
import random
from urllib import response

from flask import Flask, jsonify, json, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import knn


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
        "title": "Gas or Appendicitis?",
        'post': "Hi, all. I (25F) had some gas earlier in the night but after I burped a few times, i felt okay-ish. Shorty after that, I started experiencing a very sharp, stabbing pain in the abdomen. It’s the type of pain that feels like an excruciating stab every time you move or breathe. Normally I get this with gas but it’s always under my breastbone, never in my lower midsection. The pain feels as though it’s localized in the center of my stomach, a few centimeters above my bellybutton. It has been persisting for the past hour and a half now and it won’t go away. When I exhale, and I keep my stomach relaxed/deflated (like right before you inhale again), the pain remains until I inhale again. It went from annoying to excruciating and when I tried to go the bathroom, I found that I couldn’t stand straight. I couldn’t even sit upright without my stomach radiating with pain. It’s unbearable and so, can anyone advise if this is regular gas pain or appendicitis? I plan to go the dr in the morning if it persists but I’d like to get some general feedback here first. Ps. Don’t know if it’s relevant but I took Benadryl to sleep earlier.",
        "comment": "From your description I would guess it is not your appendix. First the pain is on the midline and too high up. You most likely have some other sort of GI distress going on. Gas can be extremely painful. What makes it worse or better? My advice is you are safe to wait until the morning to go and see the doctor, however if it gets worse, the pain changes location or type you should consider going to an urgent care/er. In rare cases it could be an obstruction. You know your body, and it is better to be on the safe side. Walking around will help move the gas through your system, a heating pack on your stomach can help with discomfort",
        'outputA': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. ",
        'outputB': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. ",
        'outputC': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. "},
        {'name': 'health_posts/earinfection.png', 'label': 'False', 
        "title": "Any tips on preventative measures for a UTI?",
        'post': "Do you have any tips so that I won't get UTIs all the time?",
        "comment": "You can try cranberry juice or supplements. I don't know if it's proven exactly but it can't hurt - I have some cheap ones I take daily",
        'outputA': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. ",
        'outputB': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. ",
        'outputC': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. "},
        {'name': 'health_posts/sinusinfection.png', 'label': 'False', 
        "title": "Thoughts on Prozac for teens? My teen is very depressed (more than the norm for a teen) and I feel like the Prozac has made it worse…",
        'post': "She’s been on the Prozac for some time now and she seems like she’s empty inside. She seems worse than before. Curious opinions on depression medicine for kids",
        "comment": "I have been on prozac since i was 13 (21 now). It might not be the right medicine for her. A big side effect of it in the beginning for me was while i wasnt able to fully feel the sad emotions, i wasnt able to fully feel the happy emotions either. My mom got my doctor to increase my dosage and it helped a little but it isnt a cure. Im still extremely depressed, just not a danger to myself anymore. Be careful with meds and always do a lot of research on them before giving them to her! Some can make the symptoms extremely worse while others kinda work but arent 100%. Ive never seen anyone have an antidepressant that is a cure.",
        'outputA': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. ",
        'outputB': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. ",
        'outputC': "🚨 HealthAdviceCheckBot here! 🚨 \n Based on my medical knowledge, I cannot confirm whether or not this is misinformation. We’ve thoroughly searched our database of misinformation, but haven’t found anything that contradicts the advice in the comment above. We encourage you to research on your own at https://www.nih.gov/. "},
        {'name': 'health_posts/painmed.png', 'label': 'True', 
        "title": "Dryer sheet allergy?",
        'post': "My boyfriend is allergic to dryer sheets. He doesn’t really care why exactly that is as long as we don’t use dryer sheets but I’m curious if anyone knows what component might trigger that allergic reaction?",
        "comment": "They are coated in toxic chemicals. Dryer sheets are one of the very worst things from a chemical allergy standpoint.",
        'outputA': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! \nBe careful! We have identified the above comment as MISINFORMATION. It closely matches the following three confirmed FALSE health claims. \n❌FALSE!❌  'Homeopathic doctors have found that patients commonly experience rashes in reaction to laundry products.' \n❌FALSE!❌  'Allergy patch tests show that 67% of people are allergic to common ingredients in dryer sheets.' \n❌FALSE!❌   'The fragrance and surfactant ingredients in dryer sheets are a known cause of allergic reactions.'\nWe recommend that you do NOT follow the above advice!",
        'outputB': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! \nBased on my medical knowledge, I am 72% sure that the above comment is ❌FALSE!❌ Use caution and do not follow that advice!",
        'outputC': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! \nThe above comment contains dangerous health advice! DO NOT FOLLOW that advice! "},
        {'name': 'health_posts/anxiety.png', 'label': 'True', 
        "title": "Sodium Bicarbonate as an Ergogenic Aid? Curious to know whether any of our 'shorter' distance friends, i.e,. 400-1500m friends have used baking soda for a competitive boost?",
        'post': "So i've been taking an online sports nutrition class to learn more about nutrition and how it impacts us as athletes. One of the most curious things though was today we discussed Sodium Bicarbonate (baking soda) and how it can be a performance aid.  This rearch is from this paper by Shelton and Praveen Kumar (2010). Totally puzzled by this I did some googling, found this study of studies and was like, hot damn, the ingredient I bake with multiple times a week has a performance enhancing ability I never knew about. Sadly per the data, it really only benefits our friends who would run the 1500m or less. So I wanted to see some anecdotal reports of anyone who has tried it and what you thought! Hell, I might try it on workouts where I do 800m repeats or something just to see in the future.",
        "comment": "Yes. Baking soda can help. However, I would only consider it for a competition, not general workouts. My hypothesis is that you should train your body how to properly and quickly flush itself of lactic acid without supplements.",
        'outputA': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! \nBe careful! We have identified the above comment as MISINFORMATION. It closely matches the following three confirmed FALSE health claims.\n❌FALSE!❌  'Baking soda is a successful doping method for runners.' \n❌FALSE!❌  'Athletes experience a boost in their performance when they take 1 tsp of baking soda before a race.' \n❌FALSE!❌   'Research from Johns Hopkins University shows that taking a small amount of baking soda has a beneficial effect on lactic acid release of college athletes.'\nWe recommend that you do NOT follow the above advice!",
        'outputB': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! Based on my medical knowledge, I am 86% sure that the above comment is ❌FALSE!❌ Use caution and do not follow that advice!",
        'outputC': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! The above comment contains dangerous health advice! DO NOT FOLLOW that advice!"},
        {'name': 'health_posts/cold.png', 'label': 'True', 
        "title": "Can you clear up a UTI without needing antibiotics?",
        'post': "For example, if you catch it early enough, can you just drown it in cranberry juice?",
        "comment": "I've succeeded with the baking soda treatment. Basically, you put teaspoon baking soda in a huge glass of water and throughout the day you drink it. With each sip of baking water, you drink normal water. Yes, you will pee every five minutes. But in the end, I was done my infection in one day.",
        'outputA': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: \n ❌FALSE!❌  'Baking soda has been proven to cure UTIs, according to research from the University of Arizona.' \n ❌FALSE!❌  'A common household cure for UTIs to take 2 teaspoons of baking soda every hour to treat a UTI.' \n ❌FALSE!❌   'Healthline.com says that if you take baking soda, your UTI will be gone within 4 hours.'",
        'outputB': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! Based on my medical knowledge, I am 93% sure that the above comment is ❌FALSE!❌ Use caution and do not follow that advice!",
        'outputC': "🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! The above comment contains dangerous health advice! DO NOT FOLLOW that advice!"}]


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
    # comment = images[0]["comment"]
    # output = knn.run_knn(comment, 3)
    # return jsonify("🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! Here are the top three FALSE claims that match the potential misinformation above: \n ❌FALSE!❌ {0} ; similarity score: {1} \n ❌FALSE!❌ {2} ; similarity score: {3} \n ❌FALSE!❌ {4} ; similarity score: {5}".format(output[0][0], output[0][1], output[1][0], output[1][1], output[2][0], output[2][1]))

    return jsonify(response_body)
# get model prediction
@app.route('/modelPrediction', methods=['POST'])
def getModelPrediction():
    # define the order of the images to be loaded
    request_data = json.loads(request.data)
    output = knn.run_knn(request_data, 3)
    if len(output) == 2:
        return jsonify("🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! Here are the top FALSE claims that match the potential misinformation above: \n ❌FALSE!❌ {0} ; similarity score: {1} \n ❌FALSE!❌ {2} ; similarity score: {3}".format(output[0][0], output[0][1], output[1][0], output[1][1]))
    else:
        return jsonify("🚨 ALERT! 🚨 \n HealthAdviceCheckBot here! Here are the top FALSE claims that match the potential misinformation above: \n ❌FALSE!❌ {0} ; similarity score: {1} \n ❌FALSE!❌ {2} ; similarity score: {3} \n ❌FALSE!❌ {4} ; similarity score: {5}".format(output[0][0], output[0][1], output[1][0], output[1][1], output[2][0], output[2][1]))
    # return jsonify("helo")

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

