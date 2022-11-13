import React, { Component, useState, useEffect } from "react";
import {Button, Modal, Checkbox, Input, Radio} from 'antd'
import Popup from '../Popup';
import "antd/dist/antd.css";
import "../main.css";


import PredictionContainer from '../../../components/predictionContainer'

function TrainingContainer() {
    const [choice, setChoice] = useState(0);
    const [imageData, setImageData] = useState([]);
    const [currentImage, setCurrentImage] = useState("");
    const [currentTitle, setCurrentTitle] = useState("");
    const [currentPost, setCurrentPost] = useState("");
    const [currentComment, setCurrentComment] = useState("");
    const [currentPrediction, setCurrentPrediction] = useState("");
    const [imageCount, setImageCount] = useState(0);
    const [showPrediction, setShowPrediction] = useState(false);
    const [showSurvey, setShowSurvey] = useState(false);
    const [taskTime, setTaskTime] = useState((Date.now() + 1000 * 1000));
    const [isOpen, setIsOpen] = useState(false);
    const [answeredQuestions, setAnsweredQuestions] = useState(false);

    const [currentTime, setCurrentTime] = useState(0);

    const [render, setRender] = useState(false);

    let totalImages = 6;
    const baseImgUrl = "./";

    const routeChange = () =>{ 
        let path = '/#/Survey'; 
        window.location.assign(path);

    }

    const nextChange = () =>{
        if (!showSurvey) {
            alert("Please make sure to review the bot's output before trying to move on.");
        } else {
            let path = '/#/Instructions'; 
            // history.push(path);
            window.location.assign(path);
        }
    }


    function newTab() {
            setAnsweredQuestions(true)
            window.open(
            "https://forms.gle/PYG7cbrJVbPamjox8", "_blank");
        }

    const sendData = (obj) => {
        fetch('http://localhost:8080/responsesData', {
          method: 'POST',
          body: JSON.stringify(obj),
          headers: {
            "Content-type": "application/json; charset=UTF-8"
          }
        }).then(response => response.json())
          .then(message => {
            console.log(message)
          })
      } 


    const onChangeMultiple= e => {
        setChoice(e.target.value);
    };

    const togglePopup = () => {
    setIsOpen(!isOpen);
    setChoice(1)
  }

    const [agree, setAgree] = useState(false);

    const handlePredict=()=>{
        setShowPrediction(true);
        setShowSurvey(true);
    };

        const checkboxHandler = () => {
        setAgree(!agree);
    }


    // testing communication with backend
    useEffect(() => {
        fetch('http://0.0.0.0:8080/time').then(res => 
        res.json()).then(data => {
            setCurrentTime(data.time);
            console.log(data.time)
        });
        }, []);
    

    // initialize image
    useEffect(() => {
        console.log('getting images')
        fetch('http://localhost:8080/imageInfo')
        .then(response => response.json())
        .then(data => {
            setImageData(data['imgs']);
            let image_name = data['imgs'][0].name
            setCurrentImage(image_name)
            setCurrentTitle(data['imgs'][0].title)
            setCurrentPost(data['imgs'][0].post)
            setCurrentComment(data['imgs'][0].comment)
            setCurrentPrediction(data['imgs'][0].outputA);
            setRender(true);
            setTaskTime(Date.now())
        });
    }, []);



    return (
      <>
       {render ?

            <div className="container">
            <div className="title">Training</div>
                <h3 id="directionsheader">In this experiment, you will interact with some Reddit posts and a Reddit bot. </h3>
                <p id="directions">In each Reddit post, the Reddit user will be seeking advice for a health issue, and another user will comment with health advice. For example, someone will ask about a solution to toenail fungus, and another user will respond with some suggestions.</p>
                <p id="directions">You will use a Reddit bot to get information about whether the comment with health advice contains misinformation. You can think of the Reddit bot as an automated system that you summon by making a Reddit comment using its name (e.g., '!healthadvicecheckbot').</p>
                <p id="directions">You will a see a post and a comment, and then <b> you will call the bot by commenting '!healthadvicecheckbot'.</b> When you summon our Reddit bot, it will make a comment that describes whether it thinks a prior comment contains misinformation related to health. </p>
                <p id="directions">Let's try an example.</p>
                <p id="directions">1. Read the Reddit post. <br />2. Read the comment. <br />3. Call the bot by typing '!healthadvicecheckbot'. <br />4. Read the bot's response. <br />5. Fill out the survey.  <br />6. Click the Continue button.</p>

            <div className="column-container"> 

            <div className="left-column"> 
                
                

                <div className="img-frame">
                    <p class="username"> Posted by user123 </p>
                    <h3 id="posttitle"> <b> Have any of you successfully treated/cured toenail fungus without going to the doctor? </b> </h3> 
                    <p id="posttext"> Not just "I heard this works" like I see on most sites/forums, but actual experiences doing so? I did 3 months of a Lamisil prescription from my doctor and it cleared up pretty much most of it but there's still some there and I ran out of Lamisil 2 months or so ago. I'm wondering if I should go through another round after asking my doctor or if there's something I can do at home that works well since my toenail fungus is fairly minor now. Thank you in advance :) </p>
                    <hr></hr>
                    <p class="username"> Commented by user789</p>
                    <p id="comment"> My aunt got toenail fungus from a sketchy pedicure place and someone (her doctor? some rando? IDK) told her to soak her foot in water with a little bit of tea tree oil for twenty minutes every evening, and it cleared up. </p>
                    <hr></hr>
                    <p class="username"> Writing a comment...</p>
                    <input type="text" id="textbox" placeholder="!healthadvicecheckbot" name="typedtext"></input>
                    <Button className="btn-2" id="replybutton" onClick={()=>{handlePredict()}}>
                       Reply
                    </Button> 

                    { showPrediction ?
                        <div>
                            <hr></hr>
                            <p class="username">Commented by HealthAdviceCheckBot</p>
                            <PredictionContainer 
                                currentPrediction={"The bot's response will appear here! The bot's reply will describe whether it thinks the comment by user789 contains misinformation. During the experiment, you will fill out a survey that will appear on the right side of the screen once you have read the bot's response."}
                            />
                        </div>
                    :
                        <>
                        </>

                    }

            <div> </div>


            

                </div>
                <p>     </p>


            </div>

            <div className="right-column"> 
            {showSurvey ? 
                <div> 
                    <div className="button-container"> 
                        <Button variant="btn btn-success"  style={{marginLeft:"70%"}}  onClick={nextChange}>
                            Continue
                        </Button>
                    </div> 
                    <div className="img-frame">The survey will appear here.</div> 
                    <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdoODu_KUojQFdWlMtdV5g3uz-P1bVTsqRPOeRH_Rc4pgb3fg/viewform?embedded=true" width="640" height="1694" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
                </div>
            : null}
                
                </div>
                </div>
                </div>


            :
                <> 
                <h1> Loading ...</h1>
                </>
            }
      </>
       
      );
}

export default TrainingContainer;