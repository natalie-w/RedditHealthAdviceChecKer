import React, { Component, useState, useEffect } from "react";
import {Button, Modal, Checkbox, Input, Radio} from 'antd'
import Popup from '../Popup';
import "antd/dist/antd.css";
import "../main.css";


import PredictionContainer from '../../../components/predictionContainer'

function Task1AContainer() {
    const [text, setText] = useState("");
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

    const sentenceSubmit = (event) =>{ 
        event.preventDefault();
        setText("Please be patient, our model is running.");
        sendData(event.target[0].value).then(setText(event.target[0].value))

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

    const sendData = (obj) => {
        fetch('http://localhost:8080/modelPrediction', {
          method: 'POST',
          body: JSON.stringify(obj),
          headers: {
            "Content-type": "application/json; charset=UTF-8"
          }
        }).then(response => response.json())
          .then(message => {

            setText(message)
          })
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
            <div className="title">Model Demo</div>
                <h3 id="directionsheader">This section is to further explore our health advice misinformation model.</h3>
                <p id="directions">1. Add text of your choice to the textbox. <br />2. Press submit. <br />3. See model output. <br /><br /> 
                Consider trying one of the following statements: 
                <ul> 
                    <li>Apple cider vinegar can help with everything including diets.</li> 
                    <li>They are coated in toxic chemicals. Dryer sheets are one of the very worst things from a chemical allergy standpoint.</li> 
                    <li>Delayed release medication helps manage ADHD symptoms all day.</li> 
                    <li>There have been no deaths due to vaping. E-cigarettes do not cause any harm, especially to your lungs!</li> 
                    <li>It is all a lie created by big sunscreen! There is no link between sun exposure and skin cancer.</li> 
                </ul> 
                </p>

            <div> 

            <form onSubmit={sentenceSubmit}>
              <label>
                Input Sentence:
                <input type="text" placeholder="Bleach is a good treatment for Covid-19." name="name" style={{ width:"600px" }}/>
              </label>
              <input type="submit" value="Submit" />
            </form>
            <div>
                            <hr></hr>
                            <PredictionContainer 
                                currentPrediction={text}
                            />
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