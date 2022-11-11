import React, { Component, useState, useEffect } from "react";
import {Button, Modal, Checkbox, Input, Radio} from 'antd'
import Popup from '../Popup';
import "antd/dist/antd.css";
import "../main.css";


import PredictionContainer from '../../../components/predictionContainer'

function Task1AContainer() {
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
            let count = imageCount + 1;
            // save data
            let data = {
                q_id: currentImage,
                user_id: localStorage.getItem("user-id"),
                ans: choice,
                time: ((Date.now() - taskTime) / 1000).toFixed(3)
            };
            console.log(data)
            sendData(data)
            if (count >= totalImages) {
                console.log('done with images')
                routeChange();
            } else {
                // reinitialize variables
                setChoice(0); 
                setImageCount(count);
                setCurrentImage(imageData[count].name);
                setCurrentPrediction(imageData[count].outputB);
                setCurrentTitle(imageData[count].title)
                setCurrentComment(imageData[count].comment)
                setCurrentPost(imageData[count].post)
                setTaskTime(Date.now())
                setShowPrediction(false);
                setShowSurvey(false);
            }
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
            setCurrentPrediction(data['imgs'][0].outputB);
            setRender(true);
            setTaskTime(Date.now())
        });
    }, []);



    return (
      <>
       {render ?

            <div className="container">
            <div className="title">Experiment C</div>
                <h3 id="directionsheader">Imagine you are scrolling through Reddit looking for a solution to a health problem you are currently experiencing.</h3>
                <p id="directions">1. Read the Reddit post. <br />2. Read the comment. <br />3. Call the bot by typing '!healthadvicecheckbot'. <br />4. Read the bot's response. <br />5. Fill out the survey. </p>

            <div className="column-container"> 

            <div className="left-column"> 
                
                

                <div className="img-frame">
                    <p class="username"> Posted by user123 </p>
                    <h3 id="posttitle"> <b> {currentTitle} </b> </h3> 
                    <p id="posttext"> {currentPost} </p>
                    <hr></hr>
                    <p class="username"> Commented by user789</p>
                    <p id="comment"> {currentComment} </p>
                    <hr></hr>
                    <p class="username"> Writing a comment...</p>
                    <input type="text" id="textbox" placeholder="!healthadvicecheckbot" name="typedtext"></input>
                    <Button className="btn-2" id="replybutton" onClick={()=>{handlePredict()}}>
                       Reply
                    </Button> 

                    { showPrediction ?
                        <div>
                            <hr></hr>
                            <p class="username">Posted by HealthAdviceCheckBot</p>
                            <PredictionContainer 
                                currentPrediction={currentPrediction}
                            />
                        </div>
                    :
                        <>
                        </>

                    }

            <div> </div>


            

                </div>
                <p> {imageCount + 1} / {totalImages} </p>


            </div>

            <div className="right-column"> 
            {showSurvey ? 
                <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSc2bYBWnfJDHVMm4bzyyZAckcDRnb4rTZ_XuPKrtObVVmNuEg/viewform?embedded=true" width="640" height="902" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe> : null}
                <div className="button-container"> 
                    <Button variant="btn btn-success"  style={{marginLeft:"70%"}}  onClick={nextChange}>
                        Continue
                    </Button>
                </div>
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

export default Task1AContainer;